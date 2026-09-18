"""Seal ARC-011 artifacts and verify the required delivery contract."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path


ARC = Path(__file__).resolve().parents[1]
SUMMARY = json.loads((ARC / "results" / "cross_corpus_summary.json").read_text())
INDEPENDENT = json.loads(
    (ARC / "results" / "independent_validation.json").read_text()
)

REQUIRED = [
    "README.md",
    "EXECUTIVE_SUMMARY.md",
    "preregistration.md",
    "preregistration_commit.txt",
    "corpus_manifest.csv",
    "run_manifest.csv",
    "core_replication.md",
    "damage_alignment.md",
    "confidence_control.md",
    "corpus_comparability.md",
    "assay_integrity.md",
    "statistical_analysis.md",
    "strongest_counterevidence.md",
    "paper_implications.md",
    "next_arc_recommendation.md",
    "provenance_and_commands.md",
    "resource_usage.md",
    "results/cross_corpus_summary.json",
    "results/independent_validation.json",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def arc_files() -> list[Path]:
    ignored = {"final_integrity.sha256", "final_validation.json", "final_validation.md"}
    return sorted(
        p
        for p in ARC.rglob("*")
        if p.is_file() and "__pycache__" not in p.parts and p.name not in ignored
    )


def main() -> None:
    figures = sorted((ARC / "figures").glob("*.png"))
    raw = sorted((ARC / "raw").glob("*.json"))
    missing = [rel for rel in REQUIRED if not (ARC / rel).is_file()]
    checks = {
        "required_files_present": not missing,
        "independent_validation_passed": bool(INDEPENDENT["passed"]),
        "verdict_is_corpus_go": SUMMARY["verdict"] == "CORPUS-GO",
        "six_raw_runs": len(raw) == 6,
        "exactly_four_figures": len(figures) == 4,
        "all_figures_nonempty": all(p.stat().st_size > 0 for p in figures),
        "pre_outcome_commit_recorded": (
            ARC / "preregistration_commit.txt"
        ).read_text().strip()
        == "f0f2a329caf6e1c113ef38e938cb69ffb6935dee",
    }
    payload = {
        "arc": "ARC-20260828-5060-011",
        "sealed_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "checks": checks,
        "missing": missing,
        "passed": all(checks.values()),
    }
    (ARC / "final_validation.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )
    status = "PASS" if payload["passed"] else "FAIL"
    lines = [
        "# Final validation",
        "",
        f"Status: **{status}**",
        "",
        *[f"- {name}: {value}" for name, value in checks.items()],
    ]
    if missing:
        lines.extend(["", "Missing:", *[f"- `{item}`" for item in missing]])
    (ARC / "final_validation.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    manifest = [
        f"{sha256(path)}  {path.relative_to(ARC).as_posix()}" for path in arc_files()
    ]
    (ARC / "final_integrity.sha256").write_text(
        "\n".join(manifest) + "\n", encoding="utf-8"
    )
    if not payload["passed"]:
        raise SystemExit("Final validation failed")


if __name__ == "__main__":
    main()
