"""Run the frozen ARC-002 deletion assay in the isolated ARC-003 directory."""

from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PREVIOUS = ROOT.parent / "ARC-20260825-5060-002" / "src" / "run_stability.py"


def main() -> None:
    spec = importlib.util.spec_from_file_location("arc002_run_stability", PREVIOUS)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load frozen evaluator: {PREVIOUS}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.ROOT = ROOT
    module.main()


if __name__ == "__main__":
    main()

