"""Guards against double-encoded UTF-8 (e.g. "Â·" for "·", "â€º" for "›") in published pages and source text."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MOJIBAKE = ("\u00e2\u20ac", "\u00c2\u00b7", "\u00c2\u00a0", "\u00c3\u00a2", "\u00f0\u0178")
GLOBS = ("docs/*.html", "docs/*.js", "docs/*.css", "docs/*.md", "docs/releases/*.md", "frontend/index.html",
         "frontend/src/**/*.js", "frontend/src/**/*.jsx", "frontend/src/**/*.css", "webapp/templates/**/*.html", "README.md")


def test_text_files_have_no_double_encoded_characters():
    offenders = []
    for pattern in GLOBS:
        for path in ROOT.glob(pattern):
            text = path.read_text(encoding="utf-8")
            for number, line in enumerate(text.splitlines(), 1):
                if any(marker in line for marker in MOJIBAKE):
                    offenders.append(f"{path.relative_to(ROOT)}:{number}")
    assert not offenders, f"Double-encoded UTF-8 found: {offenders[:20]}"


def test_html_pages_declare_utf8():
    for path in ROOT.glob("docs/*.html"):
        assert re.search(r"<meta\s+charset=['\"]utf-8['\"]\s*/?>", path.read_text(encoding="utf-8").lower()), path.name
