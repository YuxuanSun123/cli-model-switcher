#!/usr/bin/env python3
"""Smoke tests for project-aware agent recommendations and Ayatori Lite."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "cli_model_switcher.py"
FIXTURES = ROOT / "tests" / "fixtures"


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )


def run_cli_env(env: dict[str, str], *args: str) -> subprocess.CompletedProcess[str]:
    merged_env = os.environ.copy()
    merged_env.update(env)
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
        env=merged_env,
    )


def run_cli_env_no_check(env: dict[str, str], *args: str) -> subprocess.CompletedProcess[str]:
    merged_env = os.environ.copy()
    merged_env.update(env)
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        env=merged_env,
    )


def copy_fixture(name: str, parent: Path) -> Path:
    source = FIXTURES / name
    target = parent / name
    shutil.copytree(source, target, ignore=shutil.ignore_patterns(".gitkeep"))
    return target


def json_cli(*args: str) -> dict[str, object]:
    completed = run_cli(*args)
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise AssertionError(f"Expected JSON from {' '.join(args)}\nstdout:\n{completed.stdout}\nstderr:\n{completed.stderr}") from exc


def assert_targets(actual: object, expected: list[str], label: str) -> None:
    if list(actual or []) != expected:
        raise AssertionError(f"{label}: expected {expected}, got {actual}")


def assert_contains(actual: object, expected: str, label: str) -> None:
    if expected not in list(actual or []):
        raise AssertionError(f"{label}: expected {expected} in {actual}")


def test_fixture_recommendations() -> None:
    cases = {
        "empty": [],
        "github": ["copilot"],
        "cursor": ["cursor"],
        "windsurf": ["windsurf"],
        "claude": ["claude"],
    }
    with tempfile.TemporaryDirectory(prefix="ai-lite-fixtures-") as raw:
        temp = Path(raw)
        for name, expected in cases.items():
            root = copy_fixture(name, temp)
            payload = json_cli("agent", "recommend", "--dir", str(root), "--json")
            assert_targets(payload.get("install_targets"), expected, f"agent recommend {name}")

            lite = json_cli("lite", "--dir", str(root), "--dry-run", "--json")
            if expected:
                assert_targets(lite.get("targets"), expected, f"lite {name}")
                if lite.get("mode") != "recommended":
                    raise AssertionError(f"lite {name}: expected recommended mode, got {lite.get('mode')}")
            else:
                assert_targets(lite.get("targets"), ["codex", "claude", "opencode"], f"lite {name}")
                if lite.get("mode") != "fallback":
                    raise AssertionError(f"lite {name}: expected fallback mode, got {lite.get('mode')}")


def test_mixed_and_common_modes() -> None:
    with tempfile.TemporaryDirectory(prefix="ai-lite-mixed-") as raw:
        root = copy_fixture("mixed", Path(raw))
        payload = json_cli("agent", "recommend", "--dir", str(root), "--json")
        targets = payload.get("install_targets")
        for expected in ["cursor", "windsurf", "codex", "opencode", "amp", "devin", "android-studio-gemini", "openhands", "generic"]:
            assert_contains(targets, expected, "mixed recommendation targets")

        common = json_cli("lite", "--dir", str(root), "--all-common", "--dry-run", "--json")
        assert_targets(
            common.get("targets"),
            ["codex", "claude", "opencode", "gemini", "copilot", "cursor", "windsurf"],
            "lite all-common",
        )


def test_undo_preview() -> None:
    with tempfile.TemporaryDirectory(prefix="ai-lite-undo-") as raw:
        root = copy_fixture("claude", Path(raw))
        payload = json_cli("lite", "--dir", str(root), "claude", "--undo", "--dry-run", "--json")
        actions = payload.get("actions")
        if not isinstance(actions, list) or not actions:
            raise AssertionError(f"undo preview: missing actions in {payload}")
        action = actions[0].get("action") if isinstance(actions[0], dict) else None
        if action != "would-leave-unchanged":
            raise AssertionError(f"undo preview: expected would-leave-unchanged, got {action}")


def test_menu_shortcuts() -> None:
    listed = run_cli("menu", "--list").stdout
    for expected in ["lite-dry-run", "recommend", "prompt", "platforms", "report"]:
        if expected not in listed:
            raise AssertionError(f"menu --list: expected {expected!r} in output")

    prompt = run_cli("menu", "--choice", "prompt").stdout
    if "Agent switching rule" not in prompt:
        raise AssertionError("menu prompt: expected compact agent switching rule")

    with tempfile.TemporaryDirectory(prefix="ai-menu-") as raw:
        root = copy_fixture("cursor", Path(raw))
        preview = run_cli("menu", "--choice", "lite-dry-run", "--dir", str(root)).stdout
        if "Targets: cursor" not in preview or "Dry run only" not in preview:
            raise AssertionError(f"menu lite-dry-run: unexpected output\n{preview}")

        recommend = run_cli("menu", "--choice", "recommend", "--dir", str(root)).stdout
        if "Recommended agent bridge targets" not in recommend or "cursor" not in recommend:
            raise AssertionError(f"menu recommend: unexpected output\n{recommend}")


def test_readiness_report() -> None:
    with tempfile.TemporaryDirectory(prefix="ai-report-") as raw:
        home = Path(raw) / "switcher-home"
        payload = json.loads(run_cli_env({"AI_CLI_SWITCHER_HOME": str(home)}, "report", "--json").stdout)
        names = [item.get("name") for item in payload.get("profiles", [])]
        for expected in ["codex", "claude", "opencode"]:
            if expected not in names:
                raise AssertionError(f"report --json: expected profile {expected!r} in {names}")
        codex = next(item for item in payload["profiles"] if item.get("name") == "codex")
        check_names = [item.get("name") for item in codex.get("checks", [])]
        for expected in ["command", "API key", "memory"]:
            if expected not in check_names:
                raise AssertionError(f"report codex: expected check {expected!r} in {check_names}")

        one = json.loads(run_cli_env({"AI_CLI_SWITCHER_HOME": str(home)}, "report", "--profile", "codex", "--json").stdout)
        if [item.get("name") for item in one.get("profiles", [])] != ["codex"]:
            raise AssertionError(f"report --profile codex: unexpected profiles {one.get('profiles')}")


def test_policy_controls_active_use() -> None:
    with tempfile.TemporaryDirectory(prefix="ai-policy-") as raw:
        home = Path(raw) / "switcher-home"
        env = {"AI_CLI_SWITCHER_HOME": str(home)}
        run_cli_env(env, "policy", "deny", "codex")

        denied = json.loads(run_cli_env(env, "policy", "check", "codex", "--json").stdout)
        if denied.get("decision") != "deny":
            raise AssertionError(f"policy check: expected deny, got {denied}")

        blocked = run_cli_env_no_check(env, "use", "codex")
        if blocked.returncode == 0:
            raise AssertionError("policy deny: expected ai-use codex to fail")
        if "Policy denied provider 'codex'" not in (blocked.stderr + blocked.stdout):
            raise AssertionError(f"policy deny: unexpected failure\nstdout:{blocked.stdout}\nstderr:{blocked.stderr}")

        blocked_current = run_cli_env_no_check(env, "current", "--shell", "powershell")
        if blocked_current.returncode == 0:
            raise AssertionError("policy deny: expected ai-current --shell powershell to fail")

        blocked_session = run_cli_env_no_check(env, "session", "start", "codex", "--backend", "print")
        if blocked_session.returncode == 0:
            raise AssertionError("policy deny: expected ai-session start codex to fail")

        blocked_workspace = run_cli_env_no_check(env, "workspace", "start", "codex", "--backend", "print")
        if blocked_workspace.returncode == 0:
            raise AssertionError("policy deny: expected ai-workspace start codex to fail")

        run_cli_env(env, "policy", "allow", "codex")
        allowed = json.loads(run_cli_env(env, "policy", "check", "codex", "--json").stdout)
        if allowed.get("decision") != "allow":
            raise AssertionError(f"policy check: expected allow, got {allowed}")
        run_cli_env(env, "use", "codex")

        listed = json.loads(run_cli_env(env, "policy", "list", "--json").stdout)
        if len(listed.get("policies", [])) != 2:
            raise AssertionError(f"policy list: expected two rules, got {listed}")
        run_cli_env(env, "policy", "remove", "1")


def test_prompt_templates() -> None:
    with tempfile.TemporaryDirectory(prefix="ai-template-") as raw:
        home = Path(raw) / "switcher-home"
        env = {"AI_CLI_SWITCHER_HOME": str(home)}

        empty = json.loads(run_cli_env(env, "template", "list", "--json").stdout)
        if empty.get("templates") != []:
            raise AssertionError(f"template list: expected empty JSON list, got {empty}")

        run_cli_env(
            env,
            "template",
            "set",
            "handoff",
            "--description",
            "handoff prompt",
            "--system",
            "Use $style style.",
            "--prompt",
            "Handoff to $agent: $input",
            "--default",
            "agent=claude",
            "--default",
            "style=concise",
        )

        shown = json.loads(run_cli_env(env, "template", "show", "handoff", "--json").stdout)
        if shown.get("defaults", {}).get("agent") != "claude":
            raise AssertionError(f"template show: missing defaults in {shown}")

        rendered = run_cli_env(env, "template", "use", "handoff", "--input", "review this diff").stdout
        if "Use concise style." not in rendered or "Handoff to claude: review this diff" not in rendered:
            raise AssertionError(f"template use: unexpected rendering\n{rendered}")

        overridden = run_cli_env(env, "template", "use", "handoff", "--input", "continue", "--param", "agent=codex").stdout
        if "Handoff to codex: continue" not in overridden:
            raise AssertionError(f"template use --param: unexpected rendering\n{overridden}")


def test_config_explain_is_readonly() -> None:
    with tempfile.TemporaryDirectory(prefix="ai-config-") as raw:
        home = Path(raw) / "switcher-home"
        env = {"AI_CLI_SWITCHER_HOME": str(home)}
        payload = json.loads(run_cli_env(env, "config", "explain", "--profile", "codex", "--json").stdout)
        if payload.get("state", {}).get("exists") is not False:
            raise AssertionError(f"config explain: expected missing state, got {payload.get('state')}")
        if payload.get("active", {}).get("source") != "default":
            raise AssertionError(f"config explain: expected default active source, got {payload.get('active')}")
        command_source = payload.get("profile", {}).get("fields", {}).get("command", {}).get("source")
        if command_source != "default":
            raise AssertionError(f"config explain: expected default command source, got {command_source}")
        if (home / "state.json").exists():
            raise AssertionError("config explain should not create state.json")


def test_external_provider_presets() -> None:
    with tempfile.TemporaryDirectory(prefix="ai-providers-") as raw:
        home = Path(raw) / "switcher-home"
        env = {"AI_CLI_SWITCHER_HOME": str(home)}
        providers = home / "providers.d"
        providers.mkdir(parents=True)
        (providers / "company.json").write_text(
            json.dumps(
                {
                    "name": "company-ai",
                    "label": "Company AI",
                    "kind": "openai-compatible",
                    "model": "company-code",
                    "env": {
                        "OPENAI_BASE_URL": "https://gateway.example.com/v1",
                        "OPENAI_API_KEY": "${COMPANY_AI_KEY}",
                    },
                    "aliases": ["corp"],
                },
                indent=2,
            ),
            encoding="utf-8",
        )

        shown = json.loads(run_cli_env(env, "api", "show", "corp", "--json").stdout)
        if shown.get("name") != "company-ai" or not shown.get("source"):
            raise AssertionError(f"api show external alias: unexpected payload {shown}")

        providers_payload = json.loads(run_cli_env(env, "api", "providers", "--json").stdout)
        if "company-ai" not in providers_payload.get("external_presets", {}):
            raise AssertionError(f"api providers: missing company-ai in {providers_payload}")

        run_cli_env(env, "api", "apply", "company", "corp", "--command", "opencode", "--model", "company-code")
        report = json.loads(run_cli_env(env, "report", "--profile", "company", "--json").stdout)
        profile = report.get("profiles", [{}])[0]
        if profile.get("api_provider") != "company-ai":
            raise AssertionError(f"report external provider: expected company-ai, got {profile}")


def main() -> int:
    test_fixture_recommendations()
    test_mixed_and_common_modes()
    test_undo_preview()
    test_menu_shortcuts()
    test_readiness_report()
    test_policy_controls_active_use()
    test_prompt_templates()
    test_config_explain_is_readonly()
    test_external_provider_presets()
    print("Lite workflow fixtures passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
