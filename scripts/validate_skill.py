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
    "scripts/sync_skill_module.py",
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
    "docs/index.html",
    "docs/styles.css",
    "docs/site.js",
    "docs/assets/ayatori-logo.svg",
    "docs/assets/ayatori-logo.png",
    "docs/assets/demo-preview.png",
    "docs/DEMO_PAGE.md",
    "docs/RELEASE_CHECKLIST.md",
    "references/linux-macos.md",
    "references/shell-integration.md",
    "skill/cli-model-switcher/SKILL.md",
    "skill/cli-model-switcher/install.ps1",
    "skill/cli-model-switcher/install.sh",
    "skill/cli-model-switcher/agents/openai.yaml",
    "skill/cli-model-switcher/scripts/cli_model_switcher.py",
    "skill/cli-model-switcher/references/linux-macos.md",
    "skill/cli-model-switcher/references/shell-integration.md",
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
    module_skill_text = (root / "skill" / "cli-model-switcher" / "SKILL.md").read_text(encoding="utf-8")
    frontmatter = parse_frontmatter(skill_text)
    module_frontmatter = parse_frontmatter(module_skill_text)
    if frontmatter.get("name") != "cli-model-switcher":
        fail("SKILL.md frontmatter name must be cli-model-switcher")
    if module_frontmatter.get("name") != "cli-model-switcher":
        fail("standalone skill module SKILL.md frontmatter name must be cli-model-switcher")
    description = frontmatter.get("description", "")
    if "command-line AI coding agents" not in description:
        fail("SKILL.md description should explain the command-line AI agent scope")
    if skill_text != module_skill_text:
        fail("standalone skill module SKILL.md is out of sync; run scripts/sync_skill_module.py")
    for relative in [
        "install.ps1",
        "install.sh",
        "agents/openai.yaml",
        "scripts/cli_model_switcher.py",
        "references/linux-macos.md",
        "references/shell-integration.md",
    ]:
        if (root / relative).read_bytes() != (root / "skill" / "cli-model-switcher" / relative).read_bytes():
            fail(f"standalone skill module file is out of sync: {relative}")
    for forbidden in ["README.md", "CHANGELOG.md", "tests", ".github"]:
        if (root / "skill" / "cli-model-switcher" / forbidden).exists():
            fail(f"standalone skill module should not include repository-only artifact: {forbidden}")

    readme = (root / "README.md").read_text(encoding="utf-8")
    for expected in [
        "install.sh",
        "install.ps1",
        "Demo Page",
        "docs/DEMO_PAGE.md",
        "github.io/cli-model-switcher",
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
        "ai-policy",
        "ai-policy deny openrouter",
        "ai-template",
        "ai-template set handoff",
        "ai-config explain",
        "ai-route",
        "ai-route set think",
        "ai-api probe",
        "ai-gateway",
        "ai-preset",
        "ai-request",
        "providers.d",
        "ai-api providers",
        "Reference Analysis",
        "Standalone Skill Module",
        "skill/cli-model-switcher",
        "sync_skill_module.py",
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
        for expected in ["setup --lite", "ai-lite", "ai-lite --fix", "ai-lite --prompt", "ai-lite --undo", "ai-agent recommend", "ai-agent platforms amp devin junie zed kilo", "ai-agent install gitlab-duo firebase-studio android-studio-gemini openhands warp trae", "ai-policy deny openrouter", "ai-template set handoff", "ai-config explain", "ai-api providers", "ai-api probe", "ai-route set think", "ai-gateway status", "ai-preset list", "ai-request summary"]:
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

    for command in ["about", "ayatori", "lite", "ai-lite", "menu", "ai-menu", "report", "ai-report", "policy", "ai-policy", "template", "ai-template", "config", "ai-config", "route", "ai-route", "gateway", "ai-gateway", "preset", "ai-preset", "request", "ai-request", "api probe", "providers.d", "api_providers_parser", "--strict", "--choice", "--list", "lite-dry-run", "all_common", "--all-common", "--undo", "--prompt", "--fix", "--detected", "targets", "detect", "recommend", "platforms", "support", "native", "experimental", "amp", "devin", "junie", "zed", "kilo", "gitlab-duo", "firebase-studio", "android-studio-gemini", "openhands", "warp", "trae", "openclaw", "TOOLS.md", "continue", "goose", "kiro", "install-unix", "install-bin", "workspace", "agent", "secret"]:
        if command not in script:
            fail(f"cli_model_switcher.py is missing expected command text: {command}")

    tests = (root / "tests" / "test_lite_workflow.py").read_text(encoding="utf-8")
    for expected in ["agent", "recommend", "lite", "menu", "report", "policy", "template", "config", "providers.d", "route", "gateway", "preset", "request", "probe", "lite-dry-run", "prompt", "--all-common", "--undo", "fixtures"]:
        if expected not in tests:
            fail(f"test_lite_workflow.py is missing expected coverage text: {expected}")

    print("Skill repository is valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
