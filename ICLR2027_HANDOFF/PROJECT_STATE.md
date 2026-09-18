# Project state

## Current state

Candidate A is frozen at ICLR 2027 Draft 2 after the empirical chain reached `PAPER-GO` and the formal novelty audit returned `NOVELTY-BORDERLINE`. The paper has an 8-page scientific main text and 11 pages total. It builds cleanly from the archived self-contained Overleaf source. No new experiment is authorized by this migration.

The current paper is a controlled replication-and-qualification study, not a new-phenomenon or causal-mechanism paper.

## Verified facts

1. On the frozen WikiText-2 block-bypass assay, 9/9 Pythia-160M independent pretraining runs have negative late-minus-early `Delta S`; mean `-0.103527681`, run-bootstrap 95% CI `[-0.111494502, -0.095847620]`.
2. A prospectively held-out ninth run passed its frozen sign and range prediction.
3. The endpoint direction repeats in 5/5 Pythia-70M runs and 6/6 Pythia-160M runs on a HellaSwag-derived stream.
4. Within residual attenuation, magnitude-matched interventions with separated functional damage differ in top-1 damage (`+0.04296875`, 95% CI `[0.0353733, 0.0524631]`), while the damage-matched raw-magnitude contrast is much smaller (`+0.002459`, CI crossing zero).
5. Norm-controlled additive activation noise reproduces the negative endpoint direction in 5/5 runs.
6. After prospective joint KL/NLL matching and deterministic tie repair, the block/noise top-1-damage residual is `-0.016833044` (about 1.68 percentage points), 95% CI `[-0.020044850, -0.012615741]`, with 5/5 negative run medians.
7. The aggregate residual is heterogeneous: 24/103 strict matched cells (23.3%, not exactly 20%) reverse sign.
8. A frozen output-logit/decision-boundary feature block shrinks the residual by 20.18%, leaving adjusted residual `-0.0134364`, 95% CI `[-0.0176410, -0.0092317]`.
9. Internal perturbation directions differ observationally, but the causal direction experiment failed its support gate. No directional causal effect was revealed.

Every number above is indexed in `paper/current/numerical_provenance.csv` and duplicated in `RESULTS.md` with package-local source paths.

## Largest current problems, in severity order

1. **Novelty/significance:** *No Free Swap* occupies the broad claim that output-grounded layer-equivalence/protocol gaps change across Pythia training. Metric novelty is absent.
2. **Small-model scope:** only Pythia 70M/160M; the corrected cross-family result is 160M and WikiText-2 only.
3. **Construct validity:** `S` is teacher-forced top-1 agreement, not semantic equivalence, downstream capability, pruning safety, or deployment robustness.
4. **Mechanism identification:** KL/NLL and geometry are associated controls, not randomized mediators; internal direction causality remains unidentified.
5. **Support/heterogeneity:** strict matching covers 103/150 cells, 24/103 reverse sign, and layer 7 has low strict-match support.
6. **Threshold justification:** the frozen practical-equivalence half-width `0.010742188` is assay-specific and needs clearer scientific motivation.
7. **Reproduction fragmentation:** GPU inference and CPU analysis used different Python environments, and the original HellaSwag source JSONL is absent even though derived text, selected token IDs, source-document map, and hashes remain.

## Best current scientific framing

Across independently pretrained small Pythia runs, top-1 robustness to interior-block bypass declines from competent early to late checkpoints on two evaluation streams. Within a frozen attenuation assay, output-level KL/NLL damage is more informative than raw displacement, yet prospective joint KL/NLL matching does not make block bypass and norm-controlled activation noise interchangeable under the top-1-damage endpoint. Simple output geometry explains only part of the residual.

This framing is limited to the tested model family, scales, corpora, interventions, checkpoints, and metric.

## Model and experiment limitations

- Pythia 70M and 160M only; decoder-only GPT-NeoX architecture.
- WikiText-2 and one HellaSwag-derived English stream, one tokenizer.
- Block bypass/residual attenuation and norm-controlled additive activation noise only.
- Five public trajectory checkpoints in the main replication; three anchors in the controlled experiments.
- Statistical replicate is the independent pretraining run; the corrected cross-family result has five runs.
- No semantic or downstream task endpoint; no modern billion-scale model; no cross-architecture evidence.

