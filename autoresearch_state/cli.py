"""Minimal CLI proving that Research State v0.1 is program-consumable."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Mapping

from autoresearch_state.graph import render_mermaid
from autoresearch_state.validation import load_state, validate_state


def _load_valid(path: str) -> tuple[dict[str, Any] | None, int]:
    try:
        state = load_state(path)
        issues = validate_state(state)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return None, 2
    if issues:
        print(f"INVALID: {path}", file=sys.stderr)
        for issue in issues:
            print(f"- {issue}", file=sys.stderr)
        return None, 1
    return state, 0


def _by_id(state: Mapping[str, Any], collection: str) -> dict[str, Mapping[str, Any]]:
    return {str(item["id"]): item for item in state.get(collection, [])}


def cmd_validate(args: argparse.Namespace) -> int:
    try:
        state = load_state(args.state_file)
        issues = validate_state(state, schema_path=args.schema)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    if issues:
        print(f"INVALID: {args.state_file}")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print(f"VALID: {args.state_file} (schema {state['schema_version']})")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    state, code = _load_valid(args.state_file)
    if state is None:
        return code
    project = state["project"]
    decisions = _by_id(state, "decisions")
    hypotheses = _by_id(state, "hypotheses")
    dependencies = _by_id(state, "dependencies")
    tasks = _by_id(state, "tasks")

    current = decisions.get(project.get("current_decision"), {})
    research = decisions.get(project.get("current_research_decision"), {})
    active = [hypotheses[item] for item in project.get("active_hypotheses", [])]
    blockers = [
        dependencies[item]
        for item in project.get("dependencies", [])
        if item in dependencies and dependencies[item].get("status") == "BLOCKED"
    ]
    next_action = tasks.get(project.get("next_action"), {})

    print(f"Project: {project['title']} ({project['id']})")
    print(f"Status: {project['status']}")
    print(f"Phase: {project['current_phase']}")
    print(f"Current Decision: {current.get('decision_type', 'unknown')}")
    print(f"Research Verdict: {research.get('decision_type', project.get('current_research_verdict', 'unknown'))}")
    print("Active Hypotheses:")
    if active:
        for item in active:
            print(f"  - {item['id']}: {item['statement']} [{item['status']}]")
    else:
        print("  - none")
    print("Blockers:")
    if blockers:
        for item in blockers:
            print(f"  - {item['id']}: {item['description']}")
    else:
        print("  - none")
    print(f"Next Action: {next_action.get('title', 'none')}")
    if project.get("resume_point"):
        print(f"Resume Point: {project['resume_point']}")
    return 0


def cmd_graph(args: argparse.Namespace) -> int:
    state, code = _load_valid(args.state_file)
    if state is None:
        return code
    print(render_mermaid(state), end="")
    return 0


def cmd_decisions(args: argparse.Namespace) -> int:
    state, code = _load_valid(args.state_file)
    if state is None:
        return code
    print("TIMESTAMP\tTYPE\tSCOPE\tTARGET\tCONFIDENCE\tVERIFICATION")
    for decision in sorted(state.get("decisions", []), key=lambda item: item["timestamp"]):
        print(
            "\t".join(
                [
                    str(decision["timestamp"]),
                    str(decision["decision_type"]),
                    str(decision["scope"]),
                    str(decision["target_id"]),
                    str(decision["confidence"]),
                    str(decision["human_verification"]),
                ]
            )
        )
    return 0


def cmd_blockers(args: argparse.Namespace) -> int:
    state, code = _load_valid(args.state_file)
    if state is None:
        return code
    blockers = [item for item in state.get("dependencies", []) if item["status"] == "BLOCKED"]
    if not blockers:
        print("No active blockers.")
        return 0
    print("ID\tSOURCE\tTARGET\tTYPE\tDESCRIPTION")
    for item in blockers:
        print(
            "\t".join(
                [
                    item["id"],
                    item["source"],
                    item["target"],
                    item["dependency_type"],
                    item["description"],
                ]
            )
        )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="autoresearch_state", description="Research State v0.1 CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate", help="validate schema and references")
    validate_parser.add_argument("state_file")
    validate_parser.add_argument("--schema", default=None)
    validate_parser.set_defaults(func=cmd_validate)

    for name, help_text, func in (
        ("status", "show the compact project state", cmd_status),
        ("graph", "emit a Mermaid research graph", cmd_graph),
        ("decisions", "list append-only decisions", cmd_decisions),
        ("blockers", "list active blocking dependencies", cmd_blockers),
    ):
        command_parser = subparsers.add_parser(name, help=help_text)
        command_parser.add_argument("state_file")
        command_parser.set_defaults(func=func)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
