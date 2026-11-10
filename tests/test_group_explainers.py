import json
import re
from pathlib import Path

from scripts.build_explainers import PATTERNS, build_articles

ROOT = Path(__file__).resolve().parents[1]


def test_group_explainer_outputs_cover_catalog_and_are_identical():
    catalog = json.loads((ROOT / "data" / "catalog.json").read_text(encoding="utf-8"))
    expected = build_articles(catalog)
    docs = json.loads((ROOT / "frontend" / "src" / "data" / "group-explainers.json").read_text(encoding="utf-8"))
    frontend = json.loads((ROOT / "frontend" / "src" / "data" / "group-explainers.json").read_text(encoding="utf-8"))

    assert docs == frontend == expected
    assert len(docs["groups"]) == len(catalog["categories"])
    for group_index, entry in enumerate(docs["groups"]):
        article = entry["article"]
        assert article["pattern"] == PATTERNS[group_index % len(PATTERNS)]
        assert article["indicatorCount"] == sum(item["category"] == entry["name"] for item in catalog["indicators"])
        assert len(article["subgroups"]) == len(next(item for item in catalog["categories"] if item["name"] == entry["name"])["subgroups"])
        assert all(subgroup["pattern"] != article["pattern"] for subgroup in article["subgroups"])


def test_every_group_has_a_distinct_devanagari_verse():
    docs = json.loads((ROOT / "frontend" / "src" / "data" / "group-explainers.json").read_text(encoding="utf-8"))
    verses = [entry["article"]["verse"]["text"] for entry in docs["groups"]]
    assert len(set(verses)) == len(verses)
    assert all(any("\u0900" <= ch <= "\u097f" for ch in verse) for verse in verses)


def test_explainer_markup_has_no_mojibake():
    for path in ("frontend/src/components/ExplainerArticle.jsx", "frontend/src/themes.css"):
        text = (ROOT / path).read_text(encoding="utf-8")
        assert "\ufffd" not in text, path
        assert "'??" not in text and ">??" not in text, path
    component = (ROOT / "frontend" / "src" / "components" / "ExplainerArticle.jsx").read_text(encoding="utf-8")
    assert "Topic introduction" in component


def test_explainer_sources_are_short_publisher_names():
    docs = json.loads((ROOT / "frontend" / "src" / "data" / "group-explainers.json").read_text(encoding="utf-8"))
    for entry in docs["groups"]:
        lists = [entry["article"]["sources"]] + [sub["sources"] for sub in entry["article"]["subgroups"]]
        for sources in lists:
            assert len(sources) == len({name.lower() for name in sources}), entry["name"]
            assert len(sources) <= 30, entry["name"]
            for name in sources:
                assert "http" not in name and "=" not in name and "Table " not in name, name
                assert len(name) <= 120 and (not name[0].islower() or re.fullmatch(r"[a-z0-9.-]+\.[a-z]+", name)), name


def test_subgroup_articles_include_ordered_sections_and_key_numbers():
    catalog = json.loads((ROOT / "data" / "catalog.json").read_text(encoding="utf-8"))
    articles = build_articles(catalog)
    for group in articles["groups"]:
        for subgroup in group["article"]["subgroups"]:
            keys = [key for section in subgroup["sections"] for key in section["keys"]]
            assert len(keys) == len(set(keys)), subgroup["name"]
            assert min(3, len(keys)) <= len(subgroup["sections"]) <= 6, subgroup["name"]
            assert subgroup["sections"][0]["title"] and subgroup["sections"][0]["text"]
            assert all(section["keys"] for section in subgroup["sections"])
            assert {item["label"] for item in subgroup["keyNumbers"]} == {"Indicator series", "Named publishers"}
