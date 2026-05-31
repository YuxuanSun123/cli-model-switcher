#!/usr/bin/env python3
"""Build or verify the standalone Codex skill module.

The repository root is a development checkout. The standalone skill module under
skill/cli-model-switcher contains only files Codex needs when this is installed
as a skill.
"""

from __future__ import annotations

import argparse
import filecmp
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "skill" / "cli-model-switcher"

SYNC_FILES = [
    ("SKILL.md", "SKILL.md"),
    ("install.ps1", "install.ps1"),
    ("install.sh", "install.sh"),
    ("agents/openai.yaml", "agents/openai.yaml"),
    ("scripts/cli_model_switcher.py", "scripts/cli_model_switcher.py"),
    ("references/linux-macos.md", "references/linux-macos.md"),
    ("references/shell-integration.md", "references/shell-integration.md"),
]


def copy_module() -> list[str]:
    written: list[str] = []
    for source_name, target_name in SYNC_FILES:
        source = ROOT / source_name
        target = MODULE / target_name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        written.append(target_name)
    return written


def check_module() -> list[str]:
    mismatches: list[str] = []
    for source_name, target_name in SYNC_FILES:
        source = ROOT / source_name
        target = MODULE / target_name
        if not target.exists() or not filecmp.cmp(source, target, shallow=False):
            mismatches.append(target_name)
    return mismatches


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail when the standalone skill module is out of sync.")
    args = parser.parse_args()

    if args.check:
        mismatches = check_module()
        if mismatches:
            print("Standalone skill module is out of sync:")
            for item in mismatches:
                print(f"- {item}")
            print("Run: python scripts/sync_skill_module.py")
            return 1
        print(f"Standalone skill module is in sync: {MODULE}")
        return 0

    written = copy_module()
    print(f"Synced standalone skill module: {MODULE}")
    for item in written:
        print(f"- {item}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
