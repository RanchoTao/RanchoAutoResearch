"""Contract tests for Research State v0.1 schema and invariants."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from autoresearch_state.models import generate_id
from autoresearch_state.validation import load_state, validate_state


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "emergent_levy_project_state.yaml"


def fresh_state():
    return deepcopy(load_state(EXAMPLE))


def messages(state) -> str:
    return "\n".join(str(issue) for issue in validate_state(state))


def test_example_state_passes_schema_and_semantic_validation():
    assert validate_state(fresh_state()) == []


def test_invalid_status_is_rejected():
    state = fresh_state()
    state["project"]["status"] = "NOT_A_RESEARCH_STATUS"
    assert "invalid value" in messages(state)


def test_missing_required_id_is_rejected():
    state = fresh_state()
    del state["claims"][0]["id"]
    assert "missing required field 'id'" in messages(state)


def test_duplicate_ids_are_detected_globally():
    state = fresh_state()
    state["claims"][1]["id"] = state["claims"][0]["id"]
    assert "duplicate ID" in messages(state)


def test_broken_references_are_detected():
    state = fresh_state()
    state["project"]["active_hypotheses"].append(generate_id("hyp"))
    assert "broken reference" in messages(state)


def test_frozen_project_must_retain_resume_point():
    state = fresh_state()
    assert state["project"]["status"] == "FROZEN"
    assert state["project"]["resume_point"]
    state["project"]["resume_point"] = None
    assert "FROZEN project must retain a resume point" in messages(state)


def test_agent_proof_is_not_human_verification():
    state = fresh_state()
    state["theorems"][0]["status"] = "PROVED_BY_AGENT"
    state["theorems"][0]["human_verification"] = "VERIFIED"
    assert "PROVED_BY_AGENT cannot be human VERIFIED" in messages(state)


def test_branch_kill_does_not_kill_the_project():
    state = fresh_state()
    assert any(item["status"] == "REFUTED" for item in state["hypotheses"])
    assert any(
        item["decision_type"] == "KILL" and item["scope"] == "HYPOTHESIS"
        for item in state["decisions"]
    )
    assert state["project"]["status"] == "FROZEN"
    assert state["project"]["current_research_verdict"] == "RESTRICTED_GO"
    assert validate_state(state) == []
