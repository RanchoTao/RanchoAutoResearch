# Configuration map

Each subdirectory contains the frozen YAML files copied from its ARC. Values hard-coded in scripts are documented in ARC preregistrations and include deterministic pairing order, exact argmax handling, and some integrity tolerances. Before any future rerun, compare the code/config hashes against the ARC `.sha256` manifests in `logs/arc_records/`.

Canonical configurations:

- `ARC-003/independent_runs.yaml`
- `ARC-004/mechanism.yaml`
- `ARC-005/confirmatory.yaml`
- `ARC-006-INVALIDATED/confirmatory.yaml` (targeting only)
- `ARC-008/config.yaml`
- `ARC-009/config.yaml`
- `ARC-011/cross_corpus.yaml`

ARC-006R and ARC-007R are artifact reanalyses and encode much of their frozen contract in preregistration/code rather than a standalone YAML.
