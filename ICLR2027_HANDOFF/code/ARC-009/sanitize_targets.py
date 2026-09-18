"""Create the sole ARC-009 target table without exposing outcome columns."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.parent / "arc_20260827_5060_006r" / "corrected_results.csv"
OUTPUT = ROOT / "sanitized_targets.csv"
ALLOW = [
    "target_id",
    "run_id",
    "step",
    "layer",
    "match_class",
    "selected_beta",
    "target_kl",
    "target_nll_damage",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    if not SOURCE.is_file():
        raise SystemExit("LOCAL_ARTIFACT_MISSING: corrected source absent")
    with SOURCE.open(newline="", encoding="utf-8") as source:
        reader = csv.reader(source)
        header = next(reader)
        missing = [name for name in ALLOW if name not in header]
        if missing:
            raise SystemExit(f"LOCAL_ARTIFACT_MISSING: missing allowed fields {missing}")
        indexes = [header.index(name) for name in ALLOW]
        class_index = header.index("match_class")
        with OUTPUT.open("w", newline="", encoding="utf-8") as output:
            writer = csv.writer(output)
            writer.writerow(ALLOW)
            count = 0
            for raw_row in reader:
                if raw_row[class_index] != "A":
                    continue
                writer.writerow([raw_row[index] for index in indexes])
                count += 1
    if count != 103:
        OUTPUT.unlink(missing_ok=True)
        raise SystemExit(f"LOCAL_ARTIFACT_MISSING: expected 103 Class A rows, found {count}")
    audit = {
        "source_sha256": sha256(SOURCE),
        "sanitized_sha256": sha256(OUTPUT),
        "rows": count,
        "columns": ALLOW,
        "outcome_values_accessed": False,
    }
    (ROOT / "sanitization_audit.json").write_text(
        json.dumps(audit, indent=2), encoding="utf-8"
    )
    print(json.dumps(audit, indent=2))


if __name__ == "__main__":
    main()

