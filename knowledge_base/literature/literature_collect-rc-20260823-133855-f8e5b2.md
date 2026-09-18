---
created: '2026-08-23T13:48:58+00:00'
evidence:
- stage-04/candidates.jsonl
- stage-04/web_context.md
- stage-04/web_search_result.json
- stage-04/references.bib
- stage-04/search_meta.json
id: literature_collect-rc-20260823-133855-f8e5b2
run_id: rc-20260823-133855-f8e5b2
stage: 04-literature_collect
tags:
- literature_collect
- stage-04
- run-rc-20260
title: 'Stage 04: Literature Collect'
---

# Stage 04: Literature Collect

{"id": "seminal-schulman2017proximal", "title": "Proximal Policy Optimization Algorithms", "source": "seminal_library", "url": "", "year": 2017, "abstract": "Foundational paper on PPO, policy gradient, reinforcement learning.", "authors": [{"name": "Schulman et al."}], "cite_key": "schulman2017proximal", "venue": "arXiv", "collected_at": "2026-08-23T13:48:23+00:00"}
{"id": "seminal-mnih2013playing", "title": "Playing Atari with Deep Reinforcement Learning", "source": "seminal_library", "url": "", "year": 2013, "abstract": "Foundational paper on DQN, deep reinforcement learning, Atari.", "authors": [{"name": "Mnih et al."}], "cite_key": "mnih2013playing", "venue": "NIPS Workshop", "collected_at": "2026-08-23T13:48:23+00:00"}
{"id": "seminal-haarnoja2018soft", "title": "Soft Actor-Critic: Off-Policy Maximum Entropy Deep Reinforcement Learning with a Stochastic Actor", "source": "seminal_library", "url": "", "year": 2018, "abstract": "Foundational paper on SAC, soft actor-critic, entropy.", "authors": [{"name": "Haarnoja et al."}], "cite_key": "haarnoja2018soft", "venue": "ICML", "collected_at": "2026-08-23T13:48:23+00:00"}
{"id": "seminal-chen2018neural", "title": "Neural Ordinary Differential Equations", "source": "seminal_library", "url": "", "year": 2018, "abstract": "Foundational paper on neural ODE, ODE, differential equation.", "authors": [{"name": "Chen et al."}], "cite_key": "chen2018neural", "venue": "NeurIPS", "collected_at": "2026-08-23T13:48:23+00:00"}


## Web Search Results
### [1] Causal-JEPA: Learning World Models through - arXiv.org
URL: https://arxiv.org/html/2602.11389v2
By masking object-level latents and requiring each masked object state to be inferred from the surrounding context, C-JEPA imposes structured partial observability during training, creating counterfactual-like prediction queries that discourage shortcut solutions and make interaction-dependent prediction necessary under the learning objective.

### [2] FieldSeer I: Physics-Guided World Models for Long-Horizon ...
URL: https://arxiv.org/abs/2512.05361
We introduce FieldSeer I, a geometry-aware world model that forecasts electromagnetic field dynamics from partial observations in 2-D TE waveguides. The model assimilates a short prefix of observed fields, conditions on a scalar source action and structure/material map, and generates closed-loop rollouts in the physical domain. Training in a symmetric-log domain ensures numerical stability ...

### [3] GitHub - santoshkumarradha/uwm-jepa: UWM-JEPA: a JEPA world model with ...
URL: https://github.com/santoshkumarradha/uwm-jepa
Unitary density-matrix latent prediction for partially observable JEPA world models. Santosh Kumar Radha · Oktay Goktas · AgentField AI, Toronto Standard vector-latent JEPAs predict a point in representation space. UWM-JEPA represents the latent as a density matrix and rolls it forward on an isospectral orbit. Under partial observability this gives the predictor a structured latent in which ...

### [4] Uncertainty Representations in State-Space Layers for Deep...
URL: https://openreview.net/forum?id=rfPns0WJyg
Optimal decision-making under partial observability requires reasoning about the uncertainty of the environment&#x27;s hidden state. However, most reinforcement learning architectures handle partial observability with sequence models that have no internal mechanism to incorporate uncertainty in their hidden state representation, such as recurrent neural networks, deterministic state-space models ...

