# Metric novelty audit

## Frozen metric

For token positions `t` evaluated on the same teacher-forced context,

```text
S(I, c) = mean_t 1[argmax p_c(y_t | x_<t) = argmax p_{c,I}(y_t | x_<t)]
Delta S = S(I, late) - S(I, early)
```

The repository aggregates `S` over frozen interior layers and evaluation
shards. It measures intact/intervened next-token top-1 agreement. It is not
accuracy against a semantic target and it is discontinuous at tied or nearly
tied logits.

## Prior-metric comparison

| Prior metric | Relationship to `S` | Audit result |
|---|---|---|
| Lad et al. (2025), *relative accuracy* after layer deletion/swapping | Same operational top-1 agreement family: intervened top-1 is compared with the intact model on fixed contexts | Exact prior construct for `S` in the closest intervention setting |
| Deiseroth et al. (2024), divergent-token metric | Counts positions where compressed/intervened and reference argmax tokens differ | `S = 1 - DTM` when evaluated over the same positions and aggregation |
| Tropeano et al. (2025), prediction disagreement under pruning | Example/prediction disagreement rather than the exact token aggregation | Conceptually related, not mathematically identical under its published aggregation |
| Men et al. (2025), Block Influence | Hidden-state input/output cosine, not output-token agreement | Different metric |
| Garcia (2026), swap-KL/protocol gap | Distributional change and the difference between intervention protocols | Different statistic, but directly overlaps the training-trajectory question |
| Reblitz-Richardson (2026), critical perturbation amplitude | Activation-noise threshold at which a probe fails | Different statistic and endpoint |

## `Delta S`

Taking an early-to-late difference of a known agreement statistic is a new
aggregation only in a narrow implementation sense. Garcia (2026) already
measures checkpoint-wise changes in output-grounded layer equivalence, so the
trajectory operation is not a defensible standalone metric contribution.

## Verdict

- Novelty of `S`: **NONE**.
- Novelty of `Delta S` as a named statistic: **WEAK**.
- Possible contribution: the preregistered replication and matched-control
  evidence built around the statistic, not the statistic itself.

Primary sources: [Lad et al.](https://proceedings.neurips.cc/paper_files/paper/2025/hash/bcad07d4bfab51243efaa08b8ed475b3-Abstract-Conference.html),
[Deiseroth et al.](https://aclanthology.org/2024.naacl-long.377/),
[Garcia](https://arxiv.org/abs/2605.16234), and
[ShortGPT](https://aclanthology.org/2025.findings-acl.1035/).
