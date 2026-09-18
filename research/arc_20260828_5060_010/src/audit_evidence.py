"""Recompute headline values, verify seals, and write the ARC-010 evidence ledger."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]


def load(relative: str):
    return json.loads((REPO / relative).read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def verify_manifest(base: Path, manifest: Path) -> list[str]:
    failures = []
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        expected, relative = line.split(maxsplit=1)
        path = base / relative.strip()
        if not path.is_file() or sha(path) != expected.upper():
            failures.append(relative.strip())
    return failures


def ledger_row(**kwargs):
    columns = [
        "claim_id", "proposed_claim_text", "supporting_arcs", "experimental_unit",
        "n", "point_estimate", "ci_uncertainty", "seed_robustness",
        "scale_robustness", "intervention_robustness", "corpus_robustness",
        "assay_status", "preregistered_or_exploratory", "evidence_status",
        "strongest_counterevidence", "safe_paper_wording", "prohibited_overclaim",
        "source_path",
    ]
    return {column: kwargs.get(column, "") for column in columns}


def main() -> None:
    arc3 = load("meta_arc05/ARC-20260826-5060-003/results/independent_run_summary.json")
    arc4 = load("research/arc_20260826_5060_004/results/mechanism_summary.json")
    arc5 = load("research/arc_20260826_5060_005/results/family_robustness_summary.json")
    arc6 = load("research/arc_20260827_5060_006R/results/corrected_summary.json")
    arc7 = load("research/arc_20260827_5060_007R/results/geometry_summary.json")
    arc8 = load("research/arc_20260827_5060_008/results.json")
    arc9 = load("research/arc_20260828_5060_009/feasibility_summary.json")

    deltas = np.asarray([row["delta_agreement"] for row in arc3["primary"]["individual_runs"]])
    checks = {
        "arc3_9_runs": len(deltas) == 9,
        "arc3_mean": np.isclose(deltas.mean(), -0.10352768132716048),
        "arc3_median": np.isclose(np.median(deltas), -0.10410156250000013),
        "arc3_9_negative": int((deltas < 0).sum()) == 9,
        "arc4_magnitude_matched": np.isclose(
            arc4["experiment_a_magnitude_matched"]["mean_run_median_contrast"], 0.04296875
        ),
        "arc4_damage_matched": np.isclose(
            arc4["experiment_b_damage_matched"]["mean_run_median_contrast"],
            0.0024594907407407343,
        ),
        "arc5_5_negative": arc5["test_a_sign"]["negative_runs"] == 5,
        "arc6_corrected_residual": np.isclose(
            arc6["summaries"]["canonical_argmax"]["estimate"], -0.01683304398148147
        ),
        "arc6_old_invalidated": np.isclose(arc6["old_arc006_residual"], -0.019234664351851838),
        "arc7_geometry_shrinkage": np.isclose(arc7["m3_shrinkage"], 0.20178702330946507),
        "arc8_not_revealed": arc8["stage_b"]["heldout_ds_revealed"] is False,
        "arc9_pass_a": arc9["pass_a"] == 47,
        "arc9_verdict": arc9["verdict"] == "ALPHA-NOT-FEASIBLE",
    }

    seal_failures = {
        "arc003": verify_manifest(
            REPO / "meta_arc05/ARC-20260826-5060-003",
            REPO / "meta_arc05/ARC-20260826-5060-003/reports/final_artifact_manifest.sha256",
        ),
        "arc004": verify_manifest(
            REPO / "research/arc_20260826_5060_004",
            REPO / "research/arc_20260826_5060_004/final_artifact_manifest.sha256",
        ),
    }
    for name in ("006R", "007R", "008", "009"):
        date = "20260827" if name in {"006R", "007R", "008"} else "20260828"
        base = REPO / f"research/arc_{date}_5060_{name}"
        seal_failures[f"arc{name.lower()}"] = verify_manifest(base, base / "final_integrity.sha256")

    lock_text = (REPO / "research/arc_20260826_5060_005/integrity_lock.md").read_text(encoding="utf-8")
    expected_match = re.search(r"Summary SHA-256:\s*`([A-Fa-f0-9]+)`", lock_text, flags=re.S)
    expected_arc5 = expected_match.group(1).upper() if expected_match else "MISSING"
    actual_arc5 = sha(REPO / "research/arc_20260826_5060_005/results/family_robustness_summary.json")
    checks["arc5_summary_lock"] = actual_arc5 == expected_arc5
    checks["all_available_seals"] = all(not failures for failures in seal_failures.values())
    if not all(checks.values()):
        raise RuntimeError(json.dumps({"checks": checks, "seal_failures": seal_failures}, indent=2))

    rows = [
        ledger_row(
            claim_id="C01", proposed_claim_text="Block-bypass top-1 substitutability declines over Pythia-160M pretraining.",
            supporting_arcs="ARC-003", experimental_unit="independent PolyPythias-160M pretraining run",
            n="9 runs; 5 checkpoints; 10 interior layers; 3 evaluation shards",
            point_estimate=f"mean DeltaS={deltas.mean():.9f}; median={np.median(deltas):.9f}",
            ci_uncertainty="run-bootstrap 95% CI [-0.111494502,-0.095847620]",
            seed_robustness="9/9 negative; all leave-one-run-out medians negative",
            scale_robustness="same direction at 70M (5/5), but only two small scales",
            intervention_robustness="qualitative direction later reproduced with additive activation noise",
            corpus_robustness="one WikiText-2 source only", assay_status="VALID; frozen evaluator and endpoint checks passed",
            preregistered_or_exploratory="preregistered independent-run test; seed9 prospectively held out",
            evidence_status="VALID", strongest_counterevidence="single corpus; tiny Pythia scales; no downstream outcome",
            safe_paper_wording="Across nine independent Pythia-160M runs on the frozen WikiText-2 assay, later checkpoints preserve fewer intact top-1 predictions after one interior-block bypass.",
            prohibited_overclaim="Pretraining universally makes Transformer layers causally specialized.",
            source_path="meta_arc05/ARC-20260826-5060-003/results/independent_run_summary.json",
        ),
        ledger_row(
            claim_id="C02", proposed_claim_text="The endpoint direction prospectively replicates in held-out seed9.",
            supporting_arcs="ARC-003", experimental_unit="held-out pretraining run",
            n="1 held-out run; 3 evaluation shards", point_estimate="DeltaS=-0.1189453125",
            ci_uncertainty="inside frozen prediction interval [-0.134625,-0.063661]",
            seed_robustness="held-out run negative; 3/3 shards negative", scale_robustness="160M only",
            intervention_robustness="block bypass only", corpus_robustness="WikiText-2 only",
            assay_status="VALID", preregistered_or_exploratory="prospectively preregistered",
            evidence_status="VALID", strongest_counterevidence="single held-out run",
            safe_paper_wording="A prospectively frozen ninth run reproduced the sign and fell inside the predicted magnitude range.",
            prohibited_overclaim="A single held-out run proves population-wide universality.",
            source_path="meta_arc05/ARC-20260826-5060-003/reports/heldout_run_prediction.md",
        ),
        ledger_row(
            claim_id="C03", proposed_claim_text="The decline survives intact-confidence and competence controls.",
            supporting_arcs="ARC-003", experimental_unit="run x fixed intact-confidence bin",
            n="45 eligible run-bin contrasts", point_estimate="45/45 negative; mean matched change -0.113884",
            ci_uncertainty="bin-specific descriptive changes; no causal CI", seed_robustness="all nine runs represented",
            scale_robustness="70M controls also directionally supportive in prior ARC-002",
            intervention_robustness="noise-family confidence control 25/25 negative in ARC-005",
            corpus_robustness="WikiText-2 only", assay_status="VALID",
            preregistered_or_exploratory="preregistered fixed-bin robustness",
            evidence_status="VALID", strongest_counterevidence="fixed bins are not exact propensity matching",
            safe_paper_wording="The endpoint decline is not removed by fixed intact-confidence stratification, while intact NLL improves.",
            prohibited_overclaim="Confidence and token difficulty are fully controlled.",
            source_path="meta_arc05/ARC-20260826-5060-003/results/independent_run_summary.json",
        ),
        ledger_row(
            claim_id="C04", proposed_claim_text="The endpoint decline is broad across interior block locations.",
            supporting_arcs="ARC-003", experimental_unit="run x deleted interior layer",
            n="90 run-layer contrasts", point_estimate="90/90 negative; 10/10 layer medians negative",
            ci_uncertainty="layer medians range -0.065321 to -0.183811",
            seed_robustness="nine runs", scale_robustness="160M layer breadth only",
            intervention_robustness="location pattern not tested identically across families",
            corpus_robustness="WikiText-2 only", assay_status="VALID",
            preregistered_or_exploratory="preregistered robustness control", evidence_status="VALID",
            strongest_counterevidence="effect magnitude is strongly layer-dependent",
            safe_paper_wording="The direction holds for every tested interior run-layer pair, with substantial location-dependent magnitude.",
            prohibited_overclaim="Layer location is irrelevant.",
            source_path="meta_arc05/ARC-20260826-5060-003/results/layer_endpoint_deltas.csv",
        ),
        ledger_row(
            claim_id="C05", proposed_claim_text="The direction replicates at a second small Pythia scale.",
            supporting_arcs="ARC-002/ARC-003", experimental_unit="independent PolyPythias-70M run",
            n="5 runs", point_estimate="median DeltaS=-0.143338; 5/5 negative",
            ci_uncertainty="run-bootstrap 95% CI [-0.153852,-0.110297]",
            seed_robustness="5/5 negative", scale_robustness="70M and 160M only",
            intervention_robustness="block bypass", corpus_robustness="WikiText-2 only",
            assay_status="VALID; reused without retuning", preregistered_or_exploratory="confirmatory reuse after primary gate",
            evidence_status="VALID", strongest_counterevidence="both scales are small and same architecture family",
            safe_paper_wording="The endpoint direction also appears in five 70M runs; this is two-small-scale replication, not a scaling law.",
            prohibited_overclaim="The result scales to large language models.",
            source_path="meta_arc05/ARC-20260826-5060-003/results/independent_run_summary.json",
        ),
        ledger_row(
            claim_id="C06", proposed_claim_text="Substitutability decreases monotonically at every checkpoint.",
            supporting_arcs="ARC-002/ARC-003", experimental_unit="checkpoint trajectory",
            n="five public checkpoints per run", point_estimate="strict monotonicity observed at 160M ARC-003 but contradicted at 70M and not required by contract",
            ci_uncertainty="no change-point or monotonic-law inference", seed_robustness="trajectory shape not stable across all earlier runs",
            scale_robustness="fails as a universal two-scale statement", intervention_robustness="not established",
            corpus_robustness="not established", assay_status="VALID data; over-broad claim",
            preregistered_or_exploratory="not a required gate", evidence_status="INVALIDATED",
            strongest_counterevidence="70M intermediate rebounds and sparse checkpoints",
            safe_paper_wording="Early-to-late decline is supported; strict checkpoint-by-checkpoint monotonicity is not claimed.",
            prohibited_overclaim="A universal smooth training law or phase transition.",
            source_path="meta_arc05/ARC-20260826-5060-003/reports/strongest_counterevidence.md",
        ),
        ledger_row(
            claim_id="C07", proposed_claim_text="Raw perturbation magnitude alone explains the effect.",
            supporting_arcs="ARC-004", experimental_unit="matched intervention pair summarized by independent run",
            n="185 magnitude-matched pairs; 6 runs",
            point_estimate="higher-damage contrast +0.04296875 at median magnitude ratio 1.0193",
            ci_uncertainty="run-bootstrap 95% CI [0.0353733,0.0524631]",
            seed_robustness="6/6 positive; confirmatory 3/3", scale_robustness="160M only",
            intervention_robustness="within residual-attenuation family; ARC-005 complicates generalization",
            corpus_robustness="WikiText-2 only", assay_status="VALID; exact endpoints reproduced",
            preregistered_or_exploratory="preregistered matched contrast", evidence_status="INVALIDATED",
            strongest_counterevidence="observational magnitude coefficient remains; second family retains magnitude structure",
            safe_paper_wording="Within residual attenuation, equal raw displacement can yield different top-1 damage when predictive damage differs.",
            prohibited_overclaim="Magnitude never matters.",
            source_path="research/arc_20260826_5060_004/results/mechanism_summary.json",
        ),
        ledger_row(
            claim_id="C08", proposed_claim_text="Candidate A aligns more strongly with functional predictive damage than raw magnitude in the original dose family.",
            supporting_arcs="ARC-004", experimental_unit="independent run median of matched pairs",
            n="6 runs; 185 magnitude-matched and 162 damage-matched pairs",
            point_estimate="magnitude-matched damage contrast +0.042969; damage-matched magnitude contrast +0.002459",
            ci_uncertainty="95% CIs [0.035373,0.052463] and [-0.000904,0.005751]",
            seed_robustness="first contrast 6/6; residual contrast 4/6 positive",
            scale_robustness="160M only", intervention_robustness="ordering weakens under activation noise",
            corpus_robustness="WikiText-2 only", assay_status="VALID",
            preregistered_or_exploratory="preregistered controlled discrimination",
            evidence_status="VALID", strongest_counterevidence="KL/NLL and top-1 damage share intervened logits; not randomized",
            safe_paper_wording="In the original dose family, predictive damage discriminates top-1 damage better than raw displacement under frozen matching.",
            prohibited_overclaim="KL/NLL causally mediates DeltaS.",
            source_path="research/arc_20260826_5060_004/results/mechanism_summary.json",
        ),
        ledger_row(
            claim_id="C09", proposed_claim_text="The early-to-late direction is not unique to block deletion.",
            supporting_arcs="ARC-005", experimental_unit="independent run under additive activation noise",
            n="5 runs; 15 run-checkpoint aggregates", point_estimate="mean DeltaS=-0.0724648; 5/5 negative",
            ci_uncertainty="run-bootstrap 95% CI [-0.0843764,-0.0630449]",
            seed_robustness="5/5 negative; 25/25 confidence bins negative",
            scale_robustness="160M only", intervention_robustness="two intervention families qualitatively agree",
            corpus_robustness="WikiText-2 only", assay_status="VALID",
            preregistered_or_exploratory="preregistered family robustness",
            evidence_status="VALID", strongest_counterevidence="one catastrophic cell; family mapping differs quantitatively",
            safe_paper_wording="A norm-controlled additive activation-noise family reproduces the early-to-late direction in five runs.",
            prohibited_overclaim="The effect is intervention invariant.",
            source_path="research/arc_20260826_5060_005/results/family_robustness_summary.json",
        ),
        ledger_row(
            claim_id="C10", proposed_claim_text="A family-invariant KL/NLL-to-top-1 damage law explains both interventions.",
            supporting_arcs="ARC-005/ARC-006R", experimental_unit="KL/NLL-matched cell summarized by run",
            n="103 corrected Class A cells; 5 runs",
            point_estimate="corrected family residual=-0.016833044",
            ci_uncertainty="run-bootstrap 95% CI [-0.020044850,-0.012615741]",
            seed_robustness="5/5 run medians negative; LOSO range [-0.018799,-0.015652]",
            scale_robustness="160M only", intervention_robustness="residual proves quantitative non-invariance on tested support",
            corpus_robustness="WikiText-2 only", assay_status="VALID only under ARC-006R canonical tie rule",
            preregistered_or_exploratory="prospective matching; corrected preregistered repair",
            evidence_status="INVALIDATED", strongest_counterevidence="residual outside frozen equivalence region",
            safe_paper_wording="Matched KL/NLL damage does not eliminate a reproducible intervention-family residual.",
            prohibited_overclaim="KL/NLL fully determines DeltaS across interventions.",
            source_path="research/arc_20260827_5060_006R/results/corrected_summary.json",
        ),
        ledger_row(
            claim_id="C11", proposed_claim_text="The original mixed-rule ARC-006 residual equals -0.019234664.",
            supporting_arcs="ARC-006", experimental_unit="matched cell/run",
            n="103 cells", point_estimate="withdrawn mixed-rule estimate -0.019234664",
            ci_uncertainty="invalid because outcome conventions differed by family",
            seed_robustness="not relevant after assay invalidation", scale_robustness="none",
            intervention_robustness="comparison itself inconsistent", corpus_robustness="none",
            assay_status="INVALID: block topk vs noise argmax tie-breaking",
            preregistered_or_exploratory="original preregistered analysis, subsequently invalidated",
            evidence_status="INVALIDATED", strongest_counterevidence="maximum single-cell correction comparable to aggregate residual",
            safe_paper_wording="The original ARC-006 exact estimate was withdrawn and replaced by ARC-006R.",
            prohibited_overclaim="Reuse any ARC-006 exact residual or reversal count as valid evidence.",
            source_path="research/arc_20260827_5060_006R/assay_bug_report.md",
        ),
        ledger_row(
            claim_id="C12", proposed_claim_text="A corrected intervention-family residual remains after KL/NLL matching.",
            supporting_arcs="ARC-006R", experimental_unit="independent run median over corrected Class A cells",
            n="103 cells; 5 runs; 3 checkpoints; 10 layers", point_estimate="-0.016833044",
            ci_uncertainty="95% CI [-0.020044850,-0.012615741]",
            seed_robustness="5/5 negative; all LOSO below negative equivalence bound",
            scale_robustness="160M only", intervention_robustness="block versus additive noise",
            corpus_robustness="WikiText-2 only", assay_status="VALID; canonical lowest-index exact-maximum rule; seals pass",
            preregistered_or_exploratory="preregistered assay repair, unchanged matching",
            evidence_status="VALID", strongest_counterevidence="24/103 sign reversals; layer heterogeneity; only two families",
            safe_paper_wording="A seed-stable intervention-family component remains after matching KL and NLL under a corrected deterministic top-1 assay.",
            prohibited_overclaim="The residual identifies an internal mechanism.",
            source_path="research/arc_20260827_5060_006R/results/corrected_summary.json",
        ),
        ledger_row(
            claim_id="C13", proposed_claim_text="Simple output geometry fully explains the corrected family residual.",
            supporting_arcs="ARC-007R", experimental_unit="run-specific family coefficient / corrected cell",
            n="103 Class A cells; 5 runs", point_estimate="full geometry shrinkage 20.18%; adjusted residual -0.0134364",
            ci_uncertainty="adjusted 95% CI [-0.0176410,-0.0092317]",
            seed_robustness="residual persists by run; M3 heterogeneous", scale_robustness="160M only",
            intervention_robustness="two families", corpus_robustness="WikiText-2 only",
            assay_status="VALID corrected baseline reproduced exactly",
            preregistered_or_exploratory="preregistered model sequence",
            evidence_status="INVALIDATED", strongest_counterevidence="boundary-only shrinkage -1.49%; 31-cell geometry match residual -0.02436",
            safe_paper_wording="A compact output-geometry block correlates with a modest fraction of the residual but leaves most structure unexplained.",
            prohibited_overclaim="Decision-boundary geometry causes Candidate A.",
            source_path="research/arc_20260827_5060_007R/results/geometry_summary.json",
        ),
        ledger_row(
            claim_id="C14", proposed_claim_text="Hidden perturbation-direction features provide a material held-out explanation.",
            supporting_arcs="ARC-008", experimental_unit="leave-one-run-out cell prediction",
            n="103 cells; 5 held-out run folds", point_estimate="RMSE reduction 9.63%; reversal AUC gain 0.00264",
            ci_uncertainty="below frozen 10% and +0.05 gates", seed_robustness="LOO evaluation used",
            scale_robustness="160M only", intervention_robustness="block/noise directions",
            corpus_robustness="WikiText-2 only", assay_status="VALID observational analysis; causal gate failed",
            preregistered_or_exploratory="preregistered Stage A",
            evidence_status="EXPLORATORY", strongest_counterevidence="direction disagreement SD too small; improvement below gate",
            safe_paper_wording="Extracted directions are distinct but add little held-out predictive information beyond the frozen baseline.",
            prohibited_overclaim="Internal perturbation direction explains the residual.",
            source_path="research/arc_20260827_5060_008/results.json",
        ),
        ledger_row(
            claim_id="C15", proposed_claim_text="Internal perturbation direction has a measured causal effect on DeltaS.",
            supporting_arcs="ARC-008/ARC-009", experimental_unit="prospective direction-swap cell",
            n="0 revealed causal cells", point_estimate="not estimated",
            ci_uncertainty="not estimable", seed_robustness="not estimable",
            scale_robustness="none", intervention_robustness="none", corpus_robustness="none",
            assay_status="INCONCLUSIVE: outcome remained blinded after support failure",
            preregistered_or_exploratory="preregistered causal gate",
            evidence_status="INCONCLUSIVE", strongest_counterevidence="ARC-009 PASS-A 47/103 below frozen minimum 60",
            safe_paper_wording="The causal contribution of internal direction is not identifiable under the current assay.",
            prohibited_overclaim="Direction has no effect, or direction causes the residual.",
            source_path="research/arc_20260828_5060_009/feasibility_summary.json",
        ),
        ledger_row(
            claim_id="C16", proposed_claim_text="The phenomenon is robust across evaluation corpora.",
            supporting_arcs="none", experimental_unit="corpus",
            n="1 corpus", point_estimate="not estimated", ci_uncertainty="not estimable",
            seed_robustness="strong within WikiText-2", scale_robustness="70M/160M within Pythia",
            intervention_robustness="two families on same corpus", corpus_robustness="ABSENT",
            assay_status="INCONCLUSIVE", preregistered_or_exploratory="not yet tested",
            evidence_status="INCONCLUSIVE", strongest_counterevidence="all headline results reuse the same cached WikiText-2 text source",
            safe_paper_wording="All current claims are conditioned on the frozen WikiText-2 assay.",
            prohibited_overclaim="The effect generalizes across domains or token distributions.",
            source_path="meta_arc05/ARC-20260826-5060-003/reports/final_arc_report.md",
        ),
        ledger_row(
            claim_id="C17", proposed_claim_text="The effect is a general cross-architecture training law.",
            supporting_arcs="prior SmolLM2 trajectory outside mechanism chain", experimental_unit="one non-Pythia training trajectory",
            n="1 SmolLM2-360M run; 8 public checkpoints", point_estimate="same endpoint direction, smaller magnitude; pre-decay component present",
            ci_uncertainty="resample intervals only; no independent-run replication",
            seed_robustness="none outside Pythia", scale_robustness="360M single run",
            intervention_robustness="block bypass only", corpus_robustness="WikiText-2 evaluation only",
            assay_status="valid exploratory trajectory; not part of corrected family-residual chain",
            preregistered_or_exploratory="prospective but single-trajectory boundary test",
            evidence_status="EXPLORATORY", strongest_counterevidence="missed original -0.05 magnitude gate; late WSD amplification; one run",
            safe_paper_wording="One SmolLM2 trajectory supplies exploratory directional evidence only.",
            prohibited_overclaim="Universal cross-family or large-model scaling law.",
            source_path="meta_arc05/reports/research_lock_candidate.md",
        ),
        ledger_row(
            claim_id="C18", proposed_claim_text="DeltaS predicts downstream capability or pruning safety.",
            supporting_arcs="none", experimental_unit="downstream task/model",
            n="0", point_estimate="not tested", ci_uncertainty="not estimable",
            seed_robustness="none", scale_robustness="none", intervention_robustness="none",
            corpus_robustness="none", assay_status="INCONCLUSIVE",
            preregistered_or_exploratory="not tested", evidence_status="INCONCLUSIVE",
            strongest_counterevidence="S is an intact-prediction agreement assay, not task utility",
            safe_paper_wording="S operationalizes next-token block substitutability; downstream relevance remains open.",
            prohibited_overclaim="Later checkpoints are more fragile in practical deployment or should be pruned earlier.",
            source_path="meta_arc05/ARC-20260826-5060-003/reports/final_arc_report.md",
        ),
    ]

    with (ROOT / "evidence_ledger.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    audit = {
        "arc": "ARC-20260828-5060-010",
        "checks": {key: bool(value) for key, value in checks.items()},
        "seal_failures": seal_failures,
        "arc005_summary_sha256_expected": expected_arc5,
        "arc005_summary_sha256_actual": actual_arc5,
        "ledger_rows": len(rows),
        "status_counts": {status: sum(row["evidence_status"] == status for row in rows)
                          for status in ("VALID", "INVALIDATED", "INCONCLUSIVE", "EXPLORATORY")},
        "gpu_active_seconds": 0,
        "network_bytes": 0,
        "api_cost_usd": 0,
        "external_compute_cost_usd": 0,
    }
    (ROOT / "artifact_audit.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")
    print(json.dumps(audit, indent=2))


if __name__ == "__main__":
    main()

