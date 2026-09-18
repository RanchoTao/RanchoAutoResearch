# Research State v0.1 graph

The schema represents research as linked objects. Arrows below describe
semantic relations, not storage ownership.

```mermaid
flowchart TD
    Project -->|contains| Hypothesis
    Project -->|contains| Claim
    Project -->|contains| Theorem
    Project -->|contains| Experiment
    Project -->|has history| Decision
    Project -->|snapshotted by| Checkpoint
    Project -->|prioritizes| Task

    Hypothesis -->|forks to| Hypothesis
    Hypothesis -->|supported by| Claim
    Hypothesis -->|attacked by| Claim

    Claim -->|supported by| Evidence
    Claim -->|opposed by| Evidence
    Claim -->|gated by| Dependency

    Evidence -->|may reference| Paper
    Evidence -->|may reference| Experiment
    Evidence -->|may reference| Theorem
    Evidence -->|stored in| Artifact
    Evidence -->|created by| AgentRun

    Theorem -->|requires| Lemma
    Theorem -->|gated by| Dependency
    Theorem -->|proof attempt| AgentRun
    Theorem -->|counterexample attempt| AgentRun
    Theorem -->|cites| Paper

    Lemma -->|depends on| Lemma
    Experiment -->|tests| Hypothesis
    Experiment -->|produces| Evidence
    Experiment -->|produces| Artifact

    AgentRun -->|creates or modifies| Claim
    AgentRun -->|creates or modifies| Theorem
    AgentRun -->|creates| Artifact
    AgentRun -->|proposes| Decision

    Decision -->|changes state of| Project
    Decision -->|changes state of| Hypothesis
    Decision -->|changes state of| Theorem
    Decision -->|supersedes without deleting| Decision

    Dependency -->|connects source and target| Paper
    Dependency -->|connects source and target| Theorem
    Dependency -->|connects source and target| Task

    Checkpoint -->|snapshots| Project
    Checkpoint -->|records| Decision
    Checkpoint -->|records blocker| Dependency
    Checkpoint -->|resumes at| Task

    Task -->|points to| Hypothesis
    Task -->|points to| Theorem
    Task -->|points to| Paper
```

## Relation rules

- A Project can be FROZEN while a child Hypothesis remains RESTRICTED and an
  earlier sibling is REFUTED.
- Claim/Evidence polarity is explicit. The same Evidence can support one Claim
  and oppose another.
- Dependency is a first-class edge because “requires,” “blocks,” “contradicts,”
  and “extends” are not interchangeable.
- AgentRun provenance records authorship but does not confer verification.
- Decision `scope` prevents branch KILL from being interpreted as Project KILL.
- Checkpoint carries sufficient IDs and instructions for deterministic resume.

The CLI command below renders the live example graph:

```powershell
python -m autoresearch_state graph examples/emergent_levy_project_state.yaml
```