## Next ten highest-value tasks

These are a revision backlog, not authorization to run them during migration.

1. Rewrite the motivation around why intervention-protocol dependence matters for modern LLM interpretability decisions.
2. Tighten Introduction/Related Work around Garcia 2026, Lad et al. 2025, SteerCheck, and Divergent Token Metrics.
3. Add a formal construct section distinguishing top-1 agreement, predictive damage, behavioral interchangeability, and full functional equivalence.
4. Design one main overview figure showing checkpoints, intervention families, KL/NLL matching, residual, and claim boundary.
5. Reproduce the current core pipeline from a clean environment and record a single tested environment lock.
6. Justify or sensitivity-test the `0.010742188` equivalence band without changing the frozen primary result.
7. Add a modern decoder-only 2B/3–4B validation if explicitly authorized; Qwen is a candidate, not yet evidence.
8. If the small modern model supports the effect, preregister a larger 7B or approximately 27B follow-up; do not begin with the largest model.
9. Strengthen uncertainty reporting for layer heterogeneity, unmatched-cell support, and the 24/103 reversals.
10. Reorganize the narrative so the contribution is intervention-conditioned measurement reliability, not discovery of training-dependent redundancy.

## Tasks not to do yet

- Do not reopen ARC-006 outcomes or mix `topk` and `argmax` tie rules.
- Do not claim universality, scaling, downstream capability loss, KL/NLL causality, or an identified mechanism.
- Do not run Qwen 27B, MoE, broad model sweeps, or new intervention families before a clean small modern-model gate.
- Do not tune matching thresholds after seeing outcomes.
- Do not restart the failed internal-direction/continuous-alpha branch without a new preregistered identification design.
- Do not present the paper as the first training-dependent layer-redundancy study.

## Current code entry points

- Main independent-run inference: `code/ARC-003/run_independent.py`
- Main independent-run aggregation: `code/ARC-003/analyze_independent.py`
- Matched mechanism experiment: `code/ARC-004/run_mechanism.py`
- Second-family experiment: `code/ARC-005/run_activation_noise.py`
- Corrected tie repair: `code/ARC-006R/reseal_arc006.py`
- Corrected geometry analysis: `code/ARC-007R/analyze_geometry.py`
- Cross-corpus inference: `code/ARC-011/run_cross_corpus.py`
- Cross-corpus aggregation/validation: `code/ARC-011/analyze_cross_corpus.py`, `code/ARC-011/validate_results.py`

## Current paper entry

- Source: `paper/current/main.tex`
- PDF: `paper/current/candidate_a_iclr2027_draft2.pdf`
- Self-contained Overleaf bundle: `paper/current/candidate_a_iclr2027_draft2_overleaf.zip`
- Author field: `Anonymous authors`; no verified non-anonymous author list is present.

## Current data entry

- WikiText-2 frozen text: `data/wikitext2_train.txt`
- HellaSwag-derived continuation stream: `data/ARC-011/hellaswag_correct_continuations.txt`
- Exact selected token IDs: `data/ARC-011/selected_token_ids.json`
- Source-document mapping: `data/ARC-011/source_documents.csv`

## Largest reproduction risk

The pipeline is not a single tested environment: CUDA inference used the project `.venv`, while several analyses used system Python or a separate analysis venv. The original HellaSwag validation JSONL named by the old config is missing. The preserved derived stream and token IDs should permit exact evaluation, but the current `prepare_corpus.py` source path cannot regenerate them from the missing JSONL without reacquiring the public dataset and verifying its hash.

## Largest reviewer risk

An ICLR reviewer may view the paper as a careful but incremental replication/qualification of *No Free Swap* plus Lad et al., using small Pythia models and a non-semantic top-1 metric. The manuscript needs a sharper significance argument and at least one modern-model validation before making a strong conference claim.
