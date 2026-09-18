# Setup required

Before the first run, set one provider credential in the PowerShell session:

```powershell
$env:OPENAI_API_KEY = "<YOUR_OPENAI_API_KEY>"
```

`config.arc.yaml` currently uses the OpenAI-compatible backend and reads `OPENAI_API_KEY`. No provider keys were found in the current system environment, and no secret has been written to Git-tracked files.

Optional alternatives supported by the current CLI are OpenRouter, DeepSeek, MiniMax, Ollama, or ACP. Change `llm` in `config.arc.yaml` before using one of those backends. ACP also requires a working `acpx` command and an ACP-compatible CLI; that path is not ready in the current non-interactive Windows shell.

Docker Desktop is installed and was started successfully. The active configuration uses the local `sandbox` executor, so no Docker image build is required for the first run. If switching `experiment.mode` to `docker`, first build the official image documented in `config.arc.yaml`.

Use the configuration's built-in `hitl.mode: co-pilot` without a CLI `--mode` override when the USD 5 cost guardrail must apply. In this upstream version, passing `--mode co-pilot` loads a preset whose budget defaults to unlimited.

