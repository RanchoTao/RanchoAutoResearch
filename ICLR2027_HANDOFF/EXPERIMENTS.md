# Experiment ledger

`EXPERIMENT_INDEX.csv` is the compact machine-readable index. Detailed run/checkpoint/cell rows remain under `results/<ARC>/` and the complete original ARC directory copies are under `logs/arc_records/<ARC>/`.

## Common frozen assay

- Architecture: GPT-NeoX/Pythia decoder-only Transformer; Pythia-160M has 12 blocks and 162,322,944 parameters. Pythia-70M is the second-small-scale replication.
- Statistical unit: independent pretraining run, never token/layer/evaluation shard.
- Primary corpus: frozen WikiText-2 train text.
- Evaluation selections: seeds 11, 23, 37; six sequences per selection; 256 predicted positions; batch size 2; 4,608 positions per checkpoint.
- Main trajectory checkpoints: steps 14k, 36k, 72k, 107k, 143k.
- Controlled-comparison anchors: 14k, 72k, 143k.
- Interior blocks: 1–10 of the 12-block 160M model.
- Outcome: `S`, `D_S=1-S`, `Delta S=S_late-S_early`; lowest-index exact-maximum top-1 rule is canonical.

## ARC-001 — initial boundary/replication prototype

- Purpose: establish a workable checkpoint assay and competence/replication gates.
- Model/data: `EleutherAI/pythia-160m-deduped`, WikiText-2; steps 0, 1k, 10k, 50k, 143k.
- Status: completed developmental evidence; not a current headline result.
- Sources: `logs/arc_records/ARC-001/`, especially configs and aggregate JSON.
- Reproduce: only if auditing project origin; current paper uses later independent-run evidence.

## ARC-002 — first independent-run stability red team

- Purpose: determine whether the decline survives independent PolyPythias runs and a second scale.
- Models: Pythia-70M and Pythia-160M, seeds 1–5; five checkpoints.
- Intervention: single interior-block bypass/deletion-equivalent path.
- Status: completed; raw seed files are preserved and partly reused by ARC-003.
- Sources: `results/ARC-002/experiments/raw/`, `results/ARC-002/results/stability_summary.json`.

## ARC-003 — canonical independent-run replication

- Purpose/hypothesis: test whether late-minus-early block-bypass agreement is negative across genuine independent pretraining runs.
- Models: nine Pythia-160M runs; seed 9 prospectively held out; five Pythia-70M runs reused as confirmation.
- Dataset/checkpoints: WikiText-2; 14k/36k/72k/107k/143k.
- Results: 9/9 negative at 160M, 5/5 negative at 70M; NLL/KL damage and confidence/layer controls supportive.
- Paper use: primary empirical base, Figure 1a/1b.
- Confidence: high inside the frozen assay. Reproduction recommended from cached public checkpoints.
- Sources: `results/ARC-003/results/`, `logs/arc_records/ARC-003/reports/final_arc_report.md`.

## ARC-004 — matched mechanism discrimination

- Purpose/hypothesis: distinguish functional predictive damage from raw intervention magnitude.
- Model/runs: Pythia-160M; pilot seeds 1,4,9; confirmatory seeds 6,7,8.
- Intervention: residual attenuation `alpha={0.25,0.50,0.75,1.00}` on blocks 1–10.
- Matching: magnitude-matched and KL/NLL-damage-matched within run/checkpoint, deterministic non-reuse.
- Paper use: Figure 2 and Claim 3.
- Confidence: medium-high associational discrimination; not KL/NLL causality.
- Sources: `results/ARC-004/`, `configs/ARC-004/mechanism.yaml`.

## ARC-005 — intervention-family robustness

- Purpose/hypothesis: determine whether the endpoint direction and explanatory ordering survive norm-controlled additive activation noise.
- Model/runs: Pythia-160M; calibration seeds 1,4; confirmatory seeds 2,3,5,6,8.
- Intervention: local-norm-scaled frozen Gaussian directions, beta grid 0.35/0.50/0.75, direction IDs 101/202/303, blocks 1–10.
- Result: 5/5 negative endpoint; sparse original cross-family matching failed its quality gate.
- Paper use: qualitative second-family replication only; sparse residual exploratory.
- Sources: `results/ARC-005/`, `logs/arc_records/ARC-005/family_robustness_report.md`.

