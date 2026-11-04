"""Builds the India State/UT outline used by the "India in Maps" choropleths, plus the group's artwork.

Boundaries come from DataMeet's open States layer (CC BY 2.5 IN, https://github.com/datameet/maps), which
follows the Survey of India outline including Ladakh and the merged Dadra & Nagar Haveli and Daman & Diu.
The shapefile is downloaded, projected, simplified and written as compact SVG path strings to
docs/assets/maps/ (static site) and frontend/public/maps/ (React app). The artwork goes to docs/assets/ and
frontend/public/art/ next to the other scenes.

    python scripts/build_india_maps.py [path/to/Admin2]
"""
from __future__ import annotations

import html
import json
import math
import re
import struct
import sys
import tempfile
from pathlib import Path
from urllib.request import urlopen

try:
    from scripts.rbi_state_layer import canonical_state
except ImportError:  # executed directly as scripts/build_india_maps.py
    from rbi_state_layer import canonical_state

ROOT = Path(__file__).resolve().parent.parent
SOURCE_URL = "https://raw.githubusercontent.com/datameet/maps/master/States/Admin2.{ext}"
SOURCE_PAGE = "https://github.com/datameet/maps"
MAP_DIRS = [ROOT / "docs" / "assets" / "maps", ROOT / "frontend" / "public" / "maps"]
ART_DIRS = [ROOT / "docs" / "assets", ROOT / "frontend" / "public" / "art"]
WIDTH = 1000
TOLERANCE = 0.9  # output pixels
MIN_RING_AREA = 6.0  # square output pixels; smaller islands are dropped unless they are a State/UT's only land
GROUPS = [
    "Economic", "Industry Trends & Performance", "Mining & Natural Resources", "Payments & Digital Banking",
    "State Performance & Regional Health", "Public Health & Epidemiology", "Social", "Environment & Climate",
    "Agriculture & Food", "Defence & Strategic", "Crime & Security", "Judiciary & Pending Cases", "Pew Research",
    "Elections", "U.S. Elections", "Tourism & Heritage", "Air Travel & Civil Aviation", "Indian Railways",
    "Water Transport & Shipping", "Logistics & Freight", "Innovation & Technology", "Sports", "Cricket", "Hockey",
    "Football", "Lower Courts",
]


def slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def read_dbf_names(data: bytes) -> list[str]:
    count = struct.unpack("<I", data[4:8])[0]
    header, record = struct.unpack("<HH", data[8:12])
    fields, offset = [], 32
    while data[offset] != 0x0D:
        fields.append((data[offset:offset + 11].split(b"\0")[0].decode(), data[offset + 16]))
        offset += 32
    names = []
    for index in range(count):
        row = data[header + index * record + 1:header + (index + 1) * record]
        position = 0
        for name, length in fields:
            if name == "ST_NM":
                names.append(row[position:position + length].decode("latin1").strip())
            position += length
    return names


def read_shp_polygons(data: bytes) -> list[list[list[tuple[float, float]]]]:
    shapes, offset = [], 100
    while offset < len(data):
        length = struct.unpack(">i", data[offset + 4:offset + 8])[0] * 2
        body = data[offset + 8:offset + 8 + length]
        offset += 8 + length
        if struct.unpack("<i", body[:4])[0] != 5:
            shapes.append([])
            continue
        parts_count, points_count = struct.unpack("<2i", body[36:44])
        parts = list(struct.unpack(f"<{parts_count}i", body[44:44 + 4 * parts_count])) + [points_count]
        base = 44 + 4 * parts_count
        points = [struct.unpack("<2d", body[base + 16 * i:base + 16 * i + 16]) for i in range(points_count)]
        shapes.append([points[parts[i]:parts[i + 1]] for i in range(parts_count)])
    return shapes


