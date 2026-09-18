from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from researchclaw.experiment import deepseek_agent as ds


def _proposal() -> dict[str, object]:
    return {
        "hypothesis": "Reducing the learning rate will improve validation loss.",
        "rationale": "The latest run oscillated while the evaluator remained stable.",
        "change": "Change only LEARNING_RATE from 0.01 to 0.003 in main.py.",
        "files_to_modify": ["main.py"],
        "expected_effect": "val_loss should decrease.",
        "acceptance_criteria": "Support: val_loss < 0.35; reject: val_loss >= 0.35.",
        "risk": "A slower rate may not converge within the time budget.",
        "do_not_change": ["dataset split", "evaluator"],
    }


def _state() -> dict[str, object]:
    return ds.build_research_state(
        research_goal="Minimize validation loss",
        metric_key="val_loss",
        metric_direction="minimize",
        current_metric=0.4,
        best_metric=0.35,
        current_files={"main.py": "LEARNING_RATE = 0.01\nprint('val_loss: 0.4')\n"},
        recent_experiments=[
            {"iteration": i, "metric": 1.0 / (i + 1), "stdout": "x" * 10000}
            for i in range(10)
        ],
        failed_ideas=[f"failed-{i}" for i in range(30)],
        time_budget_sec=300,
        experiment_id="smoke-1",
        evaluator_definition="Parse val_loss from real stdout.",
        experiment_plan="conditions: [baseline, proposed]",
    )


def test_build_state_is_compact_and_preserves_required_evidence() -> None:
    state = _state()
    assert state["research_goal"] == "Minimize validation loss"
    assert state["constraints"]["allowed_files"] == ["main.py"]
    assert state["constraints"]["time_budget_sec"] == 300
    assert state["evaluator"]["metric_key"] == "val_loss"
    assert state["experiment_plan_summary"]
    assert len(state["recent_experiments"]) == ds.MAX_RECENT_EXPERIMENTS
    assert len(state["failed_ideas"]) == ds.MAX_FAILED_IDEAS
    assert "stdout" not in state["recent_experiments"][0]
    assert "LEARNING_RATE" in state["current_code_summary"]


def test_validate_proposal_rejects_extra_fields_and_disallowed_paths() -> None:
    proposal = _proposal()
    assert ds.validate_proposal(proposal, allowed_files=["main.py"])["files_to_modify"] == ["main.py"]

    with_extra = dict(proposal, invented_result="worked")
    with pytest.raises(ds.DeepSeekResponseError, match="schema mismatch"):
        ds.validate_proposal(with_extra)

    unsafe = dict(proposal, files_to_modify=["../outside.py"])
    with pytest.raises(ds.DeepSeekResponseError, match="Unsafe proposal path"):
        ds.validate_proposal(unsafe)

    disallowed = dict(proposal, files_to_modify=["new_framework.py"])
    with pytest.raises(ds.DeepSeekResponseError, match="outside constraints"):
        ds.validate_proposal(disallowed, allowed_files=["main.py"])


def test_missing_key_is_explicit(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    monkeypatch.setattr(ds, "_load_deepseek_env", lambda path=None: None)
    with pytest.raises(ds.DeepSeekUnavailable, match="DEEPSEEK_AVAILABLE=false"):
        ds.DeepSeekConfig.from_env()


def test_client_parses_json_and_writes_usage_log(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    response_payload = {
        "model": "deepseek-test",
        "choices": [
            {
                "finish_reason": "stop",
                "message": {"content": json.dumps(_proposal())},
            }
        ],
        "usage": {"prompt_tokens": 123, "completion_tokens": 45},
    }

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self) -> bytes:
            return json.dumps(response_payload).encode("utf-8")

    requests = []

    def fake_urlopen(request, timeout):
        requests.append((request, timeout))
        return FakeResponse()

    monkeypatch.setattr(ds.urllib.request, "urlopen", fake_urlopen)
    config = ds.DeepSeekConfig(
        api_key="sk-unit-test-secret-should-never-log",
        base_url="https://example.invalid/v1",
        model="deepseek-test",
        timeout_sec=7,
        max_retries=0,
        log_dir=tmp_path / "logs",
    )
    result = ds.DeepSeekClient(config).propose(_state(), experiment_id="exp-1")

    assert result["hypothesis"].startswith("Reducing")
    assert requests[0][1] == 7
    request_json = json.loads(requests[0][0].data.decode("utf-8"))
    assert request_json["response_format"] == {"type": "json_object"}
    assert request_json["model"] == "deepseek-test"
    assert "sk-unit-test-secret" not in json.dumps(request_json)

    log_path = tmp_path / "logs" / "deepseek_calls.jsonl"
    record = json.loads(log_path.read_text(encoding="utf-8"))
    assert record["success"] is True
    assert record["input_tokens"] == 123
    assert record["output_tokens"] == 45
    assert "sk-unit-test" not in log_path.read_text(encoding="utf-8")
    assert list((tmp_path / "logs" / "deepseek_responses").glob("*.json"))


def test_client_retries_transient_network_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import urllib.error

    response_payload = {
        "choices": [
            {"finish_reason": "stop", "message": {"content": json.dumps(_proposal())}}
        ]
    }

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self) -> bytes:
            return json.dumps(response_payload).encode()

    attempts = 0

    def flaky_urlopen(request, timeout):
        nonlocal attempts
        _ = request, timeout
        attempts += 1
        if attempts == 1:
            raise urllib.error.URLError("temporary outage")
        return FakeResponse()

    monkeypatch.setattr(ds.urllib.request, "urlopen", flaky_urlopen)
    monkeypatch.setattr(ds.time, "sleep", lambda seconds: None)
    config = ds.DeepSeekConfig(
        api_key="test-key",
        max_retries=1,
        log_dir=tmp_path / "logs",
    )
    ds.DeepSeekClient(config).analyze(_state(), experiment_id="retry-test")
    record = json.loads((config.log_dir / "deepseek_calls.jsonl").read_text())
    assert attempts == 2
    assert record["attempts"] == 2


