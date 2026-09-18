# Post hoc notes

Everything below occurred after the frozen analysis failed its quality gate.

1. The first failure was provisionally attributed to an ARC-007 extractor
   mismatch and triggered a complete raw-data regeneration.
2. The second failure, with the opposite family now reproducing exactly,
   exposed the pre-existing ARC-006 mixed-rule comparison.
3. The consistent-`topk` and consistent-`argmax` summaries were computed only
   to establish materiality and determine whether repair is worthwhile.
4. These diagnostics were not used to change geometry metrics, calipers,
   models, thresholds, or hypotheses. No ARC-007 confirmatory result exists.
