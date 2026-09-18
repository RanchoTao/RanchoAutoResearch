# Candidate A reopen policy

Candidate A research is closed. It may be reopened only when at least one of
the following conditions is documented:

1. A human coauthor or reviewer identifies a `HIGH` or `FATAL` scientific gap.
2. ICLR internal review requires one specific additional analysis.
3. External peer review or rebuttal requires a targeted experiment.
4. A reproducibility failure is discovered in a frozen result or artifact.
5. The user explicitly authorizes reopening Candidate A.

Otherwise:

```text
DO NOT resume autonomous experiment generation.
```

Paper editing remains allowed, but it must not change frozen numerical results,
validity labels, provenance, or claim scope. Any authorized scientific reopen
must create a new, explicitly linked ARC, preregister its question and stop
condition, and preserve this archive and tag unchanged.

Candidate B/C work is separate. It must not overwrite Candidate A ARC
directories, caches/results, figures, numerical provenance, IDs, or archived
files. Shared model and dataset caches may be used read-only.