def simplify(points: list[tuple[float, float]], tolerance: float) -> list[tuple[float, float]]:
    """Iterative Douglas-Peucker."""
    if len(points) < 4:
        return points
    keep = [False] * len(points)
    keep[0] = keep[-1] = True
    stack = [(0, len(points) - 1)]
    while stack:
        start, end = stack.pop()
        (x1, y1), (x2, y2) = points[start], points[end]
        dx, dy = x2 - x1, y2 - y1
        norm = math.hypot(dx, dy) or 1e-12
        best, index = -1.0, -1
        for i in range(start + 1, end):
            x, y = points[i]
            distance = abs(dy * (x - x1) - dx * (y - y1)) / norm if (dx or dy) else math.hypot(x - x1, y - y1)
            if distance > best:
                best, index = distance, i
        if best > tolerance:
            keep[index] = True
            stack += [(start, index), (index, end)]
    return [point for point, kept in zip(points, keep) if kept]


def ring_area(points: list[tuple[float, float]]) -> float:
    return abs(sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(points, points[1:] + points[:1]))) / 2


def project_factory(bbox: tuple[float, float, float, float]):
    min_lon, min_lat, max_lon, max_lat = bbox
    cos_mid = math.cos(math.radians((min_lat + max_lat) / 2))
    scale = WIDTH / ((max_lon - min_lon) * cos_mid)
    height = (max_lat - min_lat) * scale

    def project(lon: float, lat: float) -> tuple[float, float]:
        return (lon - min_lon) * cos_mid * scale, (max_lat - lat) * scale

    return project, math.ceil(height)


def ring_path(points: list[tuple[float, float]]) -> str:
    return "M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in points) + "Z"


def build_states(shp: bytes, dbf: bytes, tolerance: float = TOLERANCE, min_area: float = MIN_RING_AREA) -> dict:
    names = read_dbf_names(dbf)
    shapes = read_shp_polygons(shp)
    if len(names) != len(shapes):
        raise ValueError(f"Shapefile has {len(shapes)} shapes but {len(names)} names")
    bbox = struct.unpack("<4d", shp[36:68])
    project, height = project_factory(bbox)
    states = {}
    for raw_name, rings in zip(names, shapes):
        name = canonical_state(raw_name)
        if not name:
            raise ValueError(f"Unrecognised State/UT name in boundary file: {raw_name}")
        projected = [simplify([project(lon, lat) for lon, lat in ring], tolerance) for ring in rings]
        projected = [ring for ring in projected if len(ring) >= 3]
        largest = max(projected, key=ring_area)
        kept = [ring for ring in projected if ring is largest or ring_area(ring) >= min_area]
        states[name] = "".join(ring_path(ring) for ring in kept)
    return {
        "viewBox": f"0 0 {WIDTH} {height}",
        "source": "DataMeet Community Maps, States layer (Survey of India outline)",
        "sourceUrl": SOURCE_PAGE,
        "license": "CC BY 2.5 IN",
        "states": dict(sorted(states.items())),
    }


GROOVY_STYLE = """<style>
.spin{transform-box:view-box;transform-origin:600px 330px;animation:spin 80s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
.breathe{transform-box:fill-box;transform-origin:center;animation:breathe 9s ease-in-out infinite}
@keyframes breathe{50%{transform:scale(1.04)}}
.blob{transform-box:fill-box;transform-origin:center;animation:blob 14s ease-in-out infinite alternate}
@keyframes blob{to{transform:translate(26px,-18px) scale(1.12)}}
.ripple{transform-box:fill-box;transform-origin:center;animation:ripple 6s ease-out infinite}
@keyframes ripple{from{transform:scale(.4);opacity:.9}to{transform:scale(2.4);opacity:0}}
.slide{animation:slide 18s linear infinite}
@keyframes slide{to{transform:translateX(-160px)}}
.mandala{transform-box:view-box;transform-origin:600px 330px;animation:spin 140s linear infinite reverse}
.motif{transform-box:fill-box;transform-origin:center;animation:motif 11s ease-in-out infinite alternate}
@keyframes motif{from{transform:translateY(-10px) rotate(-6deg)}to{transform:translateY(12px) rotate(6deg)}}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
</style>"""


# Theme motifs drawn in a 120x120 box; `a` is the main colour, `b` the accent.
def _gear(a, b):
    teeth = "".join(f'<rect x="54" y="8" width="12" height="20" rx="3" fill="{a}" transform="rotate({i * 45} 60 60)"/>' for i in range(8))
    return f'{teeth}<circle cx="60" cy="60" r="34" fill="{a}"/><circle cx="60" cy="60" r="13" fill="{b}"/>'


