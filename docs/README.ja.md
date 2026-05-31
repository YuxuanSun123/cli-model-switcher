# Ayatori Nexus

**言語:** [English](../README.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [Italiano](README.it.md) | 日本語 | [简体中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md)

Ayatori Nexus は CLI Model Switcher のプロジェクト名です。コマンドライン AI コーディングエージェント向けのローカルなプロファイル切り替えツールで、Codex、Claude Code、OpenCode、Gemini CLI、ローカルモデル、OpenAI 互換ゲートウェイを切り替えながら、共通のメモリ層を使えます。

## 主な機能

- `ai-use` で現在の CLI AI プロファイルを切り替え。
- OpenCode + OpenRouter、Claude Code、Gemini CLI、DeepSeek、Ollama、LM Studio などのレシピを一発で導入。
- 中立的な `AI_CLI_MEMORY` コンテキストファイルでエージェント間の記憶を共有。
- OpenAI、Anthropic、Gemini、OpenRouter、DeepSeek、Ollama、LM Studio、Groq、Mistral、xAI、Together、Fireworks、DashScope、Moonshot、Zhipu、SiliconFlow、Volcengine、Cerebras、Perplexity、Novita、Azure OpenAI、カスタム OpenAI 互換エンドポイントの API プリセットを管理。
- PowerShell、cmd.exe、Bash、Zsh、fish、Nushell 向けのシェルヘルパーを生成。
- `ai-workspace` で複数のエージェントを同じターミナル作業領域に開き、Codex、Claude、OpenCode、レシピプロファイル間を切り替え。
- tmux、Windows Terminal、PowerShell ウィンドウ、またはコピー可能なフォールバックコマンドでセッションを開始・追跡。
- エクスポートや移行の前に、状態やメモリ内の明らかなシークレットを監査。
- プロファイル状態をマシン間でポータブルにエクスポート・インポート。

## クイックインストール

Linux、macOS、WSL:

```bash
curl -fsSL https://raw.githubusercontent.com/YuxuanSun123/cli-model-switcher/main/install.sh | sh
```

Windows PowerShell:

```powershell
irm https://raw.githubusercontent.com/YuxuanSun123/cli-model-switcher/main/install.ps1 | iex
```

ワンコマンドインストーラーは skill を `~/.codex/skills/cli-model-switcher` に clone または更新し、非対話セットアップを実行し、シェルヘルパーを導入し、Linux、macOS、WSL では `~/.local/bin` の shim を維持します。

すでにリポジトリを clone している場合:

```powershell
.\install.ps1
```

```bash
sh install.sh
```

リポジトリルートから手動セットアップ:

```powershell
py -3.12 scripts\cli_model_switcher.py setup --wizard
py -3.12 scripts\cli_model_switcher.py setup --lite
```

```bash
python3 scripts/cli_model_switcher.py setup --wizard
python3 scripts/cli_model_switcher.py setup --lite
```

書き込み前の dry-run:

```powershell
.\install.ps1 -DryRun
```

```bash
sh install.sh --dry-run
```

セットアップ後、必要に応じてシェルプロファイルを再読み込みしてから実行します:

```powershell
ai-list
ai-lite
ai-menu
ai-report
ai-use code-fast
ai-status
ai-recall
```

## レシピ

レシピを使うと、長いコマンドを書かずに便利なプロファイルを作れます:

```powershell
ai-recipe list
ai-recipe show opencode-openrouter
ai-recipe install opencode-openrouter --use
ai-recipe install claude-native gemini-cli opencode-deepseek --active claude
```

組み込みレシピ:

- `codex-openai`
- `claude-native`
- `gemini-cli`
- `opencode-openrouter`
- `opencode-openrouter-best`
- `opencode-deepseek`
- `local-ollama`
- `local-lmstudio`
- `custom-gateway`

## ターミナル作業領域

複数のエージェントを 1 つのターミナル画面で扱いたい場合は `ai-workspace` を使います。

Linux、macOS、WSL で tmux がある場合、これは「ターミナルを離れずに Codex から Claude へ切り替える」体験に最も近い方法です:

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

tmux 内では `Ctrl-b w` でエージェントウィンドウを選択し、`Ctrl-b n/p` で前後に移動し、`Ctrl-b d` でエージェントを閉じずにデタッチできます。

Windows では Windows Terminal のタブを 1 コマンドで開けます:

```powershell
ai-workspace targets set codex claude opencode-openrouter
ai-workspace up --backend wt
ai-workspace start codex claude opencode-openrouter --backend wt
```

利用できるバックエンドがない場合は、起動コマンドだけを出力できます:

```powershell
ai-workspace start codex claude --backend print
```

## エージェント内からの切り替え

Codex、Claude、OpenCode に入った後の入力は、そのエージェントが受け取ります。Agent Bridge をインストールすると、`/switch claude` を通常の会話ではなくターミナル切り替えコマンドとして扱わせることができます:

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

各プロジェクトで `ai-agent install` を実行すると、新しいエージェントセッションが `AGENTS.md` と `CLAUDE.md` を読みます。すでに起動しているエージェントには `ai-agent prompt` の出力を一度貼り付けてから、次のように入力できます:

```text
/switch claude
switch codex
next
choose
handoff claude review the current changes
```

## セッションと引き継ぎ

セッション機能は、複数の AI CLI を開いたまま、同じ switcher 状態とメモリを共有します。

```powershell
ai-session start codex
ai-session start claude
ai-session start opencode-openrouter --backend wt
ai-session start claude --backend print --cwd C:\path\to\project
ai-session list
```

Linux、macOS、WSL で tmux がある場合:

```bash
ai-session start codex --backend tmux --attach
ai-session start claude --backend tmux
ai-session switch claude
ai-session stop claude
```

handoff メモは共有メモリに書き込まれます:

```powershell
ai-handoff claude "Review the current Codex changes and look for regressions."
ai-handoff opencode-openrouter "Continue implementation using the shared memory context."
```

## よく使うコマンド

```powershell
ai-use codex
ai-use claude
ai-use opencode-openrouter
ai-use local-private

ai-workspace targets set codex claude opencode-openrouter
ai-workspace up
ai-wup
ai-workspace switch claude
ai-wgo claude
ai-lite
ai-lite --dry-run
ai-lite --fix
ai-lite --prompt
ai-lite --undo
ai-agent install codex claude opencode
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

## シェルヘルパー

セットアップコマンドはヘルパーを自動でインストールできます。手動インストール:

```powershell
py -3.12 scripts\cli_model_switcher.py install-powershell --profile $PROFILE
py -3.12 scripts\cli_model_switcher.py install-cmd --dir "$env:USERPROFILE\bin\ai-cli-switcher"
```

```bash
python3 scripts/cli_model_switcher.py install-unix --shell auto
python3 scripts/cli_model_switcher.py install-unix --shell fish
python3 scripts/cli_model_switcher.py install-bin
```

Linux、macOS、WSL では、`install-unix` が `ai-lite`、`ai-menu`、`ai-report`、`ai-workspace`、`ai-agent`、`ai-wup`、`ai-wgo` などの実行可能 shim を標準で `~/.local/bin` に置きます。これらは Agent Bridge や非対話シェルで役立ちます。

## 共有メモリ

標準のグローバルファイル:

```text
~/.ai-cli-switcher/state.json
~/.ai-cli-switcher/memory/global.md
~/.ai-cli-switcher/memory/session.md
~/.ai-cli-switcher/memory/context.md
```

プロジェクトローカルファイル:

```text
.ai-cli-switcher.json
.ai-cli-memory.md
```

アクティブプロファイルは、統合されたコンテキストファイルを `AI_CLI_MEMORY` として公開します。

## シークレット

API キーをプロファイルに直接保存しないでください。環境変数参照を使います:

```powershell
ai-profile router --command opencode --api openrouter --api-key-env OPENROUTER_API_KEY --use
```

共有や移行の前に実行:

```powershell
ai-secret audit --scope all --fail
py -3.12 scripts\cli_model_switcher.py export --portable --output ai-cli-switcher-portable.json
```

## ポータブル移行

エクスポート:

```powershell
py -3.12 scripts\cli_model_switcher.py export --portable --output ai-cli-switcher-portable.json
```

別マシンでインポート:

```powershell
py -3.12 scripts\cli_model_switcher.py import ai-cli-switcher-portable.json --merge-policy rename --active
```

## リポジトリ構成

```text
SKILL.md                         Codex skill instructions
scripts/cli_model_switcher.py    Main CLI implementation
docs/README.*.md                 Localized README pages
references/shell-integration.md  PowerShell, cmd.exe, Bash, Zsh, fish, Nushell notes
references/linux-macos.md        Linux, macOS, WSL, and Git Bash notes
agents/openai.yaml               Skill UI metadata
```

## 開発チェック

```powershell
py -3.12 -m py_compile scripts\cli_model_switcher.py
py -3.12 scripts\validate_skill.py .
py -3.12 scripts\cli_model_switcher.py secret audit --scope all --fail
```

## ステータス

これは個人用 Codex skill と、ローカルワークフロー自動化向けの独立した補助スクリプトです。