### [5] GitHub - 3D-Belief/3d-belief: A generative 3D world model for embodied ...
URL: https://github.com/3D-Belief/3d-belief
We propose 3D-Belief, a generative 3D world model that predicts unseen regions in an explicit, actionable 3D representation from partial observations and updates this belief online as new observations arrive. It enables embodied agents to reason about the 3D world under partial observability and make sequential decisions based on up-to-date ...

### [6] Observable quotient world models for knowledge-state abstraction under ...
URL: https://www.sciencedirect.com/science/article/abs/pii/S0950705126014942
Introduction Knowledge-state abstraction under partial observability is an information-selection problem. A learned state should preserve distinctions that are observable and useful for prediction or decision making, while suppressing nuisance variation that cannot be resolved by the sensing process.

### [7] ICML Poster Causal-JEPA: Learning World Models through Object-Level ...
URL: https://icml.cc/virtual/2026/poster/63623
By masking object-level latents and requiring each masked object state to be inferred from the surrounding context, C-JEPA imposes structured partial observability during training, creating counterfactual-like prediction queries that discourage shortcut solutions and make interaction-dependent prediction necessary under the learning objective.

### [8] PDF Simultaneous Deep Model-Based Reinforcement Learning and State ...
URL: https://pages.cs.wisc.edu/~jphanna/papers/Cong_Simultaneous_2026.pdf
However, autonomous robots often operate under partial observability, where the true state is hidden and must be inferred from noisy or incomplete observations. This uncertainty complicates both decision-making and model learning.

### [9] Structured World Belief Models - emergentmind.com
URL: https://www.emergentmind.com/topics/structured-world-belief-models
Structured world belief models, by explicitly representing and updating uncertainty in a principled, modular form, provide a foundation for robust decision-making and reasoning under partial observability.

### [10] Predictive World Models from Real-World Partial Observations
URL: https://ieeexplore.ieee.org/document/10211047
The problem of learning such simulations is called predictive world modeling. Recently, reinforcement learning (RL) agents leveraging world models have achieved SOTA performance in game environments. However, understanding how to apply the world modeling approach in complex real-world environments relevant to mobile robots remains an open question.

### [11] What Is a Failure Mode? Understanding Types and Examples
URL: https://sixsigmadsi.com/glossary/failure-mode/
Learn what failure modes are, how to identify them using FMEA, and how they help reduce risk and improve product reliability.

### [12] Step 4 - Failure Analysis in FMEA (Failure Modes, Effects, Causes)
URL: https://quasist.com/fmea/failure-

... (truncated, see full artifact)


