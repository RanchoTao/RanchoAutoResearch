# ARC-21: Critical-Step Supervision

Isolated screening ARC for testing whether the placement of a fixed number of
intermediate-state labels changes compositional length generalization.

No large language model or paid API is used. All targets are generated exactly.

## Status

**KILL / STOP ARC-21.** The three-seed MVP did not show that the critical-step
proxy beats a random one-state supervision budget. See
[`reports/final_arc21_report.md`](reports/final_arc21_report.md).

## Reproduce

From the AutoResearchClaw repository root with PyTorch/CUDA available:

```powershell
python arc21/src/run_mvp.py --config arc21/configs/mvp.yaml
python arc21/src/run_mvp.py --config arc21/configs/replication.yaml
python arc21/src/aggregate.py
```

The first two commands retrain all 21 runs. The aggregation command is cheap and
recreates the summary tables and four figures from saved results.
