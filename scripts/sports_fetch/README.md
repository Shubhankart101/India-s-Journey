# `scripts/sports_fetch`: official sports fetchers

This package downloads sports statistics from governing bodies and their official statistics partners. Each module writes one snapshot to [`data/sports_sources/`](../../data/sports_sources/README.md), and [`scripts/build_sports_data.py`](../build_sports_data.py) turns those snapshots into charts.

It uses only the Python standard library, because the GitHub workflows do not install packages. Wikipedia and other wiki pages are never used.

| Module | Snapshot | Sources | Feeds groups |
| --- | --- | --- | --- |
| `cricket.py` | `cricket.json` | ICC (rankings, events, player rankings), ESPNcricinfo Statsguru (the ICC's statistics partner) | Cricket |
| `hockey.py` | `hockey.json` | FIH (events, world rankings, Pro League), Hockey India | Hockey |
| `football.py` | `football.json` | FIFA (rankings, match centre), AIFF, AFC | Football |
| `individual.py` | `individual_sports.json` | BWF, ITF, ISSF, World Archery, UWW, IBA / World Boxing, IWF, World Athletics, FIDE, Pro Kabaddi League | Sports |
| `common.py` | n/a | Shared helpers | n/a |

## Running

```powershell
python scripts/refresh_sports_sources.py                  # every fetcher, then rebuild sports.json
python scripts/refresh_sports_sources.py cricket football  # chosen fetchers only
python scripts/refresh_sports_sources.py --no-build -v     # snapshots only, verbose
python -m scripts.sports_fetch.hockey                      # debug one module (prints, writes nothing)
```

The [Sports Data Update](../../.github/workflows/sports-data-update.yml) workflow runs the refresh every Tuesday at 04:15 UTC. You can also start it by hand and give a space-separated `fetchers` input. It then runs `tests/test_sports_data.py`, exports the web-app catalogue and commits `data/` and `docs/`.

## Module contract

Every fetcher module exposes:

- `SNAPSHOT`: the snapshot file name in `data/sports_sources/`.
- `PRODUCERS`: `{key: function}`. Each function takes no arguments and returns one series dict or a list of them.
- `NOT_AVAILABLE`: a list of `{item, reason}` entries for statistics no official source publishes.

A series looks like this:

```json
{
  "key": "cricket_players_men_test_batting",
  "sport": "Cricket",
  "title": "India men's Test batting: past vs current",
  "description": "...",
  "labels": ["S Tendulkar (past)", "V Kohli (current)"],
  "datasets": [{"label": "Runs", "values": [15921, 9230]}, {"label": "Average", "values": [53.78, 46.85]}],
  "source_url": "https://stats.espncricinfo.com/...",
  "publisher": "ESPNcricinfo Statsguru (ICC statistics partner)",
  "as_of": "2026-01-11",
  "notes": "..."
}
```

`series()` in `common.py` checks that every dataset has one value per label.

## Failure handling

`refresh_sports_sources.py` runs each producer separately:

1. Each new series is tagged with `producer` = the producer key.
2. If a producer raises an error (site down, layout changed, PDF-only source), the series it made last time are copied from the existing snapshot. A `stale` entry `{producer, error, kept_series}` records what happened.
3. The script exits with status 1 only when every producer of a module fails, so one broken site never wipes a chart or blocks the other sports.

Some sources publish only PDFs (for example, older federation results). Their producers raise on purpose, so the checked snapshot values are kept and the `stale` list shows why.

## Player indices: past vs current

Cricket, Hockey and Football each have a past-vs-current player subgroup. Labels end in `(past)` for retired players and `(current)` for active players. `datasets[0]` is the main measure (runs, wickets, goals) and `datasets[1]` the context measure (average, caps, appearances). The builder draws these as two bar charts.

## Adding a source

1. Add a producer function to the right module (or a new module listed in `FETCHERS` in `refresh_sports_sources.py`).
2. Use `fetch_text` / `fetch_json` / `html_tables` from `common.py`, and cite the official page in `source_url`.
3. Run the module on its own to check the output, then run the refresh script.
4. If the automatic `route()` in `build_sports_data.py` places the series in the wrong subgroup, add an entry to `TEAM_CONFIG`.
5. Add the publisher host to `OFFICIAL_HOSTS` in `tests/test_sports_data.py` and to the Sources page (`docs/sources.html` and `frontend/src/pages/Sources.jsx`).
