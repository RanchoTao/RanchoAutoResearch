from __future__ import annotations

import argparse
import csv
import json
import random
import sys
import time
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.nn.functional as F
import yaml
from torch.utils.data import DataLoader

from analysis import fit_depth_models, jaccard, linear_cka
from model import Component, ModelSpec, TinyReasoner
from task import TaskSpec, generate_dataset, generate_paired_dataset


def component_name(component: Component) -> str:
    layer, kind, index = component
    return f"L{layer}H{index}" if kind == "head" else f"L{layer}MLP"


def seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def accuracy(logits: torch.Tensor, labels: torch.Tensor) -> float:
    return float((logits.argmax(dim=-1) == labels).float().mean().item())


@torch.no_grad()
def forward_batches(model: TinyReasoner, x: torch.Tensor, device: torch.device,
                    scales: torch.Tensor | None = None, batch_size: int = 512) -> torch.Tensor:
    chunks = []
    for start in range(0, len(x), batch_size):
        chunks.append(model(x[start:start + batch_size].to(device), scales=scales).cpu())
    return torch.cat(chunks)


@torch.no_grad()
def evaluate_validation(model: TinyReasoner, loader: DataLoader, depths: list[int],
                        device: torch.device) -> tuple[float, dict[int, float]]:
    correct = {d: 0 for d in depths}
    total = {d: 0 for d in depths}
    all_correct = 0
    all_total = 0
    model.eval()
    for x, y, d in loader:
        logits = model(x.to(device))
        pred = logits.argmax(dim=-1).cpu()
        for depth in depths:
            mask = d == depth
            correct[depth] += int((pred[mask] == y[mask]).sum())
            total[depth] += int(mask.sum())
        all_correct += int((pred == y).sum())
        all_total += len(y)
    return all_correct / all_total, {d: correct[d] / total[d] for d in depths}


