# Official sports snapshots

These files are the raw values read from official sports sources. [`scripts/build_sports_data.py`](../../scripts/build_sports_data.py) builds `data/sports.json` and `docs/data/sports.json` from them alone. It reads no network sources, so a build is always reproducible from the committed snapshots.

| File | Written by | Contents |
| --- | --- | --- |
| `cricket.json` | `scripts/sports_fetch/cricket.py` | ICC team and player rankings, ICC event records, Statsguru team results and player records (men and women, Test/ODI/T20I) |
| `hockey.json` | `scripts/sports_fetch/hockey.py` | FIH event standings, world-ranking history, Pro League tables, player goals and caps |
| `football.json` | `scripts/sports_fetch/football.py` | FIFA rankings and match results (men and women), player goals and appearances |
| `individual_sports.json` | `scripts/sports_fetch/individual.py` | Badminton, tennis, shooting, archery, wrestling, boxing, weightlifting, athletics, chess, kabaddi |
| `games_verification.json` | Checked by hand | Olympic, Paralympic, Asian and Commonwealth Games medals checked against the IOC, IPC, OCA, CGF and PIB |

## Format

```json
{
  "fetched_at_utc": "2026-01-11T04:15:00Z",
  "fetcher": "cricket",
  "series": [{"key": "...", "producer": "...", "labels": [], "datasets": [], "source_url": "...", "publisher": "..."}],
  "not_available": [{"item": "...", "reason": "..."}],
  "stale": [{"producer": "...", "error": "...", "kept_series": ["..."]}]
}
```

- `stale` lists producers whose source failed on the last run. Their previous series were kept unchanged.
- `not_available` lists statistics that no official source publishes. They are shown as gaps, never estimated.

Do not edit these files by hand, except `games_verification.json`. Run `python scripts/refresh_sports_sources.py` instead. See [`scripts/sports_fetch/README.md`](../../scripts/sports_fetch/README.md).
