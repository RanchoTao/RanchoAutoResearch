# Reviewer attack surface

## Attack 1 — “This is No Free Swap with extra controls.”

**Risk: HIGH.**

This is the strongest attack. Garcia (2026) already establishes that
output-grounded layer equivalence changes over Pythia training and depends on
replacement/interchange protocol. The paper therefore concedes the broad
collision in the Introduction. The surviving delta is the controlled question:
whether protocol differences disappear after prospective joint KL/NLL matching,
tested with independent pretraining runs, two corpora for the empirical base,
and a corrected block/noise comparison. If reviewers do not value this
qualification and replication, the contribution may be judged incremental.

## Attack 2 — “KL/NLL matching is arbitrary.”

**Risk: MEDIUM.**

KL and target-token NLL are natural output-distribution and task-loss measures,
but they are not exhaustive. The design uses a prospectively frozen joint
target, reports strict and sensitivity support, records match errors, and keeps
top-1 outcomes blinded until sealing. The paper does not call KL/NLL causal or
complete. The residual means only that these two obvious severity controls do
not make the tested interventions equivalent. A richer functional metric could
absorb more of the difference.

## Attack 3 — “The effect only exists in tiny Pythia models.”

**Risk: HIGH.**

The core evidence is limited to Pythia 70M and 160M; the corrected family
comparison is 160M only. This is acknowledged in the title, abstract, setup,
and limitations. Independent pretraining replicas give unusually strong
internal validity but do not establish large-model or cross-architecture
generality. The manuscript makes no claim beyond the tested regime. This risk
is substantial for ICLR significance but is not an internal inconsistency.

## Attack 4 — “Delta S is an assay artifact.”

**Risk: HIGH.**

`S` is a known top-1 agreement statistic and is discontinuous near ties. The
paper reports competence, fixed-confidence, layer, scale, corpus, KL/NLL, and
simple geometry controls. It also discloses the top-1 tie bug, withdraws the
mixed-rule result, freezes a deterministic family-independent rule, and reports
the corrected estimate. These steps reduce known artifacts but do not prove
construct validity for semantic or downstream robustness. The paper must keep
its conclusion operational.

## Attack 5 — “You do not explain the mechanism.”

**Risk: MEDIUM.**

Correct. The contribution is empirical discrimination and falsification of
three simple accounts: pure raw magnitude, a family-invariant KL/NLL mapping,
and a compact output-geometry explanation. The internal-direction experiment
fails its support gate before outcome reveal, so no mechanism claim is made.
This is scientifically disciplined, but reviewers seeking a positive mechanism
may find the technical depth insufficient.

## Fatal-risk assessment

No attack is internally **FATAL** to a conservative Draft 0. The combination of
Attack 1 and Attack 3 is the highest submission risk: a reviewer may see a
careful small-model qualification of a very recent closest paper rather than a
main-conference contribution. No additional experiment is launched here.
