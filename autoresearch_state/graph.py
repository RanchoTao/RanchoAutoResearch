"""Mermaid graph generation for Research State documents."""

from __future__ import annotations

import re
from typing import Any, Mapping


def _node_id(object_id: str) -> str:
    return "n_" + re.sub(r"[^A-Za-z0-9_]", "_", object_id)


def _label(item: Mapping[str, Any], fallback: str) -> str:
    raw = item.get("title") or item.get("short_name") or item.get("statement") or fallback
    text = str(raw).replace('"', "'").replace("\n", " ")
    return text if len(text) <= 64 else text[:61] + "..."


def render_mermaid(state: Mapping[str, Any]) -> str:
    """Render the project and its provenance/dependency graph as Mermaid."""

    lines = ["flowchart LR"]
    project = state["project"]
    project_id = str(project["id"])
    lines.append(f'  {_node_id(project_id)}["Project: {_label(project, project_id)}"]')

    collections = (
        "hypotheses",
        "claims",
        "evidence",
        "papers",
        "theorems",
        "lemmas",
        "experiments",
        "agent_runs",
        "decisions",
        "dependencies",
        "artifacts",
        "checkpoints",
        "tasks",
    )
    index: dict[str, Mapping[str, Any]] = {project_id: project}
    for collection in collections:
        for item in state.get(collection, []):
            index[str(item["id"])] = item
            kind = {
                "hypotheses": "hypothesis",
                "evidence": "evidence",
                "agent_runs": "agent run",
                "dependencies": "dependency",
            }.get(collection, collection[:-1])
            lines.append(f'  {_node_id(str(item["id"]))}["{kind}: {_label(item, str(item["id"]))}"]')

    edges: set[tuple[str, str, str]] = set()

    def edge(source: str | None, target: str | None, label: str) -> None:
        if source and target and source in index and target in index:
            edges.add((source, target, label))

    for hypothesis in state.get("hypotheses", []):
        edge(project_id, hypothesis["id"], "contains")
        edge(hypothesis.get("parent_hypothesis"), hypothesis["id"], "forks to")
        for claim in hypothesis.get("supporting_claims", []):
            edge(hypothesis["id"], claim, "supported by")
        for claim in hypothesis.get("attacking_claims", []):
            edge(hypothesis["id"], claim, "attacked by")

    for claim in state.get("claims", []):
        for evidence in claim.get("supporting_evidence", []):
            edge(claim["id"], evidence, "support")
        for evidence in claim.get("opposing_evidence", []):
            edge(claim["id"], evidence, "opposes")

    for evidence in state.get("evidence", []):
        for field, label in (
            ("paper_id", "from paper"),
            ("experiment_id", "from experiment"),
            ("theorem_id", "from theorem"),
            ("artifact_id", "recorded in"),
            ("agent_run_id", "created by"),
        ):
            edge(evidence["id"], evidence.get(field), label)

    for theorem in state.get("theorems", []):
        edge(project_id, theorem["id"], "contains")
        for lemma in theorem.get("required_lemmas", []):
            edge(theorem["id"], lemma, "requires")
        for run in theorem.get("proof_attempts", []):
            edge(theorem["id"], run, "proof attempt")
        for run in theorem.get("counterexample_attempts", []):
            edge(theorem["id"], run, "counterexample attempt")

    for experiment in state.get("experiments", []):
        edge(project_id, experiment["id"], "contains")
        for hypothesis in experiment.get("hypothesis_ids", []):
            edge(experiment["id"], hypothesis, "tests")

    for run in state.get("agent_runs", []):
        edge(project_id, run["id"], "run")
        for artifact in run.get("artifacts", []):
            edge(run["id"], artifact, "creates")
        for claim in run.get("claims_created", []):
            edge(run["id"], claim, "creates")
        for decision in run.get("decisions_proposed", []):
            edge(run["id"], decision, "proposes")

    for decision in state.get("decisions", []):
        edge(decision["id"], decision.get("target_id"), "changes state")

    for checkpoint in state.get("checkpoints", []):
        edge(checkpoint["id"], project_id, "snapshots")

    for task in state.get("tasks", []):
        edge(task["id"], task.get("target_id"), "targets")

    for dependency in state.get("dependencies", []):
        source = str(dependency["source"])
        target = str(dependency["target"])
        dependency_id = str(dependency["id"])
        edge(source, dependency_id, str(dependency["dependency_type"]))
        edge(dependency_id, target, str(dependency["status"]))

    for source, target, label in sorted(edges):
        lines.append(f'  {_node_id(source)} -->|"{label}"| {_node_id(target)}')
    return "\n".join(lines) + "\n"
