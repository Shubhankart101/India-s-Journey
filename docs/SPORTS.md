# Sports, Cricket, Hockey and Football data

`scripts/build_sports_data.py` builds **121 chart series** into `data/sports.json` and `docs/data/sports.json`. They appear as four Explore groups on the static site and in the web app.

| Group | Subgroups | Series |
|---|---|---|
| Sports | Olympic & Paralympic Medals · Asian & Commonwealth Games · Athletics · Shooting & Archery · Combat & Strength · Racket Sports · Chess & Kabaddi | 37 |
| Cricket | Men's Cricket · Women's Cricket · ICC Tournaments · ICC Rankings · **Batting: Past vs Current** · **Bowling: Past vs Current** | 42 |
| Hockey | Men's Hockey · Women's Hockey · FIH Rankings & Pro League · **Hockey Players: Past vs Current** | 26 |
| Football | Men's Football · Women's Football · FIFA Rankings · **Footballers: Past vs Current** | 16 |

## Player indices: past vs current

Each player chart puts retired legends and active players side by side. Labels end in **(past)** or **(current)**. Every index has two charts: the main measure, and a second chart for context.

| Group | Indices | Main measure, then context | What counts as "current" |
|---|---|---|---|
| Cricket | Men's and women's Test / ODI / T20I leading run-scorers and wicket-takers (12 lists, 12 players each) | Runs, then average · Wickets, then average | Played in the last two calendar years (Statsguru career span) |
| Cricket | Indian players in the ICC rankings (men and women, top 25) | Rating, then world rank | Ranked now |
| Hockey | Men's and women's top scorers and most-capped players (6 past + 6 current each) | Goals, then caps · Caps, then goals | Listed in an India squad at an FIH event that ended in the last 24 months |
| Football | Men's top scorers and most appearances | Goals, then appearances · Appearances, then goals | Played for India in the last two years |

## Official sources only

No wiki or encyclopaedia pages are used. Every series cites the governing body or its official statistics feed. The fetchers in [`scripts/sports_fetch/`](../scripts/sports_fetch/README.md) write the raw values to [`data/sports_sources/`](../data/sports_sources/README.md):

| Snapshot | Publishers |
|---|---|
| `cricket.json` | ICC (team and player rankings feed, event records), ESPNcricinfo Statsguru (team results and player career records) |
| `hockey.json` | FIH (rankings, event standings, Pro League, squads, player profiles, Pro League stats) |
| `football.json` | FIFA (ranking history and tables, match calendar, official match line-ups) |
| `individual_sports.json` | BWF, ITF, ISSF, World Archery, UWW, IBA / World Boxing, IWF, World Athletics, FIDE, Pro Kabaddi League |
| `games_verification.json` | IOC, IPC, OCA, CGF and Press Information Bureau (checked by hand) |

The full list of publishers is on the Sources page of both sites, under **Official sports data sources**.

## Updates

The [Sports Data Update](../.github/workflows/sports-data-update.yml) workflow runs every Tuesday at 04:15 UTC:

1. `python scripts/refresh_sports_sources.py` runs the cricket, hockey, football and individual fetchers. Each producer runs on its own. If one fails, its last good series are kept and listed under `stale` in the snapshot.
2. `build_sports_data.py` rebuilds `sports.json` from the snapshots.
3. `tests/test_sports_data.py` checks the result: official hosts only, every subgroup filled, past and current players in each player index, and a fetcher for every snapshot series.
4. `export_catalog.mjs` updates the web-app catalogue. The commit then triggers the Pages deploy and Netlify.

To run it locally:

```powershell
python scripts/refresh_sports_sources.py              # all fetchers (about 10 minutes; hockey and cricket fetch one page per player)
python scripts/refresh_sports_sources.py football     # one fetcher
python scripts/build_sports_data.py                   # rebuild from committed snapshots only
python -m unittest tests.test_sports_data
node scripts/export_catalog.mjs
cd webapp; python manage.py import_catalog
```

## Caveats

- **Cricket records** come from ESPNcricinfo Statsguru, the record keeper the ICC links to. Rankings come from the ICC's own feed. The ICC publishes no women's Test player rankings.
- **Hockey player totals** are FIH career totals, which mostly start in the 2010s. Older legends, such as Dhyan Chand or Dhanraj Pillay, are under-counted or missing. FIH name order is sometimes odd ("Khan Mumtaz").
- **Football player totals** count only matches for which FIFA publishes official line-ups (100 of 103 men's matches in FIFA's feed since 1993). So Sunil Chhetri shows fewer goals than his official career total. FIFA spells his name "Chetri". There is no women's player index, because FIFA has line-ups for only 9 of 71 women's matches. AIFF and AFC publish no usable match or player data.
- **FIFA rankings:** the API does not serve the newest ranking tables. The Asian top-10 charts use the latest full table it does serve, and the date is in each title.
- **Kept, not live:** boxing world-championship medals (PDF-only reports) and IWF weightlifting medals (iwf.sport blocks automated requests) stay at their checked snapshot values.
- **Games we couldn't check online.** Some early Olympic, Asian and Commonwealth Games editions are not on an official results page we could reach. Their figures are kept and cited to the official body. CWG 2022 is 22/16/23 and Hangzhou 2022 is 28/38/41. For Asian Games 2018, the OCA's 16/23/31 is used; PIB lists 15/24/30.
- **Other gaps** that official sites do not publish:
  - FIH Olympic standings for 1932, 1952 and 1980;
  - UWW wrestling before 2025, ISSF medal standings before 2022 and Chess Olympiads before 2022;
  - several early boxing editions, and IWF Worlds before 2011;
  - kabaddi national-team results (only PKL standings are shown);
  - ATP/WTA rankings.