# Gap mining plan: execution-time configuration provenance

Date: 2026-08-24

This run reuses the prior collision map. It does not revive the broad claim-validity proposal.

## Coverage matrix

Legend: **E** explicitly evaluated; **P** partial/indirect; **A** assumed available or correct; **—** outside the stated task. The matrix records public paper/task descriptions, not inferred private capabilities.

| Capability / assumption / failure regime | CLAIMCHECK | CLAIM-BENCH | SciVer | PCF | POPPER | ScientistOne | REPRO-Bench | ReplicatorBench | SciCoQA |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Real paper claims | E | E | E | P | P | E | E | E | E |
| Literature evidence retrieval | — | — | P | P | P | E | — | P | — |
| Static source-code inspection | — | — | — | P | P | E | E | E | E |
| Experiment execution | — | — | — | P | E | E | E | E | — |
| Result/score verification | P | P | P | P | E | E | E | E | — |
| Paper–code semantic mismatch | P | — | — | — | — | E | P | P | **E** |
| Runtime command/config provenance | — | — | — | — | P | P | P | P | **—** |
| Resolved configuration after precedence | — | — | — | — | — | P | — | — | **—** |
| CLI vs environment vs config-file overrides | — | — | — | — | — | — | — | — | **—** |
| Selective omission of negative runs | P | — | — | P | P | P | P | P | — |
| Missing-artifact abstention | P | — | P | P | P | P | E | E | — |
| Matched null/counterfactual execution | — | — | — | E | E | P | P | P | — |
| Real non-replicable cases | P | — | — | — | — | P | E | E | P |
| Long-context degradation | P | E | E | P | P | P | P | P | E |
| Failure-type stratification | E | P | E | P | P | P | P | P | E |
| Calibrated support/abstention | P | P | P | P | P | P | P | P | — |

The strongest empty intersection is not generic paper–code alignment. It is verification of a paper claim against the **configuration that actually won precedence at runtime**, rather than against repository defaults or a raw launch command.

## Three serious candidate gaps

### Candidate A: runtime configuration aliasing — selected

Claim shrinking:

1. Broad: verify whether experimental claims agree with artifacts.
2. Narrower: verify paper–code agreement for ML experiment settings.
3. Narrower: distinguish repository defaults from settings used in the executed run.
4. Pilot claim: when CLI, environment, and config-file sources have precedence, a raw command or static repository can leave the effective setting ambiguous; an immutable resolved-config receipt should reduce false support for execution-dependent parameter claims.

Why it may survive: SciCoQA evaluates paper plus static code and explicitly places configurable default-hyperparameter mismatches out of scope. ScientistOne introduces method–code alignment and score checks, but the published audit taxonomy does not report a controlled benchmark over configuration precedence channels. Older workflow-provenance research captures runtime arguments, but does not test scientific-claim judgments or false-support risk.

### Candidate B: selective-run completeness

Claim shrinking:

1. Broad: detect selective evidence.
2. Narrower: detect omission of negative seeds from ML result packages.
3. Narrower: detect omission when the reported aggregate is internally consistent with the surviving logs.
4. Candidate claim: a preregistered expected-run manifest is necessary to distinguish complete evidence from a cherry-picked but internally consistent subset.

Why not selected: the mechanism is close to chain-of-evidence completeness, immutable provenance ledgers, and missing-artifact verdicts. A small synthetic pilot would largely prove the behavior of a manifest we designed, not a surprising model failure.

### Candidate C: reproduced signal without causal specificity

Claim shrinking:

1. Broad: verify reproducibility.
2. Narrower: distinguish “pipeline emitted the claimed metric” from “method caused the result.”
3. Narrower: apply matched label-shuffle or patched-method controls to successful ML reproductions.
4. Candidate claim: a non-trivial fraction of successful reproductions remain positive under a null counterfactual because the evaluator or data path leaks signal.

Why not selected: POPPER and PCF already center active falsification, while recent security-artifact work directly demonstrates failing patched counterfactuals. A general-ML pilot would require a credible collection of real suspect repositories; inventing vulnerable toy repositories would be weak evidence.

## Selected falsifiable pilot

### Research question

For execution-dependent ML claims, how much does verifier reliability change when it receives (a) static repository defaults, (b) raw launch provenance, or (c) the fully resolved runtime configuration after all override channels have been applied?

### Hypotheses

- **H0:** Raw launch provenance and resolved runtime receipts yield equal false-support rates on mismatched runs.
- **H1:** Resolved runtime receipts reduce false-support by at least 20 percentage points relative to raw launch provenance, with the largest gap for environment/config precedence cases.

### Objective oracle

Every case will execute a real scikit-learn classification experiment. The program will persist:

- paper-like parameter claim;
- source defaults;
- raw CLI invocation;
- environment and config-file inputs;
- resolved runtime configuration;
- dataset identity and hash;
- metric result and artifact hashes.

The support label is computed from the resolved value actually consumed by the executed program, not from an LLM label.

### Paired evidence conditions

1. `static`: claim + relevant source/default configuration.
2. `launch`: static evidence + raw command, environment, and config-file snippets.
3. `receipt`: claim + machine-written resolved configuration receipt.
4. `typed_diff`: deterministic extraction/comparison baseline over claim and receipt.

### Pilot scope

- Public scikit-learn bundled datasets: Iris, Wine, Breast Cancer, Digits.
- Parameters: preprocessing mode, logistic-regression `C`, evaluation metric, split seed.
- Override mechanisms: CLI, environment, JSON config, and multi-source precedence.
- Balanced aligned/mismatched cases; held-out combinations by dataset and override channel.
- Open-weight local models only; no paid API.
- Metrics: false-support rate (primary), balanced accuracy, macro-F1, abstention rate, paired bootstrap intervals, McNemar tests, and stratification by source/parameter.

