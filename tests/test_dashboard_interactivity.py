import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_static_build_uses_relative_bundle_assets_and_hash_routing():
    index = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")
    main = (ROOT / "frontend" / "src" / "main.jsx").read_text(encoding="utf-8")
    assert 'src="./build/' in index and 'href="./build/' in index
    assert "HashRouter" in main and "VITE_STATIC === '1'" in main


def test_static_api_exports_filters_search_details_and_articles():
    api_dir = ROOT / "docs" / "api"
    categories = json.loads((api_dir / "categories.json").read_text(encoding="utf-8"))
    indicators = json.loads((api_dir / "indicators.json").read_text(encoding="utf-8"))
    articles = json.loads((api_dir / "articles.json").read_text(encoding="utf-8"))
    search = json.loads((api_dir / "search-index.json").read_text(encoding="utf-8"))
    stats = json.loads((api_dir / "stats.json").read_text(encoding="utf-8"))
    assert len(categories) == stats["categories"]
    assert len(indicators) == stats["indicators"]
    assert len(articles) == stats["articles"]
    assert len(search) == len(indicators)
    record = next(item for item in indicators if item["key"] == "gdp_growth")
    assert record["series"]["labels"] and record["series"]["datasets"]
    assert dict(search)["gdp_growth"].find("real gdp growth") >= 0


def test_static_app_uses_same_api_shapes_and_legacy_urls_redirect():
    client = (ROOT / "frontend" / "src" / "api.js").read_text(encoding="utf-8")
    redirect = (ROOT / "docs" / "legacy-redirect.js").read_text(encoding="utf-8")
    for route in ("stats", "categories", "indicators", "compare", "articles"):
        assert f"/api/{route}/" in client
    assert "staticRequest" in client and "apiPage" in client and "searchIndex" in client
    for page in ("explore", "indicator", "compare", "sources", "about"):
        html = (ROOT / "docs" / f"{page}.html").read_text(encoding="utf-8")
        assert "legacy-redirect.js" in html
    aliases = json.loads((ROOT / "docs" / "api" / "legacy-aliases.json").read_text(encoding="utf-8"))
    assert aliases["groups"]["Economic"]["group"] == "Economy & Markets"
    assert "#/indicator/" in redirect and "#/compare" in redirect
