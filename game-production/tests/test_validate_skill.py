"""Regression tests for the structural validator, not for LLM behavior."""
from __future__ import annotations

import importlib.util
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("validate_skill", ROOT / "scripts/validate_skill.py")
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class BundleChecks(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "game-production"
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))

    def test_valid_bundle(self) -> None:
        self.assertEqual([], MODULE.validate(self.root))

    def test_missing_child(self) -> None:
        (self.root / "skills/game-intent-interview/SKILL.md").unlink()
        self.assertTrue(any("Missing file" in e for e in MODULE.validate(self.root)))

    def test_broken_link(self) -> None:
        path = self.root / "README.md"
        path.write_text(path.read_text() + "\n[missing](references/missing.md)\n", encoding="utf-8")
        self.assertTrue(any("Broken link" in e for e in MODULE.validate(self.root)))

    def test_external_dependency(self) -> None:
        path = self.root / "README.md"
        path.write_text(path.read_text() + "\n[external](../other-skill/SKILL.md)\n", encoding="utf-8")
        self.assertTrue(any("External local dependency" in e for e in MODULE.validate(self.root)))

    def test_invalid_frontmatter(self) -> None:
        path = self.root / "skills/gameplay-loop-design/SKILL.md"
        path.write_text(path.read_text().replace("name: gameplay-loop-design", "name: wrong"), encoding="utf-8")
        self.assertTrue(any("Wrong skill name" in e for e in MODULE.validate(self.root)))

    def test_missing_pattern(self) -> None:
        path = self.root / "references/mode-library.md"
        path.write_text(path.read_text().replace("## P13 ", "## P14 "), encoding="utf-8")
        self.assertTrue(any("Pattern library" in e for e in MODULE.validate(self.root)))

    def test_bad_scenarios(self) -> None:
        (self.root / "tests/scenarios.json").write_text("{invalid", encoding="utf-8")
        self.assertTrue(any("Invalid scenarios" in e for e in MODULE.validate(self.root)))


if __name__ == "__main__":
    unittest.main()
