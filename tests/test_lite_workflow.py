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


def main() -> int:
    test_fixture_recommendations()
    test_mixed_and_common_modes()
    test_undo_preview()
    test_menu_shortcuts()
    test_readiness_report()
    print("Lite workflow fixtures passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
