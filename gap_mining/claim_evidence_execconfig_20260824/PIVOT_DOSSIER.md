# PIVOT: Resolved execution receipts for scientific claim auditing

Date: 2026-08-24

## Decision

# PIVOT

The preregistered false-support hypothesis was not supported at its stated effect size. The pilot exposed a different, repeatable phenomenon: converting raw multi-source launch provenance into a typed resolved-config receipt substantially improved recovery of the true execution label for both tested open models, mainly by reducing false rejection and uninformative abstention. Contradictory receipts still exposed model-dependent behavior, motivating a hybrid typed comparator rather than an LLM-only verifier.

## Exact new research question

For scientific claims that depend on execution-time ML configuration, can a small, typed receipt containing the values that actually won runtime precedence improve verifier sensitivity and overall correctness relative to static repository defaults or raw launch provenance, without increasing false support?

This is not a new generic claim-verification system. It is an evidence-interface question at the boundary between execution provenance and scientific claim auditing.

## Claim shrinking

1. Scientific claim validity.
2. Paper–artifact agreement for computational experiments.
3. Paper–execution agreement for configuration-dependent claims.
4. Verification of one claimed parameter when defaults, JSON, environment, and CLI values compete under precedence.

The full coverage matrix and three candidate-gap comparison are in [GAP_MINING_PLAN.md](./GAP_MINING_PLAN.md).

## Nearest five works and non-subsumption

