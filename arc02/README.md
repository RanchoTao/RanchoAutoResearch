# ARC-02: Reasoning Circuit Phase Transition

Isolated, evidence-first investigation of whether the causal components used by a
small Transformer reorganize abruptly as controlled reasoning depth increases.

The MVP uses a jointly trained tiny Transformer, fixed-length synthetic relation
chains, component-level activation patching, direct causal ablation, and explicit
smooth-versus-piecewise model comparison. No simulated results are permitted.

## Reproduce

Use the existing CUDA environment recorded in `reports/environment_audit.md`:

```powershell
& '..\gap_mining\claim_evidence_execconfig_20260824\.venv\Scripts\python.exe' `
  '.\src\run_arc02.py' --config '.\configs\mvp.yaml'
```

