# Linux and macOS Integration

Use this reference when installing or troubleshooting the CLI model switcher on Linux, macOS, WSL, or Git Bash.

## Quick Install

Prefer the auto installer:

```bash
curl -fsSL https://raw.githubusercontent.com/YuxuanSun123/cli-model-switcher/main/install.sh | sh
```

From an existing checkout:

```bash
sh install.sh
```

Manual helper install:

```bash
python3 "$HOME/.codex/skills/cli-model-switcher/scripts/cli_model_switcher.py" install-unix --shell auto
```

This installs shell functions, adds the shim directory to interactive shell helpers, and writes POSIX executable shims into `~/.local/bin` by default. Open a new terminal or reload the shell profile printed by the installer.

For a complete first-run setup with recommended profiles and strategy aliases:

```bash
python3 "$HOME/.codex/skills/cli-model-switcher/scripts/cli_model_switcher.py" setup --full
```

For a guided first run that detects installed CLIs, installs profile recipes, refreshes helpers, and runs health checks:

```bash
python3 "$HOME/.codex/skills/cli-model-switcher/scripts/cli_model_switcher.py" setup --wizard
python3 "$HOME/.codex/skills/cli-model-switcher/scripts/cli_model_switcher.py" setup --wizard --yes --recipes opencode-openrouter,local-ollama --active opencode-openrouter
```

## Shell-Specific Install

Bash on Linux:

```bash
python3 "$HOME/.codex/skills/cli-model-switcher/scripts/cli_model_switcher.py" install-unix --shell bash --profile "$HOME/.bashrc"
source "$HOME/.bashrc"
```

Zsh on macOS:

```zsh
python3 "$HOME/.codex/skills/cli-model-switcher/scripts/cli_model_switcher.py" install-unix --shell zsh --profile "$HOME/.zshrc"
source "$HOME/.zshrc"
```

Fish:

```fish
python3 "$HOME/.codex/skills/cli-model-switcher/scripts/cli_model_switcher.py" install-unix --shell fish
```

Executable shims only, useful for non-interactive agent shells:

```bash
python3 "$HOME/.codex/skills/cli-model-switcher/scripts/cli_model_switcher.py" install-bin
python3 "$HOME/.codex/skills/cli-model-switcher/scripts/cli_model_switcher.py" install-bin --bin-dir "$HOME/.local/bin"
```

## Commands After Install

```bash
ai-list
ai-lite
ai-lite --dry-run
ai-status
ai-profile local --command opencode --model local --alias l --use
ai-profile deepseek --command opencode --api deepseek --model deepseek-chat --alias ds --use
ai-api list
ai-api apply opencode openrouter --command opencode --model openrouter/auto --use
ai-api test opencode --skip-network
ai-model list --provider openrouter
ai-model pin opencode-openrouter code
ai-strategy install
ai-recipe list
ai-recipe install opencode-openrouter --use
ai-use code-fast
ai-workspace targets set codex claude opencode-openrouter
ai-workspace up
ai-wgo claude
ai-lite
ai-agent install all
ai-agent prompt
ai-session start claude --backend tmux
ai-session switch claude
ai-handoff claude "Review the current Codex work and look for regressions."
ai-use local-private
ai-adapter opencode opencode-openrouter
ai-use claude
ai-use opencode --open-page
ai-select
ai-page list
ai-current
ai-doctor
ai-doctor --fix
ai-secret audit --scope all --fail
ai-remember --scope global --tag preference "Prefer concise answers."
ai-recall --tag preference
ai-memory tags
ai-memory compact --scope global --keep 50
python3 "$HOME/.codex/skills/cli-model-switcher/scripts/cli_model_switcher.py" export --portable --output ai-cli-switcher-portable.json
python3 "$HOME/.codex/skills/cli-model-switcher/scripts/cli_model_switcher.py" import ai-cli-switcher-portable.json --merge-policy rename --active
ai-run --help
```

## Python Compatibility

Wrappers try `AI_CLI_SWITCHER_PYTHON`, then `python3`, then `python`, then `py -3.12`.

Set a specific interpreter when needed:

```bash
export AI_CLI_SWITCHER_PYTHON=/usr/bin/python3
```

## Paths

Default state and memory live under:

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

## Platform Notes

- macOS default shell is usually zsh; use `~/.zshrc` for interactive terminals.
- Linux bash usually uses `~/.bashrc` for interactive terminals.
- macOS bash may use `~/.bash_profile`; pass `--profile` if needed.
- Agent shell tools often run non-interactive shells. `install-unix` adds `~/.local/bin` to interactive helpers, but some agents may need it in the broader login environment so commands such as `ai-lite`, `ai-agent`, `ai-workspace`, `ai-wup`, and `ai-wgo` work even when Bash/Zsh/fish functions are not loaded.
- Bash/Zsh PATH example: `export PATH="$HOME/.local/bin:$PATH"`.
- fish PATH example: `fish_add_path ~/.local/bin`.
- Keep the `ai-use` and `ai-select` shell functions for current-shell environment switching; executable shims can run commands but cannot mutate their parent shell.
- Use tmux for true same-terminal switching on Linux, macOS, and WSL: `brew install tmux`, `sudo apt install tmux`, or your distro package manager equivalent.
- `open context` uses `open` on macOS and `xdg-open` on Linux when available.
- Keep real API keys in the shell, keychain, or credential manager; store only `${ENV_VAR}` references in profiles.
- Use API presets to reduce setup steps: `ai-api list`, `ai-api show openrouter`, or `ai-profile router --command opencode --api openrouter --model openrouter/auto --use`.
- Use recipes when you want one-step profiles: `ai-recipe install opencode-openrouter --use`, `ai-recipe install claude-native gemini-cli`, or `ai-recipe install custom-gateway --active custom-gateway`.
- For private gateways and local proxies, start from `custom-openai`: `ai-profile gateway --command opencode --api custom-openai --base-url https://gateway.example/v1 --api-key-env GATEWAY_API_KEY --use`.
- For guided setup, use `setup --wizard`; for scripts and fresh machines, add `--yes --recipes ... --active ...`.
- Use strategy aliases for task switching after `setup --full` or `ai-strategy install`: `ai-use code-fast`, `ai-use code-best`, `ai-use local-private`, and `ai-use cheap-long-context`.
- Use tmux for same-terminal multi-agent work: `ai-session start codex --backend tmux --attach`, `ai-session start claude --backend tmux`, `ai-session switch claude`, and `ai-session stop claude`.
- Use `ai-handoff PROFILE "note"` to write a tagged handoff note to shared memory before opening another agent session.
- Use tagged memory to keep context tidy: `ai-remember --tag api-note "..."`, `ai-recall --tag api-note`, `ai-memory dedupe`, and `ai-memory compact --keep 50`.
- Use `ai-doctor --fix` after upgrades to refresh stale managed wrappers and repair local state issues.
- Use `ai-secret audit --scope all --fail` before portable export or before sharing state/memory files.
- Use portable export/import for cross-machine moves; `--merge-policy rename` keeps existing local profiles and imports conflicting ones with `-imported` suffixes.
