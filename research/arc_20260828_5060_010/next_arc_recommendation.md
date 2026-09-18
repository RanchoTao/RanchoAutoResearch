# One recommended next ARC

## Selection

**Candidate A — corpus robustness** is the single next experiment.

Working ARC question:

> Does the early-to-late decline in interior-block top-1 substitutability, and
> its alignment with predictive damage, survive a distinct evaluation corpus
> under the frozen Pythia-160M contract?

Do not run it without explicit human approval.

## Why this outranks alternatives

| Candidate | Reviewer importance | Information gain | Cost | Decision |
|---|---|---|---|---|
| Corpus robustness | Very high | Could preserve or collapse every empirical section at once | Low–medium | **SELECT** |
| Construct-validity/null metric | Very high | Clarifies interpretation, but may refine a corpus-specific artifact | Low–medium | Second after corpus gate |
| Larger scale (410M/1B) | Medium now | Broadens size but cannot rescue corpus/construct dependence | High | Defer |
| Another model family | High later | Tests architecture scope but adds training/cache confounds | High | Defer |
| Third intervention/baseline | Medium | Narrows the family residual, not the core phenomenon | Medium–high | Defer |

The ranking follows expected information gain × reviewer importance ÷ compute,
not headline value.

## Frozen design to preregister

- Primary scale: cached Pythia/PolyPythias-160M independent runs; use the same
  frozen runs, early/final checkpoint rule, ten interior layers, and aggregation.
- Evaluation: one semantically and distributionally distinct public text corpus,
  selected before outcomes; fixed token count, sequence length, and deterministic
  sample manifest.
- Primary statistic: the same `ΔS` definition and run-level aggregation.
- Required secondary measures: intact NLL/competence, intervention NLL damage,
  KL, intact-confidence bins, sample counts, and run-level uncertainty.
- Minimum confirmatory unit: the existing independent pretraining runs, not
  tokens or layers treated as independent replicates.
- No retuning of intervention strength, layers, endpoint, or tie rule.
- Compare corpus effect sizes with a preregistered heterogeneity/equivalence
  criterion; do not require identical magnitudes.

## GO / NARROW / KILL logic

- **GO:** direction is run-stable on the new corpus, the CI excludes zero in the
  preregistered direction, a meaningful fraction of the original magnitude
  remains, and competence/confidence controls do not remove it.
- **NARROW:** direction survives but magnitude is materially corpus-dependent;
  reframe the paper around token-distribution boundary conditions.
- **KILL current paper thesis:** sign is unstable or absent and the difference
  is not explained by a documented competence/support failure.

## Resource decision

`AUTODL NOT JUSTIFIED YET`

The RTX 5060 and existing cached 160M models should suffice. The next ARC should
stop if it unexpectedly requires new large checkpoints, >2 local GPU-hours, or a
large download; return a revised resource plan rather than escalating.