def _bars(a, b):
    return ("".join(f'<rect x="{14 + i * 24}" y="{100 - h}" width="18" height="{h}" rx="3" fill="{a}"/>' for i, h in enumerate((30, 48, 40, 72)))
            + f'<path d="M12 74 L42 52 L64 60 L104 22" fill="none" stroke="{b}" stroke-width="7" stroke-linecap="round"/><path d="M90 18 L108 18 L106 36Z" fill="{b}"/>')


def _rupee(a, b):
    return (f'<circle cx="60" cy="60" r="50" fill="{a}"/><circle cx="60" cy="60" r="40" fill="none" stroke="{b}" stroke-width="3" stroke-dasharray="4 5"/>'
            f'<path d="M40 34 H82 M40 48 H82 M44 34 C70 34 74 62 44 62 L76 92" fill="none" stroke="{b}" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/>')


def _coins_phone(a, b):
    qr = "".join(f'<rect x="{52 + (i % 4) * 9}" y="{30 + (i // 4) * 9}" width="7" height="7" fill="{b}"/>' for i in range(16) if i not in (5, 10, 15))
    return (f'<rect x="44" y="14" width="52" height="92" rx="9" fill="{a}"/>{qr}<circle cx="70" cy="96" r="4" fill="{b}"/>'
            f'<ellipse cx="24" cy="92" rx="20" ry="8" fill="{b}"/><ellipse cx="24" cy="84" rx="20" ry="8" fill="{a}"/><ellipse cx="24" cy="76" rx="20" ry="8" fill="{b}"/>')


def _health(a, b):
    return (f'<path d="M44 14 H76 V44 H106 V76 H76 V106 H44 V76 H14 V44 H44Z" fill="{a}"/>'
            f'<path d="M6 64 H36 L46 40 L58 86 L70 52 L78 64 H114" fill="none" stroke="{b}" stroke-width="7" stroke-linejoin="round" stroke-linecap="round"/>')


def _people(a, b):
    return "".join(f'<circle cx="{x}" cy="{y}" r="{r * .42:.0f}" fill="{c}"/><path d="M{x - r * .8:.0f} {y + r * 1.6:.0f} Q{x} {y + r * .3:.0f} {x + r * .8:.0f} {y + r * 1.6:.0f}Z" fill="{c}"/>'
                   for x, y, r, c in ((30, 50, 26, b), (90, 50, 26, b), (60, 40, 34, a)))


def _leaf_sun(a, b):
    rays = "".join(f'<rect x="86" y="2" width="6" height="14" rx="3" fill="{b}" transform="rotate({i * 45} 89 30)"/>' for i in range(8))
    return (f'{rays}<circle cx="89" cy="30" r="14" fill="{b}"/>'
            f'<path d="M14 108 C14 50 54 26 100 30 C100 80 70 108 14 108Z" fill="{a}"/><path d="M16 106 C40 80 60 60 92 36" fill="none" stroke="{b}" stroke-width="4"/>')


def _wheat(a, b):
    grains = "".join(f'<ellipse cx="{60 + side * 10}" cy="{22 + i * 13}" rx="6" ry="11" fill="{a}" transform="rotate({side * 30} {60 + side * 10} {22 + i * 13})"/>'
                     for i in range(5) for side in (-1, 1))
    return f'<path d="M60 16 V114" stroke="{b}" stroke-width="5"/>{grains}<ellipse cx="60" cy="12" rx="5" ry="10" fill="{a}"/>'


def _shield(a, b):
    star = " ".join(f"{60 + r * math.cos(math.radians(-90 + i * 36)):.1f},{58 + r * math.sin(math.radians(-90 + i * 36)):.1f}" for i, r in enumerate([24, 10] * 5))
    return f'<path d="M60 6 L106 22 V58 C106 86 86 104 60 114 C34 104 14 86 14 58 V22Z" fill="{a}"/><polygon points="{star}" fill="{b}"/>'


