#!/usr/bin/env python3
"""Fetch missing public election source CSVs into the ignored data/raw cache."""
from __future__ import annotations

import argparse
import gzip
import zlib
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
UA = "IndiaJourneyDataRefresh/1.0 (public data cache)"
SOURCES = {
    ROOT / "data" / "raw" / "parliament_final.csv":
        "https://raw.githubusercontent.com/gitcheckoutnikhil/india-elections-data/master/parliament_final.csv",
    ROOT / "data" / "raw" / "tcpd_ae_all_states.csv.gz":
        "https://raw.githubusercontent.com/tcpd/tcpd-ld-data-archive/main/downloads/All_States/All_States_AE.csv.gz",
}


def valid(path: Path, payload: bytes | None = None) -> bool:
    try:
        data = payload if payload is not None else path.read_bytes()
        if len(data) < 1000:
            return False
        if path.suffix == ".gz":
            if not gzip.decompress(data):
                return False
        else:
            return b"," in data[:4096]
        return True
    except (OSError, EOFError, gzip.BadGzipFile, zlib.error):
        return False


def fetch_missing(offline: bool = False) -> int:
    missing = [path for path in SOURCES if not valid(path)]
    if offline:
        for path in missing:
            print(f"offline: missing cache {path.relative_to(ROOT).as_posix()}; leaving it untouched")
        return 0
    errors = 0
    for path in missing:
        url = SOURCES[path]
        try:
            request = Request(url, headers={"User-Agent": UA})
            with urlopen(request, timeout=90) as response:
                payload = response.read()
            if not valid(path, payload):
                raise ValueError("download did not pass the local file validation")
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(payload)
            print(f"fetched {path.relative_to(ROOT).as_posix()}")
        except Exception as error:
            errors += 1
            print(f"warning: could not fetch {path.relative_to(ROOT).as_posix()}: {error}")
    return 1 if errors else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--offline", action="store_true", help="do not fetch; report missing caches")
    args = parser.parse_args()
    return fetch_missing(args.offline)


if __name__ == "__main__":
    raise SystemExit(main())
