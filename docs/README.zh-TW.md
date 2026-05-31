# Ayatori Nexus

**語言：** [English](../README.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [Italiano](README.it.md) | [日本語](README.ja.md) | [簡體中文](README.zh-CN.md) | 繁體中文

Ayatori Nexus 是 CLI Model Switcher 的專案花名：一個本機命令列 AI 設定切換器。它可以在 Codex、Claude Code、OpenCode、Gemini CLI、本機模型和 OpenAI 相容閘道之間快速切換，同時共用同一套跨工具記憶。

## 功能亮點

- 使用 `ai-use` 切換目前 CLI AI 設定。
- 使用一鍵配方安裝常用組合，例如 OpenCode + OpenRouter、Claude Code、Gemini CLI、DeepSeek、Ollama 和 LM Studio。
- 透過中立的 `AI_CLI_MEMORY` 上下文檔案在不同 agent 之間共用記憶。
- 管理多種 API 預設，包括 OpenAI、Anthropic、Gemini、OpenRouter、DeepSeek、Ollama、LM Studio、Groq、Mistral、xAI、Together、Fireworks、DashScope、Moonshot、Zhipu、SiliconFlow、Volcengine、Cerebras、Perplexity、Novita、Azure OpenAI 和自訂 OpenAI 相容端點。
- 為 PowerShell、cmd.exe、Bash、Zsh、fish 和 Nushell 產生快捷命令。
- 用 `ai-workspace` 在同一個終端工作區開啟多個 agent，然後在 Codex、Claude、OpenCode 或配方之間切換。
- 透過 tmux、Windows Terminal、PowerShell 新視窗或可複製 fallback 命令啟動和記錄多個 AI CLI 會話。
- 在匯出或遷移前掃描狀態和記憶中的疑似密鑰。
- 支援跨機器 portable 匯出和匯入。

## 快速安裝

Linux、macOS 或 WSL：

```bash
curl -fsSL https://raw.githubusercontent.com/YuxuanSun123/cli-model-switcher/main/install.sh | sh
```

Windows PowerShell：

```powershell
irm https://raw.githubusercontent.com/YuxuanSun123/cli-model-switcher/main/install.ps1 | iex
```

一鍵安裝器會把 skill clone 或更新到 `~/.codex/skills/cli-model-switcher`，執行非互動向導，安裝 shell 快捷命令，並在 Linux、macOS、WSL 上維護 `~/.local/bin` 裡的可執行 shim，方便 agent 內部呼叫。

如果已經 clone 了倉庫，也可以在本機執行：

```powershell
.\install.ps1
```

```bash
sh install.sh
```

仍然可以從倉庫根目錄手動安裝：

```powershell
py -3.12 scripts\cli_model_switcher.py setup --wizard
py -3.12 scripts\cli_model_switcher.py setup --lite
```

Linux 或 macOS：

```bash
python3 scripts/cli_model_switcher.py setup --wizard
python3 scripts\cli_model_switcher.py setup --lite
```

安裝前也可以 dry-run：

```powershell
.\install.ps1 -DryRun
```

```bash
sh install.sh --dry-run
```

安裝後依提示重新載入 shell 設定，然後執行：

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

配方可以省去手寫長命令：

```powershell
ai-recipe list
ai-recipe show opencode-openrouter
ai-recipe install opencode-openrouter --use
ai-recipe install claude-native gemini-cli opencode-deepseek --active claude
```

內建配方：

- `codex-openai`
- `claude-native`
- `gemini-cli`
- `opencode-openrouter`
- `opencode-openrouter-best`
- `opencode-deepseek`
- `local-ollama`
- `local-lmstudio`
- `custom-gateway`

## 終端工作區

當你想在同一個 terminal 介面裡切換多個 agent 時，用 `ai-workspace`。

Linux、macOS 或 WSL 上有 tmux 時，這是最接近「Codex 不中斷、直接切到 Claude」的體驗：

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

在 tmux 裡面，用 `Ctrl-b w` 選擇 agent 視窗，`Ctrl-b n/p` 前後切換，`Ctrl-b d` 只退出附著但不關閉 agent。

Windows 上可以用 Windows Terminal 一次開啟多個 tab：

```powershell
ai-workspace targets set codex claude opencode-openrouter
ai-workspace up --backend wt
ai-workspace start codex claude opencode-openrouter --backend wt
```

沒有可用的終端工作區後端時，可以列印精確啟動命令：

```powershell
ai-workspace start codex claude --backend print
```

## Agent 內切換

進入 Codex、Claude 或 OpenCode 以後，輸入會被目前 agent 接管。安裝 agent bridge 後，這些 agent 會知道 `/switch claude` 是終端切換指令，而不是普通聊天：

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

在每個專案裡執行 `ai-agent install`，後續新 agent 會讀取 `AGENTS.md` 和 `CLAUDE.md`。已經開啟的 agent 需要把 `ai-agent prompt` 的輸出貼進去一次，然後就可以說：

```text
/switch claude
switch codex
next
choose
handoff claude review the current changes
```

內建 agent bridge 目標包括：

- `codex`、`claude`、`opencode`、`gemini`、`qwen`
- `copilot` / `vscode`、`cursor`、`windsurf` / `cascade`
- `continue` / `continue-dev`、`goose`、`kiro` / `kiro-cli`
- `amp` / `sourcegraph-amp`、`devin` / `cognition`、`junie` / `jetbrains-junie`
- `zed`、`kilo` / `kilocode`、`gitlab-duo` / `duo`、`firebase-studio` / `project-idx`
- `android-studio-gemini`、`openhands` / `open-hands`、`warp`、`trae` / `traeide`
- `openclaw` / `claw` / `open-claw`
- `aider`、`cline`、`roo`
- `generic` 寫入 `AGENTS.md`，也可以用 `--file PATH` 寫入任意自訂規則檔案

`ai-agent platforms` 會顯示 support 等級：`native` 表示官方規則路徑，`compatible` 表示官方相容的共享說明檔案，`generic` 表示通用 `AGENTS.md` 橋接，`experimental` 表示路徑可能隨版本變化。`ai-agent recommend` 會掃描目前專案並給出推薦安裝命令。

## 會話和交接

會話功能可以讓多個 AI CLI 同時開著，並共用同一套 switcher 狀態和記憶。

```powershell
ai-session start codex
ai-session start claude
ai-session start opencode-openrouter --backend wt
ai-session start claude --backend print --cwd C:\path\to\project
ai-session list
```

Linux、macOS 或 WSL 上有 tmux 時：

```bash
ai-session start codex --backend tmux --attach
ai-session start claude --backend tmux
ai-session switch claude
ai-session stop claude
```

沒有可用後端時，可以只列印啟動命令：

```powershell
ai-session start claude --backend print
ai-session start opencode-openrouter --backend print --arg=--debug
ai-session stop router
```

用 handoff 把任務交接寫進共用記憶：

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

`setup` 可以自動安裝快捷命令，也可以手動安裝：

```powershell
py -3.12 scripts\cli_model_switcher.py install-powershell --profile $PROFILE
py -3.12 scripts\cli_model_switcher.py install-cmd --dir "$env:USERPROFILE\bin\ai-cli-switcher"
```

```bash
python3 scripts/cli_model_switcher.py install-unix --shell auto
python3 scripts/cli_model_switcher.py install-unix --shell fish
python3 scripts/cli_model_switcher.py install-bin
```

在 Linux、macOS 和 WSL 上，`install-unix` 預設還會把 `ai-lite`、`ai-menu`、`ai-report`、`ai-workspace`、`ai-agent`、`ai-wup`、`ai-wgo` 等可執行 shim 寫入 `~/.local/bin`。這對 agent 內部切換很重要，因為 Codex、Claude、OpenCode 這類工具呼叫 shell 命令時經常是非互動 shell，不一定會載入 Bash/Zsh/fish 函式。

繼續保留 `ai-use` 和 `ai-select` 的 shell 函式；只有被目前 shell source 的函式才能更新目前終端裡的環境變數。可執行 shim 更適合直接命令、agent bridge 和非互動 shell。`install-unix` 會把 shim 目錄加入互動式 Bash/Zsh/fish helper；如果某個 agent 仍然找不到 `ai-workspace`，Bash/Zsh 可加入 `export PATH="$HOME/.local/bin:$PATH"`，fish 可執行 `fish_add_path ~/.local/bin`。

常見快捷命令包括：

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

## 共用記憶

預設全域檔案：

```text
~/.ai-cli-switcher/state.json
~/.ai-cli-switcher/memory/global.md
~/.ai-cli-switcher/memory/session.md
~/.ai-cli-switcher/memory/context.md
```

專案本機檔案：

```text
.ai-cli-switcher.json
.ai-cli-memory.md
```

目前設定會透過 `AI_CLI_MEMORY` 暴露合併後的上下文檔案。

## 密鑰安全

不要把 API key 直接寫進 profile。請儲存環境變數引用：

```powershell
ai-profile router --command opencode --api openrouter --api-key-env OPENROUTER_API_KEY --use
```

分享狀態或遷移機器前執行：

```powershell
ai-secret audit --scope all --fail
py -3.12 scripts\cli_model_switcher.py export --portable --output ai-cli-switcher-portable.json
```

## Portable 遷移

匯出：

```powershell
py -3.12 scripts\cli_model_switcher.py export --portable --output ai-cli-switcher-portable.json
```

在另一台機器匯入：

```powershell
py -3.12 scripts\cli_model_switcher.py import ai-cli-switcher-portable.json --merge-policy rename --active
```

合併策略：

- `overwrite`：覆蓋衝突項。
- `keep`：保留本機既有項。
- `rename`：兩邊都保留，衝突匯入項會加上 `-imported` 後綴。

## 倉庫結構

```text
SKILL.md                         Codex skill 指令
scripts/cli_model_switcher.py    主 CLI 實作
docs/README.*.md                 本地化 README 頁面
references/shell-integration.md  PowerShell、cmd.exe、Bash、Zsh、fish、Nushell 說明
references/linux-macos.md        Linux、macOS、WSL 和 Git Bash 說明
agents/openai.yaml               Skill UI 中繼資料
```

## 開發校驗

```powershell
py -3.12 -m py_compile scripts\cli_model_switcher.py
py -3.12 scripts\cli_model_switcher.py secret audit --scope all --fail
py -3.12 "$env:USERPROFILE\.codex\skills\.system\skill-creator\scripts\quick_validate.py" .
```

## 狀態

這是一個個人 Codex skill 和獨立輔助腳本。當前倉庫為 private，主要面向本機工作流自動化。
