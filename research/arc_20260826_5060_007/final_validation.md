# Final validation

- Diagnostic script compilation: PASS for all ARC-007 Python sources.
- Diagnostic rerun: PASS and deterministic.
- Diagnostic rows: 103/103 Class A cells, one row per target.
- Runs represented: 2, 3, 5, 6, 8.
- Result verdict: `PRIOR ASSAY INVALIDATION`.
- Corrected consistent-`topk` estimate: -0.016796875.
- Corrected consistent-`argmax` estimate: -0.0168330439814815.
- Maximum cellwise correction: 0.0180844907407407.
- Frozen analysis quality gate: expected FAIL with
  `max_ds_difference=0.03233506944444453`; no model is fitted before failure.
- KL reproduction maximum discrepancy: 4.44e-16.
- NLL reproduction maximum discrepancy: 8.33e-16.
- Geometry identity maximum error: 0.
- Harness checks: 15/15 PASS.
- Current raw files agree with the immutable v2 pre-analysis seal. The seal's
  README and technical-log hashes intentionally differ because those documents
  were appended after the stop; the seal itself is retained as historical
  provenance rather than rewritten.
- Secret-pattern scan: PASS.
- Paid API calls: none.
- External compute: none.
- Geometry inference after invalidation: none.
