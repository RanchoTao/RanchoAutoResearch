# Corpus comparability

## Frozen evaluation exposure

| Property | WikiText-2 | HellaSwag | Assessment |
|---|---:|---:|---|
| Predicted tokens per checkpoint | 4,608 | 4,608 | Exact match |
| Sequences per checkpoint | 18 | 18 | Exact match |
| Sequence length | 256 | 256 | Exact match |
| Evaluation seeds | 11, 23, 37 | 11, 23, 37 | Exact match |
| Full local corpus tokens | 2,447,746 | 860,324 | Both sufficient |
| Unique-token fraction | 0.01011 | 0.02146 | HellaSwag is shorter/more lexically diverse per available token |
| Top-100 token fraction | 0.50936 | 0.55435 | HellaSwag is more concentrated at the head |
| Characters per token | 4.404 | 4.301 | Similar tokenizer granularity |

## Intact regime

| Metric, six frozen runs | WikiText-2 early | WikiText-2 late | HellaSwag early | HellaSwag late |
|---|---:|---:|---:|---:|
| Mean intact NLL | 3.868367 | 3.726725 | 3.123598 | 3.009253 |
| Mean intact top-1 confidence | 0.344149 | 0.356251 | 0.404549 | 0.414815 |

HellaSwag correct continuations form an easier, higher-confidence regime for
these models. All six runs nevertheless pass the unchanged NLL ≤5.5 competence
gate, and all five confidence bins remain analyzable.

## Intervention support

| Range over frozen ARC-004 cells | WikiText-2 | HellaSwag |
|---|---:|---:|
| KL | [0.00854, 1.99856] | [0.00637, 1.41621] |
| NLL damage | [-0.00302, 2.10713] | [0.00215, 1.50447] |
| Top-1 damage | [0.05816, 0.70616] | [0.04688, 0.61111] |
| Relative activation magnitude | [0.08065, 0.81942] | [0.07834, 0.85042] |

Magnitude support overlaps strongly. HellaSwag has a narrower upper damage
range, but the frozen matching procedure remains feasible in every pilot run
and produces 161/194 A/B pairs overall.

## Boundary interpretation

The comparison is scientifically meaningful but not distribution-identical:
WikiText-2 is encyclopedia prose, while HellaSwag is a stream of short
everyday-event descriptions joined to labeled correct endings. The approximately
23% smaller ΔS magnitude is evidence of quantitative corpus dependence, not
assay incompatibility. The safe boundary is “two English evaluation corpora with
different domains and formats,” not all corpora or token distributions.
