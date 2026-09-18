"""Reparse saved raw generations with the final label parser, without rerunning inference."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from infer import parse_label


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    rows = []
    for line in (root / args.input).read_text(encoding="utf-8").splitlines():
        if line:
            row = json.loads(line)
            row["prediction"] = parse_label(row["raw_output"])
            rows.append(row)
    (root / args.output).write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")
    print(json.dumps({"rows": len(rows), "parse_errors": sum(row["prediction"] == "PARSE_ERROR" for row in rows)}, indent=2))


if __name__ == "__main__":
    main()

