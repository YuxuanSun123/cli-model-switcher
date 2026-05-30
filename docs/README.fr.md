# Ayatori Nexus

**Langue :** [English](../README.md) | [Deutsch](README.de.md) | Français | [Italiano](README.it.md) | [日本語](README.ja.md) | [简体中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md)

Ayatori Nexus est le nom de projet de CLI Model Switcher : un gestionnaire local de profils pour les agents de codage IA en ligne de commande. Il permet de passer entre Codex, Claude Code, OpenCode, Gemini CLI, des modèles locaux et des passerelles compatibles OpenAI, tout en conservant une couche de mémoire partagée.

## Fonctionnalités

- Changer le profil IA actif avec `ai-use`.
- Installer des recettes prêtes à l'emploi pour OpenCode + OpenRouter, Claude Code, Gemini CLI, DeepSeek, Ollama et LM Studio.
- Partager le contexte entre agents via le fichier neutre `AI_CLI_MEMORY`.
- Gérer des préréglages API pour OpenAI, Anthropic, Gemini, OpenRouter, DeepSeek, Ollama, LM Studio, Groq, Mistral, xAI, Together, Fireworks, DashScope, Moonshot, Zhipu, SiliconFlow, Volcengine, Cerebras, Perplexity, Novita, Azure OpenAI et des points d'accès compatibles OpenAI.
- Générer des raccourcis pour PowerShell, cmd.exe, Bash, Zsh, fish et Nushell.
- Ouvrir plusieurs agents dans un même espace terminal avec `ai-workspace`, puis basculer entre Codex, Claude, OpenCode ou des profils de recette.
- Démarrer et suivre des sessions via tmux, Windows Terminal, des fenêtres PowerShell ou des commandes de secours imprimables.
- Auditer l'état et la mémoire pour détecter des secrets évidents avant export ou migration.
- Exporter et importer les profils de manière portable entre machines.

## Installation Rapide

Linux, macOS ou WSL :

```bash
curl -fsSL https://raw.githubusercontent.com/YuxuanSun123/cli-model-switcher/main/install.sh | sh
```

Windows PowerShell :

```powershell
irm https://raw.githubusercontent.com/YuxuanSun123/cli-model-switcher/main/install.ps1 | iex
```

Les installateurs en une commande clonent ou mettent à jour le skill dans `~/.codex/skills/cli-model-switcher`, exécutent la configuration non interactive, installent les raccourcis shell et maintiennent les shims `~/.local/bin` sous Linux, macOS et WSL.

Si le dépôt est déjà cloné :

```powershell
.\install.ps1
```

```bash
sh install.sh
```

Configuration manuelle depuis la racine du dépôt :

```powershell
py -3.12 scripts\cli_model_switcher.py setup --wizard
```

```bash
python3 scripts/cli_model_switcher.py setup --wizard
```

Tester l'installation sans écrire de fichiers :

```powershell
.\install.ps1 -DryRun
```

```bash
sh install.sh --dry-run
```

Après l'installation, rechargez le profil shell si l'installateur le demande :

```powershell
ai-list
ai-use code-fast
ai-status
ai-recall
```

## Recettes

Les recettes créent des profils utiles sans longues commandes :

```powershell
ai-recipe list
ai-recipe show opencode-openrouter
ai-recipe install opencode-openrouter --use
ai-recipe install claude-native gemini-cli opencode-deepseek --active claude
```

Recettes intégrées :

- `codex-openai`
- `claude-native`
- `gemini-cli`
- `opencode-openrouter`
- `opencode-openrouter-best`
- `opencode-deepseek`
- `local-ollama`
- `local-lmstudio`
- `custom-gateway`

## Espaces Terminal

Utilisez `ai-workspace` pour garder plusieurs agents dans une seule interface terminal.

Sous Linux, macOS ou WSL avec tmux, c'est l'expérience la plus proche de "passer de Codex à Claude sans quitter le terminal" :

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

Dans tmux, `Ctrl-b w` choisit une fenêtre d'agent, `Ctrl-b n/p` passe à la suivante ou précédente, et `Ctrl-b d` détache la session sans fermer les agents.

Sous Windows, Windows Terminal peut ouvrir plusieurs onglets depuis une commande :

```powershell
ai-workspace targets set codex claude opencode-openrouter
ai-workspace up --backend wt
ai-workspace start codex claude opencode-openrouter --backend wt
```

