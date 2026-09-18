# Post-hoc technical notes

## JSON scalar serialization repair

- Trigger: the first frozen confirmatory analysis invocation completed its
  calculations but failed while serializing the summary because a Pandas/NumPy
  `int64` value is not accepted by Python's default JSON encoder.
- Observed error: `TypeError: Object of type int64 is not JSON serializable`.
- Scope of repair: add a JSON `default` adapter that converts only NumPy integer,
  floating-point, and boolean scalar wrappers to the corresponding built-in
  Python scalar types.
- Scientific impact: none. No metric, data row, aggregation, matching caliper,
  bootstrap, exclusion, threshold, hypothesis, or verdict rule was changed.
- The originally frozen analysis remains preserved in git commit
  `4f167c2465cdedcf9d25fc9303164d279695af01`; this repair is deliberately left
  as an auditable post-result diff.
