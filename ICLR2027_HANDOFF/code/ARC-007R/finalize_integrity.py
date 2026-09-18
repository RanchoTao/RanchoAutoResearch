"""Validate and seal the completed ARC-007R artifact directory."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
ARC006R = ROOT.parent / "arc_20260827_5060_006R"
REQUIRED = [
    "README.md", "preregistration.md", "geometry_definitions.md", "resource_usage.md",
    "corrected_baseline_check.md", "geometry_data.csv", "geometry_family_comparison.md",
    "statistical_analysis.md", "multicollinearity_audit.md", "sign_reversal_analysis.md",
    "layer_analysis.md", "geometry_matching.md", "strongest_counterevidence.md",
    "paper_implications.md", "next_arc_recommendation.md", "EXECUTIVE_SUMMARY.md",
    "results/geometry_summary.json", "processed/geometry_pairs_corrected.csv",
]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_sha_file(base: Path, manifest: Path) -> list[str]:
    failures = []
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        expected, relative = line.split(maxsplit=1)
        path = base / relative.strip()
        if not path.is_file() or digest(path).lower() != expected.lower():
            failures.append(relative.strip())
    return failures


def main() -> None:
    missing = [name for name in REQUIRED if not (ROOT / name).is_file()]
    figures = sorted((ROOT / "figures").glob("*.png"))
    geometry = pd.read_csv(ROOT / "geometry_data.csv")
    pairs = pd.read_csv(ROOT / "processed" / "geometry_pairs_corrected.csv")
    matches = pd.read_csv(ROOT / "geometry_match_manifest.csv")
    summary = json.loads((ROOT / "results" / "geometry_summary.json").read_text(encoding="utf-8"))
    finite_geometry = bool(np.isfinite(geometry.select_dtypes(include="number").to_numpy()).all())
    finite_pairs = bool(np.isfinite(pairs.select_dtypes(include="number").to_numpy()).all())
    source_failures = verify_sha_file(ARC006R, ARC006R / "final_integrity.sha256")
    stderr_nonempty = [name for name in ["final_validation_stderr.log", "resource_validation_stderr.log"] if (ROOT / name).is_file() and (ROOT / name).stat().st_size]
    checks = {
        "required_files_present": not missing,
        "exactly_five_figures": len(figures) == 5,
        "figures_nonempty": all(path.stat().st_size > 10_000 for path in figures),
        "geometry_rows_300": len(geometry) == 300,
        "geometry_cells_150": geometry.target_id.nunique() == 150,
        "pairs_103": len(pairs) == 103,
        "corrected_reversals_24": int((pairs.family_residual > 0).sum()) == 24,
        "geometry_numeric_finite": finite_geometry,
        "pair_numeric_finite": finite_pairs,
        "matched_cells_31": int(matches.geometry_match.sum()) == 31,
        "baseline_pass": bool(summary["quality"]["baseline"]["pass"]),
        "verdict_frozen": summary["verdict"] == "GEOMETRY-PARTIAL",
        "identified": bool(summary["identified"]),
        "arc006r_final_integrity": not source_failures,
        "validation_stderr_empty": not stderr_nonempty,
    }
    validation = {
        "arc": "ARC-20260827-5060-007R", "pass": all(checks.values()),
        "checks": checks, "missing": missing, "source_integrity_failures": source_failures,
        "nonempty_stderr": stderr_nonempty, "figures": [p.name for p in figures],
        "verdict": summary["verdict"],
    }
    (ROOT / "final_validation.json").write_text(json.dumps(validation, indent=2), encoding="utf-8")
    lines = ["# Final validation", "", f"Overall: **{'PASS' if validation['pass'] else 'FAIL'}**.", ""]
    lines += [f"- {'PASS' if value else 'FAIL'}: `{name}`" for name, value in checks.items()]
    lines += ["", f"Final verdict: `{summary['verdict']}`."]
    (ROOT / "final_validation.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    if not validation["pass"]:
        raise RuntimeError(json.dumps(validation, indent=2))

    excluded = {"final_integrity.sha256"}
    files = sorted(path for path in ROOT.rglob("*") if path.is_file() and path.name not in excluded and "__pycache__" not in path.parts)
    seal = "\n".join(f"{digest(path)}  {path.relative_to(ROOT).as_posix()}" for path in files) + "\n"
    (ROOT / "final_integrity.sha256").write_text(seal, encoding="utf-8")
    print(json.dumps(validation, indent=2))


if __name__ == "__main__":
    main()
