# ARC-005 family robustness report

## Verdict

**FAMILY-PARTIAL — confidence MEDIUM.**

Candidate A generalizes qualitatively to a genuinely different intervention:
norm-controlled additive activation noise after an intact Transformer block.
The stronger ARC-004 explanatory ordering does not fully generalize. Functional
damage remains highly informative, but raw magnitude and intervention family
retain measurable structure, and the primary damage-match coverage is too low
to establish a precise cross-family law.

## Main evidence

- Sign-level Candidate A replication: 5/5 independent runs negative; mean ΔS
  -0.07246, 95% CI [-0.08438, -0.06304].
- Confidence control: 25/25 eligible run-bin changes negative.
- New-family magnitude-matched functional contrast: +0.07642, 95% CI
  [+0.06931, +0.08309], 5/5 run medians positive.
- New-family damage-matched magnitude residual: +0.02624, 95% CI
  [+0.02472, +0.02791], not small by the frozen rule.
- Cross-family residual on 26 matches: -0.01960, 90% CI
  [-0.02476, -0.01466], outside the ±0.01074 equivalence band.
- Primary match quality: FAIL, because only 17.3% of block cells matched and
  two runs fell below five matches.
- Family interaction flag: present, but strongly influenced by sparse seed5.

## Answers to the paper-level questions

1. **Does Candidate A reproduce?** Yes at the qualitative sign level, strongly:
   5/5 runs and all confidence bins support early-to-late degradation.
2. **Is functional damage more informative than raw magnitude within noise?**
   It has the larger controlled contrast (+0.0764 versus +0.0262), but raw
   magnitude is not negligible under the preregistered criterion.
3. **Is there a meaningful residual family effect?** On the limited common
   support, yes: -0.0196. Its magnitude is not yet a well-supported population
   estimate because the match-quality gate failed.
4. **Are relationships quantitatively similar?** Broad curves are similar, but
   frozen equivalence is rejected on matched support.
5. **Is there a family x damage interaction?** The formal flag triggers, but
   sparse matches and seed5 leverage make the strength uncertain.
6. **What survives?** Candidate A is not a block-deletion-only sign artifact;
   later checkpoints are less robust to a distinct, norm-controlled activation
   perturbation.
7. **What weakens?** ΔS cannot currently be described as a family-invariant
   function of KL/NLL damage, nor can magnitude be dismissed.
8. **Strongest safe cross-family claim:** two structurally distinct intervention
   families reproduce the direction of Candidate A, while the quantitative
   damage-to-ΔS mapping is family dependent on observed support.
9. **Overstated claim:** KL/NLL damage causally determines ΔS independently of
   intervention construction.
10. **Likely reviewer attack:** the primary common-support set is sparse and
    strength-grid matching is coarse, so the residual and interaction may be
    selection/support artifacts rather than a stable family effect.

## Resources and integrity

- Confirmatory runs: 5; checkpoints: 15; all passed.
- GPU-active kernel-bearing checkpoint runtime: 240.99 s including calibration
  (224.46 s confirmation only).
- End-to-end ARC wall time from initial preregistration commit through analysis:
  approximately 20 minutes.
- Peak allocated CUDA memory: 1,062,210,048 bytes (0.989 GiB).
- Peak host RAM: not instrumented; this is a resource-reporting limitation.
- ARC storage added after the recorded baseline: 8,328,609 bytes (7.94 MiB).
- API cost: USD 0. External compute cost: USD 0. Downloads: none.
- Frozen analysis commit: `4f167c2465cdedcf9d25fc9303164d279695af01`.
- One post-result JSON scalar serialization repair is fully disclosed; no
  scientific logic changed.

## Final statement

The result rules out the simplest block-deletion-only account but does not
support family invariance. Candidate A survives only with an explicit
intervention-family qualifier. Scaling the model would not resolve the present
identification problem; exact damage targeting is the higher-information next
step.
