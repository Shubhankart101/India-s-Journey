import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_scripture_verses as build  # noqa: E402

TRADITIONS = {"Hindu", "Buddhist", "Jain", "Sikh"}


class ScriptureVerseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = build.build_payload()
        cls.catalog_groups = build.catalog_groups()

    def test_corpus_has_all_traditions_and_complete_fields(self):
        verses = self.payload["verses"]
        self.assertEqual({v["tradition"] for v in verses}, TRADITIONS)
        for verse in verses:
            for field in ("id", "tradition", "language", "script", "lang", "text", "source", "english"):
                self.assertTrue(str(verse[field]).strip(), f"{verse.get('id')} missing {field}")
            self.assertTrue(verse["themes"])
        self.assertEqual(len({v["id"] for v in verses}), len(verses))

    def test_every_catalog_group_has_themes_or_fallback(self):
        themes = self.payload["GROUP_THEMES"]
        for name in self.catalog_groups:
            pool = [v for v in self.payload["verses"] if set(v["themes"]) & set(themes.get(name, []))]
            self.assertTrue(pool or name not in themes, name)
            if name in themes:
                self.assertTrue(themes[name], name)

    def test_each_group_pool_spans_three_traditions(self):
        for name in self.catalog_groups:
            themes = set(self.payload["GROUP_THEMES"].get(name, []))
            pool = [v for v in self.payload["verses"] if not themes or themes & set(v["themes"])]
            self.assertGreaterEqual(len({v["tradition"] for v in pool}), 3, name)

    def test_copies_match_build_output(self):
        json_text, _ = build.render(self.payload)
        for path in build.OUTPUTS:
            self.assertEqual(path.read_text(encoding="utf-8"), json_text, path)
        self.assertEqual(json.loads(json_text)["verses"], json.loads(build.CORPUS.read_text(encoding="utf-8"))["verses"])

    def test_react_app_bundles_scripture_ui_without_legacy_static_scripts(self):
        component = (ROOT / "frontend" / "src" / "components" / "ScriptureVerse.jsx").read_text(encoding="utf-8")
        index = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")
        self.assertIn("scripture", component.lower())
        self.assertIn('src="./build/', index)
        self.assertFalse((ROOT / "docs" / "scripture-data.js").exists())
        self.assertFalse((ROOT / "docs" / "scripture.css").exists())

    def test_static_react_components_include_sourced_verses(self):
        component = (ROOT / "frontend" / "src" / "components" / "ScriptureVerse.jsx").read_text(encoding="utf-8")
        data = json.loads((ROOT / "frontend" / "src" / "data" / "scripture-verses.json").read_text(encoding="utf-8"))
        self.assertIn("picked.source", component)
        self.assertTrue(all(verse["source"].strip() for verse in data["verses"]))


if __name__ == "__main__":
    unittest.main()
