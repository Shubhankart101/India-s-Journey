"""Guards against non-ASCII text that was lost as literal '?' (e.g. "Elections ? State history" for
"Elections · State history", "1961?2024" for "1961–2024", "India?s" for "India’s", "????" for Devanagari)
or as U+FFFD / double-encoded UTF-8, in source strings, JSX text, data and docs.

Only human-readable text is inspected (string literals, JSX text, JSON string values, Markdown and template
text), so JavaScript ternaries, optional chaining and URL query strings are not flagged."""
import io
import json
import re
import tokenize
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_PARTS = {"node_modules", "dist", "build", "__pycache__", "_cache", "raw", "raw_fiscal", "epic-sources",
              "faith-sources", "journey-sources", "substack-history"}
LOST = re.compile(r"\S \? \S|\d\?\d|^\? \S|\S \?$|\?{3,}|[A-Za-z]\?(?:s|t|ll|re|ve|d)\b(?!=)|\uFFFD|\u00e0\u00a4|\u00e2\u20ac")
QUERY = re.compile(r"\?[\w.%-]+=|https?://")


def suspicious(text):
    return any(LOST.search(line) and not QUERY.search(line) for line in text.splitlines() or [text])


def iter_files(base, suffixes):
    base = ROOT / base
    paths = [base] if base.is_file() else base.rglob("*")
    for path in paths:
        if path.suffix in suffixes and path.is_file() and not SKIP_PARTS.intersection(path.relative_to(ROOT).parts):
            yield path


def _skip_string(code, i, quote):
    i += 1
    while i < len(code) and code[i] != quote and code[i] != "\n":
        i += 2 if code[i] == "\\" else 1
    return i + 1


def js_texts(code):
    """Return (offset, text) for string literals, template text and JSX text in JS/JSX source.

    Template text next to a ${...} expression is padded with "X" so "${a} ? ${b}" reads as "X ? X"."""
    out = []
    stack = []  # brace depth markers for template ${...}
    i, n, depth, last = 0, len(code), 0, ""

    def template(i, after_expr=False):
        nonlocal depth
        i += 1
        start = i
        lead = "X" if after_expr else ""
        while i < n:
            c = code[i]
            if c == "\\":
                i += 2
                continue
            if c == "`":
                out.append((start, lead + code[start:i]))
                return i + 1
            if c == "$" and code[i + 1:i + 2] == "{":
                out.append((start, lead + code[start:i] + "X"))
                stack.append(depth)
                depth += 1
                return -(i + 2)  # resume expression scanning
            i += 1
        return i

    while i < n:
        c = code[i]
        if code.startswith("//", i) and last not in ("<",):
            j = code.find("\n", i)
            i = n if j < 0 else j
            continue
        if code.startswith("/*", i):
            j = code.find("*/", i + 2)
            i = n if j < 0 else j + 2
            continue
        if c in "'\"":
            j = _skip_string(code, i, c)
            out.append((i + 1, code[i + 1:j - 1]))
            i, last = j, "s"
            continue
        if c == "`":
            r = template(i)
            if r < 0:
                i = -r
            else:
                i = r
            last = "s"
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            m = re.match(r"\}([^<>{}`\"=;()]*)(?=</)", code[i:])  # JSX text between {expr} and a closing tag
            if m and m.group(1).strip():
                out.append((i + 1, "X" + m.group(1)))
            depth -= 1
            if stack and depth == stack[-1]:
                stack.pop()
                r = template(i, after_expr=True)  # continue template after ${...}
                if r < 0:
                    i = -r
                else:
                    i, last = r, "s"
                continue
        elif c == "/" and (last in "(,=:[!&|?{};+-*%<>~^" or re.search(r"\b(?:return|typeof|case|in|of)\s*$", code[max(0, i - 12):i])):
            j = i + 1
            in_class = False
            while j < n and code[j] != "\n":
                if code[j] == "\\":
                    j += 2
                    continue
                if code[j] == "[":
                    in_class = True
                elif code[j] == "]":
                    in_class = False
                elif code[j] == "/" and not in_class:
                    break
                j += 1
            i = j + 1
            last = "r"
            continue
        elif c == ">" and i and not code[i - 1].isspace() and code[i - 1] not in "=->":
            # JSX text runs from a tag's closing '>' to the next '<' or '{' (skips '=>' and spaced comparisons)
            m = re.match(r">([^<>{}`\"=;]*)(?=[<{])", code[i:])
            if m and m.group(1).strip():
                out.append((i + 1, m.group(1)))
        if not c.isspace():
            last = c
        i += 1
    return out


