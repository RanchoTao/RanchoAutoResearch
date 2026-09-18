# Post hoc implementation notes

## 2026-08-27: remove pandas from GPU runners

The first Stage A command stopped at import time, before loading a model or
producing any result, because the established CUDA `.venv` does not contain
pandas. Adding the system site-packages via `PYTHONPATH` was rejected after a
smoke import exposed an incompatible system `huggingface-hub` version.

The GPU runners were mechanically changed to use Python's standard `csv`
module for input/output. The system-Python analysis/freezing script retains
pandas. No sample, representation, metric, alpha, caliper, outcome, threshold,
or verdict rule changed. No package was installed or upgraded.

## 2026-08-27: Stage A norm broadcast repair

The next Stage A attempt loaded the first local checkpoint and stopped on the
first batch before writing cell results: the `[batch, token]` activation norm
needed a final singleton dimension to multiply `[batch, token, hidden]` noise.
Adding `unsqueeze(-1)` is the sole repair. It implements the already frozen
formula and changes no scientific decision.

## 2026-08-27: calibration objective domain repair

All outcome-blind calibration runs completed. Before choosing any alpha pair,
the freezer stopped because a very-low-alpha candidate had slightly negative
NLL damage and the pairwise log-ratio term lacked the `1e-12` lower bound
already used by the target-error terms. Applying the same lower bound to both
sides of every pairwise log ratio is a numerical-domain repair only. It does
not remove candidates, change weights/calipers, or access `D_S`.

## 2026-08-27: final-validator serialization repair

The final validator completed its checks but stopped before writing validation
or seal files because one pandas-derived check was a NumPy `bool_`, which the
standard JSON encoder rejects. Explicit conversion of all check values to
Python `bool` changes no check or scientific artifact.
