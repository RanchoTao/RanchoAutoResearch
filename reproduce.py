#!/usr/bin/env python3
"""Validate frozen inputs and render arXiv v1 cached displays in a disposable copy."""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import io
import json
import os
from pathlib import Path, PurePosixPath
import platform
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time

ROOT = Path(__file__).resolve().parent
RELEASE = ROOT / "releases/arxiv-2610.01165"
COMMANDS = (
    "anc/source/analysis/make_tables.py",
    "anc/source/analysis/plot_figures.py",
    "anc/source/dense/build_dense_figures.py",
    "anc/source/overview/build_overview.py",
)


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def safe_path(root: Path, name: str) -> Path:
    relative = PurePosixPath(name)
    if relative.is_absolute() or ".." in relative.parts or "\\" in name:
        raise ValueError(f"Unsafe input path: {name}")
    target = root.joinpath(*relative.parts)
    if not target.resolve().is_relative_to(root.resolve()):
        raise ValueError(f"Input escapes its root: {name}")
    return target


def verify_manifest(root: Path, manifest: Path) -> int:
    count = 0
    for line in manifest.read_text(encoding="utf-8").splitlines():
        expected, name = line.split("  ", 1)
        path = safe_path(root, name)
        if not path.is_file() or digest(path) != expected.lower():
            raise ValueError(f"Missing or hash-mismatched input: {name}; restore the pinned cache, do not recompute it.")
        count += 1
    return count


def extract_snapshot(archive: Path, target: Path) -> list[str]:
    # Reject links, devices, duplicate paths and traversal before extracting anything.
    names = set()
    arrays = []
    with tarfile.open(archive, "r:gz") as source:
        members = source.getmembers()
        for member in members:
            safe_path(target, member.name)
            if member.name in names or not (member.isfile() or member.isdir()):
                raise ValueError(f"Unsupported archive member: {member.name}")
            names.add(member.name)
        for member in members:
            path = safe_path(target, member.name)
            if member.isdir():
                path.mkdir(parents=True, exist_ok=True)
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                with source.extractfile(member) as stream, path.open("xb") as output:
                    shutil.copyfileobj(stream, output)
                if member.name.startswith("anc/source/data/broad/") and member.name.endswith(".npy"):
                    arrays.append(member.name)
    return arrays


def restore_counts(work: Path, arrays: list[str]) -> str:
    """Reverse arXiv's ZIP expansion; require the original exported NPZ hash."""
    target = work / "anc/source/data/broad/window_counts.npz"
    if not target.exists():
        import numpy as np
        buffer = io.BytesIO()
        values = {Path(name).stem: np.load(work / name, allow_pickle=False) for name in arrays}
        np.savez_compressed(buffer, **values)
        target.write_bytes(buffer.getvalue())
    expected = next(line.split("  ", 1)[0] for line in
                    (work / "anc/SHA256SUMS.txt").read_text().splitlines()
                    if line.endswith("  source/data/broad/window_counts.npz"))
    if digest(target) != expected:
        raise ValueError("Cannot restore byte-identical window_counts.npz from the arXiv-expanded arrays.")
    return expected