def _scales(a, b):
    return (f'<path d="M60 14 V100 M36 110 H84 M18 34 H102" stroke="{a}" stroke-width="7" stroke-linecap="round"/>'
            f'<path d="M18 34 L4 70 H32Z M102 34 L88 70 H116Z" fill="none" stroke="{a}" stroke-width="3"/>'
            f'<path d="M2 70 Q18 86 34 70Z M86 70 Q102 86 118 70Z" fill="{b}"/><circle cx="60" cy="14" r="8" fill="{b}"/>')


def _gavel(a, b):
    return (f'<rect x="20" y="22" width="62" height="30" rx="7" fill="{a}" transform="rotate(-35 51 37)"/>'
            f'<rect x="50" y="48" width="12" height="62" rx="5" fill="{b}" transform="rotate(-35 56 79)"/>'
            f'<rect x="58" y="100" width="56" height="12" rx="4" fill="{a}"/>')


def _ballot(a, b):
    return (f'<rect x="14" y="52" width="92" height="58" rx="6" fill="{a}"/><rect x="38" y="58" width="44" height="7" rx="3" fill="{b}"/>'
            f'<rect x="40" y="8" width="40" height="52" rx="3" fill="#fff" transform="rotate(8 60 34)"/>'
            f'<path d="M48 32 L58 42 L74 22" fill="none" stroke="{b}" stroke-width="6" stroke-linecap="round"/>'
            f'<circle cx="60" cy="88" r="9" fill="{b}"/>')


def _speech(a, b):
    return (f'<path d="M8 18 H78 V64 H34 L18 80 V64 H8Z" fill="{a}"/><path d="M46 50 H112 V92 H102 V108 L86 92 H46Z" fill="{b}"/>'
            + "".join(f'<circle cx="{x}" cy="41" r="5" fill="{b}"/>' for x in (26, 43, 60)))


def _stars_stripes(a, b):
    stripes = "".join(f'<rect x="10" y="{20 + i * 12}" width="100" height="6" fill="{a if i % 2 else b}"/>' for i in range(7))
    return f'{stripes}<rect x="10" y="20" width="44" height="42" fill="{a}"/>' + "".join(
        f'<circle cx="{18 + (i % 3) * 14}" cy="{28 + (i // 3) * 13}" r="3" fill="#fff"/>' for i in range(9))


def _dome(a, b):
    return (f'<path d="M30 74 C30 40 60 30 60 14 C60 30 90 40 90 74Z" fill="{a}"/><rect x="24" y="74" width="72" height="36" fill="{a}"/>'
            f'<path d="M48 110 V90 Q60 74 72 90 V110Z" fill="{b}"/><path d="M8 110 V52 M112 110 V52" stroke="{a}" stroke-width="8"/>'
            f'<circle cx="8" cy="48" r="6" fill="{b}"/><circle cx="112" cy="48" r="6" fill="{b}"/><circle cx="60" cy="10" r="5" fill="{b}"/>')


def _plane(a, b):
    return (f'<path d="M10 66 L110 54 Q118 60 110 66 Z" fill="{a}"/><path d="M52 62 L30 22 H44 L76 60Z M54 64 L34 100 H48 L76 66Z" fill="{b}"/>'
            f'<path d="M14 64 L6 44 H16 L28 62Z" fill="{b}"/>')


def _train(a, b):
    return (f'<rect x="14" y="20" width="92" height="66" rx="16" fill="{a}"/><rect x="26" y="32" width="68" height="22" rx="5" fill="{b}"/>'
            f'<circle cx="34" cy="72" r="7" fill="{b}"/><circle cx="86" cy="72" r="7" fill="{b}"/>'
            f'<path d="M36 86 L20 112 M84 86 L100 112 M26 102 H94" stroke="{a}" stroke-width="6" stroke-linecap="round"/>')


def _ship(a, b):
    return (f'<path d="M8 70 H112 L96 98 H24Z" fill="{a}"/><rect x="30" y="46" width="20" height="24" fill="{b}"/><rect x="54" y="40" width="20" height="30" fill="{b}"/>'
            f'<rect x="78" y="50" width="18" height="20" fill="{a}"/><path d="M4 108 q14 -10 28 0 t28 0 t28 0 t28 0" fill="none" stroke="{b}" stroke-width="5"/>')


