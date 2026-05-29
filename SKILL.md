---
name: cli-model-switcher
description: Manage and automate switching between command-line AI coding agents and model platforms such as Codex, Claude Code, OpenCode, Gemini CLI, and similar tools. Use when the user wants a skill, shortcut, shell command, profile manager, shared memory setup, or workflow for changing active CLI AI provider/model/API base/env vars while preserving shared cross-agent memory.
---

# CLI Model Switcher

## Overview

Use this skill to set up or maintain a local command-line AI profile switcher. Prefer a small, explicit profile layer that writes the active provider/model state and exposes shared memory to all CLI agents.

## Core Workflow

1. Inspect the user's shell and installed tools when needed:
   - PowerShell: `$PROFILE`, `Get-Command codex,claude,opencode`
   - cmd.exe: `%USERPROFILE%`, `where codex claude opencode`
   - Git Bash/WSL: `~/.bashrc`, `~/.zshrc`, `command -v`
   - Linux/macOS: `$SHELL`, `command -v python3 codex claude opencode`, `~/.bashrc`, `~/.zshrc`, `~/.config/fish/conf.d`
2. Use `scripts/cli_model_switcher.py` for repeatable state and memory operations.
3. Store switcher state outside a single vendor's config directory unless the user asks otherwise:
   - default state: `~/.ai-cli-switcher/state.json`
   - global memory: `~/.ai-cli-switcher/memory/global.md`
   - session memory: `~/.ai-cli-switcher/memory/session.md`
   - combined context: `~/.ai-cli-switcher/memory/context.md`
   - project config: `.ai-cli-switcher.json`
   - project memory: `.ai-cli-memory.md`
4. Treat API keys as external secrets. Never write API keys into the shared state file; reference environment variable names only.
5. After changing profiles, show the user the command they can run in their shell to apply the selected profile.

## Script Usage

Run the helper with Python 3:

