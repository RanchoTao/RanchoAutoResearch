"""Small DeepSeek strategist used by the experiment refinement loop.

DeepSeek receives a compact, evidence-backed research state and returns exactly
one experiment proposal.  It never receives shell access and never edits files.
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import re
import socket
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

DEFAULT_BASE_URL = "https://api.deepseek.com"
DEFAULT_MODEL = "deepseek-v4-pro"
DEFAULT_TIMEOUT_SEC = 120.0
DEFAULT_MAX_RETRIES = 2
MAX_RECENT_EXPERIMENTS = 6
MAX_FAILED_IDEAS = 20

PROPOSAL_FIELDS = (
    "hypothesis",
    "rationale",
    "change",
    "files_to_modify",
    "expected_effect",
    "acceptance_criteria",
    "risk",
    "do_not_change",
)
PROPOSAL_LIST_FIELDS = {"files_to_modify", "do_not_change"}

SYSTEM_PROMPT = """You are the AutoResearch Experiment Strategist.

You are not a chat bot. You choose the single next experiment that maximizes
useful evidence toward the research goal. The executor is a separate Codex
process with local file, shell, git, evaluator, and experiment access. You have
no shell access and must never claim that an unrun change worked.

Rules:
- Return one main experiment only, as a JSON object matching the exact schema.
- Prefer the smallest change that tests a clear hypothesis.
- Explain why the observed evidence supports running this experiment now.
- Name the primary metric expected to move and its direction.
- State what result supports the hypothesis and what result rejects it.
- Do not repeat a failed/rejected idea.
- Do not propose refactors, cleanup, documentation, or broad rewrites without
  direct experimental information gain.
- Negative results are valid evidence.
- Modify only files listed in constraints.allowed_files.
- If information is insufficient, propose one minimal diagnostic experiment
  that maximizes information gain.
- Never fabricate evaluator output, metrics, completed runs, commits, or files.

