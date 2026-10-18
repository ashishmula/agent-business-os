"""Tester A: every file the bootstrap prompt and CLAUDE.md point at exists, and no v1 section was lost."""

import re
import unittest

from helpers import ROOT

PATH = re.compile(r"`([A-Za-z0-9_./*-]+\.(?:md|json|toml|py)|config/\*)`")


def referenced(doc: str) -> set[str]:
    return set(PATH.findall((ROOT / doc).read_text()))


class PromptFiles(unittest.TestCase):
    def assert_exist(self, doc):
        for ref in sorted(referenced(doc)):
            hits = list(ROOT.glob(ref)) if "*" in ref else [ROOT / ref] if (ROOT / ref).exists() else []
            self.assertTrue(hits, f"{doc} points at {ref}, which does not exist")

    def test_prompt_references_exist(self):
        self.assertIn("agents/governor.md", referenced("PROMPT.md"))
        self.assert_exist("PROMPT.md")

    def test_claude_md_references_exist(self):
        self.assert_exist("CLAUDE.md")

    def test_every_v1_section_was_moved(self):
        v1 = (ROOT / "prompt-source" / "PROMPT-v1-full.md").read_text()
        moved = "".join(p.read_text() for p in (ROOT / "agents").glob("*.md"))
        for heading in re.findall(r"^#{2,3} .+$", v1, flags=re.M):
            self.assertIn(heading, moved, f"v1 heading missing from agents/*.md: {heading}")

    def test_every_v1_line_was_moved_word_for_word(self):
        # P3-MUSE-04: headings alone don't prove the rules in between survived
        v1 = (ROOT / "prompt-source" / "PROMPT-v1-full.md").read_text()
        body = v1[v1.index("\n## 1. "):]
        moved = "".join(p.read_text() for p in (ROOT / "agents").glob("*.md"))
        missing = [line for line in body.splitlines() if line.strip() and line not in moved]
        self.assertEqual(missing, [], f"{len(missing)} v1 lines missing from agents/*.md")

    def test_prompt_never_names_the_current_phase(self):
        self.assertNotRegex((ROOT / "PROMPT.md").read_text(), r"\(now\)")


if __name__ == "__main__":
    unittest.main()
