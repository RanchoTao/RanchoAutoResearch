#!/usr/bin/env python3
"""Validate and seal the ARC-010 synthesis package without model inference."""

from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]

REQUIRED = [
    "README.md",
    "evidence_ledger.csv",
    "validity_map.md",
    "paper_thesis.md",
    "paper_story.md",
    "reviewer_stress_test.md",
    "fatal_risks.md",
    "construct_validity_audit.md",
    "baseline_control_audit.md",
    "minimal_submission_matrix.md",
    "main_claims.md",
    "prohibited_claims.md",
    "figure_plan.md",
    "appendix_plan.md",
    "reproducibility_gaps.md",
    "literature_search_needed.md",
    "cost_to_finish.md",
    "next_arc_recommendation.md",
    "EXECUTIVE_SUMMARY.md",
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    missing = [name for name in REQUIRED if not (ROOT / name).is_file()]
    with (ROOT / "evidence_ledger.csv").open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["evidence_status"]] = counts.get(row["evidence_status"], 0) + 1

    audit = json.loads((ROOT / "artifact_audit.json").read_text(encoding="utf-8"))
    executive = (ROOT / "EXECUTIVE_SUMMARY.md").read_text(encoding="utf-8")
    next_arc = (ROOT / "next_arc_recommendation.md").read_text(encoding="utf-8")
    prohibited = (ROOT / "prohibited_claims.md").read_text(encoding="utf-8")

    source_paths_exist = all((REPO / row["source_path"]).exists() for row in rows)
    checks = {
        "required_files_present": not missing,
        "ledger_has_18_rows": len(rows) == 18,
        "ledger_status_counts": counts
        == {"VALID": 8, "INVALIDATED": 5, "INCONCLUSIVE": 3, "EXPLORATORY": 2},
        "all_ledger_sources_exist": source_paths_exist,
        "upstream_numeric_checks_pass": all(audit["checks"].values()),
        "upstream_seals_pass": not any(audit["seal_failures"].values()),
        "verdict_is_paper_borderline": "Final verdict: PAPER-BORDERLINE" in executive,
        "one_gap_is_cross_corpus": "cross-corpus robustness is the one\nmajor scientific gap" in executive,
        "one_selected_experiment": next_arc.count("**SELECT**") == 1,
        "experiment_not_run": "Do not run it without explicit human approval." in next_arc,
        "autodl_not_justified": "AUTODL NOT JUSTIFIED YET" in next_arc,
        "arc006_withdrawal_visible": "ARC-006" in prohibited and "invalidated" in prohibited,
        "direction_branch_closed": "No causal estimate was obtained." in prohibited,
    }

    earliest = min((ROOT / name).stat().st_ctime for name in REQUIRED)
    now = datetime.now(timezone.utc)
    wall_minutes = max(0.0, now.timestamp() - earliest) / 60.0
    result = {
        "arc": "ARC-20260828-5060-010",
        "timestamp_utc": now.isoformat(),
        "checks": checks,
        "missing": missing,
        "ledger_rows": len(rows),
        "status_counts": counts,
        "artifact_construction_interval_minutes": round(wall_minutes, 3),
        "gpu_active_seconds": 0,
        "network_bytes": 0,
        "api_cost_usd": 0,
        "external_compute_cost_usd": 0,
        "final_verdict": "PAPER-BORDERLINE",
        "selected_next_experiment": "frozen-contract cross-corpus replication",
        "passed": all(checks.values()),
    }
    (ROOT / "final_validation.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )

    validation_lines = [
        "# Final validation",
        "",
        f"Overall: **{'PASS' if result['passed'] else 'FAIL'}**",
        "",
        "| Check | Result |",
        "|---|---|",
    ]
    validation_lines.extend(
        f"| `{name}` | {'PASS' if passed else 'FAIL'} |" for name, passed in checks.items()
    )
    validation_lines += [
        "",
        f"Artifact construction interval: {wall_minutes:.3f} minutes.",
        "",
        "No model inference, GPU work, network access, API use, or external compute was performed.",
    ]
    (ROOT / "final_validation.md").write_text(
        "\n".join(validation_lines) + "\n", encoding="utf-8"
    )

    seal_targets = [ROOT / name for name in REQUIRED]
    seal_targets += [
        ROOT / "artifact_audit.json",
        ROOT / "final_validation.json",
        ROOT / "final_validation.md",
        ROOT / "provenance_and_commands.md",
        ROOT / "resource_usage.md",
        ROOT / "src" / "audit_evidence.py",
        ROOT / "src" / "finalize_integrity.py",
    ]
    manifest = []
    for path in sorted(set(seal_targets), key=lambda p: p.as_posix()):
        manifest.append(f"{sha256(path)}  {path.relative_to(ROOT).as_posix()}")
    (ROOT / "final_integrity.sha256").write_text(
        "\n".join(manifest) + "\n", encoding="utf-8"
    )

    print(json.dumps(result, indent=2))
    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