Exact JSON schema (no additional keys):
{
  "hypothesis": "non-empty string",
  "rationale": "non-empty string",
  "change": "non-empty, concrete minimal patch strategy",
  "files_to_modify": ["relative/path"],
  "expected_effect": "metric name, direction, and expected effect",
  "acceptance_criteria": "support and rejection conditions",
  "risk": "main risk and how the evaluator exposes it",
  "do_not_change": ["protected item"]
}
"""


class DeepSeekError(RuntimeError):
    """Base class for explicit DeepSeek failures."""


class DeepSeekUnavailable(DeepSeekError):
    """Raised when no API key is configured."""


class DeepSeekResponseError(DeepSeekError):
    """Raised when the API response is missing or violates the schema."""


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _load_deepseek_env(path: Path | None = None) -> None:
    """Load only DeepSeek variables from ``.env`` without overriding the process.

    The project intentionally avoids a new dotenv dependency. Values are never
    logged, and unrelated entries in the file are ignored.
    """

    env_path = path or (_repo_root() / ".env")
    if not env_path.is_file():
        return
    allowed = {"DEEPSEEK_API_KEY", "DEEPSEEK_BASE_URL", "DEEPSEEK_MODEL"}
    try:
        lines = env_path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        name, value = stripped.split("=", 1)
        name = name.strip()
        if name not in allowed or name in os.environ:
            continue
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        os.environ[name] = value


_load_deepseek_env()
DEEPSEEK_AVAILABLE = bool(os.environ.get("DEEPSEEK_API_KEY", "").strip())


def is_deepseek_available() -> bool:
    """Return current availability so tests and late env configuration work."""

    return bool(os.environ.get("DEEPSEEK_API_KEY", "").strip())


@dataclass(frozen=True)
class DeepSeekConfig:
    api_key: str
    base_url: str = DEFAULT_BASE_URL
    model: str = DEFAULT_MODEL
    timeout_sec: float = DEFAULT_TIMEOUT_SEC
    max_retries: int = DEFAULT_MAX_RETRIES
    log_dir: Path = _repo_root() / "logs"

    @classmethod
    def from_env(cls, *, log_dir: Path | None = None) -> "DeepSeekConfig":
        _load_deepseek_env()
        key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
        if not key:
            raise DeepSeekUnavailable(
                "DEEPSEEK_AVAILABLE=false: DEEPSEEK_API_KEY is missing. "
                "Set it in the process environment or the repository .env file."
            )
        base_url = os.environ.get("DEEPSEEK_BASE_URL", "").strip() or DEFAULT_BASE_URL
        model = os.environ.get("DEEPSEEK_MODEL", "").strip() or DEFAULT_MODEL
        return cls(
            api_key=key,
            base_url=base_url.rstrip("/"),
            model=model,
            log_dir=log_dir or (_repo_root() / "logs"),
        )


def _redact(text: str, api_key: str = "") -> str:
    if api_key:
        text = text.replace(api_key, "[REDACTED]")
    return re.sub(r"\bsk-[A-Za-z0-9_-]{12,}\b", "[REDACTED]", text)


def validate_proposal(value: object, *, allowed_files: Sequence[str] | None = None) -> dict[str, Any]:
    """Strictly validate the strategist's fixed proposal schema."""

    if not isinstance(value, dict):
        raise DeepSeekResponseError("DeepSeek proposal must be a JSON object")
    keys = set(value)
    expected = set(PROPOSAL_FIELDS)
    if keys != expected:
        missing = sorted(expected - keys)
        extra = sorted(keys - expected)
        raise DeepSeekResponseError(
            f"DeepSeek proposal schema mismatch (missing={missing}, extra={extra})"
        )

    normalized: dict[str, Any] = {}
    for field in PROPOSAL_FIELDS:
        item = value[field]
        if field in PROPOSAL_LIST_FIELDS:
            if not isinstance(item, list) or any(
                not isinstance(entry, str) or not entry.strip() for entry in item
            ):
                raise DeepSeekResponseError(f"DeepSeek proposal field {field!r} must be a string list")
            normalized[field] = [entry.strip().replace("\\", "/") for entry in item]
        else:
            if not isinstance(item, str) or not item.strip():
                raise DeepSeekResponseError(f"DeepSeek proposal field {field!r} must be a non-empty string")
            normalized[field] = item.strip()

    if not normalized["files_to_modify"]:
        raise DeepSeekResponseError(
            "DeepSeek proposal files_to_modify must name at least one allowed file"
        )

    for filename in normalized["files_to_modify"]:
        path = Path(filename)
        if path.is_absolute() or ".." in path.parts:
            raise DeepSeekResponseError(f"Unsafe proposal path: {filename}")
    if allowed_files is not None:
        allowed = {str(name).replace("\\", "/") for name in allowed_files}
        disallowed = sorted(set(normalized["files_to_modify"]) - allowed)
        if disallowed:
            raise DeepSeekResponseError(
                f"Proposal targets files outside constraints.allowed_files: {disallowed}"
            )
    return normalized


def _safe_ast_summary(filename: str, code: str) -> str:
    lines = [f"FILE {filename} ({len(code)} chars)"]
    if filename.endswith(".py"):
        try:
            tree = ast.parse(code)
            imports: list[str] = []
            definitions: list[str] = []
            for node in tree.body:
                if isinstance(node, ast.Import):
                    imports.extend(alias.name for alias in node.names)
                elif isinstance(node, ast.ImportFrom):
                    imports.append(node.module or "")
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    args = [arg.arg for arg in node.args.args]
                    definitions.append(f"function {node.name}({', '.join(args)})")
                elif isinstance(node, ast.ClassDef):
                    methods = [item.name for item in node.body if isinstance(item, ast.FunctionDef)]
                    definitions.append(f"class {node.name} methods={methods[:12]}")
            if imports:
                lines.append("imports: " + ", ".join(imports[:20]))
            if definitions:
                lines.extend(definitions[:30])
        except SyntaxError:
            lines.append("AST: current file has a syntax error")
    excerpt = code if len(code) <= 5000 else code[:2500] + "\n...<middle omitted>...\n" + code[-2500:]
    lines.append("CODE EXCERPT:\n" + excerpt)
    return "\n".join(lines)


