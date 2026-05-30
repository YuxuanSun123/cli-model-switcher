# Ayatori Nexus

**Sprache:** [English](../README.md) | Deutsch | [Français](README.fr.md) | [Italiano](README.it.md) | [日本語](README.ja.md) | [简体中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md)

Ayatori Nexus ist der Projektname von CLI Model Switcher: ein lokaler Profilumschalter fuer AI-Coding-Agents in der Kommandozeile. Er hilft dir, zwischen Codex, Claude Code, OpenCode, Gemini CLI, lokalen Modellen und OpenAI-kompatiblen Gateways zu wechseln, waehrend alle Agents dieselbe neutrale Speicherschicht verwenden.

## Funktionen

- Aktive CLI-AI-Profile mit `ai-use` wechseln.
- Fertige Rezepte fuer OpenCode + OpenRouter, Claude Code, Gemini CLI, DeepSeek, Ollama und LM Studio installieren.
- Gemeinsamen Kontext ueber die neutrale Datei `AI_CLI_MEMORY` teilen.
- API-Presets fuer OpenAI, Anthropic, Gemini, OpenRouter, DeepSeek, Ollama, LM Studio, Groq, Mistral, xAI, Together, Fireworks, DashScope, Moonshot, Zhipu, SiliconFlow, Volcengine, Cerebras, Perplexity, Novita, Azure OpenAI und eigene OpenAI-kompatible Endpunkte verwalten.
- Shell-Helfer fuer PowerShell, cmd.exe, Bash, Zsh, fish und Nushell erzeugen.
- Mehrere Agents in einem Terminal-Arbeitsbereich mit `ai-workspace` oeffnen und zwischen Codex, Claude, OpenCode oder Rezeptprofilen wechseln.
- Sitzungen ueber tmux, Windows Terminal, PowerShell-Fenster oder ausdruckbare Fallback-Befehle starten und nachverfolgen.
- State und Speicher vor Export oder Migration auf offensichtliche Geheimnisse pruefen.
- Profile portabel zwischen Maschinen exportieren und importieren.

## Schnellinstallation

Linux, macOS oder WSL:

```bash
curl -fsSL https://raw.githubusercontent.com/YuxuanSun123/cli-model-switcher/main/install.sh | sh
```

Windows PowerShell:

```powershell
irm https://raw.githubusercontent.com/YuxuanSun123/cli-model-switcher/main/install.ps1 | iex
```

Die Ein-Befehl-Installer klonen oder aktualisieren das Skill unter `~/.codex/skills/cli-model-switcher`, fuehren die nicht-interaktive Einrichtung aus, installieren Shell-Helfer und richten unter Linux, macOS und WSL Shims in `~/.local/bin` ein.

Wenn du das Repository bereits geklont hast:

```powershell
.\install.ps1
```

```bash
sh install.sh
```

Manuelle Einrichtung aus dem Repository-Root:

```powershell
py -3.12 scripts\cli_model_switcher.py setup --wizard
```

```bash
python3 scripts/cli_model_switcher.py setup --wizard
```

Dry-run vor Aenderungen:

```powershell
.\install.ps1 -DryRun
```

```bash
sh install.sh --dry-run
```

Nach der Einrichtung die Shell-Konfiguration neu laden, falls der Installer dazu auffordert:

```powershell
ai-list
ai-use code-fast
ai-status
ai-recall
```

## Rezepte

Rezepte erstellen nuetzliche Profile ohne lange Befehle:

```powershell
ai-recipe list
ai-recipe show opencode-openrouter
ai-recipe install opencode-openrouter --use
ai-recipe install claude-native gemini-cli opencode-deepseek --active claude
```

Eingebaute Rezepte:

- `codex-openai`
- `claude-native`
- `gemini-cli`
- `opencode-openrouter`
- `opencode-openrouter-best`
- `opencode-deepseek`
- `local-ollama`
- `local-lmstudio`
- `custom-gateway`

## Terminal-Arbeitsbereiche

Nutze `ai-workspace`, wenn du mehrere Agents in einer Terminal-Oberflaeche offen halten moechtest.

Unter Linux, macOS oder WSL mit tmux ist das die naechste Erfahrung zu "Claude/Codex wechseln, ohne das Terminal zu verlassen":

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

In tmux waehlt `Ctrl-b w` ein Agent-Fenster, `Ctrl-b n/p` wechselt vor und zurueck, und `Ctrl-b d` trennt die Sitzung ohne die Agents zu schliessen.

Unter Windows kannst du Windows Terminal Tabs aus einem Befehl oeffnen:

```powershell
ai-workspace targets set codex claude opencode-openrouter
ai-workspace up --backend wt
ai-workspace start codex claude opencode-openrouter --backend wt
```

Wenn kein Arbeitsbereich-Backend verfuegbar ist, kannst du die genauen Startbefehle ausgeben lassen:

