# CLI Model Switcher

A local profile switcher for command-line AI coding agents. It lets you move between Codex, Claude Code, OpenCode, Gemini CLI, local models, and OpenAI-compatible gateways while keeping one shared memory layer.

## What It Does

- Switch active CLI AI profiles with `ai-use`.
- Install one-step recipes for common stacks such as OpenCode + OpenRouter, Claude Code, Gemini CLI, DeepSeek, Ollama, and LM Studio.
- Share memory across agents through a neutral `AI_CLI_MEMORY` context file.
- Manage API presets for OpenAI, Anthropic, Gemini, OpenRouter, DeepSeek, Ollama, LM Studio, Groq, Mistral, xAI, Together, Fireworks, DashScope, Moonshot, Zhipu, SiliconFlow, Volcengine, Cerebras, Perplexity, Novita, Azure OpenAI, and custom OpenAI-compatible endpoints.
- Generate shell helpers for PowerShell, cmd.exe, Bash, Zsh, fish, and Nushell.
- Audit state and memory for direct-looking secrets before export or migration.
- Export/import portable profile state between machines.

## Quick Start

From the repository root:

```powershell
py -3.12 scripts\cli_model_switcher.py setup --wizard
```

Non-interactive Windows setup:

```powershell
py -3.12 scripts\cli_model_switcher.py setup --wizard --yes --recipes opencode-openrouter,local-ollama --active opencode-openrouter
```

Linux or macOS:

```bash
python3 scripts/cli_model_switcher.py setup --wizard
```

After setup, reload your shell profile if the installer asks you to. Then:

```powershell
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

## Common Commands

```powershell
ai-use codex
ai-use claude
ai-use opencode-openrouter
ai-use local-private

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
```

Generated helpers include:

- `ai-use`
- `ai-current`
- `ai-status`
- `ai-profile`
- `ai-api`
- `ai-model`
- `ai-strategy`
- `ai-recipe`
- `ai-adapter`
- `ai-doctor`
- `ai-secret`
- `ai-remember`
- `ai-recall`
- `ai-memory`
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
