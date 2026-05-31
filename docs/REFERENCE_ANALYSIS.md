# Reference Analysis

This project was compared against three open source CLI AI tools on 2026-05-31. The code was cloned locally for structural review only; no implementation code was copied.

## Reviewed Projects

| Project | Local commit reviewed | License observed | Relevant ideas |
| --- | --- | --- | --- |
| [simonw/llm](https://github.com/simonw/llm) | `be27b91` | Apache-2.0 | Model/alias visibility, prompt templates, plugin-discovered models, JSON-friendly CLI surfaces. |
| [sigoden/aichat](https://github.com/sigoden/aichat) | `82976d3` | MIT or Apache-2.0 dual license | Config examples, env overlays, role/session prelude, shell integrations, sysinfo-style diagnostics. |
| [anomalyco/opencode](https://github.com/anomalyco/opencode) | `1afa9e3` | MIT | Agent modes, provider/model catalog thinking, provider availability, policy separation, permission-oriented agent setup. |

## Findings

### LLM

- Strong separation between model aliases, default model selection, templates, and plugins keeps commands discoverable.
- The CLI exposes path/show/list commands for opaque local files, which makes support and debugging simpler.
- Useful pattern for this project: report both raw configured model and resolved capability metadata.

### AIChat

- Config is explicit and example-driven, with comments documenting env overrides and mode-specific prelude behavior.
- Session/role metadata is surfaced through interactive commands and sysinfo-like outputs.
- Useful pattern for this project: provide a single diagnostic report that users can paste into an issue without exposing secrets.

### OpenCode

- Provider configuration, provider policy, agents, and permissions are treated as separate concepts.
- Provider/model availability is derived from environment, config, auth, and catalog state rather than assumed from a single config entry.
- Useful pattern for this project: separate "configured" from "usable" when reporting profiles.

## Changes Applied Here

- Added `report` / `ai-report` as a readiness matrix for all profiles or one profile.
- The report checks command lookup, API preset metadata, base URL validity, API key env references, memory path presence, and local model capability metadata.
- JSON output is available for automation, and `--strict` exits non-zero when any profile has warnings or failures.
- The report intentionally avoids printing secret values; it only reports env var names and availability.
- Added `policy` / `ai-policy` for provider allow/deny rules inspired by OpenCode's provider policy separation.
- Added `template` / `ai-template` for reusable prompt and handoff text inspired by LLM templates and AIChat role prelude patterns.
- Added `config explain` / `ai-config explain` for sysinfo-style diagnostics that identify project, global, default, and environment sources.
- Added `providers.d/*.json` external API presets so teams can extend the provider catalog without editing the core script.

## Router/Gateway Follow-Up Review

A later pass also reviewed router and gateway-oriented projects for workflow patterns: `musistudio/claude-code-router`, `jedarden/CLASP`, `nielspeter/claude-code-proxy`, `opendev-to/opendev`, `NadirRouter/NadirClaw`, `inflaborg/ccrelay`, Relay Switch, and `Gitlawb/openclaude`.

Useful ideas from that pass:

- Route by task slot rather than forcing users to remember provider/model pairs.
- Keep provider preset packages installable and shareable.
- Cache model capability probes instead of assuming the configured model is usable.
- Treat local gateways/proxies as first-class process/env targets.
- Keep request telemetry available for future cost, latency, and fallback reports.

Changes applied here:

- Added `route` / `ai-route` task slots for `fast`, `think`, `long`, `cheap`, `local`, `critique`, and custom slots.
- Added `api probe` for local registry and optional `/models` capability checks.
- Added `gateway` / `ai-gateway` for gateway metadata, env export, process status, and logs.
- Added `preset` / `ai-preset` for provider preset manifest install/export.
- Added `request` / `ai-request` for local NDJSON telemetry logs and summaries.

## Follow-Up Candidates

- Add an optional model-catalog sync command inspired by AIChat's `models.yaml` update flow.
- Add structured issue-report export that redacts local paths and env details more aggressively.
- Add a real reverse-proxy gateway mode once the profile/router layer is stable.
