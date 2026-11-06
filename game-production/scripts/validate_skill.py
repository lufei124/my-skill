#!/usr/bin/env python3
"""Read-only structural checks for the game-production bundle; no LLM execution."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

REQUIRED = (
    "SKILL.md", "README.md", "CHANGELOG.md", "agents/openai.yaml", "assets/icon.svg",
    "skills/game-intent-interview/SKILL.md", "skills/gameplay-loop-design/SKILL.md",
    "references/design-methods.md", "references/mode-library.md", "references/sources.md",
    "references/planning-handoff.md", "references/testing-and-evidence.md",
    "references/engagement-and-monetization.md", "templates/decision-record.md",
    "templates/loop-design.md", "templates/experiment-plan.md", "tests/scenarios.json",
    "scripts/validate_skill.py", "tests/test_validate_skill.py",
)
EXPECTED_SKILLS = {
    "SKILL.md": "game-production",
    "skills/game-intent-interview/SKILL.md": "game-intent-interview",
    "skills/gameplay-loop-design/SKILL.md": "gameplay-loop-design",
}
LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


def validate(root: Path) -> list[str]:
    root = root.resolve()
    errors: list[str] = []
    text: dict[str, str] = {}
    for name in REQUIRED:
        path = root / name
        if not path.is_file():
            errors.append(f"Missing file: {name}")
            continue
        try:
            text[name] = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            errors.append(f"Cannot read {name}: {exc}")
    for name, skill in EXPECTED_SKILLS.items():
        value = text.get(name, "")
        match = re.match(r"\A---\n(.*?)\n---\n", value, re.S)
        if not match:
            errors.append(f"Invalid frontmatter: {name}")
            continue
        front = match.group(1)
        if not re.search(r"^name: " + re.escape(skill) + r"$", front, re.M):
            errors.append(f"Wrong skill name: {name}")
        desc = re.search(r"^description: (.+)$", front, re.M)
        try:
            parsed = json.loads(desc.group(1)) if desc else None
            if not isinstance(parsed, str) or not parsed.strip():
                raise ValueError("description must be a nonempty quoted string")
        except (ValueError, AttributeError):
            errors.append(f"Invalid description: {name}")
    for path in root.rglob("*.md"):
        if ".git" in path.parts:
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            errors.append(f"Cannot read {path.relative_to(root)}: {exc}")
            continue
        for raw in LINK.findall(content):
            url = urlsplit(raw.strip().strip("<>"))
            if url.scheme or url.netloc or not url.path:
                continue
            target = (path.parent / unquote(url.path)).resolve()
            if root != target and root not in target.parents:
                errors.append(f"External local dependency: {path.relative_to(root)} -> {raw}")
            elif not target.exists():
                errors.append(f"Broken link: {path.relative_to(root)} -> {raw}")
    patterns = re.findall(r"^## P(\d{2}) ", text.get("references/mode-library.md", ""), re.M)
    if patterns != [f"{i:02d}" for i in range(1, 14)]:
        errors.append("Pattern library must contain P01 through P13 exactly once in order")
    try:
        document = json.loads(text.get("tests/scenarios.json", ""))
        scenarios = document["scenarios"]
        if document.get("schema_version") != 1 or not isinstance(scenarios, list) or len(scenarios) < 10:
            raise ValueError("Need schema_version 1 and at least ten scenarios")
        ids: set[str] = set()
        for case in scenarios:
            if not isinstance(case, dict):
                raise ValueError("Scenario must be an object")
            for key in ("id", "prompt"):
                if not isinstance(case.get(key), str) or not case[key].strip():
                    raise ValueError(f"Missing string: {key}")
            for key in ("expected_routes", "must", "must_not"):
                values = case.get(key)
                if not isinstance(values, list) or not values or not all(isinstance(v, str) and v.strip() for v in values):
                    raise ValueError(f"Invalid list: {key}")
            if case["id"] in ids:
                raise ValueError("Duplicate scenario id")
            ids.add(case["id"])
    except (ValueError, KeyError, TypeError) as exc:
        errors.append(f"Invalid scenarios: {exc}")
    metadata = text.get("agents/openai.yaml", "")
    for key in ("display_name", "short_description", "default_prompt", "icon_small", "icon_large"):
        if not re.search(r"^  " + key + r": .+", metadata, re.M):
            errors.append(f"Missing agent metadata: {key}")
    for icon in re.findall(r"^  icon_(?:small|large): (.+)$", metadata, re.M):
        if not (root / icon.strip()).is_file():
            errors.append(f"Missing icon: {icon}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    errors = validate(args.root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("PASS: 3 skill entries, internal links, 13 patterns, metadata and scenario schema")
    print("Scope: structural validation only; LLM behavior, gameplay and platform runtime are NOT tested.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