def _truck(a, b):
    return (f'<rect x="6" y="30" width="70" height="52" rx="4" fill="{a}"/><path d="M76 46 H98 L114 64 V82 H76Z" fill="{b}"/>'
            f'<circle cx="28" cy="88" r="11" fill="{b}"/><circle cx="94" cy="88" r="11" fill="{a}"/>'
            f'<path d="M22 30 V82 M40 30 V82 M58 30 V82" stroke="{b}" stroke-width="3" opacity=".6"/>')


def _bulb(a, b):
    rays = "".join(f'<rect x="57" y="0" width="6" height="14" rx="3" fill="{b}" transform="rotate({d} 60 48)"/>' for d in (-60, -30, 0, 30, 60))
    return (f'{rays}<circle cx="60" cy="52" r="28" fill="{a}"/><rect x="46" y="76" width="28" height="20" rx="4" fill="{a}"/>'
            f'<path d="M48 102 H72 M50 110 H70" stroke="{b}" stroke-width="6" stroke-linecap="round"/><path d="M52 60 L60 44 L68 60" fill="none" stroke="{b}" stroke-width="4"/>')


def _ball(a, b):
    return (f'<circle cx="60" cy="60" r="48" fill="{a}"/><path d="M24 30 Q60 60 24 92 M96 30 Q60 60 96 92" fill="none" stroke="{b}" stroke-width="5" stroke-dasharray="6 5"/>')


def _bat(a, b):
    return (f'<rect x="50" y="6" width="20" height="82" rx="8" fill="{a}" transform="rotate(25 60 60)"/>'
            f'<rect x="56" y="84" width="8" height="30" rx="3" fill="{b}" transform="rotate(25 60 60)"/><circle cx="22" cy="96" r="12" fill="{b}"/>')


def _stick(a, b):
    return (f'<path d="M74 8 L44 92 Q38 108 22 104 Q10 100 16 90" fill="none" stroke="{a}" stroke-width="11" stroke-linecap="round"/>'
            f'<circle cx="92" cy="98" r="10" fill="{b}"/>')


def _football(a, b):
    patches = "".join(f'<polygon points="{" ".join(f"{cx + 9 * math.cos(math.radians(-90 + k * 72)):.1f},{cy + 9 * math.sin(math.radians(-90 + k * 72)):.1f}" for k in range(5))}" fill="{b}"/>'
                      for cx, cy in ((60, 60), (60, 26), (92, 50), (80, 90), (40, 90), (28, 50)))
    return f'<circle cx="60" cy="60" r="50" fill="{a}"/>{patches}'


def _crystal(a, b):
    return (f'<path d="M60 6 L96 40 L60 114 L24 40Z" fill="{a}"/><path d="M24 40 H96 M60 6 L46 40 L60 114 L74 40Z" fill="none" stroke="{b}" stroke-width="3"/>'
            f'<path d="M88 82 L112 106 M100 74 L112 106 L80 100" stroke="{b}" stroke-width="7" stroke-linecap="round" fill="none"/>')


MOTIFS = {
    "India in Maps": _rupee, "Economic": _rupee, "Industry Trends & Performance": _gear, "Mining & Natural Resources": _crystal,
    "Payments & Digital Banking": _coins_phone, "State Performance & Regional Health": _bars,
    "Public Health & Epidemiology": _health, "Social": _people, "Environment & Climate": _leaf_sun,
    "Agriculture & Food": _wheat, "Defence & Strategic": _shield, "Crime & Security": _shield,
    "Judiciary & Pending Cases": _scales, "Lower Courts": _gavel, "Pew Research": _speech, "Elections": _ballot,
    "U.S. Elections": _stars_stripes, "Tourism & Heritage": _dome, "Air Travel & Civil Aviation": _plane,
    "Indian Railways": _train, "Water Transport & Shipping": _ship, "Logistics & Freight": _truck,
    "Innovation & Technology": _bulb, "Sports": _ball, "Cricket": _bat, "Hockey": _stick, "Football": _football,
}


