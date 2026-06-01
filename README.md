# Ayatori Nexus

**CLI Model Switcher & Shared Memory Hub**

**Language:** English | [Deutsch](docs/README.de.md) | [Français](docs/README.fr.md) | [Italiano](docs/README.it.md) | [日本語](docs/README.ja.md) | [简体中文](docs/README.zh-CN.md) | [繁體中文](docs/README.zh-TW.md)

**Project Links:** [Demo Page](https://yuxuansun123.github.io/cli-model-switcher/) | [Changelog](CHANGELOG.md) | [Release Checklist](docs/RELEASE_CHECKLIST.md) | [Releases](https://github.com/YuxuanSun123/cli-model-switcher/releases)

[![CI](https://github.com/YuxuanSun123/cli-model-switcher/actions/workflows/ci.yml/badge.svg)](https://github.com/YuxuanSun123/cli-model-switcher/actions/workflows/ci.yml)

Ayatori Nexus is the codename for CLI Model Switcher: a local profile switcher for command-line AI coding agents. It lets you move between Codex, Claude Code, OpenCode, Gemini CLI, local models, and OpenAI-compatible gateways while keeping one shared memory layer.

The current design was compared against [LLM](https://github.com/simonw/llm), [AIChat](https://github.com/sigoden/aichat), and [OpenCode](https://github.com/anomalyco/opencode). See [Reference Analysis](docs/REFERENCE_ANALYSIS.md).

## Demo Page

The static demo site lives in `docs/` and can be published with GitHub Pages from the `main` branch and `/docs` folder:

```text
https://yuxuansun123.github.io/cli-model-switcher/
```

See [Demo Page Setup](docs/DEMO_PAGE.md) for the exact GitHub Pages steps.

## Standalone Skill Module

This repository is already a Codex skill because the repository root contains `SKILL.md`. For cleaner reuse, the standalone skill-only module is also available at:

```text
skill/cli-model-switcher/
```

That module contains only the files Codex needs at runtime or setup time: `SKILL.md`, `agents/openai.yaml`, installers, the CLI helper script, and focused references. It intentionally excludes repository-only files such as README pages, changelog, tests, and CI.

Refresh or verify the separated module after editing the root skill or helper:

```powershell
py -3.12 scripts\sync_skill_module.py
py -3.12 scripts\sync_skill_module.py --check
```

```bash
python3 scripts/sync_skill_module.py
python3 scripts/sync_skill_module.py --check
```

## Shortest Path

Use this path if you only want the simple agent bridge:

```bash
sh install.sh --lite
ai-lite
```

```powershell
.\install.ps1 -Lite
ai-lite
```

Use `ai-lite --dry-run` to preview changes, `ai-lite --prompt` for an already-running agent, and `ai-lite --undo` to remove managed bridge blocks.

Prefer a menu? Run:

```bash
ai-menu
ai-menu --list
ai-menu --choice recommend
ai-report
```

## What It Does

- Switch active CLI AI profiles with `ai-use`.
- Install one-step recipes for common stacks such as OpenCode + OpenRouter, Claude Code, Gemini CLI, DeepSeek, Ollama, and LM Studio.
- Share memory across agents through a neutral `AI_CLI_MEMORY` context file.
- Manage API presets for OpenAI, Anthropic, Gemini, OpenRouter, DeepSeek, Ollama, LM Studio, Groq, Mistral, xAI, Together, Fireworks, DashScope, Moonshot, Zhipu, SiliconFlow, Volcengine, Cerebras, Perplexity, Novita, Azure OpenAI, and custom OpenAI-compatible endpoints.
- Load extra model API presets from local `providers.d/*.json` files.
- Add provider allow/deny guardrails with `ai-policy`.
- Reuse prompt and handoff text with `ai-template`.
- Explain effective global/project/default config sources with `ai-config explain`.
- Define task route slots such as `fast`, `think`, `long`, `cheap`, `local`, and `critique` with `ai-route`.
- Probe and cache API/model capabilities with `ai-api probe`.
- Manage local OpenAI-compatible gateway process metadata and env export with `ai-gateway`.
- Install/share provider preset manifests with `ai-preset`.
- Keep local request/gateway telemetry in `ai-request` logs for cost, latency, and token summaries.
- Generate shell helpers for PowerShell, cmd.exe, Bash, Zsh, fish, and Nushell.
- Offer `ai-lite` as a minimal one-command path for users who only want project agent-bridge setup.
- Offer `ai-menu` as a small numbered menu for common setup, diagnosis, and bridge actions.
- Offer `ai-report` as a readiness matrix for all configured profiles, env refs, API presets, model capabilities, commands, and memory paths.
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
.\install.ps1 -Lite
```

```bash
sh install.sh
sh install.sh --lite
```

Manual setup from the repository root is still available:

```powershell
py -3.12 scripts\cli_model_switcher.py setup --wizard
py -3.12 scripts\cli_model_switcher.py setup --lite
```

Linux or macOS:

```bash
python3 scripts/cli_model_switcher.py setup --wizard
python3 scripts/cli_model_switcher.py setup --lite
```

Dry-run the installers before writing anything:

```powershell
.\install.ps1 -DryRun
```

```bash
sh install.sh --dry-run
```

Run the Lite fixture tests from the repository root:

```powershell
python tests/test_lite_workflow.py
```

After setup, reload your shell profile if the installer asks you to. Then:

```powershell
ayatori about
ayatori status
ai-list
ai-lite
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

## Ayatori Lite

Use `ai-lite` when you want the simple version: one command that installs the best project agent bridge files and skips profile, recipe, workspace, and API setup.

```powershell
ai-lite
ai-lite --dry-run
ai-lite --fix
ai-lite --prompt
ai-lite --undo
ai-lite --all-common
ai-lite zed kilo
ai-lite --json
```

With no targets, `ai-lite` scans the current project and installs the shortest matching bridge. If it cannot detect an agent-specific setup, it falls back to `codex claude opencode`. Use `setup --lite` or installer `--lite` when you want only this minimal bridge workflow and shell helpers.

## Quick Menu

Use `ai-menu` when you want a short numbered menu instead of remembering commands:

```powershell
ai-menu
ai-menu --list
ai-menu --choice lite-dry-run
ai-menu --choice recommend
ai-menu --choice prompt
ai-menu --choice report
```

The menu can preview or install Lite bridge files, print the already-running-agent prompt, show project recommendations, list supported platforms, run `doctor`, or print switcher paths. Use `--choice` for scripts and non-interactive terminals.

## Readiness Report

Use `ai-report` before switching machines, sharing setup instructions, or debugging a profile:

```powershell
ai-report
ai-report --profile opencode-openrouter
ai-report --json
ai-report --strict
```

The report checks command availability, API presets, base URLs, API key environment references, local model capability metadata, and memory paths without printing secret values.

## Policy, Templates, and Config

Use provider policies when a machine or project should block accidental use of a provider or gateway:

```powershell
ai-policy list
ai-policy deny openrouter
ai-policy allow openrouter
ai-policy check openrouter
ai-policy remove 1
ai-policy deny provider openai --project
```

Rules are evaluated in order, and the last matching allow/deny wins. `ai-use`, `ai-current --shell`, `ai-run`, `ai-session`, and `ai-workspace` respect deny rules.

Use templates for repeatable handoff, review, or role prompts:

```powershell
ai-template set handoff --description "handoff prompt" --prompt 'Handoff to $agent: $input' --default agent=claude
ai-template list
ai-template show handoff
ai-template use handoff --input "review the latest diff"
ai-template use handoff --param agent=codex --input "continue implementation"
```

Use config explanation when a profile behaves differently than expected:

```powershell
ai-config explain
ai-config explain --profile opencode-openrouter
ai-config explain --json
```

It reports whether each value came from project config, global state, defaults, or environment overrides.

## External Provider Presets

Put private or team API presets in `~/.ai-cli-switcher/providers.d/*.json`, then use them like built-in presets:

```json
{
  "name": "company-ai",
  "label": "Company AI Gateway",
  "kind": "openai-compatible",
  "model": "company-code",
  "env": {
    "OPENAI_BASE_URL": "https://gateway.example.com/v1",
    "OPENAI_API_KEY": "${COMPANY_AI_KEY}"
  },
  "aliases": ["corp"]
}
```

```powershell
ai-api providers
ai-api show corp
ai-api apply company corp --command opencode --model company-code --use
ai-preset install ./company-ai.json
ai-preset list
ai-preset export openrouter --output openrouter-preset.json
```

External presets may also use `{ "presets": { ... }, "aliases": { ... } }` for multi-provider files. Direct-looking secrets are refused; store keys in environment variables and reference them as `${ENV_NAME}`. `ai-preset` validates the same format before installing it into `providers.d`.

## Task Routes, Gateway, and Logs

Use `ai-route` when you want one short command per task type instead of remembering profile/model combinations:

```powershell
ai-route slots
ai-route set think opencode-openrouter anthropic/claude-sonnet-4.5
ai-route set cheap deepseek deepseek-chat
ai-route list
ai-route explain think
ai-route use think
ai-route unset cheap
```

Routes can point to profiles, aliases, strategies, recipes, or API presets. When a route pins a different model, Ayatori creates a generated profile such as `route-think` and activates it with the same policy checks used by `ai-use`.

Use `ai-api probe` to inspect and cache capability metadata:

```powershell
ai-api probe route-think --skip-network
ai-api probe opencode-openrouter --json
```

Use `ai-gateway` for local routers or proxies such as an OpenAI-compatible gateway:

```powershell
ai-gateway config default --profile opencode-openrouter --command "gateway serve"
ai-gateway env --shell powershell
ai-gateway start --print
ai-gateway status
ai-gateway logs
```

Use `ai-request` for local request/gateway telemetry:

```powershell
ai-request add --profile route-think --provider openrouter --model anthropic/claude-sonnet-4.5 --status ok --tokens-in 1200 --tokens-out 350
ai-request log --tail 20
ai-request summary
ai-request path
```

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
ai-lite
ai-lite --dry-run
ai-agent install codex claude opencode
ai-agent install gemini qwen copilot cursor windsurf aider cline roo
ai-agent install continue goose kiro
ai-agent platforms
ai-agent recommend
ai-agent recommend --json
ai-agent platforms amp devin junie zed kilo
ai-agent platforms gitlab-duo firebase-studio android-studio-gemini openhands warp trae
ai-agent platforms openclaw
ai-agent paths openclaw --dir ~/.openclaw/workspace
ai-agent install amp devin junie zed kilo
ai-agent install gitlab-duo firebase-studio android-studio-gemini openhands warp trae
ai-agent install openclaw --dir ~/.openclaw/workspace
ai-agent targets
ai-agent detect
ai-agent install --detected
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
- `amp` / `sourcegraph-amp` / `ampcode`, `devin` / `cognition` / `devin-cli`, `devin-review`
- `junie` / `jetbrains-junie`, `zed` / `zed-agent`, `kilo` / `kilo-code` / `kilocode`
- `gitlab-duo` / `duo`, `firebase-studio` / `project-idx`, `android-studio-gemini`
- `openhands` / `open-hands` / `opendevin`, `warp` / `warp-terminal`, `trae` / `traeide`
- `openclaw` / `claw` / `open-claw`
- `aider`, `cline`, `roo`
- `generic` for `AGENTS.md`, plus `--file PATH` for any custom rule file

Use `ai-agent platforms` to list platform-level adapters. Each platform reports a support level: `native` for official rule paths, `compatible` for officially compatible shared instruction files, `generic` for the generic `AGENTS.md` bridge, and `experimental` for version-dependent paths. Use `ai-agent recommend` to scan the current project and print the shortest matching `ai-agent install ...` command. Dedicated adapters now cover Amp, Devin, Junie, Zed, Kilo, GitLab Duo, Firebase Studio, Android Studio Gemini, OpenHands, Warp, Trae, and OpenClaw. OpenClaw has a dedicated adapter for its default `~/.openclaw/workspace`; `ai-agent install openclaw --dir ~/.openclaw/workspace` writes both `AGENTS.md` and `TOOLS.md` there. See the [Amp manual](https://ampcode.com/manual), [Devin rules](https://cli.devin.ai/docs/extensibility/rules), [Junie docs](https://www.jetbrains.com/help/ai-assistant/junie-agent.html), [Zed rules](https://zed.dev/docs/ai/rules), [Kilo custom instructions](https://kilo.ai/docs/customize/custom-instructions), [GitLab Duo custom rules](https://docs.gitlab.com/user/duo_agent_platform/customize/custom_rules/), [Firebase Studio Gemini docs](https://firebase.google.com/docs/studio/set-up-gemini), [Android Studio Gemini agent files](https://developer.android.com/studio/gemini/agent-files?hl=en), [OpenHands customization](https://docs.openhands.dev/openhands/usage/customization/repository), [Warp rules](https://docs.warp.dev/features/warp-ai/rules), [Trae docs](https://traeide.com/docs), and [OpenClaw agent docs](https://docs.openclaw.ai/agent) for platform conventions. Use `ai-agent targets` to list every supported target and file path, `ai-agent detect` to inspect the current project for existing agent rule files, or `ai-agent install --detected` to install only the bridges that match detected files or dedicated rule directories.

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
ai-lite
ai-lite --dry-run
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
ai-api providers
ai-api test gateway --skip-network
ai-api probe gateway --skip-network
ai-route set think opencode-openrouter anthropic/claude-sonnet-4.5
ai-route use think
ai-gateway config default --profile gateway --command "gateway serve"
ai-gateway env --shell powershell
ai-preset install ./company-ai.json
ai-request summary

ai-policy deny openrouter
ai-policy check openrouter
ai-template set handoff --prompt 'Handoff to $agent: $input' --default agent=claude
ai-template use handoff --input "review this change"
ai-config explain --profile codex

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

On Linux, macOS, and WSL, `install-unix` also installs executable shims such as `ai-lite`, `ai-menu`, `ai-report`, `ai-policy`, `ai-template`, `ai-config`, `ai-route`, `ai-gateway`, `ai-preset`, `ai-request`, `ai-workspace`, `ai-agent`, `ai-wup`, and `ai-wgo` into `~/.local/bin` by default. These shims matter for agent-side switching because agent shell tools often run non-interactive shells that do not load your Bash/Zsh/fish functions.

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
- `ai-policy`
- `ai-template`
- `ai-config`
- `ai-lite`
- `ai-menu`
- `ai-report`
- `ai-agent`
- `ai-route`
- `ai-gateway`
- `ai-preset`
- `ai-request`
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
SKILL.md                                  Live root skill instructions
skill/cli-model-switcher/                Standalone skill-only module
scripts/cli_model_switcher.py            Main CLI implementation
scripts/sync_skill_module.py             Sync root skill files into the standalone module
docs/README.*.md                         Localized README pages
references/shell-integration.md          PowerShell, cmd.exe, Bash, Zsh, fish, Nushell notes
references/linux-macos.md                Linux, macOS, WSL, and Git Bash notes
agents/openai.yaml                       Skill UI metadata
```

## Development Checks

```powershell
py -3.12 -m py_compile scripts\cli_model_switcher.py
py -3.12 scripts\sync_skill_module.py --check
py -3.12 scripts\cli_model_switcher.py secret audit --scope all --fail
py -3.12 "$env:USERPROFILE\.codex\skills\.system\skill-creator\scripts\quick_validate.py" .
```

## Status

This is a personal Codex skill and standalone helper script. The repository is currently private and optimized for local workflow automation.
