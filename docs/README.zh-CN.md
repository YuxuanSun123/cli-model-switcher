# Ayatori Nexus

**语言：** [English](../README.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [Italiano](README.it.md) | [日本語](README.ja.md) | 简体中文 | [繁體中文](README.zh-TW.md)

Ayatori Nexus 是 CLI Model Switcher 的项目花名：一个本地命令行 AI 配置切换器。它可以在 Codex、Claude Code、OpenCode、Gemini CLI、本地模型和 OpenAI 兼容网关之间快速切换，同时共享同一套跨工具记忆。

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

## 快速安装

Linux、macOS 或 WSL：

```bash
curl -fsSL https://raw.githubusercontent.com/YuxuanSun123/cli-model-switcher/main/install.sh | sh
```

Windows PowerShell：

```powershell
irm https://raw.githubusercontent.com/YuxuanSun123/cli-model-switcher/main/install.ps1 | iex
```

一键安装器会把 skill clone 或更新到 `~/.codex/skills/cli-model-switcher`，运行非交互向导，安装 shell 快捷命令，并在 Linux、macOS、WSL 上维护 `~/.local/bin` 里的可执行 shim，方便 agent 内部调用。

如果已经 clone 了仓库，也可以在本地运行：

```powershell
.\install.ps1
```

```bash
sh install.sh
```

仍然可以从仓库根目录手动安装：

```powershell
py -3.12 scripts\cli_model_switcher.py setup --wizard
py -3.12 scripts\cli_model_switcher.py setup --lite
```

Linux 或 macOS：

```bash
python3 scripts/cli_model_switcher.py setup --wizard
python3 scripts/cli_model_switcher.py setup --lite
```

安装前也可以 dry-run：

```powershell
.\install.ps1 -DryRun
```

```bash
sh install.sh --dry-run
```

安装后按提示重新加载 shell 配置，然后运行：

```powershell
ai-list
ai-lite
ai-menu
ai-report
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

## 策略、模板和配置解释

新增的诊断和自动化命令：

```powershell
ai-policy deny openrouter
ai-policy check openrouter
ai-template set handoff --prompt 'Handoff to $agent: $input' --default agent=claude
ai-template use handoff --input "review the latest diff"
ai-config explain --profile codex
ai-api providers
```

`ai-policy` 用来避免误用某个 provider，`ai-template` 用来保存可复用提示词，`ai-config explain` 用来查看有效配置来自项目、全局还是默认值，`providers.d/*.json` 可以添加团队或私有 API preset。

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

## Agent 内切换

进入 Codex、Claude 或 OpenCode 以后，输入会被当前 agent 接管。安装 agent bridge 后，这些 agent 会知道 `/switch claude` 是终端切换指令，而不是普通聊天：

```powershell
ai-lite
ai-lite --dry-run
ai-lite --fix
ai-lite --prompt
ai-lite --undo
ai-menu
ai-menu --list
ai-menu --choice recommend
ai-report
ai-report --json
ai-agent install codex claude opencode
ai-agent install gemini qwen copilot cursor windsurf aider cline roo
ai-agent install continue goose kiro
ai-agent recommend
ai-agent recommend --json
ai-agent platforms amp devin junie zed kilo
ai-agent platforms gitlab-duo firebase-studio android-studio-gemini openhands warp trae
ai-agent install amp devin junie zed kilo
ai-agent install gitlab-duo firebase-studio android-studio-gemini openhands warp trae
ai-agent platforms openclaw
ai-agent install openclaw --dir ~/.openclaw/workspace
ai-agent targets
ai-agent detect
ai-agent install --detected
ai-agent install --file .my-agent-rules.md
ai-agent prompt
```

在每个项目里运行 `ai-agent install`，后续新 agent 会读取 `AGENTS.md` 和 `CLAUDE.md`。已经打开的 agent 需要把 `ai-agent prompt` 的输出粘贴进去一次，然后就可以说：

```text
/switch claude
switch codex
next
choose
handoff claude review the current changes
```

内置 agent bridge 目标包括：

- `codex`、`claude`、`opencode`、`gemini`、`qwen`
- `copilot` / `vscode`、`cursor`、`windsurf` / `cascade`
- `continue` / `continue-dev`、`goose`、`kiro` / `kiro-cli`
- `amp` / `sourcegraph-amp`、`devin` / `cognition`、`junie` / `jetbrains-junie`
- `zed`、`kilo` / `kilocode`、`gitlab-duo` / `duo`、`firebase-studio` / `project-idx`
- `android-studio-gemini`、`openhands` / `open-hands`、`warp`、`trae` / `traeide`
- `openclaw` / `claw` / `open-claw`
- `aider`、`cline`、`roo`
- `generic` 写入 `AGENTS.md`，也可以用 `--file PATH` 写入任意自定义规则文件

`ai-agent platforms` 会显示 support 等级：`native` 表示官方规则路径，`compatible` 表示官方兼容的共享说明文件，`generic` 表示通用 `AGENTS.md` 桥接，`experimental` 表示路径可能随版本变化。`ai-agent recommend` 会扫描当前项目并给出推荐安装命令。

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
ai-lite
ai-lite --dry-run
ai-lite --fix
ai-lite --prompt
ai-lite --undo
ai-agent install codex claude opencode
ai-agent install gemini qwen copilot cursor windsurf aider cline roo
ai-agent install continue goose kiro
ai-agent recommend
ai-agent platforms amp devin junie zed kilo
ai-agent install amp devin junie zed kilo
ai-agent install gitlab-duo firebase-studio android-studio-gemini openhands warp trae
ai-agent platforms openclaw
ai-agent install openclaw --dir ~/.openclaw/workspace
ai-agent targets
ai-agent detect
ai-agent install --detected
ai-agent prompt
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
python3 scripts/cli_model_switcher.py install-bin
```

在 Linux、macOS 和 WSL 上，`install-unix` 默认还会把 `ai-lite`、`ai-menu`、`ai-report`、`ai-workspace`、`ai-agent`、`ai-wup`、`ai-wgo` 等可执行 shim 写入 `~/.local/bin`。这对 agent 内部切换很重要，因为 Codex、Claude、OpenCode 这类工具调用 shell 命令时经常是非交互 shell，不一定会加载 Bash/Zsh/fish 函数。

继续保留 `ai-use` 和 `ai-select` 的 shell 函数；只有被当前 shell source 的函数才能更新当前终端里的环境变量。可执行 shim 更适合直接命令、agent bridge 和非交互 shell。`install-unix` 会把 shim 目录加入交互式 Bash/Zsh/fish helper；如果某个 agent 仍然找不到 `ai-workspace`，Bash/Zsh 可加入 `export PATH="$HOME/.local/bin:$PATH"`，fish 可运行 `fish_add_path ~/.local/bin`。

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
- `ai-lite`
- `ai-menu`
- `ai-report`
- `ai-agent`
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
docs/README.*.md                 本地化 README 页面
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
