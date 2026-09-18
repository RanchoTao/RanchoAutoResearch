# Search log

## Protocol

- Search date: 2026-08-28.
- Primary window: 2019–2026, with older foundational work when necessary.
- Sources: official arXiv/OpenReview/proceedings/PMLR/ACL pages and lightweight
  scholarly metadata returned by the search service.
- Deep-read threshold: T3–T5 only.
- PDF policy: inspect abstracts/HTML first; at most 15 high-threat/context PDFs.
- No paid API, model/data download, repository clone, package change, or GPU use.
- Repository `AGENTS.md` DeepSeek-first loop does not apply to this nonexperiment
  literature ARC; calling DeepSeek would also violate the no-paid-API contract.

## Cluster coverage and representative queries

| Cluster | Representative query families | Coverage result |
|---|---|---|
| A. Parameter perturbation | `neural network parameter perturbation behavior`; `weight perturbation pretrained language model`; `Pythia weight noise` | Covered; strongest boundary paper is Kim et al. (2026), with older function/parameter-space theory as context. |
| B. Ablation/intervention | `layer ablation language models`; `block deletion transformer`; `protocol dependent layer redundancy` | Covered; Lad et al. and Garcia are the central collisions. |
| C. Functional damage | `KL divergence parameter perturbation`; `NLL change weight perturbation`; `predictive distribution perturbation transformer` | Covered; DTM, SteerCheck, and function-space-distance work delimit novelty. |
| D. Weight/function geometry | `parameter distance functional distance neural networks`; `loss landscape perturbation transformer`; `model weight geometry behavioral change` | Covered; broad raw-distance insufficiency is established background. |
| E. Representation/output geometry | `logit geometry perturbation`; `decision boundary transformer perturbation`; `hidden representation intervention language model` | Covered; no direct prior was found for the exact corrected family residual, but intervention-geometry artifacts are well known. |
| F. Robustness | `transformer robustness parameter noise`; `model degradation weight corruption`; `activation noise pretraining checkpoints` | Covered; training-dependent PTQ and probe fragility are close contextual threats. |
| G. Pythia-specific | `Pythia perturbation`; `Pythia ablation`; `Pythia checkpoint layer redundancy`; `Pythia loss landscape` | Covered; Garcia is a direct Pythia checkpoint collision. |
| H. Mechanistic interventions | `activation patching metrics methods`; `causal tracing language model`; `interchange intervention transformer` | Covered; these delimit protocol validity but are not the same estimand. |

Recent-work sweeps explicitly included 2025–2026 arXiv, ICLR, NeurIPS, ACL,
NAACL, and adjacent proceedings records. Additional searches covered pruning,
layer dropping, self-repair, causal abstraction, and network-distance theory to
test whether the result was a renamed standard method or a trivial implication.

## Triage outcome

- Candidate records retained: 33.
- T5 direct collision: 1.
- T4 novelty threats: 6.
- T3 close context: 3.
- T2 adjacent: 21.
- T1 background: 2.

Only the ten T3–T5 papers were deep-read. For each, the audit inspected the
abstract, introduction/problem statement, method definitions, principal results,
conclusion, and available limitations. Exact section anchors are recorded in
`top_10_closest_papers.md`.

## Search disposition

The search began from the five frozen claims and converged on three distinct
collision fronts:

1. **metric collision:** Lad et al. and DTM remove novelty from `S`;
2. **phenomenon collision:** Garcia removes novelty from the broad statement that
   output-grounded layer equivalence changes over Pythia training;
3. **control-method collision:** SteerCheck prevents a general first claim for
   KL-matched intervention-family comparisons.

No inspected paper jointly reports Candidate A's independent-pretraining-run,
two-corpus block-bypass replication and the corrected prospective block/noise
damage-matched residual. This absence is evidence for a narrow residual claim,
not proof of exhaustive novelty.

## Sources used

Primary records came from [arXiv](https://arxiv.org/),
[OpenReview](https://openreview.net/),
[NeurIPS proceedings](https://proceedings.neurips.cc/),
[PMLR](https://proceedings.mlr.press/), and
[ACL Anthology](https://aclanthology.org/). Search-result snippets were used only
for discovery; decisive comparisons use the linked primary records.
