# Literature shortlist curation record

Stage 4 used real OpenAlex and arXiv records (`real_search=true`). Stage 5's ACP
response failed JSON parsing twice, so the built-in fallback selected the first
15 ranked records. That fallback was relevant after the ranking fix, but it did
not cover the core world-model lineage required for a defensible novelty audit.

`curated_titles.txt` therefore defines a transparent 20-paper shortlist selected
only from the real Stage 4 records. The strata are:

- world-model foundations and strong standard baselines (World Models, PlaNet,
  Dreamer, DreamerV2, DreamerV3, and an MBRL survey);
- partial-observability foundations (POMDP planning, policy gradients, and
  predictive-state planning);
- learned belief/state representations under partial observability;
- the nearest direct structured-observation work, including delayed
  observations, structured history selection, latent dynamics from partial
  observations, and robustness/systematic-generalization studies.

No title or metadata was generated manually. The Stage 5 JSONL is rebuilt by
exact-title lookup against `stage-04/candidates.jsonl`; the rebuild fails if any
title is absent or non-unique. The original failed/fallback outputs are retained
under `audit/` and are not visible to subsequent pipeline stages.
