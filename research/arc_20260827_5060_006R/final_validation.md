# Final validation

- Verdict: `006R-RESIDUAL-CONFIRMED`.
- Corrected table grain: 150/150 unique cells; no duplicate target IDs.
- Match classes: A=103, B=31, C=16; assignments changed=0.
- Runs/checkpoints/layers: 5/3/10, all frozen identities retained.
- Canonical residual identity: every row equals
  `corrected_noise_ds-corrected_block_ds`.
- Primary residual: -0.01683304398148147.
- 95% run-bootstrap CI: [-0.02004484953703703,
  -0.012615740740740743].
- Negative run medians: 5/5.
- LOSO range: [-0.01879882812499998, -0.015652126736111098].
- Frozen equivalence bound unchanged at +/-0.0107421875; result remains outside.
- Global-rule difference: 0.00003616898148146516, below 0.0025.
- Corrected sign reversals: 24/103; eight memberships changed.
- Layer row counts sum to 103; ten layers present; layer 7 flagged low support.
- Source manifest: 12/12 entries verified with SHA-256 and record counts.
- Canonical source harnesses: 15/15 pass; historical source harnesses: 15/15 pass.
- Independent pandas/NumPy QA assertions: PASS.
- Python source compilation: PASS.
- Figure 1 and Figure 2 inspected at exported resolution: PASS.
- Secret-pattern scan: PASS.
- Model/dataset/package downloads: none.
- GPU/model inference: none.
- Paid API/external compute: none.
- Machine-wide WLAN threshold warning recorded; no ARC Python network
  connection or remote operation was observed.
- ARC-007 geometry analysis: not executed.
