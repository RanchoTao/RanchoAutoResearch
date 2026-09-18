"""Program-consumption tests for the minimal Research State CLI."""

from __future__ import annotations

from pathlib import Path

from autoresearch_state.cli import main
from autoresearch_state.graph import render_mermaid
from autoresearch_state.validation import load_state


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "emergent_levy_project_state.yaml"


def test_dependency_graph_can_be_generated():
    graph = render_mermaid(load_state(EXAMPLE))
    assert graph.startswith("flowchart LR\n")
    assert "dependency:" in graph
    assert "REQUIRES" in graph
    assert "BLOCKED" in graph


def test_cli_status_reports_frozen_state_without_losing_research_verdict(capsys):
    assert main(["status", str(EXAMPLE)]) == 0
    output = capsys.readouterr().out
    assert "Status: FROZEN" in output
    assert "Research Verdict: RESTRICTED_GO" in output
    assert "Paper I" in output
    assert "Resume Point:" in output


def test_cli_validate_accepts_the_real_example(capsys):
    assert main(["validate", str(EXAMPLE)]) == 0
    assert "VALID:" in capsys.readouterr().out


def test_cli_lists_append_only_decision_history(capsys):
    assert main(["decisions", str(EXAMPLE)]) == 0
    output = capsys.readouterr().out
    assert "KILL" in output
    assert "RESTRICTED_GO" in output
    assert "FREEZE" in output


def test_cli_lists_blocking_dependency(capsys):
    assert main(["blockers", str(EXAMPLE)]) == 0
    output = capsys.readouterr().out
    assert "BLOCKED" not in output  # the table is concise; the command filters by status
    assert "Paper I" in output
    assert "REQUIRES" in output