def motif_layer(theme: str, colours: tuple[str, str, str, str]) -> str:
    draw = MOTIFS.get(theme, _rupee)
    spots = [(70, 70, 1.15), (1010, 60, 1.0), (980, 400, 1.3), (90, 420, 1.05), (300, 40, .7), (840, 250, .75)]
    return "".join(
        f'<g transform="translate({x} {y}) scale({s})"><g class="motif" style="animation-delay:-{i * 2}s" opacity=".85">'
        f'{draw(colours[i % 4], colours[(i + 2) % 4])}</g></g>'
        for i, (x, y, s) in enumerate(spots)
    )


def mandala(colour_a: str, colour_b: str) -> str:
    petals = "".join(
        f'<ellipse cx="600" cy="{330 - radius}" rx="{width}" ry="{length}" fill="{colour_a if i % 2 else colour_b}" '
        f'transform="rotate({i * 360 / count:.1f} 600 330)"/>'
        for radius, count, width, length in ((300, 32, 14, 34), (250, 24, 10, 22))
        for i in range(count)
    )
    dots = "".join(f'<circle cx="600" cy="{330 - 330}" r="5" fill="{colour_b}" transform="rotate({i * 7.5} 600 330)"/>' for i in range(48))
    return f'<g class="mandala" opacity=".3">{petals}{dots}<circle cx="600" cy="330" r="276" fill="none" stroke="{colour_a}" stroke-width="2" stroke-dasharray="2 8"/></g>'

# Retro palettes: background, sunburst A, sunburst B, stripe colours (4), outline, glow.
GROOVY_PALETTES = [
    ("#2b1055", "#ff9933", "#ff5e7e", ("#ffd23f", "#ff9933", "#ee4266", "#540d6e"), "#fff4d6", "#ffd23f"),
    ("#0b3d2e", "#3fb950", "#f6c344", ("#f6c344", "#f3722c", "#43aa8b", "#277da1"), "#fefae0", "#90be6d"),
    ("#1d0b3a", "#7b2ff7", "#f107a3", ("#ffbe0b", "#fb5607", "#ff006e", "#8338ec"), "#fdf0ff", "#ff006e"),
    ("#06283d", "#1fb6ff", "#ff7b54", ("#ffd56f", "#ff7b54", "#1fb6ff", "#47b5ff"), "#e8f9ff", "#ffd56f"),
    ("#3d0c11", "#d62828", "#f77f00", ("#fcbf49", "#f77f00", "#d62828", "#003049"), "#fff3e0", "#fcbf49"),
    ("#10002b", "#c77dff", "#48cae4", ("#ffd166", "#06d6a0", "#118ab2", "#ef476f"), "#f1e9ff", "#06d6a0"),
]


