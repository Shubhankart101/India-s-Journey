from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEB_APP = "https://indias-journey.onrender.com/"
CONTACT_URL = "https://politypolicy.substack.com/about"


def test_react_footer_keeps_project_links_and_thanks():
    layout = (ROOT / "frontend" / "src" / "components" / "Layout.jsx").read_text(encoding="utf-8")
    config = (ROOT / "frontend" / "src" / "config.js").read_text(encoding="utf-8")
    assert f"export const WEB_APP_URL = '{WEB_APP}'" in config
    assert f"POLITYPOLICY_CONTACT_URL = '{CONTACT_URL}'" in config
    assert "WEB_APP_URL, POLITYPOLICY_CONTACT_URL" in layout
    assert "Web app (Render)" in layout and "Tushar Gupta of PolityPolicy" in layout
    for label in ("API", "Sources", "Backup site", "Mirror", "GitHub"):
        assert label in layout


def test_shared_footer_styles_are_in_react_stylesheet():
    css = (ROOT / "frontend" / "src" / "styles.css").read_text(encoding="utf-8")
    assert "footer-btn" in css and "footer-thanks" in css and "focus-visible" in css
    assert "prefers-reduced-motion" in css


def test_static_build_loads_the_same_react_layout():
    index = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")
    assert 'src="./build/' in index
    assert (ROOT / "docs" / "build").is_dir()