```powershell
ai-workspace start codex claude --backend print
```

## Wechsel aus dem Agent heraus

Sobald du in Codex, Claude oder OpenCode bist, gehoert deine Eingabe diesem Agent. Installiere die Agent-Bridge, damit Befehle wie `/switch claude` als Terminal-Wechsel verstanden werden:

```powershell
ai-agent install codex claude opencode
ai-agent install gemini qwen copilot cursor windsurf aider cline roo
ai-agent install continue goose kiro
ai-agent platforms openclaw
ai-agent install openclaw --dir ~/.openclaw/workspace
ai-agent targets
ai-agent detect
ai-agent install --detected
ai-agent install --file .my-agent-rules.md
ai-agent prompt
```

Fuehre `ai-agent install` in jedem Projekt aus, damit neue Agent-Sitzungen `AGENTS.md` und `CLAUDE.md` lesen. Fuer bereits laufende Agents einmal die Ausgabe von `ai-agent prompt` einfuegen und dann z. B. sagen:

```text
/switch claude
switch codex
next
choose
handoff claude review the current changes
```

## Sitzungen und Uebergaben

Sitzungen halten mehrere AI-CLIs offen, waehrend sie denselben Switcher-State und Speicher verwenden.

```powershell
ai-session start codex
ai-session start claude
ai-session start opencode-openrouter --backend wt
ai-session start claude --backend print --cwd C:\path\to\project
ai-session list
```

Unter Linux, macOS oder WSL mit tmux:

```bash
ai-session start codex --backend tmux --attach
ai-session start claude --backend tmux
ai-session switch claude
ai-session stop claude
```

Uebergaben werden in den gemeinsamen Speicher geschrieben:

```powershell
ai-handoff claude "Review the current Codex changes and look for regressions."
ai-handoff opencode-openrouter "Continue implementation using the shared memory context."
```

## Haeufige Befehle

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
ai-agent install codex claude opencode
ai-agent install continue goose kiro
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

## Shell-Helfer

Die Einrichtung kann Helfer automatisch installieren. Manuelle Installation:

```powershell
py -3.12 scripts\cli_model_switcher.py install-powershell --profile $PROFILE
py -3.12 scripts\cli_model_switcher.py install-cmd --dir "$env:USERPROFILE\bin\ai-cli-switcher"
```

```bash
python3 scripts/cli_model_switcher.py install-unix --shell auto
python3 scripts/cli_model_switcher.py install-unix --shell fish
python3 scripts/cli_model_switcher.py install-bin
```

Unter Linux, macOS und WSL installiert `install-unix` standardmaessig ausfuehrbare Shims wie `ai-workspace`, `ai-agent`, `ai-wup` und `ai-wgo` in `~/.local/bin`. Diese Shims sind wichtig fuer Agent-Bridge-Befehle und nicht-interaktive Shells.

## Gemeinsamer Speicher

Globale Standarddateien:

```text
~/.ai-cli-switcher/state.json
~/.ai-cli-switcher/memory/global.md
~/.ai-cli-switcher/memory/session.md
~/.ai-cli-switcher/memory/context.md
```

Projektdateien:

```text
.ai-cli-switcher.json
.ai-cli-memory.md
```

Das aktive Profil stellt die zusammengefuehrte Kontextdatei ueber `AI_CLI_MEMORY` bereit.

## Geheimnisse

Speichere API-Keys nicht direkt in Profilen. Nutze Umgebungsvariablen:

```powershell
ai-profile router --command opencode --api openrouter --api-key-env OPENROUTER_API_KEY --use
```

Vor Teilen oder Migration:

```powershell
ai-secret audit --scope all --fail
py -3.12 scripts\cli_model_switcher.py export --portable --output ai-cli-switcher-portable.json
```

## Portable Migration

Export:

```powershell
py -3.12 scripts\cli_model_switcher.py export --portable --output ai-cli-switcher-portable.json
```

Import auf einer anderen Maschine:

```powershell
py -3.12 scripts\cli_model_switcher.py import ai-cli-switcher-portable.json --merge-policy rename --active
```

## Repository-Struktur

```text
SKILL.md                         Codex skill instructions
scripts/cli_model_switcher.py    Main CLI implementation
docs/README.*.md                 Localized README pages
references/shell-integration.md  PowerShell, cmd.exe, Bash, Zsh, fish, Nushell notes
references/linux-macos.md        Linux, macOS, WSL, and Git Bash notes
agents/openai.yaml               Skill UI metadata
```

## Entwicklungspruefungen

```powershell
py -3.12 -m py_compile scripts\cli_model_switcher.py
py -3.12 scripts\validate_skill.py .
py -3.12 scripts\cli_model_switcher.py secret audit --scope all --fail
```

## Status

Dies ist ein persoenliches Codex Skill und ein eigenstaendiges Hilfsskript fuer lokale Workflow-Automatisierung.
