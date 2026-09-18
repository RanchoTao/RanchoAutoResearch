# 当前状态

AutoResearchClaw 0.5.0 已安装到 `.venv`，配置验证、CLI、Python 导入和本地 sandbox 检查均已通过。尚未运行任何科研任务或调用付费 API。

# 启动环境

```powershell
cd C:\Users\RanchoTao\Desktop\RanchoAutoResearch\AutoResearchClaw
.\.venv\Scripts\Activate.ps1
$env:OPENAI_API_KEY = "<YOUR_OPENAI_API_KEY>"
researchclaw doctor --config config.arc.yaml
```

# DeepSeek 科研策略层

把 `.env.example` 中的三项复制到已被 Git 忽略的 `.env`，只填写本机值：

```dotenv
DEEPSEEK_API_KEY=<YOUR_DEEPSEEK_API_KEY>
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-v4-pro
```

也可以在启动 `researchclaw` 的同一个 PowerShell 进程里设置同名环境变量；
进程环境变量优先于 `.env`。配置后，Stage 13 默认执行
`DeepSeek thinks -> Codex implements/runs -> real metric -> DeepSeek analyzes`。
未配置或 API 失败时会明确记录 `DEEPSEEK_AVAILABLE=false` 并回退到原
Codex-only 循环。

填好 key 后先做一次真实 API smoke test（不会启动正式实验）：

```powershell
.\.venv\Scripts\python.exe -m researchclaw.experiment.deepseek_agent smoke
```

# 第一次运行

```powershell
researchclaw run --config config.arc.yaml --topic "<MY_RESEARCH_TOPIC>"
```

`config.arc.yaml` 已启用原生 `co-pilot` HITL。请不要额外传 `--mode co-pilot`：当前上游 CLI 会用无成本上限的预设覆盖配置；省略该参数才能保留已设置的 USD 5 guardrail。

# 需要我完成的事情

- 设置 `OPENAI_API_KEY`，或在 `config.arc.yaml` 中改选其他官方支持的 backend。
- 在 `.env` 中设置 `DEEPSEEK_API_KEY`，启用低 Codex 消耗的实验策略循环。
- 确认研究主题后再运行；不要添加 `--auto-approve`。

# 已发现的问题

- API Key 尚未配置，因此 `researchclaw doctor` 的 provider 检查会失败；设置 key 后再运行 doctor 即可验证 backend。
- Docker Engine 可用，但官方实验镜像尚未构建；当前使用无需镜像的本地 sandbox。
- Codex CLI 在当前非交互 shell 中被 Windows 拒绝启动，且未安装 `acpx`，所以未启用 ACP backend。
- OpenCode 未安装，相关可选功能已禁用。

# 当前版本

- Repository: `https://github.com/aiming-lab/AutoResearchClaw.git`
- Branch: `main`
- Commit: `e2e23c93b4943fd21cc531deb09850d8fda55357`
