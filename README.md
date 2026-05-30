# Ayatori Nexus

**CLI Model Switcher & Shared Memory Hub**

**Language:** English | [Deutsch](docs/README.de.md) | [Français](docs/README.fr.md) | [Italiano](docs/README.it.md) | [日本語](docs/README.ja.md) | [简体中文](docs/README.zh-CN.md) | [繁體中文](docs/README.zh-TW.md)

**Project Links:** [Changelog](CHANGELOG.md) | [Releases](https://github.com/YuxuanSun123/cli-model-switcher/releases)

[![CI](https://github.com/YuxuanSun123/cli-model-switcher/actions/workflows/ci.yml/badge.svg)](https://github.com/YuxuanSun123/cli-model-switcher/actions/workflows/ci.yml)

Ayatori Nexus is the codename for CLI Model Switcher: a local profile switcher for command-line AI coding agents. It lets you move between Codex, Claude Code, OpenCode, Gemini CLI, local models, and OpenAI-compatible gateways while keeping one shared memory layer.

## What It Does

- Switch active CLI AI profiles with `ai-use`.
- Install one-step recipes for common stacks such as OpenCode + OpenRouter, Claude Code, Gemini CLI, DeepSeek, Ollama, and LM Studio.
- Share memory across agents through a neutral `AI_CLI_MEMORY` context file.
- Manage API presets for OpenAI, Anthropic, Gemini, OpenRouter, DeepSeek, Ollama, LM Studio, Groq, Mistral, xAI, Together, Fireworks, DashScope, Moonshot, Zhipu, SiliconFlow, Volcengine, Cerebras, Perplexity, Novita, Azure OpenAI, and custom OpenAI-compatible endpoints.
- Generate shell helpers for PowerShell, cmd.exe, Bash, Zsh, fish, and Nushell.
- Open several agents in one terminal workspace with `ai-workspace`, then switch between Codex, Claude, OpenCode, or recipes from that workspace.
- Start and track AI CLI sessions through tmux, Windows Terminal, PowerShell windows, or printable fallback commands.
- Audit state and memory for direct-looking secrets before export or migration.
- Export/import portable profile state between machines.

## Quick Install

Linux, macOS, or WSL:

```bash
curl -fsSL https://raw.githubusercontent.com/YuxuanSun123/cli-model-switcher/main/install.sh | sh
```

Windows PowerShell:

```powershell
irm https://raw.githubusercontent.com/YuxuanSun123/cli-model-switcher/main/install.ps1 | iex
```

The one-command installers clone or update the skill under `~/.codex/skills/cli-model-switcher`, run the guided non-interactive setup, install shell helpers, and keep the Linux/macOS/WSL `~/.local/bin` shims in place for agent-side commands.

If you already cloned the repository, run the installer locally:

```powershell
.\install.ps1
```

```bash
sh install.sh
```

Manual setup from the repository root is still available:

```powershell
py -3.12 scripts\cli_model_switcher.py setup --wizard
```

Linux or macOS:

```bash
python3 scripts/cli_model_switcher.py setup --wizard
```

Dry-run the installers before writing anything:

```powershell
.\install.ps1 -DryRun
```

```bash
sh install.sh --dry-run
```

After setup, reload your shell profile if the installer asks you to. Then:

```powershell
ayatori about
ayatori status
ai-list
ai-use code-fast
ai-status
ai-recall
```

## Recipes

Recipes create useful profiles without long command lines:

```powershell
ai-recipe list
ai-recipe show opencode-openrouter
ai-recipe install opencode-openrouter --use
ai-recipe install claude-native gemini-cli opencode-deepseek --active claude
```

Built-in recipes:

- `codex-openai`
- `claude-native`
- `gemini-cli`
- `opencode-openrouter`
- `opencode-openrouter-best`
- `opencode-deepseek`
- `local-ollama`
- `local-lmstudio`
- `custom-gateway`

## Terminal Workspaces

Use `ai-workspace` when you want one terminal interface for several agents.

On Linux, macOS, or WSL with tmux, this is the closest experience to "switch Claude/Codex without leaving the terminal":

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

Inside tmux, use `Ctrl-b w` to choose an agent window, `Ctrl-b n/p` to move next/previous, and `Ctrl-b d` to detach without closing agents.

On Windows, use Windows Terminal tabs from one command:

```powershell
ai-workspace targets set codex claude opencode-openrouter
ai-workspace up --backend wt
ai-workspace start codex claude opencode-openrouter --backend wt
```

If no terminal workspace backend is available, print the exact launch commands:

```powershell
ai-workspace start codex claude --backend print
```

## Agent-Inside Switching

Once you are inside Codex, Claude, or OpenCode, your input belongs to that agent. Install the agent bridge so those agents know that `/switch claude` should run the terminal switch command instead of answering in chat:

```powershell
ai-agent install codex claude opencode
ai-agent install gemini qwen copilot cursor windsurf aider cline roo
ai-agent install continue goose kiro
ai-agent targets
ai-agent detect
ai-agent install --file .my-agent-rules.md
ai-agent prompt
```

Use `ai-agent install` in each project so future agent sessions read `AGENTS.md` and `CLAUDE.md`. For an already-running agent, paste the output of `ai-agent prompt` once, then say:

```text
/switch claude
switch codex
next
choose
handoff claude review the current changes
```

Built-in agent bridge targets include:

- `codex`, `claude`, `opencode`, `gemini`, `qwen`
- `copilot` / `vscode`, `cursor`, `windsurf` / `cascade`
- `continue` / `continue-dev`, `goose`, `kiro` / `kiro-cli`
- `aider`, `cline`, `roo`
- `generic` for `AGENTS.md`, plus `--file PATH` for any custom rule file

Use `ai-agent targets` to list every supported target and file path, or `ai-agent detect` to inspect the current project for existing agent rule files before installing bridges.

## Sessions and Handoffs

Sessions let you keep multiple AI CLIs open while they share the same switcher state and memory.

```powershell
ai-session start codex
ai-session start claude
ai-session start opencode-openrouter --backend wt
ai-session start claude --backend print --cwd C:\path\to\project
ai-session list
```

On Linux, macOS, or WSL with tmux:

```bash
ai-session start codex --backend tmux --attach
ai-session start claude --backend tmux
ai-session switch claude
ai-session stop claude
```

If no supported session backend is available, print the launch command instead:

```powershell
ai-session start claude --backend print
ai-session start opencode-openrouter --backend print --arg=--debug
ai-session stop router
```

Use handoff notes to pass work between agents through shared memory:

```powershell
ai-handoff claude "Review the current Codex changes and look for regressions."
ai-handoff opencode-openrouter "Continue implementation using the shared memory context."
```

## Common Commands

```powershell
ayatori about
ayatori status
ayatori workspace up
ayatori agent prompt

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
ai-agent install codex claude opencode
ai-agent install gemini qwen copilot cursor windsurf aider cline roo
ai-agent install continue goose kiro
ai-agent targets
ai-agent detect
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

## Shell Helpers

The setup command can install helpers automatically. Manual installers are also available:

```powershell
py -3.12 scripts\cli_model_switcher.py install-powershell --profile $PROFILE
py -3.12 scripts\cli_model_switcher.py install-cmd --dir "$env:USERPROFILE\bin\ai-cli-switcher"
```

```bash
python3 scripts/cli_model_switcher.py install-unix --shell auto
python3 scripts/cli_model_switcher.py install-unix --shell fish
python3 scripts/cli_model_switcher.py install-bin
```

On Linux, macOS, and WSL, `install-unix` also installs executable shims such as `ai-workspace`, `ai-agent`, `ai-wup`, and `ai-wgo` into `~/.local/bin` by default. These shims matter for agent-side switching because agent shell tools often run non-interactive shells that do not load your Bash/Zsh/fish functions.

Keep the shell functions for `ai-use`, `ai-select`, and branded `ayatori use` / `ayatori select`; they are the pieces that can update the current shell environment. The executable shims are for direct commands, agent-side bridges, and non-interactive shells. `install-unix` adds the shim directory to interactive Bash/Zsh/fish helpers; if an agent still cannot find `ai-workspace`, add `export PATH="$HOME/.local/bin:$PATH"` to Bash/Zsh or run `fish_add_path ~/.local/bin` in fish.

Generated helpers include:

- `ayatori`, `ayatori-nexus`
- `ai-about`
- `ai-use`
- `ai-current`
- `ai-status`
- `ai-profile`
- `ai-api`
- `ai-model`
- `ai-strategy`
- `ai-recipe`
- `ai-adapter`
- `ai-agent`
- `ai-session`
- `ai-workspace`
- `ai-ws`, `ai-wup`, `ai-wgo`, `ai-wpick`
- `ai-handoff`
- `ai-doctor`
- `ai-secret`
- `ai-remember`
- `ai-recall`
- `ai-memory`
- `ai-page`
- `ai-open-memory`
- `ai-run`

## Shared Memory

Default global files:

```text
~/.ai-cli-switcher/state.json
~/.ai-cli-switcher/memory/global.md
~/.ai-cli-switcher/memory/session.md
~/.ai-cli-switcher/memory/context.md
```

Project-local files:

```text
.ai-cli-switcher.json
.ai-cli-memory.md
```

The active profile exposes the combined memory file through `AI_CLI_MEMORY`.

## Secrets

Do not store API keys directly in profiles. Store environment references instead:

```powershell
ai-profile router --command opencode --api openrouter --api-key-env OPENROUTER_API_KEY --use
```

Before sharing state or migrating machines:

```powershell
ai-secret audit --scope all --fail
py -3.12 scripts\cli_model_switcher.py export --portable --output ai-cli-switcher-portable.json
```

## Portable Migration

Export:

```powershell
py -3.12 scripts\cli_model_switcher.py export --portable --output ai-cli-switcher-portable.json
```

Import on another machine:

```powershell
py -3.12 scripts\cli_model_switcher.py import ai-cli-switcher-portable.json --merge-policy rename --active
```

Merge policies:

- `overwrite`: replace conflicting imported names.
- `keep`: keep existing local names.
- `rename`: preserve both sides by importing conflicts with an `-imported` suffix.

## Repository Layout

```text
SKILL.md                         Codex skill instructions
scripts/cli_model_switcher.py    Main CLI implementation
docs/README.*.md                 Localized README pages
references/shell-integration.md  PowerShell, cmd.exe, Bash, Zsh, fish, Nushell notes
references/linux-macos.md        Linux, macOS, WSL, and Git Bash notes
agents/openai.yaml               Skill UI metadata
```

## Development Checks

```powershell
py -3.12 -m py_compile scripts\cli_model_switcher.py
py -3.12 scripts\cli_model_switcher.py secret audit --scope all --fail
py -3.12 "$env:USERPROFILE\.codex\skills\.system\skill-creator\scripts\quick_validate.py" .
```

## Status

This is a personal Codex skill and standalone helper script. The repository is currently private and optimized for local workflow automation.