def test_stage13_hands_validated_proposal_to_codex_executor(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from researchclaw.adapters import AdapterBundle
    from researchclaw.config import RCConfig
    from researchclaw.llm.client import LLMResponse
    from researchclaw.pipeline.stage_impls import _execution

    run_dir = tmp_path / "run"
    stage_dir = run_dir / "stage-13"
    stage_dir.mkdir(parents=True)
    code_dir = run_dir / "stage-10"
    code_dir.mkdir()
    (code_dir / "experiment.py").write_text(
        "print('primary_metric: 0.5')\n", encoding="utf-8"
    )
    runs_dir = run_dir / "stage-12" / "runs"
    runs_dir.mkdir(parents=True)
    (runs_dir / "run-1.json").write_text(
        json.dumps(
            {
                "run_id": "run-1",
                "status": "completed",
                "metrics": {"primary_metric": 0.5},
            }
        ),
        encoding="utf-8",
    )
    cfg = RCConfig.from_dict(
        {
            "project": {"name": "deepseek-smoke", "mode": "docs-first"},
            "research": {
                "topic": "Improve the real primary metric",
                "domains": ["ml"],
            },
            "runtime": {"timezone": "UTC"},
            "notifications": {"channel": "console"},
            "knowledge_base": {"backend": "markdown", "root": str(tmp_path / "kb")},
            "llm": {
                "provider": "openai-compatible",
                "base_url": "http://localhost.invalid/v1",
                "api_key_env": "DEEPSEEK_TEST_ONLY_KEY",
                "api_key": "test-only",
                "primary_model": "fake",
            },
            "experiment": {
                "mode": "sandbox",
                "time_budget_sec": 30,
                "max_iterations": 1,
                "metric_key": "primary_metric",
                "metric_direction": "minimize",
                "sandbox": {"python_path": sys.executable},
            },
        },
        project_root=tmp_path,
        check_paths=False,
    )

    captured_states: list[dict[str, object]] = []

    class FakeConfig:
        @classmethod
        def from_env(cls):
            return cls()

    class FakeStrategist:
        def __init__(self, config):
            assert isinstance(config, FakeConfig)

        def propose(self, state, *, experiment_id):
            captured_states.append(state)
            return _proposal() | {
                "hypothesis": "A smaller printed test value validates the handoff path.",
                "change": "Change the primary_metric value in main.py from 0.5 to 0.3.",
                "expected_effect": "primary_metric should decrease from 0.5 to 0.3.",
                "acceptance_criteria": "Support below 0.5; reject at or above 0.5.",
            }

        analyze = propose

    monkeypatch.setattr(ds, "is_deepseek_available", lambda: True)
    monkeypatch.setattr(ds, "DeepSeekConfig", FakeConfig)
    monkeypatch.setattr(ds, "DeepSeekClient", FakeStrategist)

    class FakeCodex:
        def __init__(self):
            self.prompts: list[str] = []

        def chat(self, messages, **kwargs):
            _ = kwargs
            self.prompts.append(messages[-1]["content"])
            return LLMResponse(
                content="```python\nprint('primary_metric: 0.3')\n```",
                model="fake-codex",
            )

    codex = FakeCodex()
    _execution._execute_iterative_refine(
        stage_dir, run_dir, cfg, AdapterBundle(), llm=codex
    )

    refinement_log = json.loads(
        (stage_dir / "refinement_log.json").read_text(encoding="utf-8")
    )
    assert captured_states[0]["constraints"]["allowed_files"] == ["main.py"]
    assert "APPROVED DEEPSEEK EXPERIMENT PROPOSAL" in codex.prompts[0]
    assert refinement_log["iterations"][0]["strategy_source"] == "deepseek"
    assert refinement_log["best_metric"] == pytest.approx(0.3)
    assert (stage_dir / "deepseek" / "proposal-iter1.json").is_file()
