# Execution-config claim verification pilot

The final decision and interpretation are in [PIVOT_DOSSIER.md](./PIVOT_DOSSIER.md).

## Reproduce

From this directory in PowerShell:

```powershell
& '.\.venv\Scripts\python.exe' 'generate_cases.py'
& '.\.venv\Scripts\python.exe' 'infer.py' --model 'models/Qwen2.5-Coder-1.5B-Instruct' --batch-size 8 --output 'outputs/predictions_qwen_coder_1_5b.jsonl'
& '.\.venv\Scripts\python.exe' 'infer.py' --model 'models/Qwen2.5-3B-Instruct' --batch-size 2 --output 'outputs/predictions_qwen_3b.jsonl'
& '.\.venv\Scripts\python.exe' 'rule_baselines.py'
& '.\.venv\Scripts\python.exe' 'combine_results.py'
```

The local model directories are intentionally not tracked by Git. See `requirements.txt` and the model revisions in the dossier.

