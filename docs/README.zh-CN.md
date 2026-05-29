# CLI Model Switcher

**语言：** [English](../README.md) | 简体中文 | [繁體中文](README.zh-TW.md)

CLI Model Switcher 是一个本地命令行 AI 配置切换器。它可以在 Codex、Claude Code、OpenCode、Gemini CLI、本地模型和 OpenAI 兼容网关之间快速切换，同时共享同一套跨工具记忆。

## 功能亮点

- 使用 `ai-use` 切换当前 CLI AI 配置。
- 使用一键配方安装常用组合，例如 OpenCode + OpenRouter、Claude Code、Gemini CLI、DeepSeek、Ollama 和 LM Studio。
- 通过中立的 `AI_CLI_MEMORY` 上下文文件在不同 agent 之间共享记忆。
- 管理多种 API 预设，包括 OpenAI、Anthropic、Gemini、OpenRouter、DeepSeek、Ollama、LM Studio、Groq、Mistral、xAI、Together、Fireworks、DashScope、Moonshot、Zhipu、SiliconFlow、Volcengine、Cerebras、Perplexity、Novita、Azure OpenAI 和自定义 OpenAI 兼容端点。
- 为 PowerShell、cmd.exe、Bash、Zsh、fish 和 Nushell 生成快捷命令。
- 用 `ai-workspace` 在同一个终端工作区打开多个 agent，然后在 Codex、Claude、OpenCode 或配方之间切换。
- 通过 tmux、Windows Terminal、PowerShell 新窗口或可复制 fallback 命令启动和记录多个 AI CLI 会话。
- 在导出或迁移前扫描状态和记忆中的疑似密钥。
- 支持跨机器 portable 导出和导入。

## 快速开始

在仓库根目录运行：

```powershell
py -3.12 scripts\cli_model_switcher.py setup --wizard
```

Windows 非交互安装：

```powershell
py -3.12 scripts\cli_model_switcher.py setup --wizard --yes --recipes opencode-openrouter,local-ollama --active opencode-openrouter
```

Linux 或 macOS：

```bash
python3 scripts/cli_model_switcher.py setup --wizard
```

安装后按提示重新加载 shell 配置，然后运行：

```powershell
ai-list
ai-use code-fast
ai-status
ai-recall
```

## 配方

配方可以免去手写长命令：

```powershell
ai-recipe list
ai-recipe show opencode-openrouter
ai-recipe install opencode-openrouter --use
ai-recipe install claude-native gemini-cli opencode-deepseek --active claude
```

内置配方：

- `codex-openai`
- `claude-native`
- `gemini-cli`
- `opencode-openrouter`
- `opencode-openrouter-best`
- `opencode-deepseek`
- `local-ollama`
- `local-lmstudio`
- `custom-gateway`

## 终端工作区

当你想在同一个 terminal 界面里切换多个 agent 时，用 `ai-workspace`。

Linux、macOS 或 WSL 上有 tmux 时，这是最接近“Codex 不中断、直接切到 Claude”的体验：

```bash
ai-workspace targets set codex claude opencode-openrouter
ai-workspace targets set codex claude opencode-openrouter --project
ai-workspace up
ai-wup
ai-workspace start codex claude opencode-openrouter --backend tmux --attach
ai-workspace switch claude
ai-wgo claude
ai-workspace choose
ai-workspace next
ai-workspace prev
ai-workspace add gemini
ai-workspace switch codex
ai-workspace list
ai-workspace stop
```

在 tmux 里面，用 `Ctrl-b w` 选择 agent 窗口，`Ctrl-b n/p` 前后切换，`Ctrl-b d` 只退出附着但不关闭 agent。

Windows 上可以用 Windows Terminal 一次打开多个 tab：

```powershell
ai-workspace targets set codex claude opencode-openrouter
ai-workspace up --backend wt
ai-workspace start codex claude opencode-openrouter --backend wt
```

没有可用的终端工作区后端时，可以打印精确启动命令：

```powershell
ai-workspace start codex claude --backend print
```

## 会话和交接

会话功能可以让多个 AI CLI 同时开着，并共享同一套 switcher 状态和记忆。

```powershell
ai-session start codex
ai-session start claude
ai-session start opencode-openrouter --backend wt
ai-session start claude --backend print --cwd C:\path\to\project
ai-session list
```

Linux、macOS 或 WSL 上有 tmux 时：

```bash
ai-session start codex --backend tmux --attach
ai-session start claude --backend tmux
ai-session switch claude
ai-session stop claude
```

