# AutoResearchClaw agent protocol

Repository-wide operating guidance is in `RESEARCHCLAW_AGENTS.md`. For
experiment optimization, the following protocol takes precedence.

## DeepSeek-first experiment loop

When `DEEPSEEK_API_KEY` is configured, DeepSeek is the research strategist and
Codex is the local executor/supervisor. Stage 13 implements this automatically.

For every normal experiment round:

1. Read only the compact current state and latest real evaluator result.
2. Obtain one structured proposal from the local DeepSeek helper. Do not repeat
   the same long Codex brainstorm before or after this call.
3. Sanity-check that the proposal matches repository facts, allowed files,
   evaluator semantics, hardware, and time budget.
4. If there is no obvious conflict, implement the proposal with the smallest
   patch, run the real evaluator, and record the metric exactly as emitted.
5. Feed the new result into the next compact state. Failed proposals belong in
   the rejected-idea index and must not be silently retried.

Codex may do deeper independent research reasoning only when DeepSeek is
unavailable, the proposal conflicts with repository facts, the patch cannot be
implemented, the evaluator appears wrong, several rounds make no progress, or
DeepSeek repeats an explicitly failed idea. Every such fallback must be logged
as `codex-only-fallback`; never invent a DeepSeek response.

DeepSeek never gets shell, git, file-write, or deletion authority. Codex retains
all local execution, code editing, validation, experiment running, git,
truthfulness checks, and exception handling.

Manual helper usage:

```powershell
.\.venv\Scripts\python.exe -m researchclaw.experiment.deepseek_agent propose `
  --state <compact-state.json> --output <proposal.json> `
  --experiment-id <id>
```

Use `analyze` instead of `propose` after a real result is available. Never pass
the whole repository as state and never place credentials in state or prompts.
After configuring the key, `python -m researchclaw.experiment.deepseek_agent
smoke` performs one API/schema/logging check without starting a long experiment.
