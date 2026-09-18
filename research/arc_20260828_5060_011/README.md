# ARC-20260828-5060-011

Cross-corpus robustness test for Candidate A under a frozen Pythia-160M
protocol. This ARC changes one scientific factor: the evaluation corpus.

The corpus is selected and preregistered before any new intervention outcome is
computed. Network, downloads, APIs, package changes, model scaling, new
intervention families, and mechanism discovery are prohibited.

## Outcome

Final verdict: **CORPUS-GO**. Six of six independent HellaSwag runs reproduced
the negative endpoint effect under the frozen Pythia-160M protocol. The
run-bootstrap 95% confidence interval excludes zero, the frozen confidence
control passes, and the functional-damage alignment survives. The effect is
smaller than on WikiText-2, and a small damage-matched perturbation-magnitude
residual remains.

The optional second intervention-family check was not run because it was not
required by the preregistered verdict and would have changed more than the one
authorized scientific factor.

## Reproduction

The exact preparation, inference, analysis, and validation commands are in
`provenance_and_commands.md`. The final human entry point is
`EXECUTIVE_SUMMARY.md`; machine-readable results are in
`results/cross_corpus_summary.json` and `results/independent_validation.json`.