def inventory(root: Path) -> dict[str, str]:
    return {p.relative_to(root).as_posix(): digest(p) for p in sorted(root.rglob("*")) if p.is_file()}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify-only", action="store_true", help="Standard-library archive and legacy hash verification only")
    parser.add_argument("--output", type=Path, default=ROOT.parent / "reproduced-arxiv-2610.01165")
    parser.add_argument("--allow-version-mismatch", action="store_true", help="Record a display-only diagnostic run with different package versions")
    args = parser.parse_args()
    spec = json.loads((RELEASE / "dependencies.json").read_text())
    archive = RELEASE / "source-v1.tar.gz"
    legacy = RELEASE / "legacy-inputs.sha256"
    if digest(archive) != spec["release_archive"]["sha256"] or digest(legacy) != spec["legacy_manifest_sha256"]:
        raise ValueError("Pinned archive or legacy manifest has changed")
    legacy_count = verify_manifest(ROOT, legacy)
    if args.verify_only:
        print(json.dumps({"archive_hash": "PASS", "legacy_inputs_verified": legacy_count,
                          "clean_room_inference": "NOT_RUN", "display_generation": "NOT_RUN"}, indent=2))
        return 0
    versions = {name: importlib.metadata.version(name) for name in spec["display_environment"]["packages"]}
    mismatches = {name: {"expected": expected, "actual": versions[name]} for name, expected
                  in spec["display_environment"]["packages"].items() if versions[name] != expected}
    if mismatches and not args.allow_version_mismatch:
        raise ValueError(f"Display dependency versions differ: {mismatches}. Install requirements-display.txt or explicitly allow a diagnostic mismatch.")
    output = args.output.expanduser().resolve()
    if output.is_relative_to(ROOT) or ROOT.is_relative_to(output):
        raise ValueError("Output must be outside the repository and must not contain it")
    output.mkdir(parents=True, exist_ok=False)
    receipt = {"arxiv": "2610.01165v1", "status": "RUNNING", "scope": "cached table checks and display generation",
               "clean_room_inference": "NOT_RUN", "statistical_resampling": "NOT_RUN", "model_inference": "NOT_RUN",
               "archive_sha256": digest(archive), "legacy_inputs_verified": legacy_count,
               "python": sys.version, "platform": platform.platform(), "packages": versions,
               "version_mismatches": mismatches, "commands": []}
    started = time.monotonic()
    try:
        with tempfile.TemporaryDirectory(prefix="arxiv-2610.01165-") as temporary:
            work = Path(temporary) / "source"
            work.mkdir()
            arrays = extract_snapshot(archive, work)
            receipt["restored_window_counts_sha256"] = restore_counts(work, arrays)
            receipt["ancillary_inputs_verified"] = verify_manifest(work / "anc", work / "anc/SHA256SUMS.txt")
            frozen = inventory(work)
            # These four reviewed rendering commands have no acquisition path.
            # Block networking in their Python processes as a further offline guard.
            guard = Path(temporary) / "guard"
            guard.mkdir()
            (guard / "sitecustomize.py").write_text(
                "import socket\ndef blocked(*a, **k): raise RuntimeError('Cached reproduction forbids network access')\n"
                "socket.create_connection=blocked\nsocket.socket.connect=blocked\nsocket.socket.connect_ex=blocked\n")
            env = dict(os.environ, HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1", HF_DATASETS_OFFLINE="1",
                       WANDB_MODE="offline", CUDA_VISIBLE_DEVICES="", MPLBACKEND="Agg", PYTHONDONTWRITEBYTECODE="1",
                       PYTHONPATH=str(guard), MPLCONFIGDIR=str(Path(temporary) / "matplotlib"))
            for index, script in enumerate(COMMANDS, 1):
                result = subprocess.run([sys.executable, script], cwd=work, env=env, text=True,
                                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=300)
                (output / f"{index:02d}-{Path(script).stem}.log").write_text(result.stdout, encoding="utf-8")
                receipt["commands"].append({"script": script, "returncode": result.returncode})
                if result.returncode:
                    raise RuntimeError(f"Display command failed: {script}; see output log")
            # Only existing validation records are expected to change in the disposable copy.
            for name, expected in frozen.items():
                if not name.startswith("anc/validation/") and digest(work / name) != expected:
                    raise ValueError(f"A cached/source/canonical input was modified in the disposable copy: {name}")
            for directory in ("anc/generated", "anc/validation", "anc/source/dense/qa"):
                shutil.copytree(work / directory, output / Path(directory).name)
            dense = output / "dense"
            dense.mkdir()
            for path in (work / "anc/source/dense").iterdir():
                if path.is_file() and path.suffix in (".pdf", ".svg", ".png"):
                    shutil.copy2(path, dense / path.name)
            canonical_tables = work / "tables"
            generated_tables = output / "generated/tables"
            comparison = {p.name: digest(p) == digest(generated_tables / p.name) for p in canonical_tables.glob("*.tex")}
            receipt["canonical_table_byte_comparison"] = comparison
            if len(comparison) != 11 or not all(comparison.values()):
                raise ValueError("Generated tables differ from the 11 canonical arXiv v1 tables")
            expected_panels = json.loads((work / "anc/source/figure_sources.json").read_text())
            for name in expected_panels:
                if not (output / f"generated/figures/{name}.pdf").is_file():
                    raise ValueError(f"Missing regenerated panel: {name}")
            for name in ("generated/figures/fig1_dense.pdf", "dense/fig2_dense.pdf", "dense/fig3_dense.pdf"):
                if not (output / name).is_file():
                    raise ValueError(f"Missing dense manuscript figure: {name}")
            receipt["display_files_sha256"] = inventory(output)
            receipt["legacy_inputs_verified_after"] = verify_manifest(ROOT, legacy)
            if digest(archive) != spec["release_archive"]["sha256"]:
                raise ValueError("Source archive changed during display generation")
            receipt["status"] = "PASS"
    except Exception as error:
        receipt["status"] = "FAIL"
        receipt["error"] = str(error)
        raise
    finally:
        receipt["elapsed_seconds"] = time.monotonic() - started
        (output / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": receipt["status"], "output": str(output), "clean_room_inference": "NOT_RUN"}, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, RuntimeError, OSError, importlib.metadata.PackageNotFoundError) as error:
        print(f"Cached reproduction stopped: {error}", file=sys.stderr)
        raise SystemExit(1)