## ARC-006 — prospective inverse targeting, original outcomes invalidated

- Purpose: outcome-blind continuous search for noise strengths matching block targets in KL/NLL.
- Model/runs: Pythia-160M seeds 2,3,5,6,8; steps 14k/72k/143k; 150 target cells.
- Valid part: target assignments and match diagnostics; 103/150 strict Class A and 134/150 A+B.
- Invalid part: original `D_S`, family residual, reversals, and downstream outcome analysis used inconsistent top-1 tie handling.
- Paper use: matching provenance only. Never cite original outcome estimates.
- Sources: `logs/arc_records/ARC-006-INVALIDATED/`, `results/ARC-006-INVALIDATED/`.

## ARC-006R — deterministic top-1 repair and reseal

- Purpose: recompute ARC-006 outcomes with a family-independent lowest-index exact-maximum rule without changing targets/matches/exclusions.
- Compute: local artifact-only recomputation; no model loading/GPU.
- Result: corrected family residual `-0.016833044`; 5/5 negative run medians; 24/103 sign reversals.
- Paper use: canonical Figure 3/cross-family result.
- Confidence: high for the frozen matched estimand; generalization is bounded.
- Sources: `results/ARC-006R/`, `logs/arc_records/ARC-006R/deterministic_top1_rule.md`.

## ARC-007R — corrected output-geometry analysis

- Purpose/hypothesis: test whether simple output-logit/decision-boundary geometry accounts for the corrected residual.
- Input: ARC-006R outcomes plus saved logits/margins; no new inference.
- Result: full geometry block shrinks residual by 20.18%, adjusted residual remains negative; reversal prediction and layer explanation fail.
- Paper use: Figure 4 and bounded associational qualification.
- Sources: `results/ARC-007R/`, `logs/arc_records/ARC-007R/EXECUTIVE_SUMMARY.md`.

## ARC-008 — internal-direction observational/counterfactual attempt

- Purpose: test whether hidden perturbation direction explains or causes the family residual.
- Model/runs: Pythia-160M seeds 2,3,5,6,8; saved activations plus blinded calibration.
- Result: directions are nearly orthogonal, but predictive gates miss; counterfactual support only 15/103, so top-1 outcome is not revealed.
- Paper use: negative/inconclusive mechanism boundary only.
- Sources: `results/ARC-008/`, `logs/arc_records/ARC-008/EXECUTIVE_SUMMARY.md`.

## ARC-009 — continuous-alpha feasibility

- Purpose: improve causal direction matching support without revealing `D_S`.
- Model/runs: same 103 Class A cells, five Pythia-160M runs.
- Result: PASS-A 47/103, PASS-B 29/103; feasibility gate fails; no top-1 outcome or causal estimate.
- Paper use: negative identification boundary only.
- Sources: `results/ARC-009/`, `logs/arc_records/ARC-009/feasibility_summary.json`.

## ARC-011 — cross-corpus robustness

- Purpose/hypothesis: test whether the endpoint and matched-control ordering reproduce on a distinct evaluation stream.
- Model/runs: Pythia-160M seeds 1,4,6,7,8,9; steps 14k/72k/143k.
- Dataset: deterministic correct-continuation stream derived from HellaSwag validation; 4,608 positions per checkpoint.
- Intervention: residual attenuation; same matching contract as ARC-004.
- Result: 6/6 negative endpoint; confidence and matched-control ordering reproduce at smaller magnitude.
- Paper use: Figure 1c, corpus boundary.
- Sources: `results/ARC-011/`, `data/ARC-011/`, `configs/ARC-011/cross_corpus.yaml`.

## Nonexperimental audits

- ARC-010: evidence consolidation/reviewer stress test; no new scientific inference.
- ARC-012: bounded literature/novelty audit; no experiment.

Both are preserved under `logs/arc_records/` because they determine claim validity and positioning.
