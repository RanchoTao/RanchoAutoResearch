"""Shared conventions for Research State v0.1.

The JSON Schema remains the normative field contract.  This module only holds
conventions needed by the validator and CLI; it deliberately avoids a second,
competing object model.
"""

from __future__ import annotations

import os
import time
from typing import Final

SCHEMA_VERSION: Final = "0.1.0"
HUMAN_VERIFICATION: Final = (
    "UNREVIEWED",
    "PARTIALLY_REVIEWED",
    "VERIFIED",
    "REJECTED",
)

COLLECTION_PREFIXES: Final[dict[str, str]] = {
    "hypotheses": "hyp",
    "claims": "claim",
    "evidence": "ev",
    "papers": "paper",
    "theorems": "thm",
    "lemmas": "lem",
    "experiments": "exp",
    "agent_runs": "run",
    "decisions": "dec",
    "dependencies": "dep",
    "artifacts": "art",
    "checkpoints": "chk",
    "tasks": "task",
}

ALL_PREFIXES: Final = {"project": "proj", **COLLECTION_PREFIXES}

_CROCKFORD = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"


def _encode_crockford(value: int, width: int) -> str:
    chars = ["0"] * width
    for index in range(width - 1, -1, -1):
        chars[index] = _CROCKFORD[value & 31]
        value >>= 5
    return "".join(chars)


def generate_id(prefix: str, *, timestamp_ms: int | None = None) -> str:
    """Generate a prefixed ULID-style stable identifier.

    The 26-character payload is lexicographically time-sortable.  Prefixes make
    logs and graph errors human-debuggable.  IDs are generated once and must not
    be regenerated when an object is edited.
    """

    if prefix not in set(ALL_PREFIXES.values()):
        allowed = ", ".join(sorted(set(ALL_PREFIXES.values())))
        raise ValueError(f"unknown Research State ID prefix {prefix!r}; use {allowed}")
    milliseconds = timestamp_ms if timestamp_ms is not None else time.time_ns() // 1_000_000
    if milliseconds < 0 or milliseconds >= 2**48:
        raise ValueError("timestamp_ms must fit in 48 bits")
    randomness = int.from_bytes(os.urandom(10), "big")
    return f"{prefix}_{_encode_crockford(milliseconds, 10)}{_encode_crockford(randomness, 16)}"

