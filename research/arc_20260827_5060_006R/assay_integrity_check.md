# Assay integrity check

- [x] Identical canonical top-1 code path for block and noise.
- [x] Exact ties resolve to the lowest token index.
- [x] No family-specific selection branch.
- [x] No `D_S` leakage into targeting or matching.
- [x] Equivalence bound unchanged.
- [x] No seed/checkpoint/layer excluded.
- [x] Matching classes and tolerances unchanged.
- [x] No post-hoc threshold change.
- [x] 150 unique cells and 103 Class A cells reproduced.
- [x] Source harness checks passed.

Path checks:

```json
{
  "topk_block_vs_arc006_max_abs": 1.1102230246251565e-16,
  "topk_noise_vs_arc006_max_abs": 0.019820601851851916,
  "argmax_block_vs_arc006_max_abs": 0.03233506944444453,
  "argmax_noise_vs_arc006_max_abs": 1.3877787807814457e-16
}
```

**PASS**
