# Reproducibility package audit

## What is currently present

| Evidence block | Scripts/configs | Raw/processed data | Figures | Provenance/seal | Current status |
|---|---|---|---|---|---|
| ARC-003 core | `run_independent.py`, `analyze_independent.py`, `independent_runs.yaml` | Present under `experiments/` and `results/` | Six regeneration targets present | Commands, run provenance, preregistration and final manifests | Substantively reproducible in the original environment. |
| ARC-004 discrimination | `run_mechanism.py`, `analyze_mechanism.py`, `mechanism.yaml` | `raw/`, `processed/`, `matching_diagnostics/`, `results/` | Four figures | Assay validation, manifests, commands, resource logs | Strong package, but not unified with ARC-003. |
| ARC-005 second family | Activation-noise and two analysis scripts; calibration/confirmatory configs | Raw, processed, diagnostics, results present | Five figures | Summary hash independently matches its lock | Strong local package. |
| ARC-006R repair | `reseal_arc006.py` | Corrected results present; derives from upstream ARC-006/005 artifacts | Two figures | Assay bug report and repaired seals | Reproducible only with upstream dependency chain intact. |

## Ranked gaps

| Rank | Gap | Severity | Required repair before submission |
|---:|---|---|---|
| 1 | No unified environment lock across ARC-003–006R. | HIGH | Record exact Python/CUDA/PyTorch/Transformers/Numpy versions and produce one installable lock or container specification. |
| 2 | No single top-level reproduction command. | HIGH | Add a read-only orchestrator that validates cached inputs and regenerates tables/figures without rerunning expensive inference unless requested. |
| 3 | Model checkpoints and corpus cache are external dependencies, not content-addressed in one manifest. | HIGH | Record repository/model revisions, exact checkpoint IDs, corpus hashes, expected cache paths, and offline failure messages. |
| 4 | ARC-006R depends on upstream raw artifacts and its dependency graph is implicit. | MEDIUM | Add an explicit input manifest and verify hashes before repair analysis. |
| 5 | Figure scripts/interfaces and style are ARC-specific. | MEDIUM | Add one figure-regeneration manifest mapping every main/appendix panel to command and input hash. |
| 6 | Exact commands are distributed across per-ARC reports. | MEDIUM | Consolidate commands and working directories in a top-level reproduction guide. |
| 7 | No clean-environment reproduction has been documented. | HIGH | Run later on a fresh local environment after the scientific gates, logging outputs and runtime. |

## Boundaries of this audit

ARC-010 verified stored summaries and available integrity manifests; it did not
rerun model inference or create an environment. Large engineering repairs are
deliberately deferred until the selected scientific gap is resolved.
