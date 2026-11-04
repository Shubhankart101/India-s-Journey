"""Builds the India State/UT outline used by the "India in Maps" choropleths, plus the group's artwork.

Boundaries come from DataMeet's open States layer (CC BY 2.5 IN, https://github.com/datameet/maps), which
follows the Survey of India outline including Ladakh and the merged Dadra & Nagar Haveli and Daman & Diu.
The shapefile is downloaded, projected, simplified and written as compact SVG path strings to
docs/assets/maps/ (static site) and frontend/public/maps/ (React app). The artwork goes to docs/assets/ and
frontend/public/art/ next to the other scenes.

    python scripts/build_india_maps.py [path/to/Admin2]
"""
from __future__ import annotations

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
    "Football",
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
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
</style>"""

# Retro palettes: background, sunburst A, sunburst B, stripe colours (4), outline, glow.
GROOVY_PALETTES = [
    ("#2b1055", "#ff9933", "#ff5e7e", ("#ffd23f", "#ff9933", "#ee4266", "#540d6e"), "#fff4d6", "#ffd23f"),
    ("#0b3d2e", "#3fb950", "#f6c344", ("#f6c344", "#f3722c", "#43aa8b", "#277da1"), "#fefae0", "#90be6d"),
    ("#1d0b3a", "#7b2ff7", "#f107a3", ("#ffbe0b", "#fb5607", "#ff006e", "#8338ec"), "#fdf0ff", "#ff006e"),
    ("#06283d", "#1fb6ff", "#ff7b54", ("#ffd56f", "#ff7b54", "#1fb6ff", "#47b5ff"), "#e8f9ff", "#ffd56f"),
    ("#3d0c11", "#d62828", "#f77f00", ("#fcbf49", "#f77f00", "#d62828", "#003049"), "#fff3e0", "#fcbf49"),
    ("#10002b", "#c77dff", "#48cae4", ("#ffd166", "#06d6a0", "#118ab2", "#ef476f"), "#f1e9ff", "#06d6a0"),
]


def groovy_art(outline: str, view_box: str, seed: int, title: str) -> str:
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
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 660" preserveAspectRatio="xMidYMid slice" role="img" aria-label="{title}">
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
    scenes = [("india-maps", "India in Maps")] + [(f"maps-{slug(name)}", f"{name} on the map") for name in GROUPS]
    for seed, (name, title) in enumerate(scenes):
        svg = groovy_art(outline, geometry["viewBox"], seed, title)
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
