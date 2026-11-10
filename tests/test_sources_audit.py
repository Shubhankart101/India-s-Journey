import json
from pathlib import Path

from scripts.audit_sources import audit_catalog

ROOT = Path(__file__).resolve().parents[1]


def _item(**overrides):
    item = {
        "key": "gdp_growth",
        "title": "Real GDP growth",
        "source_url": "https://data.worldbank.org/indicator/NY.GDP.MKTP.KD.ZG?locations=IN",
        "details": "Sourced from the World Bank indicator NY.GDP.MKTP.KD.ZG.",
        "series": {"source": "World Bank API NY.GDP.MKTP.KD.ZG"},
    }
    item.update(overrides)
    return item


def _codes(*items):
    return {error["code"] for error in audit_catalog({"indicators": list(items)})["errors"]}


def test_published_catalog_sources_are_clean():
    catalog = json.loads((ROOT / "data" / "catalog.json").read_text(encoding="utf-8"))
    report = audit_catalog(catalog)
    assert report["errors"] == [], report["summary"]


def test_clean_item_passes():
    assert _codes(_item()) == set()


def test_audit_flags_bad_urls_and_mismatches():
    assert "invalid_source_url" in _codes(_item(source_url="World Bank API NY.GDP.MKTP.KD.ZG"))
    assert "world_bank_code_mismatch" in _codes(_item(source_url="https://data.worldbank.org/indicator/SP.POP.TOTL"))
    assert "publisher_host_mismatch" in _codes(_item(source_url="https://example.com/data"))
    assert "doubled_github_url" in _codes(_item(source_url="https://github.com/https://github.com/a/b"))
    assert "blank_source" in _codes(_item(series={"source": ""}))
    assert "duplicate_key" in _codes(_item(), _item())
