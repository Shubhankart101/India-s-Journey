import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "frontend/src/data/group-explainers.json").read_text(encoding="utf-8"))
CATALOG = json.loads((ROOT / "data/catalog.json").read_text(encoding="utf-8"))


def subgroups():
    for group in DATA["groups"]:
        for sub in group["article"]["subgroups"]:
            yield group, sub


def test_every_subgroup_has_clean_sections():
    count = 0
    for group, sub in subgroups():
        count += 1
        sections = sub["sections"]
        keys = [key for section in sections for key in section["keys"]]
        assert len(keys) == len(set(keys)), sub.get("name")
        assert min(3, len(keys)) <= len(sections) <= 6, sub.get("name")
        for section in sections:
            assert section["title"].strip() and section["text"].strip()
            assert 1 <= len(section["keys"]) <= 5
            assert "?" not in section["title"] and "\ufffd" not in section["text"]
        assert sub["format"] in ("article", "map")
    assert count >= 100