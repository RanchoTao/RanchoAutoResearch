# Strongest counterevidence

1. **The new-corpus effect is smaller.** Mean |ΔS| is 76.6% of the nine-run
   WikiText-2 effect (bootstrap ratio CI [0.6449, 0.8801]); on the same six run
   IDs the ratio is 73.4%. Corpus affects magnitude.
2. **Seed1 is materially weaker.** Its HellaSwag ΔS is -0.05323, versus the
   other runs' -0.07543 to -0.09236. It remains negative in 3/3 resamples and
   removing it does not remove the aggregate effect.
3. **Raw magnitude is not exactly null after damage matching.** The HellaSwag
   residual is +0.002984 with 95% CI [+0.001555, +0.004485], 6/6 run medians
   positive. It is small relative to +0.040437 but differs from WikiText-2's
   zero-crossing interval.
4. **One low-confidence comparison is close to zero.** Seed1 in `[0,.05)` has
   ΔS -0.012684. It is the least-negative of 30 comparisons; no comparison
   reverses sign.
5. **The corpora differ in intact regime.** HellaSwag is easier and more
   confident (early NLL 3.124 versus 3.868; confidence .405 versus .344), so the
   experiment establishes robustness across these regimes, not matched-domain
   equality.
6. **Corpus construction is a limitation.** Correct endings are selected using
   labels and short records are concatenated with double newlines. This is
   deterministic and outcome-independent, but it is not the original HellaSwag
   multiple-choice task and can create cross-record contexts.
7. **Only two English corpora are tested.** Cross-corpus evidence is real but
   insufficient for universal domain, language, tokenizer, or dataset claims.

No ΔS sign reversal, excluded seed, failed harness, matching violation, or
result-dependent preprocessing was observed.
