# Changelog

All notable changes to this project are documented here.

This project currently follows a lightweight release format while it is still a personal Codex skill and local workflow tool.

## [Unreleased]

### Added

- `menu` / `ai-menu`, a compact numbered menu for Lite setup, project recommendations, supported platforms, already-running-agent prompt text, doctor checks, and path lookup.

## [0.4.0] - 2026-05-31

### Added

- `lite` / `ai-lite`, a simplified one-command project agent bridge setup that auto-recommends targets and falls back to Codex, Claude, and OpenCode.
- `ai-lite --fix`, `--prompt`, `--undo`, and `--all-common`, plus `setup --lite` and installer `--lite` for minimal installs.
- Lite smoke coverage in CI and release validation, plus a README shortest path for minimal setup.
- German, Japanese, French, and Italian README pages, plus expanded language navigation.
- `about` command and `ayatori` / `ayatori-nexus` shell entrypoints for the Ayatori Nexus project codename.
- `agent recommend` for project-aware bridge install suggestions, plus platform support levels in `agent platforms`.
- Agent platform adapters for Amp, Devin, Junie, Zed, Kilo, GitLab Duo, Firebase Studio, Android Studio Gemini, OpenHands, Warp, and Trae.
- `agent platforms` command plus an OpenClaw platform adapter for `~/.openclaw/workspace` with `AGENTS.md` and `TOOLS.md` bridge files.
- `agent targets` and `agent detect` commands, plus Continue, Goose, and Kiro agent bridge targets.
- `agent install --detected` to install only bridge targets discovered in the current project.

## [0.3.0] - 2026-05-29

### Added

- `workspace` command and `ai-workspace` shell helper for opening several agents in one terminal workspace and switching between them with tmux or Windows Terminal tabs.
- `workspace up`, `workspace targets`, `workspace add`, `workspace next`, and `workspace prev` to reduce repeated typing in same-terminal multi-agent workflows.
- Project-local workspace targets, detailed `workspace show/status`, interactive `workspace choose`, and short shell helpers `ai-ws`, `ai-wup`, `ai-wgo`, and `ai-wpick`.
- `agent` command and `ai-agent` helper for installing Codex/Claude/OpenCode instruction bridges, so agent-side requests like `/switch claude` can run `ai-workspace switch claude`.
- Additional agent bridge targets for Gemini, Qwen Code, GitHub Copilot/VS Code, Cursor, Windsurf/Cascade, Aider, Cline, Roo Code, generic `AGENTS.md`, and custom `--file` rule paths.
- `install-bin` for POSIX executable shims on Linux, macOS, and WSL, plus default shim installation and interactive PATH setup from `install-unix` for agent-side and non-interactive shell compatibility.
- GitHub Actions CI for Windows, Linux, and macOS validation.
- One-command installers: `install.sh` for Linux/macOS/WSL and `install.ps1` for Windows PowerShell.

### Fixed

- macOS path and URL opening now prefers the native `open` command before Linux `xdg-open`.
- Session launch commands now refresh the combined memory context using the requested `--cwd`, so project memory is included when starting an agent from another directory.
- Session and workspace profile resolution now respects the requested `--cwd` when project-local profiles or aliases are present.
- Explicit profile names now take precedence over recipe aliases, so a profile named `opencode` is not shadowed by an `opencode` recipe alias.
- Empty project-local workspace targets now override global targets, allowing project resets to fall back to suggestions.
- PowerShell wrapper generation now includes the previously missing `ai-page` helper.
- PowerShell `ai-current`, `ai-status`, `ai-paths`, and `ai-list` helpers now forward optional arguments such as `--json`.
- `ai-run` now uses the same profile environment builder as shell/session launch commands and includes `AI_CLI_API_PROVIDER` and `AI_CLI_API_KIND`.
- Session lookup now resolves profile aliases, recipe aliases, and strategy names when switching, attaching, or stopping sessions.

## [0.2.0] - 2026-05-29

### Added

- `session` command for starting, listing, switching, attaching, and stopping managed AI CLI sessions.
- `handoff` command for writing shared-memory handoff notes and opening a target agent session.
- Session backends for tmux, Windows Terminal, PowerShell windows, and printable fallback launch commands.
- `ai-session` and `ai-handoff` shell helpers for PowerShell, cmd.exe, Bash/Zsh, and fish.
- README documentation for multi-agent terminal workflows.

## [0.1.0] - 2026-05-29

### Added

- Initial `cli-model-switcher` Codex skill and standalone Python CLI.
- Profile switching for Codex, Claude Code, OpenCode, Gemini CLI, local model workflows, and custom OpenAI-compatible gateways.
- Shared memory files with global, project, session, and combined context layers.
- Shell helper generation for PowerShell, cmd.exe, Bash, Zsh, fish, and Nushell-compatible environment output.
- API preset management for OpenAI, Anthropic, Gemini, Azure OpenAI, OpenRouter, DeepSeek, Ollama, LM Studio, Groq, Mistral, xAI, Together, Fireworks, DashScope, Moonshot, Zhipu, SiliconFlow, Volcengine, Cerebras, Perplexity, Novita, and custom OpenAI-compatible endpoints.
- Model registry, model aliases, and task strategies such as `code-fast`, `code-best`, `local-private`, and `cheap-long-context`.
- Recipe system for one-step profile setup, including `codex-openai`, `claude-native`, `gemini-cli`, `opencode-openrouter`, `opencode-openrouter-best`, `opencode-deepseek`, `local-ollama`, `local-lmstudio`, and `custom-gateway`.
- `setup --wizard` for guided or non-interactive first-run setup.
- `doctor --fix` for local state repair, stale wrapper refresh, bad alias cleanup, missing memory repair, and active profile validation.
- `secret audit` for scanning switcher state, project config, and memory files without printing secret values.
- Portable export/import with conflict merge policies: `overwrite`, `keep`, and `rename`.
- English README plus Simplified Chinese and Traditional Chinese README pages.

### Security

- Direct-looking API keys and tokens are refused in profile env values by default.
- Memory writes reject obvious secrets unless explicitly forced.
- Portable export refuses direct-looking secrets unless explicitly allowed.

### Validation

- Python syntax check with `py_compile`.
- Skill structure validation through `skill-creator` quick validation.
- Local smoke tests for recipes, setup wizard, wrappers, portable migration, doctor repair, and secret audit.