```powershell
py -3.12 scripts/cli_model_switcher.py init
py -3.12 scripts/cli_model_switcher.py setup --shell auto
py -3.12 scripts/cli_model_switcher.py setup --full
py -3.12 scripts/cli_model_switcher.py setup --wizard
py -3.12 scripts/cli_model_switcher.py setup --wizard --yes --recipes opencode-openrouter,local-ollama --active opencode-openrouter
py -3.12 scripts/cli_model_switcher.py status
py -3.12 scripts/cli_model_switcher.py list
py -3.12 scripts/cli_model_switcher.py paths
py -3.12 scripts/cli_model_switcher.py api list
py -3.12 scripts/cli_model_switcher.py api show openrouter
py -3.12 scripts/cli_model_switcher.py api apply opencode openrouter --command opencode --model anthropic/claude-sonnet-4.5 --use
py -3.12 scripts/cli_model_switcher.py api test opencode --skip-network
py -3.12 scripts/cli_model_switcher.py adapter opencode opencode-openrouter
py -3.12 scripts/cli_model_switcher.py model list --provider openrouter
py -3.12 scripts/cli_model_switcher.py model pin opencode-openrouter code
py -3.12 scripts/cli_model_switcher.py model alias set mycode openrouter anthropic/claude-sonnet-4.5 --cap coding=true
py -3.12 scripts/cli_model_switcher.py strategy install
py -3.12 scripts/cli_model_switcher.py strategy use code-fast
py -3.12 scripts/cli_model_switcher.py recipe list
py -3.12 scripts/cli_model_switcher.py recipe show opencode-openrouter
py -3.12 scripts/cli_model_switcher.py recipe install opencode-openrouter --use
py -3.12 scripts/cli_model_switcher.py recipe install claude-native gemini-cli opencode-deepseek --active claude
py -3.12 scripts/cli_model_switcher.py session start claude --backend print
py -3.12 scripts/cli_model_switcher.py session start claude --backend tmux --attach
py -3.12 scripts/cli_model_switcher.py session list
py -3.12 scripts/cli_model_switcher.py session switch claude
py -3.12 scripts/cli_model_switcher.py handoff claude "Review the current Codex work and look for regressions."
py -3.12 scripts/cli_model_switcher.py profile local --command opencode --model local-model --alias l --use
py -3.12 scripts/cli_model_switcher.py profile deepseek --command opencode --api deepseek --model deepseek-chat --alias ds --use
py -3.12 scripts/cli_model_switcher.py add gemini --command gemini --model gemini-2.5-pro
py -3.12 scripts/cli_model_switcher.py add local --project --command opencode --model local-model
py -3.12 scripts/cli_model_switcher.py set codex --model gpt-5 --env OPENAI_BASE_URL=https://api.openai.com/v1
py -3.12 scripts/cli_model_switcher.py set claude --page console=https://claude.ai/
py -3.12 scripts/cli_model_switcher.py alias set fast codex
py -3.12 scripts/cli_model_switcher.py use codex
py -3.12 scripts/cli_model_switcher.py use fast
py -3.12 scripts/cli_model_switcher.py use code-fast
py -3.12 scripts/cli_model_switcher.py use local-private
py -3.12 scripts/cli_model_switcher.py use claude --open-page
py -3.12 scripts/cli_model_switcher.py select
py -3.12 scripts/cli_model_switcher.py page list
py -3.12 scripts/cli_model_switcher.py page open opencode home
py -3.12 scripts/cli_model_switcher.py page set opencode docs https://opencode.ai/
py -3.12 scripts/cli_model_switcher.py project-init --active claude
py -3.12 scripts/cli_model_switcher.py use claude --project
py -3.12 scripts/cli_model_switcher.py current --shell powershell
py -3.12 scripts/cli_model_switcher.py current --shell fish
py -3.12 scripts/cli_model_switcher.py current --shell nu
py -3.12 scripts/cli_model_switcher.py remember --scope global --tag preference "Preference: keep answers concise."
py -3.12 scripts/cli_model_switcher.py remember --scope project --tag command "This repo uses pnpm."
py -3.12 scripts/cli_model_switcher.py recall
py -3.12 scripts/cli_model_switcher.py recall --tag preference
py -3.12 scripts/cli_model_switcher.py memory tags
py -3.12 scripts/cli_model_switcher.py memory dedupe --scope global
py -3.12 scripts/cli_model_switcher.py memory compact --scope global --keep 50
py -3.12 scripts/cli_model_switcher.py forget-session
py -3.12 scripts/cli_model_switcher.py doctor
py -3.12 scripts/cli_model_switcher.py doctor --fix
py -3.12 scripts/cli_model_switcher.py doctor --fix --json
py -3.12 scripts/cli_model_switcher.py secret audit --scope all --fail
py -3.12 scripts/cli_model_switcher.py secret audit --scope memory --json
py -3.12 scripts/cli_model_switcher.py export --output ai-cli-switcher.json
py -3.12 scripts/cli_model_switcher.py export --portable --output ai-cli-switcher-portable.json
py -3.12 scripts/cli_model_switcher.py import ai-cli-switcher.json --merge-policy overwrite
py -3.12 scripts/cli_model_switcher.py import ai-cli-switcher-portable.json --merge-policy rename --active
py -3.12 scripts/cli_model_switcher.py open context --print
py -3.12 scripts/cli_model_switcher.py install-powershell --profile $PROFILE
py -3.12 scripts/cli_model_switcher.py install-cmd --dir %USERPROFILE%\bin\ai-cli-switcher
py -3.12 scripts/cli_model_switcher.py install-shell --output ~/.config/ai-cli-switcher/ai-cli-switcher.sh
py -3.12 scripts/cli_model_switcher.py install-fish --output ~/.config/fish/conf.d/ai-cli-switcher.fish
python3 scripts/cli_model_switcher.py install-unix --shell auto
```

The helper creates starter profiles for `codex`, `claude`, and `opencode`. Edit profile fields to match the user's actual commands and model names.

Use `run` to start the active CLI with common `AI_CLI_*` variables applied:

```powershell
py -3.12 scripts/cli_model_switcher.py run --help
```

## Profile Model

Each profile should include:

