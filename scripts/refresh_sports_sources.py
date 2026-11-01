"""Refresh the official sports snapshots, then rebuild the Sports, Cricket, Hockey and Football charts.

Usage:
    python scripts/refresh_sports_sources.py                 # every fetcher
    python scripts/refresh_sports_sources.py cricket hockey  # selected fetchers
    python scripts/refresh_sports_sources.py --no-build      # snapshots only

Each fetcher module in scripts/sports_fetch/ downloads its series from the governing body
(ICC, FIH, FIFA/AIFF, BWF, FIDE, ...). A series whose download fails keeps its previous
snapshot and is listed under "stale" so a temporary outage never blanks a chart. The run
exits non-zero only when every producer of every fetcher fails.
"""
from __future__ import annotations

import argparse
import importlib
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.sports_fetch.common import load_snapshot, write_snapshot  # noqa: E402

FETCHERS = ("cricket", "hockey", "football", "individual")


def refresh(name: str) -> tuple[int, int]:
    module = importlib.import_module(f"scripts.sports_fetch.{name}")
    previous = {item["key"]: item for item in load_snapshot(module.SNAPSHOT).get("series", [])}
    fresh: dict[str, dict] = {}
    stale: list[dict] = []
    ok = failed = 0
    for key, producer in module.PRODUCERS.items():
        try:
            result = producer()
            items = result if isinstance(result, list) else [result]
            for item in items:
                item["producer"] = key
                fresh[item["key"]] = item
            ok += 1
            print(f"  ok    {name}:{key} ({len(items)} series)")
        except Exception as exc:  # keep the last good copy of anything that fails
            failed += 1
            message = f"{type(exc).__name__}: {exc}"[:300]
            print(f"  STALE {name}:{key} -> {message}")
            if "-v" in sys.argv:
                traceback.print_exc()
            kept = [item for item in previous.values() if item.get("producer", item["key"]) == key]
            for item in kept:
                if item["key"] not in fresh:
                    fresh[item["key"]] = item
            stale.append({"producer": key, "error": message, "kept_series": [item["key"] for item in kept]})
    # Preserve series produced by a producer that no longer exists only if nothing replaced them.
    order = list(previous) + [key for key in fresh if key not in previous]
    payload = {
        "fetched_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "fetcher": f"scripts/sports_fetch/{name}.py",
        "series": [fresh[key] for key in order if key in fresh],
        "not_available": list(getattr(module, "NOT_AVAILABLE", [])),
        "stale": stale,
    }
    write_snapshot(module.SNAPSHOT, payload)
    print(f"{name}: {ok} producers refreshed, {failed} kept from the previous snapshot -> data/sports_sources/{module.SNAPSHOT}")
    return ok, failed


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("fetchers", nargs="*", help=f"fetchers to run: {', '.join(FETCHERS)} (default: all)")
    parser.add_argument("--no-build", action="store_true", help="skip rebuilding data/sports.json")
    parser.add_argument("-v", action="store_true", help="print tracebacks for failed producers")
    args = parser.parse_args(argv)
    unknown = sorted(set(args.fetchers) - set(FETCHERS))
    if unknown:
        parser.error(f"unknown fetcher(s): {', '.join(unknown)}")
    total_ok = total_failed = 0
    for name in args.fetchers or FETCHERS:
        ok, failed = refresh(name)
        total_ok += ok
        total_failed += failed
    if not args.no_build:
        from scripts import build_sports_data
        build_sports_data.main()
    if total_ok == 0 and total_failed:
        print("Every sports producer failed; snapshots were left as they were.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
