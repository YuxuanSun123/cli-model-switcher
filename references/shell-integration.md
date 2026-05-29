# Shell Integration

Use this reference when adding shortcuts that apply the active CLI AI profile to the user's shell.

## PowerShell

Prefer the installer:

```powershell
py -3.12 "$env:USERPROFILE\.codex\skills\cli-model-switcher\scripts\cli_model_switcher.py" install-powershell --profile $PROFILE
. $PROFILE
```

Set `$env:AI_CLI_SWITCHER_PYTHON` if the wrapper should use a specific Python command, such as `py -3.12`.

Or add functions to `$PROFILE` manually:

```powershell
function ai-use {
  param([Parameter(Mandatory=$true)][string]$Name)
  py -3.12 "$env:USERPROFILE\.codex\skills\cli-model-switcher\scripts\cli_model_switcher.py" use $Name | Write-Host
  Invoke-Expression (py -3.12 "$env:USERPROFILE\.codex\skills\cli-model-switcher\scripts\cli_model_switcher.py" current --shell powershell)
}

function ai-current {
  py -3.12 "$env:USERPROFILE\.codex\skills\cli-model-switcher\scripts\cli_model_switcher.py" current
}

function ai-status {
  py -3.12 "$env:USERPROFILE\.codex\skills\cli-model-switcher\scripts\cli_model_switcher.py" status
}

function ai-paths {
  py -3.12 "$env:USERPROFILE\.codex\skills\cli-model-switcher\scripts\cli_model_switcher.py" paths
}

function ai-list {
  py -3.12 "$env:USERPROFILE\.codex\skills\cli-model-switcher\scripts\cli_model_switcher.py" list
}

function ai-profile {
  py -3.12 "$env:USERPROFILE\.codex\skills\cli-model-switcher\scripts\cli_model_switcher.py" profile @args
}

function ai-api {
  py -3.12 "$env:USERPROFILE\.codex\skills\cli-model-switcher\scripts\cli_model_switcher.py" api @args
}

function ai-model {
  py -3.12 "$env:USERPROFILE\.codex\skills\cli-model-switcher\scripts\cli_model_switcher.py" model @args
}

function ai-strategy {
  py -3.12 "$env:USERPROFILE\.codex\skills\cli-model-switcher\scripts\cli_model_switcher.py" strategy @args
}

function ai-recipe {
  py -3.12 "$env:USERPROFILE\.codex\skills\cli-model-switcher\scripts\cli_model_switcher.py" recipe @args
}

function ai-adapter {
  py -3.12 "$env:USERPROFILE\.codex\skills\cli-model-switcher\scripts\cli_model_switcher.py" adapter @args
}

function ai-select {
  py -3.12 "$env:USERPROFILE\.codex\skills\cli-model-switcher\scripts\cli_model_switcher.py" select
  Invoke-Expression (py -3.12 "$env:USERPROFILE\.codex\skills\cli-model-switcher\scripts\cli_model_switcher.py" current --shell powershell)
}

function ai-doctor {
  py -3.12 "$env:USERPROFILE\.codex\skills\cli-model-switcher\scripts\cli_model_switcher.py" doctor @args
}

function ai-secret {
  py -3.12 "$env:USERPROFILE\.codex\skills\cli-model-switcher\scripts\cli_model_switcher.py" secret @args
}

function ai-remember {
  py -3.12 "$env:USERPROFILE\.codex\skills\cli-model-switcher\scripts\cli_model_switcher.py" remember @args
}

function ai-recall {
  py -3.12 "$env:USERPROFILE\.codex\skills\cli-model-switcher\scripts\cli_model_switcher.py" recall @args
}

function ai-memory {
  py -3.12 "$env:USERPROFILE\.codex\skills\cli-model-switcher\scripts\cli_model_switcher.py" memory @args
}

function ai-open-memory {
  py -3.12 "$env:USERPROFILE\.codex\skills\cli-model-switcher\scripts\cli_model_switcher.py" open context @args
}

function ai-run {
  py -3.12 "$env:USERPROFILE\.codex\skills\cli-model-switcher\scripts\cli_model_switcher.py" run @args
}
```

Usage:

```powershell
ai-use codex
ai-use claude
ai-status
ai-profile local --command opencode --model local --alias l --use
ai-profile deepseek --command opencode --api deepseek --model deepseek-chat --alias ds --use
ai-api list
ai-api show openrouter
ai-api test deepseek --skip-network
ai-model list --provider openrouter
ai-strategy install
ai-recipe list
ai-recipe install opencode-openrouter --use
ai-use code-fast
ai-adapter opencode opencode-openrouter
ai-current
ai-paths
ai-list
ai-select
ai-doctor
ai-doctor --fix
ai-secret audit --scope all --fail
ai-remember "Project uses pnpm and strict TypeScript."
ai-remember --scope global --tag preference "Prefer concise answers."
ai-recall --tag preference
ai-memory compact --scope global --keep 50
py -3.12 "$env:USERPROFILE\.codex\skills\cli-model-switcher\scripts\cli_model_switcher.py" export --portable --output ai-cli-switcher-portable.json
py -3.12 "$env:USERPROFILE\.codex\skills\cli-model-switcher\scripts\cli_model_switcher.py" import ai-cli-switcher-portable.json --merge-policy rename --active
py -3.12 "$env:USERPROFILE\.codex\skills\cli-model-switcher\scripts\cli_model_switcher.py" remember --scope project "Use pnpm here."
py -3.12 "$env:USERPROFILE\.codex\skills\cli-model-switcher\scripts\cli_model_switcher.py" forget-session
py -3.12 "$env:USERPROFILE\.codex\skills\cli-model-switcher\scripts\cli_model_switcher.py" project-init --active codex
py -3.12 "$env:USERPROFILE\.codex\skills\cli-model-switcher\scripts\cli_model_switcher.py" use claude --project
ai-recall
ai-open-memory
ai-run --help
```

