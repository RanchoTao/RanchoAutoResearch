# Candidate B GO/KILL rules

## Objective

Optimize discovery for:

```text
expected scientific information gain
------------------------------------
compute + time + network cost
```

Early-stage default: **KILL aggressively**. A negative result is a valid and
useful outcome. Do not optimize the process for producing `GO` labels.

## Minimum advancement conditions

A candidate advances only if all of the following are present:

- a precise, falsifiable scientific question;
- plausible novelty grounded in verified literature rather than naming;
- a feasible local experiment with a predefined outcome metric;
- controls capable of detecting a trivial implementation artifact;
- a bounded runtime and explicit stop condition;
- a credible path from the pilot to a paper-level contribution.

## Kill conditions

Kill or return to triage when direct prior work subsumes the claim, the cheapest
test is not decisive, the phenomenon is determined by the generator or metric,
budget/fairness controls fail, held-out evidence contradicts the claim, or the
required first evidence exceeds the approved local resource envelope.

Every decision must record the evidence that would have produced the opposite
decision. No candidate inherits Candidate A evidence as a new result.