没有可用后端时，可以只打印启动命令：

```powershell
ai-session start claude --backend print
ai-session start opencode-openrouter --backend print --arg=--debug
ai-session stop router
```

用 handoff 把任务交接写进共享记忆：

```powershell
ai-handoff claude "Review the current Codex changes and look for regressions."
ai-handoff opencode-openrouter "Continue implementation using the shared memory context."
```

## 常用命令

```powershell
ai-use codex
ai-use claude
ai-use opencode-openrouter
ai-use local-private

ai-workspace targets set codex claude opencode-openrouter
ai-workspace up
ai-wup
ai-workspace start codex claude opencode-openrouter --backend tmux --attach
ai-workspace switch claude
ai-wgo claude
ai-workspace add gemini
ai-session start claude
ai-handoff claude "Review this task from another angle."

ai-profile gateway --command opencode --api custom-openai --base-url https://gateway.example/v1 --api-key-env GATEWAY_API_KEY --use
ai-api test gateway --skip-network

ai-remember --scope global --tag preference "Prefer concise answers."
ai-recall --tag preference
ai-memory compact --scope global --keep 50

ai-doctor --fix
ai-secret audit --scope all --fail
```

## Shell 快捷命令

`setup` 可以自动安装快捷命令，也可以手动安装：

```powershell
py -3.12 scripts\cli_model_switcher.py install-powershell --profile $PROFILE
py -3.12 scripts\cli_model_switcher.py install-cmd --dir "$env:USERPROFILE\bin\ai-cli-switcher"
```

```bash
python3 scripts/cli_model_switcher.py install-unix --shell auto
python3 scripts/cli_model_switcher.py install-unix --shell fish
```

常见快捷命令包括：

- `ai-use`
- `ai-current`
- `ai-status`
- `ai-profile`
- `ai-api`
- `ai-model`
- `ai-strategy`
- `ai-recipe`
- `ai-adapter`
- `ai-session`
- `ai-workspace`
- `ai-ws`、`ai-wup`、`ai-wgo`、`ai-wpick`
- `ai-handoff`
- `ai-doctor`
- `ai-secret`
- `ai-remember`
- `ai-recall`
- `ai-memory`
- `ai-page`
- `ai-open-memory`
- `ai-run`

## 共享记忆

默认全局文件：

```text
~/.ai-cli-switcher/state.json
~/.ai-cli-switcher/memory/global.md
~/.ai-cli-switcher/memory/session.md
~/.ai-cli-switcher/memory/context.md
```

项目本地文件：

```text
.ai-cli-switcher.json
.ai-cli-memory.md
```

当前配置会通过 `AI_CLI_MEMORY` 暴露合并后的上下文文件。

## 密钥安全

不要把 API key 直接写进 profile。请存环境变量引用：

```powershell
ai-profile router --command opencode --api openrouter --api-key-env OPENROUTER_API_KEY --use
```

分享状态或迁移机器前运行：

```powershell
ai-secret audit --scope all --fail
py -3.12 scripts\cli_model_switcher.py export --portable --output ai-cli-switcher-portable.json
```

## Portable 迁移

导出：

```powershell
py -3.12 scripts\cli_model_switcher.py export --portable --output ai-cli-switcher-portable.json
```

在另一台机器导入：

```powershell
py -3.12 scripts\cli_model_switcher.py import ai-cli-switcher-portable.json --merge-policy rename --active
```

合并策略：

- `overwrite`：覆盖冲突项。
- `keep`：保留本地已有项。
- `rename`：两边都保留，冲突导入项会加 `-imported` 后缀。

## 仓库结构

```text
SKILL.md                         Codex skill 指令
scripts/cli_model_switcher.py    主 CLI 实现
references/shell-integration.md  PowerShell、cmd.exe、Bash、Zsh、fish、Nushell 说明
references/linux-macos.md        Linux、macOS、WSL 和 Git Bash 说明
agents/openai.yaml               Skill UI 元数据
```

## 开发校验

```powershell
py -3.12 -m py_compile scripts\cli_model_switcher.py
py -3.12 scripts\cli_model_switcher.py secret audit --scope all --fail
py -3.12 "$env:USERPROFILE\.codex\skills\.system\skill-creator\scripts\quick_validate.py" .
```

## 状态

这是一个个人 Codex skill 和独立辅助脚本。当前仓库为 private，主要面向本地工作流自动化。
