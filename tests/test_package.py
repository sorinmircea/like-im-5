import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/like-im-5/SKILL.md"
VERSION = "0.1.0"


class PackageTest(unittest.TestCase):
    def read_json(self, relative_path):
        return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))

    def test_skill_uses_portable_frontmatter(self):
        text = SKILL.read_text(encoding="utf-8")
        frontmatter = text.split("---\n", 2)[1]
        keys = {
            line.split(":", 1)[0]
            for line in frontmatter.splitlines()
            if line and not line.startswith(" ")
        }

        self.assertEqual({"name", "description"}, keys)
        self.assertIn("name: like-im-5", frontmatter)
        self.assertIn("pull request description", frontmatter)

    def test_openai_metadata_supports_both_activation_modes(self):
        metadata = (ROOT / "skills/like-im-5/agents/openai.yaml").read_text(encoding="utf-8")

        self.assertIn("$like-im-5", metadata)
        self.assertIn("allow_implicit_invocation: true", metadata)

    def test_manifest_names_and_versions_match(self):
        paths = [
            ".codex-plugin/plugin.json",
            ".claude-plugin/plugin.json",
            "gemini-extension.json",
            "qwen-extension.json",
            "kimi.plugin.json",
            "package.json",
            "plugin.json",
        ]

        for path in paths:
            with self.subTest(path=path):
                manifest = self.read_json(path)
                self.assertEqual("like-im-5", manifest["name"])
                self.assertEqual(VERSION, manifest["version"])

    def test_manifests_use_the_canonical_skill_directory(self):
        self.assertTrue(SKILL.is_file())
        self.assertEqual("./skills/", self.read_json(".codex-plugin/plugin.json")["skills"])
        self.assertEqual("skills", self.read_json("qwen-extension.json")["skills"])
        self.assertEqual("./skills/", self.read_json("kimi.plugin.json")["skills"])
        self.assertEqual(["./skills"], self.read_json("package.json")["pi"]["skills"])

    def test_pr_sections_are_ordered(self):
        text = SKILL.read_text(encoding="utf-8")
        why = text.index("## Why")
        how = text.index("## How", why)
        proof = text.index("## Proof", how)

        self.assertLess(why, how)
        self.assertLess(how, proof)

    def test_option_comparisons_prefer_compact_tables(self):
        text = SKILL.read_text(encoding="utf-8")

        self.assertIn("one option in each row", text)
        self.assertIn("shared criteria in columns", text)
        self.assertIn("recommended option outside the table", text)

    def test_skill_cuts_repetition_and_total_length(self):
        text = SKILL.read_text(encoding="utf-8")

        self.assertIn("Say each thing once", text)
        self.assertIn("shorter than the draft", text)
        self.assertIn("6. Nothing is said twice.", text)

    def test_skill_keeps_sentences_unambiguous(self):
        text = SKILL.read_text(encoding="utf-8")

        self.assertIn("## Keep sentences unambiguous", text)
        self.assertIn("under 20 words", text)
        self.assertIn("spin up", text)
        self.assertIn("Use one name for one thing", text)
        self.assertIn("Stop when the sentence has one meaning", text)
        self.assertIn("7. No hedge became a fact", text)

    def test_readme_credits_the_sentence_rule_source(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("ASD-STE100", text)
        self.assertIn("not reproduced", text)

    def test_skill_covers_code_comments(self):
        text = SKILL.read_text(encoding="utf-8")
        frontmatter = text.split("---\n", 2)[1]

        self.assertIn("code comment", frontmatter)
        self.assertIn("docstring", frontmatter)
        self.assertIn("## Write code comments", text)
        self.assertIn("A comment is not a page", text)
        self.assertIn("Use the identifier's own name", text)

    def test_no_scaffold_placeholders_remain(self):
        for path in (SKILL, ROOT / ".codex-plugin/plugin.json", ROOT / "README.md"):
            with self.subTest(path=path):
                self.assertNotIn("[TODO:", path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