## cmd.exe

Prefer the installer:

```bat
py -3.12 "%USERPROFILE%\.codex\skills\cli-model-switcher\scripts\cli_model_switcher.py" install-cmd --dir "%USERPROFILE%\bin\ai-cli-switcher"
```

Then add `%USERPROFILE%\bin\ai-cli-switcher` to PATH if it is not already there. The installer creates native wrappers:

```bat
ai-use claude
ai-status
ai-use opencode --open-page
ai-select
ai-profile local --command opencode --model local --alias l --use
ai-profile deepseek --command opencode --api deepseek --model deepseek-chat --alias ds --use
ai-api apply opencode openrouter --command opencode --model openrouter/auto --use
ai-api test opencode --skip-network
ai-model list --provider openrouter
ai-strategy install
ai-recipe list
ai-recipe install opencode-openrouter --use
ai-use code-fast
ai-adapter opencode opencode-openrouter
ai-memory tags
ai-page list
ai-page open claude home
ai-current
ai-doctor
ai-doctor --fix
ai-secret audit --scope all --fail
ai-run --help
```

cmd.exe cannot permanently update the current environment from Python alone, so `ai-use.cmd` and `ai-select.cmd` are batch wrappers that apply emitted `set` commands in the current cmd.exe session. Minimal manual wrapper:

```bat
@echo off
py -3.12 "%USERPROFILE%\.codex\skills\cli-model-switcher\scripts\cli_model_switcher.py" use %1
for /f "usebackq delims=" %%i in (`py -3.12 "%USERPROFILE%\.codex\skills\cli-model-switcher\scripts\cli_model_switcher.py" current --shell cmd`) do %%i
```

## Bash or Zsh

Prefer the installer:

```bash
python3 "$HOME/.codex/skills/cli-model-switcher/scripts/cli_model_switcher.py" install-unix --shell auto
```

The installer detects bash/zsh from `$SHELL`, writes `~/.config/ai-cli-switcher/ai-cli-switcher.sh`, and adds a managed source block to the relevant profile. Manual functions:

```bash
ai-use() {
  python3 "$HOME/.codex/skills/cli-model-switcher/scripts/cli_model_switcher.py" use "$@"
  eval "$(python3 "$HOME/.codex/skills/cli-model-switcher/scripts/cli_model_switcher.py" current --shell bash)"
}

ai-current() {
  python3 "$HOME/.codex/skills/cli-model-switcher/scripts/cli_model_switcher.py" current "$@"
}

ai-api() {
  python3 "$HOME/.codex/skills/cli-model-switcher/scripts/cli_model_switcher.py" api "$@"
}

ai-model() {
  python3 "$HOME/.codex/skills/cli-model-switcher/scripts/cli_model_switcher.py" model "$@"
}

ai-strategy() {
  python3 "$HOME/.codex/skills/cli-model-switcher/scripts/cli_model_switcher.py" strategy "$@"
}

ai-recipe() {
  python3 "$HOME/.codex/skills/cli-model-switcher/scripts/cli_model_switcher.py" recipe "$@"
}

ai-adapter() {
  python3 "$HOME/.codex/skills/cli-model-switcher/scripts/cli_model_switcher.py" adapter "$@"
}

ai-memory() {
  python3 "$HOME/.codex/skills/cli-model-switcher/scripts/cli_model_switcher.py" memory "$@"
}

ai-doctor() {
  python3 "$HOME/.codex/skills/cli-model-switcher/scripts/cli_model_switcher.py" doctor "$@"
}

ai-secret() {
  python3 "$HOME/.codex/skills/cli-model-switcher/scripts/cli_model_switcher.py" secret "$@"
}

ai-remember() {
  python3 "$HOME/.codex/skills/cli-model-switcher/scripts/cli_model_switcher.py" remember "$@"
}
```

## fish

Prefer the installer:

```fish
python3 "$HOME/.codex/skills/cli-model-switcher/scripts/cli_model_switcher.py" install-unix --shell fish
```

The generated file in `~/.config/fish/conf.d/ai-cli-switcher.fish` is loaded automatically by new fish sessions. To apply the active profile manually:

```fish
python3 "$HOME/.codex/skills/cli-model-switcher/scripts/cli_model_switcher.py" current --shell fish | source
```

## Nushell

Nushell can consume emitted env commands directly:

```nu
python3 ~/.codex/skills/cli-model-switcher/scripts/cli_model_switcher.py current --shell nu | save -f /tmp/ai-cli-switcher.nu
source /tmp/ai-cli-switcher.nu
```

## Environment Contract

The helper emits these common variables:

- `AI_CLI_PROVIDER`
- `AI_CLI_MODEL`
- `AI_CLI_COMMAND`
- `AI_CLI_MEMORY`
- `AI_CLI_API_PROVIDER` when a profile uses an API preset
- `AI_CLI_API_KIND` when a profile uses an API preset

`AI_CLI_MEMORY` points to the combined context file generated from global, project, and session memory layers.

Provider-specific CLIs may need additional variables. API presets emit common variables such as `OPENAI_API_KEY`, `OPENAI_BASE_URL`, `OPENAI_API_BASE`, `OPENAI_API_BASE_URL`, `ANTHROPIC_API_KEY`, or provider-specific key names by referencing shell variables. Keep real secrets in the shell, OS credential store, or vendor config, and store only variable names in switcher state.
