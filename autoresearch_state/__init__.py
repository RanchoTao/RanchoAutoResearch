"""Machine-readable research state for AutoResearchClaw.

Research State v0.1 is intentionally independent from the pipeline engine.  It
loads YAML or JSON, validates the document contract and cross-object references,
and renders small command-line views.
"""

from autoresearch_state.models import SCHEMA_VERSION, generate_id
from autoresearch_state.validation import (
    ResearchStateValidationError,
    ValidationIssue,
    load_state,
    validate_state,
)

__all__ = [
    "SCHEMA_VERSION",
    "ResearchStateValidationError",
    "ValidationIssue",
    "generate_id",
    "load_state",
    "validate_state",
]

