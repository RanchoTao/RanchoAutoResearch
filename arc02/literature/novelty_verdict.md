# ARC-02 novelty verdict

```text
NOVELTY STATUS: YELLOW
```

## Verdict

The broad statement “reasoning is implemented by sparse/recurrent circuits that
emerge during training” is already occupied. The narrower ARC-02 question is not
yet directly answered in the audited primary literature:

> For a single jointly trained model evaluated above an accuracy floor, does the
> *causally sufficient component set* change smoothly or reorganize across a
> four-or-more-level semantic-depth sweep?

The collision risk is high because Chen et al. (2026) already compare one- and
two-hop mechanistic patterns and Wang et al. (2025) compare circuits across task
complexities. ARC-02 survives only because neither work estimates a
depth-indexed sufficient circuit, cross-depth topology/overlap, or a formal
change point under matched controls.

## Conditions for continuing

- Treat “circuit” as an operational, method-relative set of attention-head and
  MLP outputs whose retained computation preserves at least 90% of full-model
  accuracy.
- Require direct ablation in addition to activation patching.
- Keep sequence length, edge count, vocabulary, distractors, and training
  distribution matched across depths.
- Analyze correct-only examples and do not interpret an accuracy cliff as a
  circuit transition.
- Compare linear, smooth quadratic, and piecewise models; a visual elbow is not
  evidence.
- If patching and ablation rankings disagree strongly, or a candidate break
  disappears under method/accuracy controls, downgrade or KILL.

## Kill gate decision

Proceed to one-seed MVP only. The novelty evidence does not justify scale-up.