Si aucun backend n'est disponible, imprimez les commandes de lancement :

```powershell
ai-workspace start codex claude --backend print
```

## Bascule Depuis Un Agent

Une fois dans Codex, Claude ou OpenCode, votre saisie appartient à cet agent. Installez le pont d'agent pour que `/switch claude` soit compris comme une commande de changement de terminal :

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

Exécutez `ai-agent install` dans chaque projet afin que les nouvelles sessions lisent `AGENTS.md` et `CLAUDE.md`. Pour un agent déjà lancé, collez une fois la sortie de `ai-agent prompt`, puis utilisez :

```text
/switch claude
switch codex
next
choose
handoff claude review the current changes
```

## Sessions et Passages de Relais

Les sessions gardent plusieurs CLI IA ouvertes tout en partageant le même état et la même mémoire.

```powershell
ai-session start codex
ai-session start claude
ai-session start opencode-openrouter --backend wt
ai-session start claude --backend print --cwd C:\path\to\project
ai-session list
```

Sous Linux, macOS ou WSL avec tmux :

```bash
ai-session start codex --backend tmux --attach
ai-session start claude --backend tmux
ai-session switch claude
ai-session stop claude
```

Les notes de relais sont écrites dans la mémoire partagée :

```powershell
ai-handoff claude "Review the current Codex changes and look for regressions."
ai-handoff opencode-openrouter "Continue implementation using the shared memory context."
```

## Commandes Courantes

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

## Raccourcis Shell

La commande de configuration peut installer les raccourcis automatiquement. Installation manuelle :

```powershell
py -3.12 scripts\cli_model_switcher.py install-powershell --profile $PROFILE
py -3.12 scripts\cli_model_switcher.py install-cmd --dir "$env:USERPROFILE\bin\ai-cli-switcher"
```

```bash
python3 scripts/cli_model_switcher.py install-unix --shell auto
python3 scripts/cli_model_switcher.py install-unix --shell fish
python3 scripts/cli_model_switcher.py install-bin
```

Sous Linux, macOS et WSL, `install-unix` installe aussi des shims exécutables comme `ai-workspace`, `ai-agent`, `ai-wup` et `ai-wgo` dans `~/.local/bin`. Ces shims sont utiles pour les ponts d'agent et les shells non interactifs.

## Mémoire Partagée

Fichiers globaux par défaut :

```text
~/.ai-cli-switcher/state.json
~/.ai-cli-switcher/memory/global.md
~/.ai-cli-switcher/memory/session.md
~/.ai-cli-switcher/memory/context.md
```

Fichiers locaux au projet :

```text
.ai-cli-switcher.json
.ai-cli-memory.md
```

Le profil actif expose le contexte fusionné via `AI_CLI_MEMORY`.

## Secrets

Ne stockez pas les clés API directement dans les profils. Utilisez des variables d'environnement :

```powershell
ai-profile router --command opencode --api openrouter --api-key-env OPENROUTER_API_KEY --use
```

Avant partage ou migration :

```powershell
ai-secret audit --scope all --fail
py -3.12 scripts\cli_model_switcher.py export --portable --output ai-cli-switcher-portable.json
```

## Migration Portable

Export :

```powershell
py -3.12 scripts\cli_model_switcher.py export --portable --output ai-cli-switcher-portable.json
```

Import sur une autre machine :

```powershell
py -3.12 scripts\cli_model_switcher.py import ai-cli-switcher-portable.json --merge-policy rename --active
```

## Structure Du Dépôt

```text
SKILL.md                         Codex skill instructions
scripts/cli_model_switcher.py    Main CLI implementation
docs/README.*.md                 Localized README pages
references/shell-integration.md  PowerShell, cmd.exe, Bash, Zsh, fish, Nushell notes
references/linux-macos.md        Linux, macOS, WSL, and Git Bash notes
agents/openai.yaml               Skill UI metadata
```

## Vérifications De Développement

```powershell
py -3.12 -m py_compile scripts\cli_model_switcher.py
py -3.12 scripts\validate_skill.py .
py -3.12 scripts\cli_model_switcher.py secret audit --scope all --fail
```

## Statut

Ce projet est un skill Codex personnel et un script autonome pour automatiser des workflows locaux.
