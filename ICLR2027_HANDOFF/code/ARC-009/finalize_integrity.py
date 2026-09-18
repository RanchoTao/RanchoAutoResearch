"""Validate, blind-audit, and seal ARC-009."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "README.md", "preregistration.md", "blinding_audit.md",
    "pilot_diagnostics.md", "solver_definition.md", "alpha_search_manifest.csv",
    "calibration_results.csv", "failure_modes.md", "coverage_analysis.md",
    "resource_usage.md", "feasibility_report.md", "next_arc_recommendation.md",
    "EXECUTIVE_SUMMARY.md", "caliper_diagnostics.md", "statistical_analysis.md",
    "strongest_counterevidence.md", "paper_implications.md",
    "provenance_and_commands.md", "visual_qa.md", "feasibility_summary.json",
]
FORBIDDEN_COLUMNS = {"d_s", "ds", "flips", "residual", "reversal", "top1_flip"}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(base: Path, manifest: Path) -> list[str]:
    failures = []
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        expected, relative = line.split(maxsplit=1)
        path = base / relative.strip()
        if not path.is_file() or sha(path).lower() != expected.lower():
            failures.append(relative.strip())
    return failures


def main() -> None:
    data = pd.read_csv(ROOT / "calibration_results.csv")
    manifest = pd.read_csv(ROOT / "alpha_search_manifest.csv")
    targets = pd.read_csv(ROOT / "sanitized_targets.csv")
    summary = json.loads((ROOT / "feasibility_summary.json").read_text(encoding="utf-8"))
    source_audit = json.loads((ROOT / "sanitization_audit.json").read_text(encoding="utf-8"))
    forbidden_hits = {}
    for name, frame in (("results", data), ("manifest", manifest), ("targets", targets)):
        hits = FORBIDDEN_COLUMNS.intersection({str(column).lower() for column in frame.columns})
        if hits:
            forbidden_hits[name] = sorted(hits)
    upstream = {}
    for name in ("arc_20260827_5060_006r", "arc_20260827_5060_007r", "arc_20260827_5060_008"):
        base = ROOT.parent / name
        upstream[name] = verify(base, base / "final_integrity.sha256")
    figures = sorted((ROOT / "figures").glob("*.png"))
    checks = {
        "required_artifacts": all((ROOT / path).is_file() for path in REQUIRED),
        "sanitized_schema": list(targets.columns) == [
            "target_id", "run_id", "step", "layer", "match_class",
            "selected_beta", "target_kl", "target_nll_damage",
        ],
        "sanitized_hash": sha(ROOT / "sanitized_targets.csv") == source_audit["sanitized_sha256"],
        "universe_103": len(data) == 103 and data.target_id.nunique() == 103
                        and set(data.target_id) == set(targets.target_id),
        "manifest_412": len(manifest) == 412,
        "finite_results": np.isfinite(data.select_dtypes(include="number")).all().all(),
        "alpha_bounded": ((data.block_alpha >= data.alpha_min) & (data.block_alpha <= data.alpha_max)
                          & (data.noise_alpha >= data.alpha_min) & (data.noise_alpha <= data.alpha_max)).all(),
        "no_forbidden_columns": not forbidden_hits,
        "no_confirm_files": not any(ROOT.rglob("confirm_seed*")),
        "pass_a_47": int((data.calibration_class == "PASS-A").sum()) == 47,
        "pass_b_29": int((data.calibration_class == "PASS-B").sum()) == 29,
        "tradeoff_27": int((data.calibration_class == "FAIL-TRADEOFF").sum()) == 27,
        "verdict": summary["verdict"] == "ALPHA-NOT-FEASIBLE",
        "outcome_blind": summary["outcome_blind"] is True,
        "four_supported_figures": len(figures) == 4 and all(path.stat().st_size > 10000 for path in figures),
        "upstream_seals": all(not failures for failures in upstream.values()),
    }
    checks = {key: bool(value) for key, value in checks.items()}
    result = {
        "pass": all(checks.values()), "checks": checks,
        "forbidden_column_hits": forbidden_hits, "upstream_failures": upstream,
        "figures": [path.name for path in figures], "verdict": summary["verdict"],
    }
    (ROOT / "final_validation.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    (ROOT / "final_validation.md").write_text(
        "# Final validation\n\nOverall: **" + ("PASS" if result["pass"] else "FAIL") + "**.\n\n"
        + "\n".join(f"- {'PASS' if value else 'FAIL'}: `{key}`" for key, value in checks.items())
        + f"\n\nFinal verdict: `{summary['verdict']}`.\n", encoding="utf-8"
    )
    if not result["pass"]:
        raise RuntimeError(json.dumps(result, indent=2))
    files = sorted(
        path for path in ROOT.rglob("*")
        if path.is_file() and path.name != "final_integrity.sha256" and "__pycache__" not in path.parts
    )
    (ROOT / "final_integrity.sha256").write_text(
        "\n".join(f"{sha(path)}  {path.relative_to(ROOT).as_posix()}" for path in files) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