{
  "topic": "World Models under Structured Partial Observability: identify a narrow failure mode and a simple latent-dynamics mechanism worth testing",
  "web_results_count": 18,
  "scholar_papers_count": 0,
  "crawled_pages_count": 5,
  "pdf_extractions_count": 0,
  "has_search_answer": false,
  "elapsed_seconds": 35.51118619996123,
  "web_results": [
    {
      "title": "Causal-JEPA: Learning World Models through - arXiv.org",
      "url": "https://arxiv.org/html/2602.11389v2",
      "snippet": "By masking object-level latents and requiring each masked object state to be inferred from the surrounding context, C-JEPA imposes structured partial observability during training, creating counterfactual-like prediction queries that discourage shortcut solutions and make interaction-dependent prediction necessary under the learning objective.",
      "content": "",
      "score": 0.0,
      "source": "duckduckgo"
    },
    {
      "title": "FieldSeer I: Physics-Guided World Models for Long-Horizon ...",
      "url": "https://arxiv.org/abs/2512.05361",
      "snippet": "We introduce FieldSeer I, a geometry-aware world model that forecasts electromagnetic field dynamics from partial observations in 2-D TE waveguides. The model assimilates a short prefix of observed fields, conditions on a scalar source action and structure/material map, and generates closed-loop rollouts in the physical domain. Training in a symmetric-log domain ensures numerical stability ...",
      "content": "",
      "score": 0.0,
      "source": "duckduckgo"
    },
    {
      "title": "GitHub - santoshkumarradha/uwm-jepa: UWM-JEPA: a JEPA world model with ...",
      "url": "https://github.com/santoshkumarradha/uwm-jepa",
      "snippet": "Unitary density-matrix latent prediction for partially observable JEPA world models. Santosh Kumar Radha \u00b7 Oktay Goktas \u00b7 AgentField AI, Toronto Standard vector-latent JEPAs predict a point in representation space. UWM-JEPA represents the latent as a density matrix and rolls it forward on an isospectral orbit. Under partial observability this gives the predictor a structured latent in which ...",
      "content": "",
      "score": 0.0,
      "source": "duckduckgo"
    },
    {
      "title": "Uncertainty Representations in State-Space Layers for Deep...",
      "url": "https://openreview.net/forum?id=rfPns0WJyg",
      "snippet": "Optimal decision-making under partial observability requires reasoning about the uncertainty of the environment&#x27;s hidden state. However, most reinforcement learning architectures handle partial observability with sequence models that have no internal mechanism to incorporate uncertainty in their hidden state representation, such as recurrent neural networks, deterministic state-space models ...",
      "content": "",
      "score": 0.0,
      "source": "duckduckgo"
    },
    {
      "title": "GitHub - 3D-Belief/3d-belief: A generative 3D world model for embodied ...",
      "url": "https://github.com/3D-Belief/3d-belief",
      "snippet": "We propose 3D-Belief, a generative 3D world model that predicts unseen regions in an explicit, actionable 3D representation from partial observations and updates this belief online as new observations arrive. It enables embodied agents to reason about the 3D world under partial observability and make sequential decisions based on up-to-date ...",
      "content": "",
      "score": 0.0,
      "source": "duckduckgo"
    },
    {
      "title": "Observable quotient world models for knowledge-state abstraction under ...",
      "url": "https://www.sciencedirect.com/science/article/abs/pii/S0950705126014942",
      "snippet": "Introduction Knowledge-state abstraction under partial observability is an information-selection problem. A learned state should preserve distinctions that are observable and useful for prediction or decision making, while suppressing nuisance variation that cannot be resolved by the sensing process.",
      "content": "",
      "score": 0.0,
      "source": "duckduckgo"
    },
    {
      "title": "ICML Poster Causal-JEPA: Learning World Models through Object-Level ...",
      "url": "https://icml.cc/virtual/2026/poster/63623",
      "snippet": "By masking object-level latents and requiring each masked object state to be inferred from the surrounding context, C-JEPA imposes structured partial observability during training, creating counterfactual-like prediction queries that discourage shortcut solutions and make interaction-dependent prediction necessary under the learning objective.",
      "content": "",
      "score": 0.0,
      "source": "duckduckgo"
    },
    {
      "title": "PDF Simultaneous Deep Model-Based Reinforcement Learning and State ...",
      "url": "https://pages.cs.wisc.edu/~jphanna/papers/Cong_Simultaneous_2026.pdf",
      "snippet": "However, autonomous robots often operate under partial observability, where the true state is hidden and must be inferred from noisy or incomplete obse

... (truncated, see full artifact)


@article{schulman2017proximal,
  title={Proximal Policy Optimization Algorithms},
  author={Schulman et al.},
  year={2017},
  url={},
}

@article{mnih2013playing,
  title={Playing Atari with Deep Reinforcement Learning},
  author={Mnih et al.},
  year={2013},
  url={},
}

@article{haarnoja2018soft,
  title={Soft Actor-Critic: Off-Policy Maximum Entropy Deep Reinforcement Learning with a Stochastic Actor},
  author={Haarnoja et al.},
  year={2018},
  url={},
}

@article{chen2018neural,
  title={Neural Ordinary Differential Equations},
  author={Chen et al.},
  year={2018},
  url={},
}


{
  "real_search": false,
  "queries_used": [
    "World Models under Structured Partial Observability",
    "identify a narrow failure mode and",
    "world models",
    "models under",
    "under structured",
    "structured partial"
  ],
  "year_min": 2020,
  "total_candidates": 4,
  "bibtex_entries": 4,
  "ts": "2026-08-23T13:48:58+00:00"
}