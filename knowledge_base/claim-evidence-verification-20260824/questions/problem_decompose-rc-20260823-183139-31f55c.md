---
created: '2026-08-23T18:33:54+00:00'
evidence:
- stage-02/problem_tree.md
id: problem_decompose-rc-20260823-183139-31f55c
run_id: rc-20260823-183139-31f55c
stage: 02-problem_decompose
tags:
- problem_decompose
- stage-02
- run-rc-20260
title: 'Stage 02: Problem Decompose'
---

# Stage 02: Problem Decompose

## Source

User-provided SMART research goal and Stage 15 guidance for **Claim–Evidence Verification for Autonomous AI Research**. No external literature was consulted in this decomposition.

## Sub-questions

1. **Does the proposed contribution remain novel after a 2023–2026 primary-source audit?**
   - Does any existing benchmark jointly evaluate complete research bundles, artifact-aware verification, paired scientific interventions, failure localization, and risk-sensitive false-support?
   - Which five works are the nearest neighbors, and which proposed capability—if any—remains uncovered?
   - Would reusing or extending an existing benchmark be more defensible than creating ARCV-Bench?

2. **Can ARCV-Bench establish reliable, non-circular ground truth?**
   - Which support states and failure families can annotators distinguish consistently?
   - What evidence is sufficient to label a claim supported, partially supported, unsupported, contradicted, or unverifiable?
   - Can two independent annotators reach substantial agreement without relying on the evaluated verifier?
   - How should ambiguity, inaccessible artifacts, and incomplete execution records be handled?

3. **Are the interventions scientifically valid and causally decisive?**
   - Does each mutation change exactly one factor that determines what the evidence warrants?
   - Should the correct support judgment change under that intervention?
   - Are paired originals and mutations equivalent on irrelevant dimensions?
   - Can decisive evidence and the induced failure be localized unambiguously?

4. **Can the benchmark resist superficial shortcuts?**
   - Can lexical-only, metadata-only, source-identity, or mutation-template classifiers predict labels?
   - Are valid and invalid cases balanced for style, length, terminology, and artifact availability?
   - Do source-level and held-out-family splits prevent near-duplicate and transformation leakage?
   - Do results persist on genuine cases rather than only semi-synthetic mutations?

5. **What evaluation protocol actually measures evidence sensitivity?**
   - How should intervention consistency reward changes when evidence warrants them and stability when it does not?
   - What cost matrix appropriately emphasizes dangerous false support?
   - How should status prediction, failure diagnosis, evidence localization, and calibration be scored jointly?
   - Which paired-bootstrap procedure and confidence intervals are appropriate for paired bundles?

6. **Does the evidence-graph-and-falsification method improve over credible baselines?**
   - Does explicit evidence-graph construction add value beyond an equally budgeted structured checklist?
   - Does targeted falsification reduce false-support errors without excessive false rejection?
   - Which graph components and falsification questions are responsible for any improvement?
   - Does the method satisfy the stated thresholds on false support, intervention consistency, macro-F1, diagnosis, and localization?

7. **Are the baseline comparisons faithful and fair?**
   - What is the strongest reproducible existing verifier identified by the audit?
   - Can all four comparison families receive matched source material, retrieval context, model capability, and call budgets?
   - Where exact matching is impossible, which asymmetries could explain the result?
   - Are prompts, decoding settings, evidence access, and failure-recovery policies fully documented?

8. **Can the pilot be executed credibly within the hard resource limits?**
   - Can 150–300 provenance-tracked cases be collected and annotated within the overnight window?
   - Can four comparison families run within approximately USD 5 and four GPU-hours?
   - What is the minimum statistically useful pilot if the full target is infeasible?
   - Which stages need early stop rules to avoid consuming resources after novelty or label-quality failure?

9. **Will positive results survive reviewer-style validity attacks?**
   - How much performance remains on held-out source papers and unseen mutation or scenario families?
   - Do evidence ablations show dependence on decisive artifacts rather than prose cues?
   - Are results robust across domains, model families, and genuine versus mutated cases?
   - What evidence rebuts circular labeling, contamination, benchmark artificiality, checklist triviality, and weak real-world relevance?

10. **What evidence should trigger GO, PIVOT, or KILL?**
    - Which novelty finding, annotation result, shortcut test, or pilot outcome is independently fatal?
    - What two scientific pivots are permissible, and how would each change the research question rather than merely tune the method?
    - If results are mixed, which single next experiment has the highest expected information gain?
    - Which datasets, annotations, and evaluation tools should be preserved if the project is killed?

## Priority Ranking

| Rank | Sub-question | Priority | Decision gate |
|---:|---|---|

... (truncated, see full artifact)
