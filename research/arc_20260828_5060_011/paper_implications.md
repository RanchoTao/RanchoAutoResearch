# Paper-level implications

## 1. Does Candidate A replicate on a distinct corpus?

Yes. The preregistered frozen-protocol verdict is `CORPUS-GO`.

## 2. How many runs reproduce the expected sign?

Six of six independent Pythia-160M runs; all 18 evaluation resamples are also
negative.

## 3. How does effect size compare with WikiText-2?

Mean ΔS is -0.07926 on HellaSwag versus -0.10353 in the nine-run WikiText-2
reference. The absolute ratio is 0.766, with bootstrap CI [0.645, 0.880]. The
direction is robust but magnitude is corpus-dependent.

## 4. Does functional-damage alignment replicate?

Yes. At matched raw magnitude the mean run-median functional-damage contrast is
+0.04044, 6/6 positive, CI [+0.03763, +0.04371], closely matching WikiText-2.

## 5. Does the raw-magnitude alternative remain weakened?

Yes, not eliminated. After KL/NLL matching its mean contrast is +0.00298—about
7.4% of the main contrast—but its CI is above zero. The paper must disclose this
corpus difference.

## 6. Does confidence matching preserve the effect?

Yes. All 30 eligible run-bin comparisons are negative; the run-bootstrap CI for
the mean bin effect is [-0.10029, -0.07410].

## 7. Is there meaningful corpus dependence?

Yes quantitatively. HellaSwag is easier and more confident, has a narrower
intervention-damage range, and yields a roughly 23% smaller |ΔS|. None of these
differences removes the direction or key control structure.

## 8. What boundary condition must be stated?

The validated claim covers two English corpora—WikiText-2 encyclopedia prose and
deterministically constructed HellaSwag everyday-event continuations—under one
tokenizer, one small-model architecture family, and one frozen next-token assay.

## 9. Can the paper claim cross-corpus robustness?

Yes, with that bounded wording: the phenomenon and primary control structure are
not specific to WikiText-2. It cannot claim domain, language, or dataset
universality.

## 10. What would still be overstated?

Universal LLM specialization, large-model scaling, downstream fragility,
cross-language robustness, KL/NLL causality, exact intervention invariance, and
an identified internal mechanism remain unsupported.

## 11. Is another major experiment required before drafting?

No. The largest experimental blocker identified by ARC-010 is resolved. The
paper should now freeze the empirical story and begin drafting. A primary-source
novelty audit and reproducibility packaging remain mandatory drafting tasks; an
alternative-metric construct control is still high value for review but should
not delay the initial manuscript or reopen discovery.

## Paper-status update

On empirical readiness, ARC-010 upgrades from `PAPER-BORDERLINE` to
`PAPER-GO`. This is not a claim that novelty is already verified.