def train_model(model: TinyReasoner, val_loader: DataLoader, depths: list[int],
                task_spec: TaskSpec, config: dict, device: torch.device,
                output_dir: Path, seed: int) -> dict:
    train_cfg = config["training"]
    optimizer = torch.optim.AdamW(
        model.parameters(), lr=float(train_cfg["learning_rate"]),
        weight_decay=float(train_cfg["weight_decay"])
    )
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
        optimizer, T_max=int(train_cfg["max_epochs"])
    )
    use_amp = device.type == "cuda"
    best_macro = -1.0
    best_epoch = 0
    stale = 0
    target_streak = 0
    history = []
    started = time.perf_counter()
    for epoch in range(1, int(train_cfg["max_epochs"]) + 1):
        # A fresh procedural sample each epoch prevents the high-capacity model
        # from memorizing a fixed finite graph set instead of learning traversal.
        train_epoch = generate_dataset(
            int(config["task"]["train_examples"]), depths, seed + 1000 + epoch,
            task_spec,
        )
        train_loader = DataLoader(
            train_epoch, batch_size=int(train_cfg["batch_size"]), shuffle=True,
            pin_memory=True, num_workers=0,
        )
        model.train()
        loss_sum = 0.0
        seen = 0
        for x, y, _ in train_loader:
            x, y = x.to(device, non_blocking=True), y.to(device, non_blocking=True)
            optimizer.zero_grad(set_to_none=True)
            with torch.autocast(device_type=device.type, dtype=torch.bfloat16, enabled=use_amp):
                logits = model(x)
                loss = F.cross_entropy(logits, y)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            loss_sum += float(loss.item()) * len(y)
            seen += len(y)
        scheduler.step()
        macro, by_depth = evaluate_validation(model, val_loader, depths, device)
        min_depth = min(by_depth.values())
        row = {"epoch": epoch, "loss": loss_sum / seen, "macro_accuracy": macro,
               "min_depth_accuracy": min_depth, **{f"depth_{d}": by_depth[d] for d in depths}}
        history.append(row)
        print(json.dumps(row), flush=True)
        if macro > best_macro + 1e-5:
            best_macro = macro
            best_epoch = epoch
            stale = 0
            torch.save(model.state_dict(), output_dir / "model.pt")
        else:
            stale += 1
        if min_depth >= float(train_cfg["accuracy_target"]):
            target_streak += 1
        else:
            target_streak = 0
        if target_streak >= 3:
            break
        if stale >= int(train_cfg["patience"]) and epoch >= 20:
            break
    runtime = time.perf_counter() - started
    model.load_state_dict(torch.load(output_dir / "model.pt", map_location=device, weights_only=True))
    macro, by_depth = evaluate_validation(model, val_loader, depths, device)
    with (output_dir / "training_history.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(history[0]))
        writer.writeheader()
        writer.writerows(history)
    return {"best_epoch": best_epoch, "runtime_seconds": runtime,
            "macro_accuracy": macro, "accuracy_by_depth": by_depth,
            "target_met_all_depths": min(by_depth.values()) >= float(train_cfg["accuracy_target"])}


def logit_margin(logits: torch.Tensor, positive: torch.Tensor,
                 negative: torch.Tensor | None = None) -> torch.Tensor:
    positive_logit = logits.gather(1, positive[:, None]).squeeze(1)
    if negative is not None:
        negative_logit = logits.gather(1, negative[:, None]).squeeze(1)
    else:
        masked = logits.clone()
        masked.scatter_(1, positive[:, None], float("-inf"))
        negative_logit = masked.max(dim=1).values
    return positive_logit - negative_logit


@torch.no_grad()
def discover_depth_circuits(model: TinyReasoner, paired: dict[int, dict[str, torch.Tensor]],
                            depths: list[int], device: torch.device, fidelity: float,
                            random_controls: int, seed: int) -> tuple[dict, list[dict]]:
    model.eval()
    results: dict = {}
    score_rows: list[dict] = []
    rng = random.Random(seed + 991)
    for depth in depths:
        batch = paired[depth]
        clean_x = batch["clean_x"].to(device)
        corrupt_x = batch["corrupt_x"].to(device)
        clean_y = batch["clean_y"].to(device)
        corrupt_y = batch["corrupt_y"].to(device)
        clean_logits, clean_cache, _ = model(clean_x, return_cache=True)
        corrupt_logits = model(corrupt_x)
        valid = ((clean_logits.argmax(-1) == clean_y) &
                 (corrupt_logits.argmax(-1) == corrupt_y))
        if int(valid.sum()) < 32:
            raise RuntimeError(f"Only {int(valid.sum())} correct clean/corrupt pairs at depth {depth}")
        clean_x, corrupt_x = clean_x[valid], corrupt_x[valid]
        clean_y, corrupt_y = clean_y[valid], corrupt_y[valid]
        clean_logits, clean_cache, _ = model(clean_x, return_cache=True)
        corrupt_logits = model(corrupt_x)
        clean_margin = logit_margin(clean_logits, clean_y)
        corrupt_pair_margin = logit_margin(corrupt_logits, clean_y, corrupt_y)

        patch_scores: dict[Component, float] = {}
        ablation_scores: dict[Component, float] = {}
        for component in model.components:
            patched = model(corrupt_x, patch={component: clean_cache[component]})
            patch_effect = logit_margin(patched, clean_y, corrupt_y) - corrupt_pair_margin
            scales = model.scales_for(disabled={component})
            ablated = model(clean_x, scales=scales)
            ablation_effect = clean_margin - logit_margin(ablated, clean_y)
            patch_scores[component] = float(patch_effect.mean().item())
            ablation_scores[component] = float(ablation_effect.mean().item())
            score_rows.append({
                "depth": depth, "component": component_name(component),
                "method": "activation_patching", "score": patch_scores[component],
            })
            score_rows.append({
                "depth": depth, "component": component_name(component),
                "method": "zero_ablation", "score": ablation_scores[component],
            })

        method_result = {}
        full_accuracy = accuracy(clean_logits, clean_y)
        for method, scores in (("activation_patching", patch_scores),
                               ("zero_ablation", ablation_scores)):
            ranking = sorted(model.components, key=lambda c: scores[c], reverse=True)
            selected: set[Component] = set()
            retain_curve = []
            threshold = fidelity * full_accuracy
            for component in ranking:
                selected.add(component)
                retained_logits = model(clean_x, scales=model.scales_for(enabled=selected))
                retained_accuracy = accuracy(retained_logits, clean_y)
                retain_curve.append(retained_accuracy)
                if retained_accuracy >= threshold:
                    break
            retained_logits = model(clean_x, scales=model.scales_for(enabled=selected))
            ablated_logits = model(clean_x, scales=model.scales_for(disabled=selected))
            random_retain, random_ablate = [], []
            for _ in range(random_controls):
                random_set = set(rng.sample(model.components, len(selected)))
                random_retain.append(accuracy(
                    model(clean_x, scales=model.scales_for(enabled=random_set)), clean_y
                ))
                random_ablate.append(accuracy(
                    model(clean_x, scales=model.scales_for(disabled=random_set)), clean_y
                ))
            method_result[method] = {
                "ranking": [component_name(c) for c in ranking],
                "selected": [component_name(c) for c in sorted(selected)],
                "selected_components": selected,
                "size": len(selected),
                "retain_curve": retain_curve,
                "retained_accuracy": accuracy(retained_logits, clean_y),
                "circuit_ablated_accuracy": accuracy(ablated_logits, clean_y),
                "random_retain_accuracy_mean": float(np.mean(random_retain)),
                "random_retain_accuracy_sd": float(np.std(random_retain, ddof=1)),
                "random_ablate_accuracy_mean": float(np.mean(random_ablate)),
                "random_ablate_accuracy_sd": float(np.std(random_ablate, ddof=1)),
            }
        results[depth] = {
            "n_correct_pairs": int(valid.sum()),
            "full_accuracy": full_accuracy,
            "method_jaccard": jaccard(
                method_result["activation_patching"]["selected_components"],
                method_result["zero_ablation"]["selected_components"],
            ),
            "methods": method_result,
        }
        print(f"depth={depth} pairs={int(valid.sum())} sizes="
              f"{method_result['activation_patching']['size']}/"
              f"{method_result['zero_ablation']['size']}", flush=True)
    return results, score_rows


@torch.no_grad()
def representation_analysis(model: TinyReasoner, spec: TaskSpec, depths: list[int],
                            n: int, seed: int, device: torch.device) -> dict:
    representations = {}
    for depth in depths:
        batch = generate_paired_dataset(n, [depth], seed, spec)[depth]
        _, _, reps = model(batch["clean_x"].to(device), return_representations=True)
        representations[depth] = [value.cpu().numpy() for value in reps]
    adjacent = {}
    for left, right in zip(depths[:-1], depths[1:]):
        adjacent[f"{left}-{right}"] = [
            linear_cka(representations[left][layer], representations[right][layer])
            for layer in range(len(representations[left]))
        ]
    return {"adjacent_cka_by_layer": adjacent}


def serializable_circuits(circuits: dict) -> dict:
    output = {}
    for depth, record in circuits.items():
        output[str(depth)] = {k: v for k, v in record.items() if k != "methods"}
        output[str(depth)]["methods"] = {}
        for method, values in record["methods"].items():
            output[str(depth)]["methods"][method] = {
                k: v for k, v in values.items() if k != "selected_components"
            }
    return output


def make_figures(circuits: dict, representation: dict, depths: list[int],
                 figures_dir: Path) -> None:
    figures_dir.mkdir(parents=True, exist_ok=True)
    methods = ["activation_patching", "zero_ablation"]
    labels = {"activation_patching": "Activation patching", "zero_ablation": "Zero ablation"}

    fig, ax = plt.subplots(figsize=(6, 4))
    for method in methods:
        ax.plot(depths, [circuits[d]["methods"][method]["size"] for d in depths],
                marker="o", label=labels[method])
    ax.set(xlabel="Reasoning depth", ylabel="Causal circuit size (components)", xticks=depths)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(figures_dir / "figure1_circuit_size.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6, 4))
    x = depths[1:]
    for method in methods:
        overlap = []
        for left, right in zip(depths[:-1], depths[1:]):
            a = circuits[left]["methods"][method]["selected_components"]
            b = circuits[right]["methods"][method]["selected_components"]
            overlap.append(jaccard(a, b))
        ax.plot(x, overlap, marker="o", label=labels[method])
    ax.set(xlabel="Deeper member of adjacent pair", ylabel="Adjacent circuit Jaccard", xticks=x,
           ylim=(-0.03, 1.03))
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(figures_dir / "figure2_adjacent_overlap.png", dpi=180)
    plt.close(fig)

    method = "zero_ablation"
    n_layers = max(c[0] for c in next(iter(circuits.values()))["methods"][method]["selected_components"]) + 1
    heatmap = np.zeros((n_layers, len(depths)))
    for column, depth in enumerate(depths):
        selected = circuits[depth]["methods"][method]["selected_components"]
        for layer in range(n_layers):
            heatmap[layer, column] = sum(c[0] == layer for c in selected) / max(1, len(selected))
    fig, ax = plt.subplots(figsize=(6, 4))
    image = ax.imshow(heatmap, aspect="auto", origin="lower", cmap="viridis")
    ax.set(xlabel="Reasoning depth", ylabel="Transformer layer",
           xticks=range(len(depths)), xticklabels=depths, yticks=range(n_layers))
    fig.colorbar(image, ax=ax, label="Fraction of circuit")
    fig.tight_layout()
    fig.savefig(figures_dir / "figure3_layer_depth_heatmap.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 4))
    width = 0.2
    positions = np.arange(len(depths))
    full = [circuits[d]["full_accuracy"] for d in depths]
    retained = [circuits[d]["methods"][method]["retained_accuracy"] for d in depths]
    ablated = [circuits[d]["methods"][method]["circuit_ablated_accuracy"] for d in depths]
    random_ablated = [circuits[d]["methods"][method]["random_ablate_accuracy_mean"] for d in depths]
    for offset, values, label in ((-1.5, full, "Full"), (-0.5, retained, "Retained circuit"),
                                  (0.5, ablated, "Circuit ablated"),
                                  (1.5, random_ablated, "Random ablation")):
        ax.bar(positions + offset * width, values, width, label=label)
    ax.set(xlabel="Reasoning depth", ylabel="Accuracy on correct-only paired subset",
           xticks=positions, xticklabels=depths, ylim=(0, 1.05))
    ax.legend(frameon=False, ncol=2)
    fig.tight_layout()
    fig.savefig(figures_dir / "figure4_ablation_performance.png", dpi=180)
    plt.close(fig)

    cka = np.asarray(list(representation["adjacent_cka_by_layer"].values()))
    fig, ax = plt.subplots(figsize=(7, 3.5))
    image = ax.imshow(cka, aspect="auto", cmap="magma", vmin=0, vmax=1)
    ax.set(xlabel="Representation stage (0=embedding)", ylabel="Adjacent depths",
           yticks=range(len(cka)), yticklabels=list(representation["adjacent_cka_by_layer"]))
    fig.colorbar(image, ax=ax, label="Linear CKA")
    fig.tight_layout()
    fig.savefig(figures_dir / "figure5_representation_cka.png", dpi=180)
    plt.close(fig)


def write_tables(circuits: dict, depths: list[int], output_dir: Path,
                 score_rows: list[dict]) -> None:
    with (output_dir / "component_scores.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["depth", "component", "method", "score"])
        writer.writeheader()
        writer.writerows(score_rows)
    rows = []
    for depth in depths:
        for method in ("activation_patching", "zero_ablation"):
            record = circuits[depth]["methods"][method]
            rows.append({
                "depth": depth, "method": method, "n_correct_pairs": circuits[depth]["n_correct_pairs"],
                "full_accuracy": circuits[depth]["full_accuracy"], "circuit_size": record["size"],
                "retained_accuracy": record["retained_accuracy"],
                "circuit_ablated_accuracy": record["circuit_ablated_accuracy"],
                "random_retain_accuracy_mean": record["random_retain_accuracy_mean"],
                "random_ablate_accuracy_mean": record["random_ablate_accuracy_mean"],
                "cross_method_jaccard": circuits[depth]["method_jaccard"],
            })
    with (output_dir / "circuit_summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()
    config_path = args.config.resolve()
    arc_root = config_path.parent.parent
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    output_dir = (arc_root / config["output_dir"]).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    figures_dir = arc_root / "figures"
    seed = int(config["seed"])
    seed_everything(seed)
    if not torch.cuda.is_available():
        raise RuntimeError("ARC-02 MVP requires the audited CUDA device")
    device = torch.device("cuda")
    torch.backends.cuda.matmul.allow_tf32 = True

    task_cfg = config["task"]
    depths = [int(value) for value in task_cfg["depths"]]
    task_spec = TaskSpec(entities=int(task_cfg["entities"]), edges=int(task_cfg["edges"]),
                         max_depth=max(depths))
    validation = generate_dataset(int(task_cfg["validation_examples"]), depths, seed + 2, task_spec)
    batch_size = int(config["training"]["batch_size"])
    val_loader = DataLoader(validation, batch_size=batch_size, shuffle=False, pin_memory=True,
                            num_workers=0)

    model_cfg = config["model"]
    model_spec = ModelSpec(
        vocab_size=task_spec.vocab_size, max_seq_len=task_spec.sequence_length,
        n_entities=task_spec.entities, d_model=int(model_cfg["d_model"]),
        n_layers=int(model_cfg["n_layers"]), n_heads=int(model_cfg["n_heads"]),
        d_mlp=int(model_cfg["d_mlp"]),
    )
    model = TinyReasoner(model_spec).to(device)
    parameter_count = sum(p.numel() for p in model.parameters())
    print(f"device={torch.cuda.get_device_name(0)} parameters={parameter_count}", flush=True)
    overall_started = time.perf_counter()
    training = train_model(model, val_loader, depths, task_spec, config, device,
                           output_dir, seed)
    if not training["target_met_all_depths"]:
        raise RuntimeError(f"Accuracy control failed: {training['accuracy_by_depth']}")

    paired = {
        depth: generate_paired_dataset(
            int(task_cfg["circuit_examples_per_depth"]), [depth], seed + 100, task_spec
        )[depth]
        for depth in depths
    }
    circuits, score_rows = discover_depth_circuits(
        model, paired, depths, device,
        float(config["circuit"]["fidelity_fraction"]),
        int(config["circuit"]["random_controls"]), seed,
    )
    representation = representation_analysis(
        model, task_spec, depths,
        min(256, int(task_cfg["circuit_examples_per_depth"])), seed + 200, device
    )
    phase_models = {}
    for method in ("activation_patching", "zero_ablation"):
        phase_models[method] = fit_depth_models(
            depths, [circuits[d]["methods"][method]["size"] for d in depths]
        )
    total_runtime = time.perf_counter() - overall_started
    result = {
        "seed": seed,
        "device": torch.cuda.get_device_name(0),
        "parameter_count": parameter_count,
        "training": training,
        "circuits": serializable_circuits(circuits),
        "representation": representation,
        "phase_models": phase_models,
        "total_runtime_seconds": total_runtime,
        "torch_cuda_max_memory_bytes": int(torch.cuda.max_memory_allocated()),
    }
    (output_dir / "results.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    write_tables(circuits, depths, output_dir, score_rows)
    make_figures(circuits, representation, depths, figures_dir)
    print(json.dumps({"status": "complete", "output": str(output_dir),
                      "runtime_seconds": total_runtime}), flush=True)


if __name__ == "__main__":
    main()
