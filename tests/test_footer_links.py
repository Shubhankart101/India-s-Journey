import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
FLY_URL = "https://india-s-journey.fly.dev/"
CONTACT_URL = "https://politypolicy.substack.com/about"
PAGES = sorted(p for p in (ROOT / "docs").glob("*.html") if "site-footer" in p.read_text(encoding="utf-8"))


def footer(path):
    match = re.search(r'<footer class="site-footer">(.*?)</footer>', path.read_text(encoding="utf-8"), re.S)
    assert match, path.name
    return match.group(1)


def test_every_static_page_has_a_footer():
    assert {p.name for p in PAGES} >= {"index.html", "explore.html", "about.html", "compare.html", "sources.html", "404.html"}


@pytest.mark.parametrize("page", PAGES, ids=lambda p: p.name)
def test_static_footer_links_fly_web_app(page):
    assert f'<a href="{FLY_URL}" rel="noopener">Web app (Fly.io)</a>' in footer(page)


@pytest.mark.parametrize("page", PAGES, ids=lambda p: p.name)
def test_static_footer_thanks_tushar_with_contact_button(page):
    html = footer(page)
    assert 'class="footer-thanks"' in html
    assert "Tushar Gupta of PolityPolicy" in html
    button = re.search(r'<a class="footer-btn" href="([^"]+)"([^>]*)>([^<]+)</a>', html)
    assert button, page.name
    href, attrs, text = button.groups()
    assert href == CONTACT_URL
    assert 'target="_blank"' in attrs and "noopener" in attrs and "aria-label=" in attrs
    assert "Contact Tushar" in text


@pytest.mark.parametrize("page", PAGES, ids=lambda p: p.name)
def test_static_footer_keeps_existing_links(page):
    html = footer(page)
    for label in ("API", "Sources", "Backup site", "Mirror", "GitHub"):
        assert f">{label}</a>" in html, label


def test_footer_button_styles_exist_for_static_and_react():
    for css in (ROOT / "docs" / "product-theme.css", ROOT / "frontend" / "src" / "styles.css"):
        text = css.read_text(encoding="utf-8")
        assert "footer-btn" in text and "footer-thanks" in text and "focus-visible" in text, css.name
        assert "prefers-reduced-motion" in text, css.name


def test_react_footer_matches_static_footer():
    config = (ROOT / "frontend" / "src" / "config.js").read_text(encoding="utf-8")
    assert f"FLY_APP_URL = '{FLY_URL}'" in config
    assert f"POLITYPOLICY_CONTACT_URL = '{CONTACT_URL}'" in config
    layout = (ROOT / "frontend" / "src" / "components" / "Layout.jsx").read_text(encoding="utf-8")
    assert "FLY_APP_URL, POLITYPOLICY_CONTACT_URL" in layout
    assert "<a href={FLY_APP_URL}" in layout and "Web app (Fly.io)" in layout
    assert 'className="footer-btn" href={POLITYPOLICY_CONTACT_URL}' in layout
    assert "Tushar Gupta of PolityPolicy" in layout
