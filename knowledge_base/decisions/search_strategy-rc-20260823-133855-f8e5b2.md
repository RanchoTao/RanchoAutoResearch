---
created: '2026-08-23T13:48:22+00:00'
evidence:
- stage-03/search_plan.yaml
- stage-03/sources.json
- stage-03/queries.json
id: search_strategy-rc-20260823-133855-f8e5b2
run_id: rc-20260823-133855-f8e5b2
stage: 03-search_strategy
tags:
- search_strategy
- stage-03
- run-rc-20260
title: 'Stage 03: Search Strategy'
---

# Stage 03: Search Strategy

deduplication:
  fuzzy_threshold: 0.9
  method: title_doi_hash
filters:
  language:
  - en
  min_year: 2020
  peer_review_preferred: true
generated: '2026-08-23T13:48:22+00:00'
search_strategies:
- max_results_per_query: 60
  name: keyword_core
  queries:
  - World Models under Structured Partial Observability
  - identify a narrow failure mode and
  - world models
  - models under
  - under structured
  sources:
  - arxiv
  - semantic_scholar
  - openreview
- depth: 1
  name: backward_forward_citation
  queries:
  - structured partial
  sources:
  - semantic_scholar
  - google_scholar
topic: 'World Models under Structured Partial Observability: identify a narrow failure
  mode and a simple latent-dynamics mechanism worth testing'


{
  "sources": [
    {
      "id": "arxiv",
      "name": "arXiv",
      "type": "api",
      "url": "https://export.arxiv.org/api/query",
      "status": "available",
      "query": "World Models under Structured Partial Observability: identify a narrow failure mode and a simple latent-dynamics mechanism worth testing",
      "verified_at": "2026-08-23T13:48:22+00:00"
    },
    {
      "id": "semantic_scholar",
      "name": "Semantic Scholar",
      "type": "api",
      "url": "https://api.semanticscholar.org/graph/v1/paper/search",
      "status": "available",
      "query": "World Models under Structured Partial Observability: identify a narrow failure mode and a simple latent-dynamics mechanism worth testing",
      "verified_at": "2026-08-23T13:48:22+00:00"
    }
  ],
  "count": 2,
  "generated": "2026-08-23T13:48:22+00:00"
}

{
  "queries": [
    "World Models under Structured Partial Observability",
    "identify a narrow failure mode and",
    "world models",
    "models under",
    "under structured",
    "structured partial"
  ],
  "year_min": 2020,
  "model_queries_extracted": false,
  "fallback_reason": null
}