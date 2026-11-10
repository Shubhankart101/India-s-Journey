#!/usr/bin/env python3
"""Run the project's data producers in dependency order without discarding good data."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
@dataclass(frozen=True)
class Step:
    name: str
    command: tuple[str, ...]
    outputs: tuple[str, ...] = ()
    dependencies: tuple[str, ...] = ()
    network: bool = False
    source: str = ""
    cadence: str = "On demand"
    offline_cache: tuple[str, ...] = ()
    offline_cache_groups: tuple[tuple[str, ...], ...] = ()
    required_cache: tuple[str, ...] = ()
    notes: str = ""


def py(script: str, *args: str) -> tuple[str, ...]:
    return (sys.executable, str(ROOT / "scripts" / script), *args)


# Paths in outputs are relative to the repository root; globs allow the sports
# refresh task to preserve/restore its source snapshots as well as sports.json.
STEPS: tuple[Step, ...] = (
    Step("fetch-election-caches", py("fetch_election_caches.py"),
         outputs=("data/raw/parliament_final.csv", "data/raw/tcpd_ae_all_states.csv.gz"),
         network=True, source="ECI-derived archive; TCPD Lok Dhaba", cadence="As needed",
         notes="Downloads missing public CSV caches only."),
    Step("site-status", py("check_site_status.py"),
         outputs=("data/latest.json", "data/latest-status.json"), network=True,
         source="PolityPolicy public homepage", cadence="Daily"),
    Step("collect-substack", py("collect_substack.py"), outputs=("data/substack-latest.json",),
         network=True, source="PolityPolicy public article feed", cadence="Weekly"),
    Step("collect-indian-matrix", py("collect_indian_matrix.py"), outputs=("data/indian-matrix-latest.json", "docs/data/indian-matrix-latest.json"),
         network=True, source="Indian Matrix public article feed", cadence="Daily"),
    Step("collect-us-campaign-finance", py("collect_us_campaign_finance.py"), outputs=("data/us-campaign-finance.json",),
         network=True, source="Federal Election Commission", cadence="Daily"),
    Step("collect-election-results", py("collect_election_results.py"), outputs=("data/election-results.json", "docs/data/election-results.json"),
         network=True, source="Election Commission of India; U.S. National Archives", cadence="Every 3 hours on counting days"),
    Step("collect-historical-elections", py("collect_historical_elections.py"), outputs=("data/historical-elections.json", "docs/data/historical-elections.json"),
         network=True, source="Election Commission of India statistical reports", cadence="Monthly"),
    Step("collect-recent-elections", py("collect_recent_indian_elections.py"), outputs=("data/recent-indian-elections.json", "docs/data/recent-indian-elections.json"),
         network=True, source="Election Commission of India; India Votes Data", cadence="Daily"),
    Step("collect-ncrb", py("collect_ncrb_and_analyses.py"), outputs=("data/ncrb-and-analyses.json", "docs/data/ncrb-and-analyses.json"),
         network=True, source="NCRB and Indian Matrix", cadence="Monthly"),
    Step("collect-pew-snapshots", py("collect_pew_snapshots.py"), outputs=("data/pew-snapshots.json",),
         network=True, source="Pew Research Center", cadence="Weekly"),
    Step("collect-pew-reports", py("collect_pew_india_reports.py"), outputs=("data/pew-india-reports.json", "docs/data/pew-india-reports.json"),
         network=True, source="Pew Research Center India report catalogue", cadence="Weekly"),
    Step("fetch-economic-survey", py("fetch_economic_survey_monthly.py"), outputs=("data/economic-survey-monthly.json", "docs/data/economic-survey-monthly.json"),
         network=True, source="Ministry of Finance Economic Survey", cadence="Monthly; check on 5th, 15th and 25th"),
    Step("refresh-sports", py("refresh_sports_sources.py", "--no-build"),
         outputs=("data/sports.json", "data/sports_sources/*.json"), network=True,
         source="Official sports federations and ranking sources", cadence="Weekly"),
    Step("build-sports", py("build_sports_data.py"), outputs=("data/sports.json",),
         dependencies=("refresh-sports",), source="Cached sports source snapshots", cadence="On source refresh",
         offline_cache=("data/sports_sources/*.json",)),
    Step("build-election-indices", py("build_election_indices.py"), outputs=("data/election-indices.json", "docs/data/election-indices.json"),
         dependencies=("collect-recent-elections",), required_cache=("data/recent-indian-elections.json",),
         source="Recent Indian election results", cadence="On election data refresh"),
    Step("build-niti-reports", py("build_niti_reports.py"), outputs=("data/niti-reports.json",),
         source="NITI Aayog reports and transcribed report tables", cadence="On report release"),
    Step("build-lwe-insurgency", py("build_lwe_insurgency.py"), outputs=("data/lwe-insurgency.json",),
         source="PIB, ORF and ICFS reports", cadence="On report release"),
    Step("build-voter-roll", py("build_voter_roll.py"), outputs=("data/voter-roll.json", "frontend/src/data/voter-roll.json", "frontend/public/data/voter-roll.json"),
         source="Election Commission of India and official population sources", cadence="On ECI revision"),
    Step("build-union-budget", py("build_union_budget.py"), outputs=("data/union_budget.json",),
         source="Union Budget: Budget at a Glance PDFs", cadence="Annual",
         offline_cache_groups=tuple(
             (f"data/raw_fiscal/bag{year}-{str(year + 1)[-2:]}_bag{part}.pdf",
              f"data/raw_fiscal/bag{year}-{str(year + 1)[-2:]}_bag{part}.lay.txt")
             for year in range(2014, 2027) for part in range(1, 7)
             if not (year in {2015, 2016} and part == 6)
         ), notes="Network runs fetch missing PDFs; offline uses cached layout text or PDFs."),
    Step("build-borrowing", py("build_borrowing.py"), outputs=("data/borrowing.json",),
         source="RBI Handbook of Statistics on the Indian Economy", cadence="Annual",
         offline_cache=tuple(f"data/raw_fiscal/rbi/p{pid}.html" for pid in (105, 106, 107, 109, 110, 113, 149, 239)),
         notes="The builder downloads missing RBI tables in network mode."),
    Step("build-state-fiscal", py("build_state_fiscal.py"), outputs=("data/state_fiscal.json",),
         source="RBI Handbook of Statistics on Indian States; RBI State Finances", cadence="Annual",
         offline_cache=tuple(f"data/raw_fiscal/rbi/p{pid}.html" for pid in sorted({
             23729, *range(23755, 23763), *(23449 + n for n in (164, 165, 166, 168, 169, 170, 171, 174, 21, 22, 19))
         })), notes="The builder downloads missing RBI tables in network mode."),
    Step("build-fiscal-layer", py("build_fiscal_layer.py"),
         outputs=("data/fiscal-series.json", "frontend/src/data/fiscal-views.json"),
         dependencies=("build-union-budget", "build-borrowing", "build-state-fiscal"),
         required_cache=("data/union_budget.json", "data/borrowing.json", "data/state_fiscal.json"),
         source="Derived from the Union Budget and RBI fiscal datasets", cadence="After fiscal inputs"),
    Step("build-lok-sabha-atlas", py("build_lok_sabha_atlas.py"),
         outputs=("data/lok-sabha-atlas.json", "frontend/public/data/lok-sabha-atlas.json", "frontend/src/data/lok-sabha-atlas.json"), dependencies=("fetch-election-caches", "collect-recent-elections"),
         required_cache=("data/raw/parliament_final.csv",), source="ECI-derived constituency history; recent ECI results",
         cadence="After election results", notes="Requires the downloadable historical CSV cache."),
    Step("pull-faith-verses", py("pull_faith_verses.py"),
         outputs=("data/faith-sources/verses.json",), network=True,
         required_cache=("data/epic-sources/mahabharata.json", "data/epic-sources/ramayana.json"),
         source="Wikisource, SuttaCentral, BaniDB and cached epic sources", cadence="On source update"),
    Step("build-epic-atlas", py("build_epic_atlas.py"),
         outputs=("data/epic-kingdoms.json", "frontend/public/data/epic-kingdoms.json", "frontend/src/data/epic-kingdoms.json"), dependencies=("pull-faith-verses",),
         required_cache=("data/epic-sources/mahabharata.json", "data/epic-sources/ramayana.json", "data/faith-sources/verses.json"),
         source="Curated epic places and verified public-text verses", cadence="On content update",
         notes="The two curated epic JSON inputs are not mirrored by an upstream download."),
    Step("build-faith-journeys", py("build_faith_journeys.py"),
         outputs=("data/faith-journeys.json", "docs/data/faith-journeys.json", "frontend/public/data/faith-journeys.json", "frontend/src/data/faith-journeys.json"), dependencies=("build-epic-atlas",),
         required_cache=("data/epic-sources/mahabharata.json", "data/epic-sources/ramayana.json", "data/faith-sources/verses.json"),
         source="Cached verses and curated journey specifications", cadence="On source update"),
    Step("build-atlas-series", py("build_atlas_series.py"), outputs=("data/atlas-series.json",),
         dependencies=("build-lok-sabha-atlas", "build-epic-atlas", "build-faith-journeys"),
         required_cache=("data/lok-sabha-atlas.json", "data/epic-kingdoms.json", "data/faith-journeys.json"),
         source="Lok Sabha atlas, epic atlas and faith journeys", cadence="After atlas builds"),
    Step("collect-legal", py("legal_fetch/njdg.py"),
         outputs=("data/legal/njdg_snapshot.json", "data/legal/njdg_history.json"), network=True,
         source="National Judicial Data Grid", cadence="Weekly"),
    Step("generate-public-charts", py("generate_public_charts.py"), outputs=("data/chart-latest.json",),
         dependencies=("collect-indian-matrix", "collect-substack", "collect-us-campaign-finance", "collect-ncrb",
                       "collect-pew-snapshots", "collect-pew-reports", "fetch-economic-survey", "collect-legal"),
         network=True, source="World Bank, RBI, MoSPI, UNESCO, NJDG and other official sources", cadence="Daily"),
    Step("export-catalog", ("node", str(ROOT / "scripts" / "export_catalog.mjs")),
         outputs=("data/catalog.json",), source="Dashboard definitions and published datasets", cadence="After data builds"),
    Step("build-scripture-bundle", py("build_scripture_verses.py"),
         outputs=("frontend/src/data/scripture-verses.json",), dependencies=("export-catalog",),
         required_cache=("data/catalog.json", "data/scripture-verses.json"),
         source="Reviewed scripture corpus and exported catalogue", cadence="After catalogue export"),
    Step("build-explainers", py("build_explainers.py"), dependencies=("export-catalog",),
         required_cache=("data/catalog.json",), source="Exported catalogue", cadence="After catalogue export"),
)

# Entries without a command are intentional: keep source attribution configuration
# and the scripture corpus as reviewed editorial inputs, not generated snapshots.
MANUAL_DATASETS = {
    "source_publishers.json": ("Curated publisher/host mapping", "Manually maintained", "As reviewed"),
    "scripture-verses.json": ("Reviewed scripture corpus", "Manually maintained editorial source", "As reviewed"),
}
WORKFLOW_DATASETS = {"latest.json": "site-status", "latest-status.json": "site-status"}
STEP_BY_NAME = {step.name: step for step in STEPS}
DATASET_REGISTRY: dict[str, dict[str, str]] = {}
for _step in STEPS:
    for _output in _step.outputs:
        _path = Path(_output)
        if _path.parent == Path("data") and _path.suffix == ".json" and "*" not in _path.name:
            DATASET_REGISTRY[_path.name] = {
                "step": _step.name, "source": _step.source, "script": _step.command[-1], "cadence": _step.cadence,
            }
for _name, (_source, _script, _cadence) in MANUAL_DATASETS.items():
    DATASET_REGISTRY[_name] = {"step": "manual", "source": _source, "script": _script, "cadence": _cadence}


def _dataset_name(name: str) -> str:
    return Path(name).name


def select_steps(names: Iterable[str] | None) -> list[Step]:
    if not names:
        return list(STEPS)
    selected: set[str] = set()
    known_datasets = set(DATASET_REGISTRY) | set(WORKFLOW_DATASETS)
    unknown: list[str] = []
    for raw in names:
        name = raw.strip()
        if not name:
            continue
        matches = [step.name for step in STEPS if step.name == name]
        if not matches:
            stem = Path(name).stem
            matches = [step.name for step in STEPS
                       if Path(step.command[1]).name == name or Path(step.command[1]).stem == stem]
        if not matches:
            stem = Path(name).stem
            matches = [step.name for step in STEPS
                       if any(Path(output).name == _dataset_name(name) or Path(output).stem == stem
                              for output in step.outputs if "*" not in output)]
        if matches:
            selected.update(matches)
        elif _dataset_name(name) in known_datasets:
            detail = "workflow-generated" if _dataset_name(name) in WORKFLOW_DATASETS else "manually curated"
            raise ValueError(f"{name} is {detail} and has no standalone producer to select")
        else:
            unknown.append(name)
    if unknown:
        raise ValueError("unknown --only name(s): " + ", ".join(unknown))

    selected.update(("export-catalog", "build-scripture-bundle", "build-explainers"))
    changed = True
    while changed:
        changed = False
        for step in STEPS:
            if step.name in selected:
                for dependency in step.dependencies:
                    if dependency not in selected:
                        selected.add(dependency)
                        changed = True
            elif any(dependency in selected for dependency in step.dependencies):
                selected.add(step.name)
                changed = True
    return [step for step in STEPS if step.name in selected]


def _matches(root: Path, pattern: str) -> list[Path]:
    if "*" in pattern:
        return sorted(root.glob(pattern))
    path = root / pattern
    return [path] if path.exists() else []


def _cache_usable(path: Path) -> bool:
    if not path.is_file():
        return False
    try:
        size = path.stat().st_size
    except OSError:
        return False
    minimum = 3000 if path.suffix.lower() == ".html" else 1000 if path.suffix.lower() in {".pdf", ".csv", ".gz"} else 1
    return size >= minimum


def _cache_missing(root: Path, patterns: Iterable[str]) -> list[str]:
    return [pattern for pattern in patterns if not any(_cache_usable(path) for path in _matches(root, pattern))]


def _output_files(root: Path, patterns: Iterable[str]) -> list[Path]:
    found = {path for pattern in patterns for path in _matches(root, pattern)}
    return sorted(found)


def _snapshot(paths: Iterable[Path]) -> dict[Path, bytes | None]:
    return {path: path.read_bytes() if path.is_file() else None for path in paths}


def _restore(snapshot: dict[Path, bytes | None]) -> None:
    for path, content in snapshot.items():
        if content is None:
            if path.exists():
                path.unlink()
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)


def _stable_json(value: object) -> object:
    volatile = {"generated_at_utc", "generated", "generated_at", "updated_at", "collected_at", "fetched_at_utc"}
    if isinstance(value, dict):
        return {key: _stable_json(item) for key, item in value.items() if key not in volatile}
    if isinstance(value, list):
        return [_stable_json(item) for item in value]
    return value


def _unchanged_json(before: bytes, after: bytes) -> bool:
    try:
        return _stable_json(json.loads(before)) == _stable_json(json.loads(after))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return before == after


def _run_step(step: Step, offline: bool, dry_run: bool) -> tuple[str, str]:
    if step.network and offline:
        return "skipped", "network disabled"
    if step.required_cache:
        missing = _cache_missing(ROOT, step.required_cache)
        if missing:
            return "skipped", "missing required cache: " + ", ".join(missing[:4])
    if offline:
        missing = _cache_missing(ROOT, step.offline_cache)
        missing.extend(
            " or ".join(group) for group in step.offline_cache_groups
            if not any(_cache_usable(path) for pattern in group for path in _matches(ROOT, pattern))
        )
        if missing:
            return "skipped", "missing offline cache: " + ", ".join(missing[:4])
    command = list(step.command)
    if step.name == "build-union-budget" and not offline:
        command.append("--fetch")
    display = subprocess.list2cmdline(command)
    if dry_run:
        return "planned", display

    outputs = _output_files(ROOT, step.outputs)
    previous = _snapshot(outputs)
    print(f"\n==> {step.name}: {display}", flush=True)
    try:
        result = subprocess.run(command, cwd=ROOT, check=False)
    except OSError as error:
        _restore(previous)
        return "failed", f"could not start producer ({error}); previous outputs restored"
    current_outputs = _output_files(ROOT, step.outputs)
    # Include newly created outputs in rollback if a producer fails.
    for path in current_outputs:
        previous.setdefault(path, None)
    if result.returncode:
        _restore(previous)
        return "failed", f"exit {result.returncode}; previous outputs restored"
    changed: list[str] = []
    for path, old in previous.items():
        if old is None:
            if path.exists():
                changed.append(path.relative_to(ROOT).as_posix())
        elif path.exists():
            new = path.read_bytes()
            if _unchanged_json(old, new):
                path.write_bytes(old)
            elif old != new:
                changed.append(path.relative_to(ROOT).as_posix())
        else:
            changed.append(path.relative_to(ROOT).as_posix() + " (removed)")
    return "changed" if changed else "unchanged", ", ".join(changed) if changed else "no output changes"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run India data producers in dependency order; failed producers keep prior outputs.")
    parser.add_argument("--only", nargs="+", metavar="NAME",
                        help="run selected producer names or data/*.json names (comma-separated names are accepted)")
    parser.add_argument("--offline", action="store_true", help="disable network producers and use complete local caches only")
    parser.add_argument("--skip-network", action="store_true", help="skip network producers but run cache-backed builders")
    parser.add_argument("--dry-run", action="store_true", help="show the ordered plan without running producers")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    requested = [part for item in (args.only or []) for part in item.split(",") if part.strip()]
    try:
        steps = select_steps(requested or None)
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    offline = args.offline or args.skip_network
    print("Data update plan" + (" (dry run)" if args.dry_run else "") + (" (offline)" if offline else ""))
    statuses: dict[str, list[str]] = {}
    step_results: dict[str, tuple[str, str]] = {}
    for step in steps:
        missing_dependencies = []
        if not args.dry_run:
            for dependency in step.dependencies:
                dependency_step = STEP_BY_NAME[dependency]
                dependency_status = step_results.get(dependency, ("planned", ""))[0]
                if dependency_status in {"failed", "skipped"} and not _output_files(ROOT, dependency_step.outputs):
                    missing_dependencies.append(dependency)
        if missing_dependencies:
            status, detail = "skipped", "dependency outputs unavailable: " + ", ".join(missing_dependencies)
        else:
            status, detail = _run_step(step, offline, args.dry_run)
        step_results[step.name] = (status, detail)
        statuses.setdefault(status, []).append(step.name)
        print(f"{status:10} {step.name}: {detail}")
    print("\nSummary: " + "; ".join(f"{key}={len(value)}" for key, value in statuses.items()))
    for status in ("changed", "failed", "skipped"):
        if statuses.get(status):
            print(f"{status.title()}: {', '.join(statuses[status])}")
    return 1 if statuses.get("failed") else 0


if __name__ == "__main__":
    raise SystemExit(main())