- `provider`: stable name such as `codex`, `claude`, or `opencode`
- `command`: executable command to launch the CLI
- `model`: model or alias for the provider
- `api_provider`: optional model API preset such as `openai`, `openrouter`, `deepseek`, `gemini`, `ollama`, or `custom-openai`
- `api_kind`: optional API surface such as `openai-compatible`, `anthropic`, or `azure-openai`
- `env`: non-secret environment values or references to secret env var names
- `memory_path`: path to the shared memory file

When a user asks for "realtime switching", implement shell functions or aliases that call the helper and then apply its emitted environment commands. See `references/shell-integration.md` when adding shortcuts to PowerShell, cmd.exe, Bash, or Zsh.

Prefer script commands over manual JSON edits:

- `setup --shell auto` initializes state and installs the best shell helper for the current platform.
- `setup --full` initializes state, creates recommended profiles (`codex`, `claude`, `gemini`, `opencode-openrouter`, `opencode-deepseek`, `local-ollama`), installs strategy aliases, detects installed CLI tools, and installs shell helpers. Use `--no-install` to skip wrapper writes.
- `setup --wizard` detects installed CLI tools, offers profile recipes, chooses an active profile, installs shell helpers, then runs `doctor --fix` and `secret audit`. Use `--yes --recipes NAME1,NAME2 --active PROFILE` for non-interactive setup.
- `status` prints the active profile, scope, command status, and memory path.
- `profile NAME --command COMMAND --model MODEL --alias SHORT --use` creates or updates a profile, optionally aliases it, and activates it in one step.
- `profile NAME --command COMMAND --api PRESET --model MODEL --use` creates or updates a profile with a model API preset in one step.
- `api list`, `api show PRESET`, and `api apply PROFILE PRESET --command COMMAND --use` manage built-in API presets.
- `api test PROFILE` checks command availability, key env vars, base URL format, and OpenAI-compatible `/models` connectivity unless `--skip-network` is used.
- `adapter codex|claude|gemini|opencode [PROFILE]` prints CLI-specific environment and config snippets for the active or named profile.
- Built-in API presets include `openai`, `anthropic`, `gemini`, `azure-openai`, `openrouter`, `deepseek`, `groq`, `ollama`, `lmstudio`, `mistral`, `xai`, `together`, `fireworks`, `dashscope`, `moonshot`, `zhipu`, `siliconflow`, `volcengine`, `cerebras`, `perplexity`, `novita`, and `custom-openai`.
- Use `--base-url` and `--api-key-env ENV` with `api apply` or `profile --api` to point a preset at a private gateway, proxy, regional endpoint, or alternate key variable.
- `model list --provider PROVIDER`, `model show NAME`, and `model pin PROFILE MODEL_OR_ALIAS` manage known model choices and store capabilities on profiles.
- `model alias set NAME PROVIDER MODEL --cap KEY=VALUE` adds custom model aliases such as `fast`, `cheap`, `code`, or `local`.
- `strategy install` creates task aliases so `use code-fast`, `use code-best`, `use local-private`, and `use cheap-long-context` switch to the matching profile/model/API.
- `recipe list`, `recipe show NAME`, and `recipe install NAME --use` install common profile bundles without remembering long arguments. Built-in recipes include `codex-openai`, `claude-native`, `gemini-cli`, `opencode-openrouter`, `opencode-openrouter-best`, `opencode-deepseek`, `local-ollama`, `local-lmstudio`, and `custom-gateway`.
- `session start PROFILE --backend auto|tmux|wt|powershell|print`, `session list`, `session switch NAME`, and `session stop NAME` manage multiple AI CLI sessions through tmux, Windows Terminal, PowerShell windows, or printed fallback commands.
- `handoff PROFILE "NOTE"` writes a tagged session-memory handoff note and starts the target session so another agent can continue with the shared context.
- `add NAME --command COMMAND --model MODEL` creates a new profile.
- `add NAME --project --command COMMAND --model MODEL` creates a project-local profile override.
- `set NAME --model MODEL --env KEY=VALUE` updates an existing profile.
- Store secret env values as references such as `--env OPENAI_API_KEY=${OPENAI_API_KEY}`; direct-looking secrets are refused unless `--allow-secret-env` is passed.
- `remove NAME` deletes a non-active profile.
- `alias set NAME TARGET` creates a short name for a profile.
- `select` opens a numbered menu for switching profiles without remembering names.
- `use NAME --open-page [LABEL]` switches the CLI profile and opens the profile page.
- `page list`, `page open PROFILE LABEL`, and `page set PROFILE LABEL URL` manage web pages linked to profiles.
- `paths` prints all config and memory locations.
- `export --output FILE` and `import FILE` move global profiles and aliases between machines.
- `export --portable --output FILE` rewrites switcher-owned paths to portable placeholders and refuses direct-looking env secrets unless `--allow-secret-env` is passed.
- `import FILE --merge-policy overwrite|keep|rename` controls conflicts when importing profiles, profile aliases, and model aliases. Use `rename` when combining machines without losing either side.
- `open context` opens the combined memory file; use `--print` when a path is enough.
- `project-init --active NAME` creates project-local config and memory.
- `use NAME --project` sets the active profile for the current project only.
- `forget-session` clears temporary session memory.
- `doctor` checks command availability, env vars, state files, and memory files.
- `doctor --fix` repairs missing or corrupt state, invalid active profiles, broken aliases, missing memory files, and stale managed wrappers when possible. Use `--json` for automation.
- `secret audit --scope all|state|project|memory` scans profiles and memory without printing secret values. Use `--fail` in scripts to return nonzero when findings exist.
- `install-powershell --profile $PROFILE` writes `ai-use`, `ai-current`, `ai-status`, `ai-paths`, `ai-list`, `ai-profile`, `ai-api`, `ai-model`, `ai-strategy`, `ai-recipe`, `ai-adapter`, `ai-session`, `ai-handoff`, `ai-select`, `ai-doctor`, `ai-secret`, `ai-remember`, `ai-recall`, `ai-memory`, `ai-open-memory`, and `ai-run` functions to the current PowerShell profile.
- `install-cmd --dir DIR` writes native cmd.exe `.cmd` wrappers such as `ai-use.cmd`, `ai-select.cmd`, `ai-page.cmd`, and `ai-run.cmd`.
- `install-shell --output FILE` writes Bash/Zsh helper functions.
- `install-fish --output FILE` writes fish helper functions.
- `install-unix --shell auto|bash|zsh|fish` installs Linux/macOS shell helpers and updates the relevant shell profile.
- `current --shell` supports `powershell`, `cmd`, `bash`, `zsh`, `fish`, and `nu`.
- Set `AI_CLI_SWITCHER_PYTHON` when wrappers need a specific Python command, such as `py -3.12` or `python3`.