| Work | Collision | Why it does not subsume this pilot claim |
|---|---|---|
| [SciCoQA](https://aclanthology.org/2026.acl-long.1795/) | First large benchmark for paper–code discrepancies; includes data/training/evaluation categories and long-context analysis | Its public task supplies a static versioned paper and codebase. The dataset card explicitly excludes configurable default-hyperparameter mismatches. It does not ablate raw launch provenance against resolved runtime receipts. |
| [ScientistOne / Chain-of-Evidence](https://arxiv.org/abs/2605.26340) | Score, specification, reference, and method–code audits over autonomous-research outputs | It motivates evidence chains and method–code alignment, but its published four-check evaluation does not report a controlled configuration-precedence benchmark or evidence-representation ablation. |
| [REPRO-Bench](https://arxiv.org/abs/2507.18901) | Agents assess papers against real reproduction packages | It evaluates end-to-end reproducibility decisions, not whether the same verifier changes behavior when effective run state is represented as raw sources versus a resolved receipt. |
| [ReplicatorBench](https://arxiv.org/abs/2602.11354) | Human-verified replicable/non-replicable claims and execution agents with different code access | It studies resource retrieval, experiment design/execution, and interpretation, but not runtime override precedence or typed configuration receipts. |
| [Capturing end-to-end provenance for machine learning pipelines](https://doi.org/10.1016/j.is.2024.102495) | Git/MLflow metadata are converted to W3C-PROV-compatible graphs | It establishes that run configuration can be captured and evaluates query coverage/runtime. It does not evaluate scientific-claim verdicts or LLM false-support/false-rejection behavior. |

The pilot therefore does not claim to invent provenance capture. It asks whether **resolving provenance before verification** changes a verifier's scientific judgment.

## Original pilot hypothesis

- **H0:** Raw launch provenance and resolved receipts yield equal false-support rates on mismatched runs.
- **H1:** Receipts reduce false support by at least 20 percentage points, with the largest effect under multi-source precedence.

Outcome: **H1 was falsified at the preregistered effect size.**

- Qwen2.5-Coder-1.5B: launch and receipt both had 0% false support; difference 0 points.
- Qwen2.5-3B: launch 7.81%, receipt 0%; paired difference 7.81 points, bootstrap 95% CI [1.56, 15.63], exact McNemar p=0.0625.

The direction for the 3B model favored receipts, but the effect was below 20 points and not conventionally significant under the exact paired test.

## Experimental design

### Executed cases

- 128 independent real program executions.
- Four public scikit-learn datasets: Iris, Wine, Breast Cancer, and Digits.
- Four claimed parameters: preprocessing scaler, logistic-regression `C`, evaluation metric, and split seed.
- Four override mechanisms: CLI, environment variable, JSON config, and conflicting multi-source precedence.
- 64 aligned and 64 contradicted executions.
- Resolution contract: defaults < JSON config < environment < explicit CLI.

Each case trained and evaluated an actual logistic-regression pipeline and persisted the resolved configuration, winning source, dataset hash, score, and score hash. Labels were computed from the value consumed by the executed program, not by an LLM.

### Evidence conditions

1. `static`: claim plus repository default; no proof of executed state.
2. `launch`: claim plus defaults, config input, environment input, CLI input, and precedence rule.
3. `receipt`: claim plus the resolved runtime value and winning source.

### Models

- Qwen2.5-Coder-1.5B-Instruct, Hugging Face revision `2e1fd397ee46e1388853d2af2c993145b0f1098a`.
- Qwen2.5-3B-Instruct, Hugging Face revision `aa8e72537993ba99e69dfaafa59ed015b17504d1`.
- Greedy local inference on one RTX 5060 Laptop GPU; no paid API.

### Metrics and statistics

- Primary: false-support rate among truly contradicted executions.
- Secondary/exploratory: false-rejection rate, actual execution-label accuracy, abstention rate.
- Case-level paired bootstrap with 10,000 resamples.
- Exact McNemar/binomial tests for paired correctness changes.

## Pilot results

| Model | Evidence | Execution-label accuracy | False support | False rejection | Abstention |
|---|---|---:|---:|---:|---:|
| Qwen2.5-Coder-1.5B | static | 50.00% | 0.00% | 100.00% | 0.00% |
| Qwen2.5-Coder-1.5B | launch | 57.81% | 0.00% | 78.13% | 3.13% |
| Qwen2.5-Coder-1.5B | receipt | **80.47%** | 0.00% | **39.06%** | 0.00% |
| Qwen2.5-3B | static | 0.00% | 0.00% | 100.00% | 100.00% |
| Qwen2.5-3B | launch | 4.69% | 7.81% | 98.44% | 84.38% |
| Qwen2.5-3B | receipt | **50.78%** | **0.00%** | **0.00%** | 49.22% |

Receipt minus launch accuracy:

- 1.5B: +22.66 points, paired bootstrap 95% CI [14.84, 30.47]; 31 receipt-only-correct versus 2 launch-only-correct cases; exact p = 1.31e-7.
- 3B: +46.09 points, paired bootstrap 95% CI [35.94, 55.47]; 64 receipt-only-correct versus 5 launch-only-correct cases; exact p = 4.12e-14.

The accuracy gain was positive for every override mechanism in both models:

| Mechanism | 1.5B gain | 3B gain |
|---|---:|---:|
| CLI | +15.63 points | +43.75 points |
| JSON config | +28.13 | +50.00 |
| Environment | +15.63 | +43.75 |
| Multi-source precedence | +31.25 | +46.88 |

Deterministic identifiability controls:

| Control | Accuracy | False support |
|---|---:|---:|
| Assume repository default | 50% | 100% |
| Parse CLI only | 75% | 50% |
| Correct precedence resolver | 100% | 0% |
| Typed receipt comparison | 100% | 0% |

These controls show that launch evidence is sufficient in principle. The LLM result is therefore an evidence-consumption failure, not an information-theoretic impossibility.

## New hypothesis exposed by the negative result

> **H-new:** For configuration-dependent scientific claims, pre-resolving execution provenance into a typed receipt will improve verifier execution-label accuracy by at least 15 percentage points over raw launch evidence across unseen override mechanisms, without increasing false support. A deterministic typed comparator layered before natural-language reasoning will additionally convert contradictory receipts from abstention into correct contradiction decisions.

Why this is a pivot: the original claim predicted a large reduction in unsafe positive verdicts. The stronger observed effect was instead a reduction in false rejection/abstention and a large increase in evidence usability. In Qwen2.5-3B, 63 of 64 contradicted receipt cases were still labeled `UNVERIFIABLE`, even though the receipt contained both values. That failure motivates a typed comparison layer rather than simply richer prompting.

## Figures

- [Combined verifier metrics](./outputs/combined_verifier_metrics.png)
- [Receipt gain by override mechanism](./outputs/receipt_gain_by_mechanism.png)

## Limitations

- The configurations are controlled and the executions are real, but the paper-like claims are synthetic.
- Only two small Qwen-family models were tested; this is not cross-family evidence.
- Logistic regression and four bundled datasets are much simpler than real autonomous-research repositories.
- Prompt wording may affect the unusually asymmetric response modes.
- The receipt schema directly exposes the target field; real systems require claim-to-field alignment and tamper resistance.
- `static` lacks runtime evidence by design; its execution-label accuracy should not be interpreted as a fair verifier-quality score.
- The deterministic comparator is an oracle-quality control in this pilot, not yet a general parser for natural-language scientific claims.

## Next three experiments

1. **Cross-model and prompt robustness.** Test at least four unrelated open model families in the 3B–8B range, randomized label order, paraphrased claims, and blinded evidence serialization. Confirm the +15-point accuracy hypothesis and measure calibrated abstention.
2. **Real-repository external validity.** Add runtime invocation/MLflow traces to a preregistered sample of real SciCoQA or reproducibility-package cases with configuration-dependent claims; have humans adjudicate claim-to-field mappings.
3. **Hybrid verifier and adversarial receipts.** Implement claim-to-schema extraction plus deterministic typed comparison, then test missing fields, conflicting receipts, tampered hashes, unseen precedence rules, and selective run omission against LLM-only and static paper–code baselines.

## Plausible contribution if the pivot survives

An execution-grounded claim-auditing benchmark and hybrid verification method showing that static paper–code agreement is insufficient for configuration-dependent claims, quantifying when raw provenance is unusable to verifiers, and demonstrating that typed resolved receipts plus deterministic comparison improve sensitivity without weakening false-support safeguards.

## Resource and integrity record

- Python 3.13.9; PyTorch 2.11.0+cu128; Transformers 4.56.2; scikit-learn 1.7.2.
- Full-model inference: 103.6 seconds (1.5B) and 312.7 seconds (3B); smoke tests add approximately 19 seconds. Upper-bound GPU-active time was about 0.13 GPU-hours.
- No paid API, fabricated output, simulated experiment, external communication, publication, or submission.

