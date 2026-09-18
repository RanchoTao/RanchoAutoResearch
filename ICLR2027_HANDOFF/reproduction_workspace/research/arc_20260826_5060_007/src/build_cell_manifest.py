"""Copy the frozen ARC-006 targeting manifest without outcome fields."""

from __future__ import annotations

import csv
from pathlib import Path


ARC_ROOT = Path(__file__).resolve().parents[1]
SOURCE = ARC_ROOT.parent / "arc_20260826_5060_006" / "target_manifest.csv"
OUTPUT = ARC_ROOT / "cell_manifest.csv"
FIELDS = [
    "target_id", "run_id", "step", "progress", "layer", "selected_beta",
    "match_class", "target_kl", "target_nll_damage", "achieved_kl",
    "achieved_nll_damage", "relative_kl_error", "relative_nll_error",
]


def main() -> None:
    with SOURCE.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 150:
        raise RuntimeError(f"expected 150 frozen targets, found {len(rows)}")
    keys = [(row["run_id"], row["step"], row["layer"]) for row in rows]
    if len(set(keys)) != 150:
        raise RuntimeError("ARC-006 target keys are not unique")
    if set(row["match_class"] for row in rows) != {"A", "B", "C"}:
        raise RuntimeError("unexpected ARC-006 match classes")
    with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows([{field: row[field] for field in FIELDS} for row in rows])
    print({"rows": len(rows), "class_a": sum(row["match_class"] == "A" for row in rows)})


if __name__ == "__main__":
    main()