## Shared Memory Rules

Keep shared memory portable and vendor-neutral:

- Store user preferences, project conventions, and recurring context.
- Use `global` for durable personal preferences, `project` for repository conventions, and `session` for temporary context.
- Expose `memory/context.md` as the combined memory entrypoint through `AI_CLI_MEMORY`.
- Avoid credentials, private tokens, session cookies, or unrelated personal data.
- `remember` refuses obvious API keys, tokens, passwords, and secrets unless `--force` is passed.
- `remember --tag TAG`, `recall --tag TAG`, and `memory tags` organize durable notes by tags such as `preference`, `project`, `command`, `bugfix`, and `api-note`.
- `memory dedupe`, `memory compact --keep N`, and `memory archive` keep shared memory small while preserving archived entries under `~/.ai-cli-switcher/memory/archive`.
- `import` refuses direct-looking secrets in env values unless `--allow-secret-env` is passed.
- Run `secret audit --scope all --fail` before exporting, sharing logs, or migrating state to another machine.
- Prefer short dated entries over long transcripts.
- When importing memory from vendor-specific files, preserve the original file and append a summarized entry to the shared memory file.

## Implementation Notes

For simple setup requests, create the state directory, initialize profiles, and provide shell shortcut instructions. For deeper integration, update the user's shell profile only after making the exact file and command clear.

For Linux or macOS setup, read `references/linux-macos.md`.