def summarize_project_files(files: Mapping[str, str], *, max_chars: int = 16000) -> str:
    """Produce an AST-aware, bounded code summary instead of sending a repo dump."""

    parts: list[str] = []
    used = 0
    for filename, code in sorted(files.items()):
        summary = _safe_ast_summary(str(filename), str(code))
        remaining = max_chars - used
        if remaining <= 0:
            break
        if len(summary) > remaining:
            summary = summary[:remaining] + "\n...<state code budget reached>"
        parts.append(summary)
        used += len(summary)
    return "\n\n".join(parts)


def _compact_experiment(item: Mapping[str, Any]) -> dict[str, Any]:
    keep = (
        "run_id",
        "iteration",
        "status",
        "metric",
        "metrics",
        "primary_metric",
        "improved",
        "kept",
        "elapsed_sec",
        "timed_out",
        "error",
        "runtime_issues",
        "validation_summary",
        "deepseek_proposal",
    )
    compact = {key: item[key] for key in keep if key in item}
    proposal = compact.get("deepseek_proposal")
    if isinstance(proposal, dict):
        compact["deepseek_proposal"] = {
            key: proposal[key] for key in ("hypothesis", "change", "expected_effect") if key in proposal
        }
    return compact


def build_research_state(
    *,
    research_goal: str,
    metric_key: str,
    metric_direction: str,
    current_metric: float | None,
    best_metric: float | None,
    current_files: Mapping[str, str],
    recent_experiments: Sequence[Mapping[str, Any]],
    failed_ideas: Sequence[str] = (),
    best_commit: str = "",
    hardware: Mapping[str, Any] | None = None,
    time_budget_sec: int = 0,
    experiment_id: str = "",
    evaluator_definition: str = "",
    experiment_plan: str = "",
) -> dict[str, Any]:
    """Build the bounded state shared between the real loop and CLI helper."""

    allowed_files = sorted(str(name).replace("\\", "/") for name in current_files)
    return {
        "experiment_id": experiment_id,
        "research_goal": research_goal.strip(),
        "experiment_plan_summary": experiment_plan.strip()[:6000],
        "current_metric": {
            "name": metric_key,
            "value": current_metric,
            "direction": metric_direction,
        },
        "best_metric": {
            "name": metric_key,
            "value": best_metric,
            "direction": metric_direction,
        },
        "best_commit": best_commit,
        "recent_experiments": [
            _compact_experiment(item) for item in recent_experiments[-MAX_RECENT_EXPERIMENTS:]
        ],
        "current_code_summary": summarize_project_files(current_files),
        "constraints": {
            "allowed_files": allowed_files,
            "hardware": dict(hardware or {}),
            "time_budget_sec": int(time_budget_sec),
            "one_experiment_per_round": True,
            "deepseek_has_shell_access": False,
        },
        "evaluator": {
            "metric_key": metric_key,
            "metric_direction": metric_direction,
            "definition": evaluator_definition.strip(),
            "results_must_come_from_real_execution": True,
        },
        "failed_ideas": [str(idea)[:1000] for idea in failed_ideas[-MAX_FAILED_IDEAS:]],
    }


