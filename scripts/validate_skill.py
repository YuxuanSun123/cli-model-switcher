#!/usr/bin/env python3
"""Lightweight repository validation for CI.

This keeps GitHub Actions independent from a local Codex installation while
still checking the pieces that make this repository usable as a skill.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


REQUIRED_FILES = [
    "SKILL.md",
    "README.md",
    "CHANGELOG.md",
    "scripts/cli_model_switcher.py",
    "tests/test_lite_workflow.py",
    "tests/fixtures/empty/.gitkeep",
    "tests/fixtures/github/.github/.gitkeep",
    "tests/fixtures/cursor/.cursor/rules/existing.mdc",
    "tests/fixtures/windsurf/.windsurf/rules/existing.md",
    "tests/fixtures/claude/CLAUDE.md",
    "tests/fixtures/mixed/AGENTS.md",
    "docs/README.de.md",
    "docs/README.fr.md",
    "docs/README.it.md",
    "docs/README.ja.md",
    "docs/README.zh-CN.md",
    "docs/README.zh-TW.md",
    "docs/RELEASE_CHECKLIST.md",
    "references/linux-macos.md",
    "references/shell-integration.md",
]

LOCALIZED_READMES = [
    "docs/README.de.md",
    "docs/README.fr.md",
    "docs/README.it.md",
    "docs/README.ja.md",
    "docs/README.zh-CN.md",
    "docs/README.zh-TW.md",
]


def fail(message: str) -> None:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(1)


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        fail("SKILL.md must start with YAML-style frontmatter")
    end = text.find("\n---\n", 4)
    if end == -1:
        fail("SKILL.md frontmatter must be closed with ---")
    raw = text[4:end]
    data: dict[str, str] = {}
    for line in raw.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if not match:
            fail(f"unsupported frontmatter line: {line!r}")
        key, value = match.groups()
        value = value.strip().strip('"').strip("'")
        data[key] = value
    return data


def main() -> int:
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd().resolve()
    for relative in REQUIRED_FILES:
        path = root / relative
        if not path.exists():
            fail(f"required file is missing: {relative}")
        if path.is_file() and path.stat().st_size == 0:
            fail(f"required file is empty: {relative}")

    skill_text = (root / "SKILL.md").read_text(encoding="utf-8")
    frontmatter = parse_frontmatter(skill_text)
    if frontmatter.get("name") != "cli-model-switcher":
        fail("SKILL.md frontmatter name must be cli-model-switcher")
    description = frontmatter.get("description", "")
    if "command-line AI coding agents" not in description:
        fail("SKILL.md description should explain the command-line AI agent scope")

    readme = (root / "README.md").read_text(encoding="utf-8")
    for expected in [
        "install.sh",
        "install.ps1",
        "install.sh --lite",
        "Shortest Path",
        "Release Checklist",
        ".\\install.ps1 -Lite",
        "python tests/test_lite_workflow.py",
        "ai-workspace",
        "ai-lite",
        "ai-menu",
        "ai-menu --list",
        "ai-menu --choice recommend",
        "ai-report",
        "ai-report --json",
        "Reference Analysis",
        "ai-agent",
        "install-bin",
        "Ayatori Nexus",
        "ayatori",
        "ai-about",
        "ai-agent targets",
        "ai-agent detect",
        "ai-agent platforms",
        "ai-agent recommend",
        "ai-agent recommend --json",
        "setup --lite",
        "ai-lite --dry-run",
        "ai-lite --fix",
        "ai-lite --prompt",
        "ai-lite --undo",
        "ai-lite --all-common",
        "ai-agent platforms amp devin junie zed kilo",
        "ai-agent install amp devin junie zed kilo",
        "ai-agent install --detected",
        "amp",
        "devin",
        "junie",
        "zed",
        "kilo",
        "gitlab-duo",
        "firebase-studio",
        "android-studio-gemini",
        "openhands",
        "warp",
        "trae",
        "support",
        "native",
        "experimental",
        "openclaw",
        "~/.openclaw/workspace",
        "continue",
        "goose",
        "kiro",
        "README.de.md",
        "README.fr.md",
        "README.it.md",
        "README.ja.md",
        "简体中文",
        "繁體中文",
    ]:
        if expected not in readme:
            fail(f"README.md is missing expected topic: {expected}")

    for relative in LOCALIZED_READMES:
        localized = (root / relative).read_text(encoding="utf-8")
        if "Ayatori Nexus" not in localized:
            fail(f"{relative} is missing the Ayatori Nexus codename")
        for expected in ["English", "Deutsch", "Français", "Italiano", "日本語", "繁體中文"]:
            if expected not in localized:
                fail(f"{relative} is missing language navigation entry: {expected}")
        if "简体中文" not in localized and "簡體中文" not in localized:
            fail(f"{relative} is missing Simplified Chinese language navigation")
        for expected in ["setup --lite", "ai-lite", "ai-lite --fix", "ai-lite --prompt", "ai-lite --undo", "ai-agent recommend", "ai-agent platforms amp devin junie zed kilo", "ai-agent install gitlab-duo firebase-studio android-studio-gemini openhands warp trae"]:
            if expected not in localized:
                fail(f"{relative} is missing expanded agent platform command: {expected}")

    for relative in ["install.ps1", "install.sh"]:
        installer = (root / relative).read_text(encoding="utf-8")
        for expected in ["ayatori about", "ayatori status"]:
            if expected not in installer:
                fail(f"{relative} is missing installer next-step hint: {expected}")

    script = (root / "scripts" / "cli_model_switcher.py").read_text(encoding="utf-8")
    reference_analysis = (root / "docs" / "REFERENCE_ANALYSIS.md").read_text(encoding="utf-8")
    for expected in ["simonw/llm", "sigoden/aichat", "anomalyco/opencode", "ai-report"]:
        if expected not in reference_analysis:
            fail(f"REFERENCE_ANALYSIS.md is missing expected topic: {expected}")

    for command in ["about", "ayatori", "lite", "ai-lite", "menu", "ai-menu", "report", "ai-report", "--strict", "--choice", "--list", "lite-dry-run", "all_common", "--all-common", "--undo", "--prompt", "--fix", "--detected", "targets", "detect", "recommend", "platforms", "support", "native", "experimental", "amp", "devin", "junie", "zed", "kilo", "gitlab-duo", "firebase-studio", "android-studio-gemini", "openhands", "warp", "trae", "openclaw", "TOOLS.md", "continue", "goose", "kiro", "install-unix", "install-bin", "workspace", "agent", "secret"]:
        if command not in script:
            fail(f"cli_model_switcher.py is missing expected command text: {command}")

    tests = (root / "tests" / "test_lite_workflow.py").read_text(encoding="utf-8")
    for expected in ["agent", "recommend", "lite", "menu", "report", "lite-dry-run", "prompt", "--all-common", "--undo", "fixtures"]:
        if expected not in tests:
            fail(f"test_lite_workflow.py is missing expected coverage text: {expected}")

    print("Skill repository is valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
