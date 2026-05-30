# Ayatori Nexus

**Lingua:** [English](../README.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | Italiano | [日本語](README.ja.md) | [简体中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md)

Ayatori Nexus è il nome di progetto di CLI Model Switcher: un gestore locale di profili per agenti di coding AI da riga di comando. Ti permette di passare tra Codex, Claude Code, OpenCode, Gemini CLI, modelli locali e gateway compatibili con OpenAI mantenendo una memoria condivisa.

## Funzionalità

- Cambiare il profilo CLI AI attivo con `ai-use`.
- Installare ricette pronte per OpenCode + OpenRouter, Claude Code, Gemini CLI, DeepSeek, Ollama e LM Studio.
- Condividere il contesto tra agenti tramite il file neutrale `AI_CLI_MEMORY`.
- Gestire preset API per OpenAI, Anthropic, Gemini, OpenRouter, DeepSeek, Ollama, LM Studio, Groq, Mistral, xAI, Together, Fireworks, DashScope, Moonshot, Zhipu, SiliconFlow, Volcengine, Cerebras, Perplexity, Novita, Azure OpenAI e endpoint personalizzati compatibili con OpenAI.
- Generare helper per PowerShell, cmd.exe, Bash, Zsh, fish e Nushell.
- Aprire più agenti in un unico workspace terminale con `ai-workspace` e passare tra Codex, Claude, OpenCode o profili ricetta.
- Avviare e tracciare sessioni tramite tmux, Windows Terminal, finestre PowerShell o comandi di fallback stampabili.
- Controllare stato e memoria per segreti evidenti prima di esportazione o migrazione.
- Esportare e importare profili in modo portabile tra macchine.

## Installazione Rapida

Linux, macOS o WSL:

```bash
curl -fsSL https://raw.githubusercontent.com/YuxuanSun123/cli-model-switcher/main/install.sh | sh
```

Windows PowerShell:

```powershell
irm https://raw.githubusercontent.com/YuxuanSun123/cli-model-switcher/main/install.ps1 | iex
```

Gli installer a comando singolo clonano o aggiornano lo skill in `~/.codex/skills/cli-model-switcher`, eseguono la configurazione non interattiva, installano gli helper shell e mantengono gli shim in `~/.local/bin` su Linux, macOS e WSL.

Se il repository è già stato clonato:

```powershell
.\install.ps1
```

```bash
sh install.sh
```

Configurazione manuale dalla radice del repository:

```powershell
py -3.12 scripts\cli_model_switcher.py setup --wizard
```

```bash
python3 scripts/cli_model_switcher.py setup --wizard
```

Prova senza scrivere file:

```powershell
.\install.ps1 -DryRun
```

```bash
sh install.sh --dry-run
```

Dopo l'installazione, ricarica il profilo shell se richiesto:

```powershell
ai-list
ai-use code-fast
ai-status
ai-recall
```

## Ricette

Le ricette creano profili utili senza comandi lunghi:

```powershell
ai-recipe list
ai-recipe show opencode-openrouter
ai-recipe install opencode-openrouter --use
ai-recipe install claude-native gemini-cli opencode-deepseek --active claude
```

Ricette integrate:

- `codex-openai`
- `claude-native`
- `gemini-cli`
- `opencode-openrouter`
- `opencode-openrouter-best`
- `opencode-deepseek`
- `local-ollama`
- `local-lmstudio`
- `custom-gateway`

## Workspace Terminale

Usa `ai-workspace` quando vuoi tenere più agenti in una sola interfaccia terminale.

Su Linux, macOS o WSL con tmux, questa è l'esperienza più vicina a "passare da Codex a Claude senza uscire dal terminale":

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

In tmux, `Ctrl-b w` sceglie la finestra dell'agente, `Ctrl-b n/p` passa avanti o indietro e `Ctrl-b d` scollega la sessione senza chiudere gli agenti.

Su Windows puoi aprire più tab di Windows Terminal con un comando:

```powershell
ai-workspace targets set codex claude opencode-openrouter
ai-workspace up --backend wt
ai-workspace start codex claude opencode-openrouter --backend wt
```

Se non è disponibile alcun backend, stampa i comandi di avvio:

```powershell
ai-workspace start codex claude --backend print
```

## Cambio Dentro L'Agent

Una volta dentro Codex, Claude o OpenCode, l'input appartiene a quell'agent. Installa il bridge per far interpretare `/switch claude` come comando di cambio terminale:

```powershell
ai-agent install codex claude opencode
ai-agent install gemini qwen copilot cursor windsurf aider cline roo
ai-agent install continue goose kiro
ai-agent targets
ai-agent detect
ai-agent install --detected
ai-agent install --file .my-agent-rules.md
ai-agent prompt
```

Esegui `ai-agent install` in ogni progetto così le nuove sessioni leggeranno `AGENTS.md` e `CLAUDE.md`. Per un agent già aperto, incolla una volta l'output di `ai-agent prompt`, poi usa:

```text
/switch claude
switch codex
next
choose
handoff claude review the current changes
```

## Sessioni e Passaggi

Le sessioni mantengono aperte più CLI AI condividendo lo stesso stato e la stessa memoria.

```powershell
ai-session start codex
ai-session start claude
ai-session start opencode-openrouter --backend wt
ai-session start claude --backend print --cwd C:\path\to\project
ai-session list
```

Su Linux, macOS o WSL con tmux:

```bash
ai-session start codex --backend tmux --attach
ai-session start claude --backend tmux
ai-session switch claude
ai-session stop claude
```

Le note di handoff vengono scritte nella memoria condivisa:

```powershell
ai-handoff claude "Review the current Codex changes and look for regressions."
ai-handoff opencode-openrouter "Continue implementation using the shared memory context."
```

## Comandi Comuni

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

## Helper Shell

La configurazione può installare automaticamente gli helper. Installazione manuale:

```powershell
py -3.12 scripts\cli_model_switcher.py install-powershell --profile $PROFILE
py -3.12 scripts\cli_model_switcher.py install-cmd --dir "$env:USERPROFILE\bin\ai-cli-switcher"
```

```bash
python3 scripts/cli_model_switcher.py install-unix --shell auto
python3 scripts/cli_model_switcher.py install-unix --shell fish
python3 scripts/cli_model_switcher.py install-bin
```

Su Linux, macOS e WSL, `install-unix` installa anche shim eseguibili come `ai-workspace`, `ai-agent`, `ai-wup` e `ai-wgo` in `~/.local/bin`. Sono utili per bridge degli agenti e shell non interattive.

## Memoria Condivisa

File globali predefiniti:

```text
~/.ai-cli-switcher/state.json
~/.ai-cli-switcher/memory/global.md
~/.ai-cli-switcher/memory/session.md
~/.ai-cli-switcher/memory/context.md
```

File locali del progetto:

```text
.ai-cli-switcher.json
.ai-cli-memory.md
```

Il profilo attivo espone il contesto combinato tramite `AI_CLI_MEMORY`.

## Segreti

Non salvare API key direttamente nei profili. Usa variabili d'ambiente:

```powershell
ai-profile router --command opencode --api openrouter --api-key-env OPENROUTER_API_KEY --use
```

Prima di condividere o migrare:

```powershell
ai-secret audit --scope all --fail
py -3.12 scripts\cli_model_switcher.py export --portable --output ai-cli-switcher-portable.json
```

## Migrazione Portabile

Export:

```powershell
py -3.12 scripts\cli_model_switcher.py export --portable --output ai-cli-switcher-portable.json
```

Import su un'altra macchina:

```powershell
py -3.12 scripts\cli_model_switcher.py import ai-cli-switcher-portable.json --merge-policy rename --active
```

## Struttura Del Repository

```text
SKILL.md                         Codex skill instructions
scripts/cli_model_switcher.py    Main CLI implementation
docs/README.*.md                 Localized README pages
references/shell-integration.md  PowerShell, cmd.exe, Bash, Zsh, fish, Nushell notes
references/linux-macos.md        Linux, macOS, WSL, and Git Bash notes
agents/openai.yaml               Skill UI metadata
```

## Verifiche Di Sviluppo

```powershell
py -3.12 -m py_compile scripts\cli_model_switcher.py
py -3.12 scripts\validate_skill.py .
py -3.12 scripts\cli_model_switcher.py secret audit --scope all --fail
```

## Stato

Questo progetto è uno skill Codex personale e uno script autonomo per automatizzare workflow locali.