class DeepSeekClient:
    """Minimal OpenAI-compatible DeepSeek chat-completions client."""

    def __init__(self, config: DeepSeekConfig | None = None) -> None:
        self.config = config or DeepSeekConfig.from_env()

    def propose(self, state: Mapping[str, Any], *, experiment_id: str = "") -> dict[str, Any]:
        return self._call("propose", state, experiment_id=experiment_id)

    def analyze(self, state: Mapping[str, Any], *, experiment_id: str = "") -> dict[str, Any]:
        return self._call("analyze", state, experiment_id=experiment_id)

    def _endpoint(self) -> str:
        base = self.config.base_url.rstrip("/")
        return base if base.endswith("/chat/completions") else base + "/chat/completions"

    def _call(self, mode: str, state: Mapping[str, Any], *, experiment_id: str) -> dict[str, Any]:
        if mode not in {"propose", "analyze"}:
            raise ValueError(f"Unsupported DeepSeek mode: {mode}")
        allowed_files = None
        constraints = state.get("constraints")
        if isinstance(constraints, Mapping):
            raw_allowed = constraints.get("allowed_files")
            if isinstance(raw_allowed, list) and all(isinstance(item, str) for item in raw_allowed):
                allowed_files = raw_allowed

        instruction = (
            "Analyze the latest real result, then choose the next single experiment."
            if mode == "analyze"
            else "Choose the first single experiment from the current evidence."
        )
        serialized_state = _redact(
            json.dumps(dict(state), ensure_ascii=False, separators=(",", ":")),
            self.config.api_key,
        )
        request_payload = {
            "model": self.config.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": instruction + " Return JSON only.\n\nRESEARCH STATE:\n" + serialized_state,
                },
            ],
            "response_format": {"type": "json_object"},
            "max_tokens": 4096,
        }

        started = time.monotonic()
        last_error: Exception | None = None
        response_payload: dict[str, Any] | None = None
        attempts = 0
        for attempt in range(self.config.max_retries + 1):
            attempts = attempt + 1
            try:
                response_payload = self._request_once(request_payload)
                break
            except (json.JSONDecodeError, DeepSeekResponseError) as exc:
                last_error = exc
                break
            except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, socket.timeout) as exc:
                last_error = exc
                retryable = not isinstance(exc, urllib.error.HTTPError) or exc.code in {
                    408, 409, 429, 500, 502, 503, 504
                }
                if attempt >= self.config.max_retries or not retryable:
                    break
                time.sleep(min(2**attempt, 4))

        latency = time.monotonic() - started
        if response_payload is None:
            message = _redact(str(last_error or "unknown API error"), self.config.api_key)
            self._write_call_log(
                mode=mode,
                experiment_id=experiment_id,
                success=False,
                latency_s=latency,
                attempts=attempts,
                error=message,
            )
            raise DeepSeekError(f"DeepSeek API failed after {attempts} attempt(s): {message}")

        trace_path = self._write_raw_response(response_payload, mode, experiment_id)
        try:
            choices = response_payload.get("choices")
            if not isinstance(choices, list) or not choices or not isinstance(choices[0], dict):
                raise DeepSeekResponseError("DeepSeek response has no choices[0]")
            first = choices[0]
            if first.get("finish_reason") == "length":
                raise DeepSeekResponseError("DeepSeek JSON response was truncated (finish_reason=length)")
            message = first.get("message")
            if not isinstance(message, dict) or not isinstance(message.get("content"), str):
                raise DeepSeekResponseError("DeepSeek response has no message.content")
            content = message["content"].strip()
            if not content:
                raise DeepSeekResponseError("DeepSeek returned empty JSON content")
            parsed = json.loads(content)
            proposal = validate_proposal(parsed, allowed_files=allowed_files)
        except (json.JSONDecodeError, DeepSeekResponseError) as exc:
            self._write_call_log(
                mode=mode,
                experiment_id=experiment_id,
                success=False,
                latency_s=latency,
                attempts=attempts,
                error=_redact(str(exc), self.config.api_key),
                response=response_payload,
                raw_response_path=trace_path,
            )
            raise DeepSeekResponseError(f"Invalid DeepSeek proposal: {exc}") from exc

        self._write_call_log(
            mode=mode,
            experiment_id=experiment_id,
            success=True,
            latency_s=latency,
            attempts=attempts,
            response=response_payload,
            raw_response_path=trace_path,
        )
        return proposal

    def _request_once(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        body = json.dumps(dict(payload), ensure_ascii=False).encode("utf-8")
        request = urllib.request.Request(
            self._endpoint(),
            data=body,
            method="POST",
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "AutoResearchClaw-DeepSeek-Strategist/1.0",
            },
        )
        with urllib.request.urlopen(request, timeout=self.config.timeout_sec) as response:
            raw = response.read().decode("utf-8", errors="replace")
        parsed = json.loads(raw)
        if not isinstance(parsed, dict):
            raise DeepSeekResponseError("DeepSeek HTTP response must be a JSON object")
        return parsed

    def _write_raw_response(self, payload: Mapping[str, Any], mode: str, experiment_id: str) -> str:
        response_dir = self.config.log_dir / "deepseek_responses"
        response_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        safe_id = re.sub(r"[^A-Za-z0-9_.-]+", "-", experiment_id or "unknown")[:80]
        path = response_dir / f"{stamp}-{safe_id}-{mode}.json"
        path.write_text(json.dumps(dict(payload), ensure_ascii=False, indent=2), encoding="utf-8")
        return str(path)

    def _write_call_log(
        self,
        *,
        mode: str,
        experiment_id: str,
        success: bool,
        latency_s: float,
        attempts: int,
        error: str = "",
        response: Mapping[str, Any] | None = None,
        raw_response_path: str = "",
    ) -> None:
        usage = response.get("usage") if isinstance(response, Mapping) else None
        usage = usage if isinstance(usage, Mapping) else {}
        record: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "mode": mode,
            "model": self.config.model,
            "experiment_id": experiment_id,
            "success": success,
            "latency_s": round(latency_s, 3),
            "input_tokens": usage.get("prompt_tokens", usage.get("input_tokens")),
            "output_tokens": usage.get("completion_tokens", usage.get("output_tokens")),
            "attempts": attempts,
        }
        if error:
            record["error"] = _redact(error, self.config.api_key)[:2000]
        if raw_response_path:
            record["raw_response_path"] = raw_response_path
        self.config.log_dir.mkdir(parents=True, exist_ok=True)
        log_path = self.config.log_dir / "deepseek_calls.jsonl"
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="DeepSeek AutoResearch Experiment Strategist")
    parser.add_argument("mode", choices=("propose", "analyze", "smoke"))
    parser.add_argument("--state", type=Path, help="Compact research-state JSON")
    parser.add_argument("--output", type=Path, help="Validated proposal output JSON")
    parser.add_argument("--experiment-id", default="")
    parser.add_argument("--log-dir", type=Path, default=None)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    try:
        if args.mode == "smoke":
            state = build_research_state(
                research_goal=(
                    "API connectivity smoke test only: choose one harmless parameter "
                    "diagnostic; no research result has been run."
                ),
                metric_key="smoke_metric",
                metric_direction="maximize",
                current_metric=None,
                best_metric=None,
                current_files={"main.py": "SMOKE_PARAMETER = 1\n"},
                recent_experiments=[],
                time_budget_sec=1,
                experiment_id=args.experiment_id or "deepseek-smoke",
                evaluator_definition="No evaluator run; validate proposal structure only.",
            )
            output_path = args.output or (
                _repo_root() / "logs" / "deepseek_smoke_proposal.json"
            )
        else:
            if args.state is None or args.output is None:
                raise DeepSeekResponseError(
                    "propose/analyze require both --state and --output"
                )
            state = json.loads(args.state.read_text(encoding="utf-8"))
            if not isinstance(state, dict):
                raise DeepSeekResponseError("State file must contain a JSON object")
            output_path = args.output
        config = DeepSeekConfig.from_env(log_dir=args.log_dir)
        client = DeepSeekClient(config)
        if args.mode in {"propose", "smoke"}:
            proposal = client.propose(
                state, experiment_id=args.experiment_id or "deepseek-smoke"
            )
        else:
            proposal = client.analyze(state, experiment_id=args.experiment_id)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(proposal, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"DeepSeek {args.mode} succeeded; validated proposal saved to {output_path}")
        return 0
    except (OSError, json.JSONDecodeError, DeepSeekError) as exc:
        print(_redact(f"DeepSeek {args.mode} failed: {exc}"))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