def python_texts(code):
    kinds = {tokenize.STRING, getattr(tokenize, "FSTRING_MIDDLE", -1), getattr(tokenize, "TSTRING_MIDDLE", -1)}
    for tok in tokenize.generate_tokens(io.StringIO(code).readline):
        if tok.type in kinds:
            yield tok.start[0], tok.string


def json_texts(node, where=""):
    if isinstance(node, str):
        yield where, node
    elif isinstance(node, dict):
        for key, value in node.items():
            yield f"{where}/{key}", str(key)
            yield from json_texts(value, f"{where}/{key}")
    elif isinstance(node, list):
        for index, value in enumerate(node):
            yield from json_texts(value, f"{where}[{index}]")


def markup_text(code):
    code = re.sub(r"(?is)<(script|style)\b.*?</\1>", "", code)
    code = re.sub(r"(?s)\{%.*?%\}|\{\{.*?\}\}|```.*?```|`[^`\n]*`", "", code)
    return code


def test_js_sources_have_no_lost_characters():
    offenders = []
    for path in iter_files("frontend/src", {".js", ".jsx", ".mjs"}):
        code = path.read_text(encoding="utf-8")
        for offset, text in js_texts(code):
            if suspicious(text):
                offenders.append(f"{path.relative_to(ROOT)}:{code.count(chr(10), 0, offset) + 1}: {text.strip()[:80]!r}")
    for path in iter_files("scripts", {".js", ".mjs"}):
        code = path.read_text(encoding="utf-8")
        for offset, text in js_texts(code):
            if suspicious(text):
                offenders.append(f"{path.relative_to(ROOT)}:{code.count(chr(10), 0, offset) + 1}: {text.strip()[:80]!r}")
    assert not offenders, "Characters lost as '?' or mojibake:\n" + "\n".join(offenders[:30])


def test_python_sources_have_no_lost_characters():
    offenders = []
    for base in ("scripts", "webapp"):
        for path in iter_files(base, {".py"}):
            for line, text in python_texts(path.read_text(encoding="utf-8")):
                if suspicious(text):
                    offenders.append(f"{path.relative_to(ROOT)}:{line}: {text.strip()[:80]!r}")
    assert not offenders, "Characters lost as '?' or mojibake:\n" + "\n".join(offenders[:30])


def test_data_files_have_no_lost_characters():
    offenders = []
    for base in ("data", "frontend/src/data", "webapp"):
        for path in iter_files(base, {".json"}):
            node = json.loads(path.read_text(encoding="utf-8"))
            offenders += [f"{path.relative_to(ROOT)}{where}: {text[:80]!r}" for where, text in json_texts(node) if suspicious(text)]
        for path in iter_files(base, {".csv"}):
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if suspicious(line):
                    offenders.append(f"{path.relative_to(ROOT)}:{number}: {line[:80]!r}")
    assert not offenders, "Characters lost as '?' or mojibake:\n" + "\n".join(offenders[:30])


def test_docs_and_templates_have_no_lost_characters():
    offenders = []
    paths = [ROOT / "README.md", *ROOT.glob("docs/*.md"), *ROOT.glob("docs/releases/*.md"), *ROOT.glob("docs/*.html"),
             *iter_files("webapp/templates", {".html", ".txt"})]
    for path in paths:
        for number, line in enumerate(markup_text(path.read_text(encoding="utf-8")).splitlines(), 1):
            if suspicious(line):
                offenders.append(f"{path.relative_to(ROOT)}:{number}: {line.strip()[:80]!r}")
    assert not offenders, "Characters lost as '?' or mojibake:\n" + "\n".join(offenders[:30])


def test_detector_catches_known_corruptions():
    for bad in ("Elections ? India, in numbers", "1961?2024", "? All State/UT results", "Official dataset ?",
                "India?s medal", "??????? ????", "caf\uFFFD"):
        assert suspicious(bad), bad
    for good in ("What happened?", "/explore?category=economy", "Pass ?keys=a,b", "Elections · India, in numbers"):
        assert not suspicious(good), good
    texts = [text for _, text in js_texts("const a = x ? 'one' : `t ${y ? 'b' : 'c'} z`;\nconst r = /a?b/;\n"
                                          "const f = () => (x > 1 ? [1] : []);\nreturn /[\",]/.test(t) ? 'q' : t;\n"
                                          "const el = <p>Elections ? State</p>;\nconst v = `${a} ? ${b}`;\n"
                                          "const l = <a href={u}>{name} ?</a>;")]
    flagged = [t for t in texts if suspicious(t)]
    assert flagged == ["Elections ? State", "X ? X", "X ?"], flagged
