"""Builds frontend/public/maps/world-asia.json: a simplified Mercator basemap of Europe, Africa, Asia and Australasia.

Countries come from Natural Earth 1:50m (public domain, naturalearthdata.com). India is drawn from the Survey of India
outline already used by the India maps (frontend/public/maps/india-states.json) so the national boundary matches the rest
of the site. Coordinates are Mercator with K units per degree of longitude; scripts and the browser share project().

    python scripts/build_world_basemap.py
"""
from __future__ import annotations

import json
import math
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "data" / "journey-sources" / "_cache"
NE_URL = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_50m_admin_0_countries.geojson"
INDIA = ROOT / "frontend" / "public" / "maps" / "india-states.json"
OUT = ROOT / "frontend" / "public" / "maps" / "world-asia.json"
COPIES = []
K = 10
LON_RANGE = (-20.0, 160.0)
LAT_RANGE = (-15.0, 66.0)
TOLERANCE = 0.05
MIN_AREA = 0.35  # square degrees; drops specks but keeps Sri Lanka, Japan, Britain and Cyprus
INDIA_BBOX = (68.09347709896305, 6.75436793493344, 97.41149826167937, 37.07761064660468)
INDIA_WIDTH = 1000


def mercator(lon: float, lat: float) -> tuple[float, float]:
    return lon * K, -math.degrees(math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))) * K


def load_ne() -> dict:
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / "ne_50m_admin_0_countries.geojson"
    if not path.exists():
        subprocess.run(["curl.exe", "-s", "-L", "--fail", "-o", str(path), NE_URL], check=True)
    return json.loads(path.read_text(encoding="utf-8"))


def perpendicular(point, start, end) -> float:
    (x, y), (x1, y1), (x2, y2) = point, start, end
    dx, dy = x2 - x1, y2 - y1
    if dx == dy == 0:
        return math.hypot(x - x1, y - y1)
    t = max(0.0, min(1.0, ((x - x1) * dx + (y - y1) * dy) / (dx * dx + dy * dy)))
    return math.hypot(x - (x1 + t * dx), y - (y1 + t * dy))


def simplify(points: list, tolerance: float) -> list:
    if len(points) < 3:
        return points
    keep = [False] * len(points)
    keep[0] = keep[-1] = True
    stack = [(0, len(points) - 1)]
    while stack:
        a, b = stack.pop()
        far, index = 0.0, -1
        for i in range(a + 1, b):
            d = perpendicular(points[i], points[a], points[b])
            if d > far:
                far, index = d, i
        if far > tolerance and index > 0:
            keep[index] = True
            stack.extend([(a, index), (index, b)])
    return [p for p, k in zip(points, keep) if k]


def area(ring: list) -> float:
    return abs(sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(ring, ring[1:] + ring[:1]))) / 2


def ring_path(ring: list) -> str:
    clamped = [(min(max(lon, LON_RANGE[0]), LON_RANGE[1]), min(max(lat, LAT_RANGE[0]), LAT_RANGE[1])) for lon, lat in ring]
    pts = [mercator(*p) for p in simplify(clamped, TOLERANCE)]
    if len(pts) < 3:
        return ""
    return "M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + "Z"


def india_path() -> str:
    min_lon, min_lat, max_lon, max_lat = INDIA_BBOX
    cos_mid = math.cos(math.radians((min_lat + max_lat) / 2))
    scale = INDIA_WIDTH / ((max_lon - min_lon) * cos_mid)
    states = json.loads(INDIA.read_text(encoding="utf-8"))["states"]
    out = []
    for d in states.values():
        for sub in re.findall(r"M[^Z]+Z", d):
            pts = []
            for pair in re.findall(r"(-?\d+\.?\d*),(-?\d+\.?\d*)", sub):
                x, y = float(pair[0]), float(pair[1])
                lon = x / (cos_mid * scale) + min_lon
                lat = max_lat - y / scale
                pts.append(mercator(lon, lat))
            if len(pts) > 2:
                out.append("M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + "Z")
    return "".join(out)


def build() -> dict:
    paths = []
    for feature in load_ne()["features"]:
        props = feature["properties"]
        name = props.get("NAME") or props.get("ADMIN")
        iso = props.get("ISO_A3") or ""
        if name == "India":
            continue
        geometry = feature["geometry"]
        polygons = geometry["coordinates"] if geometry["type"] == "MultiPolygon" else [geometry["coordinates"]]
        parts = []
        for polygon in polygons:
            ring = polygon[0]
            lons = [p[0] for p in ring]
            lats = [p[1] for p in ring]
            if max(lons) < LON_RANGE[0] or min(lons) > LON_RANGE[1] or max(lats) < LAT_RANGE[0] or min(lats) > LAT_RANGE[1]:
                continue
            if area(ring) < MIN_AREA:
                continue
            parts.append(ring_path(ring))
        d = "".join(part for part in parts if part)
        if d:
            paths.append({"n": name, "i": iso, "d": d})
    paths.append({"n": "India", "i": "IND", "d": india_path()})
    return {
        "k": K,
        "source": "Natural Earth 1:50m countries (public domain); India from the Survey of India outline used across this site",
        "sourceUrl": "https://www.naturalearthdata.com/downloads/50m-cultural-vectors/50m-admin-0-countries-2/",
        "license": "Public domain",
        "note": "Borders are a cartographic convention for orientation, not an authority on boundaries.",
        "paths": paths,
    }


def main() -> None:
    data = build()
    text = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    OUT.write_text(text, encoding="utf-8")
    for copy in COPIES:
        copy.parent.mkdir(parents=True, exist_ok=True)
        copy.write_text(text, encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)}: {len(data['paths'])} shapes, {len(text) // 1024} KB")


if __name__ == "__main__":
    main()