def groovy_art(outline: str, view_box: str, seed: int, title: str, theme: str = "India in Maps") -> str:
    background, burst_a, burst_b, stripes, ink, glow = GROOVY_PALETTES[seed % len(GROOVY_PALETTES)]
    _, _, map_w, map_h = (float(part) for part in view_box.split())
    scale = 480 / map_h
    tx, ty = 600 - map_w * scale / 2, 56
    rays = "".join(
        f'<path d="M600 330L{600 + 1400 * math.cos(math.radians(a)):.0f} {330 + 1400 * math.sin(math.radians(a)):.0f}'
        f'L{600 + 1400 * math.cos(math.radians(a + 7.5)):.0f} {330 + 1400 * math.sin(math.radians(a + 7.5)):.0f}Z" '
        f'fill="{burst_a if i % 2 else burst_b}" opacity=".2"/>'
        for i, a in enumerate(range(0 + seed * 3, 360 + seed * 3, 15))
    )
    waves = "".join(
        f'<path class="slide" d="M-40 {566 + i * 22}' + "".join(f" q40 -26 80 0 t80 0" for _ in range(20))
        + f' V700 H-40Z" fill="{stripes[i % 4]}" opacity="{0.55 + i * 0.1:.2f}"/>'
        for i in range(4)
    )
    blobs = "".join(
        f'<circle class="blob" cx="{x}" cy="{y}" r="{r}" fill="{stripes[(i + seed) % 4]}" opacity=".35" '
        f'style="animation-delay:-{i * 3}s"/>'
        for i, (x, y, r) in enumerate([(140, 140, 90), (1060, 120, 70), (1010, 420, 110), (190, 430, 60)])
    )
    dots = "".join(f'<circle cx="{x}" cy="{y}" r="2.2" fill="{ink}" opacity=".25"/>'
                   for x in range(30, 1200, 60) for y in range(30, 360, 60))
    stripe_fills = "".join(
        f'<rect x="0" y="{i * 25}" width="{map_w:.0f}" height="25" fill="{stripes[i % 4]}"/>' for i in range(int(map_h // 25) + 2)
    )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 660" preserveAspectRatio="xMidYMid slice" role="img" aria-label="{html.escape(title)}">
{GROOVY_STYLE}
<defs>
<radialGradient id="g{seed}" cx="50%" cy="50%" r="60%"><stop offset="0" stop-color="{glow}" stop-opacity=".55"/><stop offset="1" stop-color="{background}" stop-opacity="0"/></radialGradient>
<clipPath id="c{seed}"><use href="#o{seed}"/></clipPath>
<path id="o{seed}" d="{outline}"/>
</defs>
<rect width="1200" height="660" fill="{background}"/>
<g class="spin">{rays}</g>
<rect width="1200" height="660" fill="url(#g{seed})"/>
{dots}{blobs}
{mandala(burst_a, glow)}
{motif_layer(theme, stripes)}
<circle class="ripple" cx="600" cy="330" r="120" fill="none" stroke="{glow}" stroke-width="3"/>
<circle class="ripple" cx="600" cy="330" r="120" fill="none" stroke="{burst_a}" stroke-width="3" style="animation-delay:-3s"/>
<g class="breathe"><g transform="translate({tx:.1f} {ty}) scale({scale:.4f})">
<use href="#o{seed}" fill="{ink}" opacity=".18" transform="translate(14 14)"/>
<g clip-path="url(#c{seed})">{stripe_fills}</g>
<use href="#o{seed}" fill="none" stroke="{ink}" stroke-width="{2.4 / scale:.1f}" stroke-linejoin="round"/>
</g></g>
{waves}
</svg>
"""


def write_art(geometry: dict) -> list[str]:
    outline = "".join(geometry["states"].values())
    written = []
    scenes = [("india-maps", "India in Maps", "India in Maps")] + [(f"maps-{slug(name)}", f"{name} on the map", name) for name in GROUPS]
    for seed, (name, title, theme) in enumerate(scenes):
        svg = groovy_art(outline, geometry["viewBox"], seed, title, theme)
        for folder in ART_DIRS:
            folder.mkdir(parents=True, exist_ok=True)
            (folder / f"{name}.svg").write_text(svg, encoding="utf-8")
        written.append(f"{name}.svg")
    return written


def download(folder: Path) -> Path:
    for ext in ("shp", "dbf"):
        with urlopen(SOURCE_URL.format(ext=ext), timeout=120) as response:
            (folder / f"Admin2.{ext}").write_bytes(response.read())
    return folder / "Admin2"


def main(argv: list[str]) -> None:
    with tempfile.TemporaryDirectory() as temp:
        base = Path(argv[1]) if len(argv) > 1 else download(Path(temp))
        shp, dbf = base.with_suffix(".shp").read_bytes(), base.with_suffix(".dbf").read_bytes()
        geometry = build_states(shp, dbf)
        art_geometry = build_states(shp, dbf, tolerance=3.0, min_area=60.0)
    payload = json.dumps(geometry, separators=(",", ":"))
    for folder in MAP_DIRS:
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "india-states.json").write_text(payload, encoding="utf-8")
    art = write_art(art_geometry)
    print(f"{len(geometry['states'])} States/UTs, {len(payload) / 1024:.0f} KB; {len(art)} artworks")


if __name__ == "__main__":
    main(sys.argv)
