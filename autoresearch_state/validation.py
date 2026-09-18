"""Schema and graph-integrity validation for Research State v0.1."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Mapping

import yaml

from autoresearch_state.models import COLLECTION_PREFIXES, HUMAN_VERIFICATION


@dataclass(frozen=True)
class ValidationIssue:
    """One human-readable validation failure."""

    path: str
    message: str

    def __str__(self) -> str:
        return f"{self.path}: {self.message}"


class ResearchStateValidationError(ValueError):
    """Raised when a caller requests exception-based validation."""

    def __init__(self, issues: Iterable[ValidationIssue]):
        self.issues = tuple(issues)
        super().__init__("\n".join(str(issue) for issue in self.issues))


def default_schema_path() -> Path:
    return Path(__file__).resolve().parent.parent / "schemas" / "research_state_v0.1.schema.json"


def load_state(path: str | Path) -> dict[str, Any]:
    """Load a YAML or JSON Research State document without mutating it."""

    state_path = Path(path)
    text = state_path.read_text(encoding="utf-8")
    if state_path.suffix.lower() == ".json":
        data = json.loads(text)
    else:
        data = yaml.safe_load(text)
    if not isinstance(data, dict):
        raise ValueError(f"Research State root must be an object: {state_path}")
    return data


def load_schema(path: str | Path | None = None) -> dict[str, Any]:
    schema_path = Path(path) if path is not None else default_schema_path()
    data = json.loads(schema_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"JSON Schema root must be an object: {schema_path}")
    return data


def _resolve_ref(root_schema: Mapping[str, Any], ref: str) -> Mapping[str, Any]:
    if not ref.startswith("#/"):
        raise ValueError(f"only local JSON Schema references are supported: {ref}")
    node: Any = root_schema
    for part in ref[2:].split("/"):
        key = part.replace("~1", "/").replace("~0", "~")
        node = node[key]
    if not isinstance(node, Mapping):
        raise ValueError(f"JSON Schema reference does not resolve to an object: {ref}")
    return node


def _is_type(value: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, Mapping)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "null":
        return value is None
    return True


def _validate_schema_node(
    value: Any,
    schema: Mapping[str, Any],
    root_schema: Mapping[str, Any],
    path: str,
) -> list[ValidationIssue]:
    """Validate the Draft 2020-12 subset used by the v0.1 contract.

    Keeping this small validator in-tree lets the CLI work with the project's
    existing dependencies.  The schema itself is standard JSON Schema and can
    also be validated with a full implementation in downstream integrations.
    """

    if "$ref" in schema:
        return _validate_schema_node(value, _resolve_ref(root_schema, str(schema["$ref"])), root_schema, path)

    if "anyOf" in schema:
        branch_issues = [
            _validate_schema_node(value, branch, root_schema, path)
            for branch in schema["anyOf"]
        ]
        if not any(not issues for issues in branch_issues):
            return [ValidationIssue(path, "does not match any allowed schema")]
        return []

    expected = schema.get("type")
    expected_types = [expected] if isinstance(expected, str) else list(expected or [])
    if expected_types and not any(_is_type(value, item) for item in expected_types):
        return [ValidationIssue(path, f"expected type {' or '.join(expected_types)}")]

    issues: list[ValidationIssue] = []
    if "const" in schema and value != schema["const"]:
        issues.append(ValidationIssue(path, f"must equal {schema['const']!r}"))
        return issues
    if "enum" in schema and value not in schema["enum"]:
        issues.append(ValidationIssue(path, f"invalid value {value!r}; allowed: {', '.join(map(str, schema['enum']))}"))
        return issues

    if isinstance(value, str):
        if "minLength" in schema and len(value) < int(schema["minLength"]):
            issues.append(ValidationIssue(path, f"must contain at least {schema['minLength']} characters"))
        pattern = schema.get("pattern")
        if pattern and re.fullmatch(str(pattern), value) is None:
            issues.append(ValidationIssue(path, f"does not match pattern {pattern}"))
        if schema.get("format") == "date-time":
            try:
                datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                issues.append(ValidationIssue(path, "must be an ISO-8601 date-time"))

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            issues.append(ValidationIssue(path, f"must be >= {schema['minimum']}"))
        if "maximum" in schema and value > schema["maximum"]:
            issues.append(ValidationIssue(path, f"must be <= {schema['maximum']}"))

    if isinstance(value, list):
        if "minItems" in schema and len(value) < int(schema["minItems"]):
            issues.append(ValidationIssue(path, f"must contain at least {schema['minItems']} items"))
        item_schema = schema.get("items")
        if isinstance(item_schema, Mapping):
            for index, item in enumerate(value):
                issues.extend(_validate_schema_node(item, item_schema, root_schema, f"{path}[{index}]"))

    if isinstance(value, Mapping):
        required = schema.get("required", [])
        for key in required:
            if key not in value:
                issues.append(ValidationIssue(path, f"missing required field {key!r}"))
        properties = schema.get("properties", {})
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key in properties:
                issues.extend(_validate_schema_node(child, properties[key], root_schema, child_path))
            elif schema.get("additionalProperties") is False:
                issues.append(ValidationIssue(child_path, "unknown field"))
            elif isinstance(schema.get("additionalProperties"), Mapping):
                issues.extend(
                    _validate_schema_node(child, schema["additionalProperties"], root_schema, child_path)
                )
    return issues


def _as_refs(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [item for item in value if isinstance(item, str)]
    return []


REFERENCE_FIELDS: dict[str, dict[str, tuple[str, ...] | None]] = {
    "project": {
        "current_decision": ("dec",),
        "current_research_decision": ("dec",),
        "dependencies": ("dep",),
        "active_hypotheses": ("hyp",),
        "next_action": ("task",),
    },
    "hypotheses": {
        "project_id": ("proj",),
        "parent_hypothesis": ("hyp",),
        "children": ("hyp",),
        "supporting_claims": ("claim",),
        "attacking_claims": ("claim",),
        "agent_run_id": ("run",),
    },
    "claims": {
        "project_id": ("proj",),
        "supporting_evidence": ("ev",),
        "opposing_evidence": ("ev",),
        "dependencies": ("dep",),
        "source": None,
        "agent_run_id": ("run",),
    },
    "evidence": {
        "project_id": ("proj",),
        "supports": ("claim",),
        "opposes": ("claim",),
        "artifact_id": ("art",),
        "paper_id": ("paper",),
        "experiment_id": ("exp",),
        "theorem_id": ("thm",),
        "agent_run_id": ("run",),
    },
    "papers": {
        "project_id": ("proj",),
        "cited_by_project_claims": ("claim",),
        "artifact_id": ("art",),
    },
    "theorems": {
        "project_id": ("proj",),
        "dependencies": ("dep",),
        "required_lemmas": ("lem",),
        "proof_attempts": ("run",),
        "counterexample_attempts": ("run",),
        "references": ("paper",),
        "supporting_claims": ("claim",),
    },
    "lemmas": {
        "project_id": ("proj",),
        "parent_theorems": ("thm",),
        "dependencies": None,
        "proof_attempts": ("run",),
        "references": ("paper",),
        "counterexamples": ("ev",),
    },
    "experiments": {
        "project_id": ("proj",),
        "hypothesis_ids": ("hyp",),
        "artifacts": ("art",),
        "result_evidence": ("ev",),
        "agent_run_id": ("run",),
    },
    "agent_runs": {
        "project_id": ("proj",),
        "inputs": None,
        "outputs": None,
        "artifacts": ("art",),
        "claims_created": ("claim",),
        "claims_modified": ("claim",),
        "decisions_proposed": ("dec",),
    },
    "decisions": {
        "project_id": ("proj",),
        "target_id": None,
        "supporting_evidence": ("ev",),
        "opposing_evidence": ("ev",),
        "supersedes": ("dec",),
        "next_action": ("task",),
        "agent_run_id": ("run",),
    },
    "dependencies": {"source": None, "target": None},
    "artifacts": {
        "project_id": ("proj",),
        "agent_run_id": ("run",),
        "related_objects": None,
    },
    "checkpoints": {
        "project_id": ("proj",),
        "current_decision": ("dec",),
        "active_hypotheses": ("hyp",),
        "blocking_dependencies": ("dep",),
        "next_action": ("task",),
        "artifacts": ("art",),
    },
    "tasks": {
        "project_id": ("proj",),
        "target_id": None,
        "depends_on": None,
        "result": None,
        "agent_run_id": ("run",),
    },
}


def _semantic_issues(state: Mapping[str, Any]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    id_to_path: dict[str, str] = {}
    id_to_prefix: dict[str, str] = {}

    project = state.get("project")
    if isinstance(project, Mapping) and isinstance(project.get("id"), str):
        project_id = str(project["id"])
        id_to_path[project_id] = "$.project.id"
        id_to_prefix[project_id] = "proj"
        if not project_id.startswith("proj_"):
            issues.append(ValidationIssue("$.project.id", "project ID must use proj_ prefix"))

    for collection, prefix in COLLECTION_PREFIXES.items():
        values = state.get(collection, [])
        if not isinstance(values, list):
            continue
        for index, item in enumerate(values):
            if not isinstance(item, Mapping) or not isinstance(item.get("id"), str):
                continue
            object_id = str(item["id"])
            item_path = f"$.{collection}[{index}].id"
            if object_id in id_to_path:
                issues.append(
                    ValidationIssue(item_path, f"duplicate ID {object_id!r}; first used at {id_to_path[object_id]}")
                )
            else:
                id_to_path[object_id] = item_path
                id_to_prefix[object_id] = prefix
            if not object_id.startswith(f"{prefix}_"):
                issues.append(ValidationIssue(item_path, f"ID must use {prefix}_ prefix"))

    def check_refs(owner_path: str, item: Mapping[str, Any], rules: Mapping[str, tuple[str, ...] | None]) -> None:
        for field, allowed_prefixes in rules.items():
            for ref in _as_refs(item.get(field)):
                ref_path = f"{owner_path}.{field}"
                if ref not in id_to_path:
                    issues.append(ValidationIssue(ref_path, f"broken reference {ref!r}"))
                elif allowed_prefixes is not None and id_to_prefix.get(ref) not in allowed_prefixes:
                    allowed = ", ".join(f"{prefix}_" for prefix in allowed_prefixes)
                    issues.append(ValidationIssue(ref_path, f"reference {ref!r} must target {allowed}"))

    if isinstance(project, Mapping):
        check_refs("$.project", project, REFERENCE_FIELDS["project"])
        if project.get("status") == "FROZEN" and not project.get("resume_point"):
            issues.append(ValidationIssue("$.project.resume_point", "FROZEN project must retain a resume point"))

    for collection, rules in REFERENCE_FIELDS.items():
        if collection == "project":
            continue
        values = state.get(collection, [])
        if not isinstance(values, list):
            continue
        for index, item in enumerate(values):
            if isinstance(item, Mapping):
                check_refs(f"$.{collection}[{index}]", item, rules)

    for collection in ("claims", "evidence", "theorems", "decisions"):
        values = state.get(collection, [])
        if not isinstance(values, list):
            continue
        for index, item in enumerate(values):
            if not isinstance(item, Mapping):
                continue
            verification = item.get("human_verification")
            if verification not in HUMAN_VERIFICATION:
                issues.append(
                    ValidationIssue(
                        f"$.{collection}[{index}].human_verification",
                        "missing or invalid human verification state",
                    )
                )

    for index, theorem in enumerate(state.get("theorems", [])):
        if not isinstance(theorem, Mapping):
            continue
        if theorem.get("status") == "PROVED_BY_AGENT" and theorem.get("human_verification") == "VERIFIED":
            issues.append(
                ValidationIssue(
                    f"$.theorems[{index}]",
                    "PROVED_BY_AGENT cannot be human VERIFIED; promote status to HUMAN_VERIFIED after review",
                )
            )

    for index, evidence in enumerate(state.get("evidence", [])):
        if not isinstance(evidence, Mapping):
            continue
        if evidence.get("verified") is True and evidence.get("verification_status") != "VERIFIED":
            issues.append(
                ValidationIssue(
                    f"$.evidence[{index}].verification_status",
                    "verified=true requires verification_status=VERIFIED",
                )
            )
    return issues


def validate_state(
    state: Mapping[str, Any],
    *,
    schema_path: str | Path | None = None,
    raise_on_error: bool = False,
) -> list[ValidationIssue]:
    """Validate schema fields, unique IDs, cross-references, and invariants."""

    schema = load_schema(schema_path)
    issues = _validate_schema_node(state, schema, schema, "$")
    issues.extend(_semantic_issues(state))
    if raise_on_error and issues:
        raise ResearchStateValidationError(issues)
    return issues
