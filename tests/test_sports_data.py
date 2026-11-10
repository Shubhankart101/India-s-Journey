import importlib
import json
import sys
import types
import unittest
from pathlib import Path
from unittest import mock

from scripts import build_sports_data as sports
from scripts import refresh_sports_sources as refresh

ROOT = Path(__file__).resolve().parents[1]
GROUPS = {
    "Sports": set(sports.SPORTS_SUBGROUPS),
    "Cricket": set(sports.CRICKET_SUBGROUPS),
    "Hockey": set(sports.HOCKEY_SUBGROUPS),
    "Football": set(sports.FOOTBALL_SUBGROUPS),
}
PLAYER_SUBGROUPS = {sports.SUB_BATTING, sports.SUB_BOWLING, sports.SUB_HOCKEY_PLAYERS, sports.SUB_FOOTBALL_PLAYERS}
OFFICIAL_HOSTS = (
    "olympics.com", "paralympic.org", "ocasia.org", "thecgf.com", "pib.gov.in", "icc-cricket.com", "espncricinfo.com",
    "fih.hockey", "hockeyindia.org", "fifa.com", "the-aiff.com", "the-afc.com", "bwfbadminton.com", "daviscup.com",
    "billiejeankingcup.com", "issf-sports.org", "worldarchery.sport", "uww.org", "iba.sport", "worldboxing", "iwf.sport",
    "worldathletics.org", "fide.com", "chess-results.com", "prokabaddi.com", "yas.gov.in",
)
SNAPSHOT_FILES = ("cricket.json", "hockey.json", "football.json", "individual_sports.json", "games_verification.json")


class SportsDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads((ROOT / "data" / "sports.json").read_text(encoding="utf-8"))
        cls.series = cls.payload["series"]

    def test_published_files_match_the_builder(self):
        deployed = json.loads((ROOT / "data" / "sports.json").read_text(encoding="utf-8"))
        self.assertEqual(self.payload, deployed)
        self.assertEqual(self.series, sports.build())
        self.assertEqual(self.payload["series_count"], len(self.series))

    def test_every_series_is_placed_in_a_group_with_an_official_source(self):
        seen = {}
        for key, item in self.series.items():
            with self.subTest(key=key):
                category, subgroup = item["meta"]["category"], item["meta"]["subgroup"]
                self.assertIn(subgroup, GROUPS[category])
                seen.setdefault(category, set()).add(subgroup)
                self.assertNotIn("wikipedia", item["source"].lower())
                self.assertTrue(any(host in item["source"] for host in OFFICIAL_HOSTS), item["source"])
                values = [item["values"]] if "values" in item else [dataset["values"] for dataset in item["datasets"]]
                for row in values:
                    self.assertEqual(len(row), len(item["labels"]))
                    self.assertTrue(all(value is None or isinstance(value, (int, float)) for value in row))
        self.assertEqual(seen, GROUPS)

    def test_medal_tallies_reconcile_with_official_totals(self):
        def totals(key):
            return tuple(sum(dataset["values"]) for dataset in self.series[key]["datasets"])

        self.assertEqual(totals("sports_olympic_medals_by_games"), (10, 10, 21))
        self.assertEqual(totals("sports_olympic_medals_by_sport"), (10, 10, 21))
        self.assertEqual(totals("sports_paralympic_medals_by_sport"), (16, 21, 23))
        self.assertEqual(totals("sports_asian_games_medals_by_edition"), (204, 265, 395))
        self.assertEqual(totals("sports_cwg_medals_by_edition"), (216, 207, 180))

    def test_team_and_individual_records_cover_results(self):
        for key in ("cricket_men_alltime_results", "cricket_women_alltime_results", "hockey_fih_olympics_india_men_positions_record",
                    "football_fifa_india_men_results_by_competition", "sports_chess_olympiad_india_match_record_record"):
            labels = {dataset["label"] for dataset in self.series[key]["datasets"]}
            self.assertTrue({"Won", "Lost"} <= labels, key)
        sports_covered = {item["meta"]["subgroup"] for item in self.series.values() if item["meta"]["category"] == "Sports"}
        self.assertTrue({"Athletics", "Shooting & Archery", "Combat & Strength", "Racket Sports", "Chess & Kabaddi"} <= sports_covered)

    def test_player_indices_compare_past_and_current_players(self):
        players = {key: item for key, item in self.series.items() if item["meta"]["subgroup"] in PLAYER_SUBGROUPS}
        self.assertTrue(players)
        for subgroup in PLAYER_SUBGROUPS:
            items = [item for item in players.values() if item["meta"]["subgroup"] == subgroup]
            with self.subTest(subgroup=subgroup):
                self.assertTrue(items)
                labels = [label for item in items for label in item["labels"]]
                self.assertTrue(any("(past)" in label for label in labels), subgroup)
                self.assertTrue(any("(current)" in label for label in labels), subgroup)
                for item in items:
                    self.assertTrue(all(value is None or value >= 0 for value in item["values"]))

    def test_official_snapshots_are_committed(self):
        for name in SNAPSHOT_FILES:
            payload = json.loads((ROOT / "data" / "sports_sources" / name).read_text(encoding="utf-8"))
            self.assertTrue(payload)
        self.assertFalse((ROOT / "data" / "sports_sources" / "team_sports.json").exists())
        self.assertNotIn("wikipedia", (ROOT / "scripts" / "build_sports_data.py").read_text(encoding="utf-8").lower())

    def test_every_snapshot_series_has_a_fetcher(self):
        for name in refresh.FETCHERS:
            module = importlib.import_module(f"scripts.sports_fetch.{name}")
            with self.subTest(fetcher=name):
                self.assertTrue(callable(getattr(module, "PRODUCERS", {}).get(next(iter(module.PRODUCERS)))))
                snapshot = json.loads((ROOT / "data" / "sports_sources" / module.SNAPSHOT).read_text(encoding="utf-8"))
                for item in snapshot["series"]:
                    self.assertIn(item.get("producer", item["key"]), module.PRODUCERS, item["key"])
                    self.assertNotIn("wikipedia", item.get("source_url", "").lower())
                self.assertNotIn("wikipedia", Path(module.__file__).read_text(encoding="utf-8").lower())
        workflow = (ROOT / ".github" / "workflows" / "sports-data-update.yml").read_text(encoding="utf-8")
        self.assertIn("scripts/refresh_sports_sources.py", workflow)
        self.assertIn("export_catalog.mjs", workflow)

    def test_refresh_keeps_last_good_series_when_a_source_fails(self):
        old = {"series": [{"key": "a", "producer": "a", "labels": ["x"], "datasets": [{"label": "Won", "values": [1]}]},
                          {"key": "b", "producer": "b", "labels": ["x"], "datasets": [{"label": "Won", "values": [2]}]}]}
        fake = types.ModuleType("scripts.sports_fetch.fake")
        fake.SNAPSHOT = "fake.json"

        def broken():
            raise RuntimeError("source offline")

        fake.PRODUCERS = {"a": lambda: {"key": "a", "labels": ["x"], "datasets": [{"label": "Won", "values": [5]}]}, "b": broken}
        written = {}
        with mock.patch.dict(sys.modules, {"scripts.sports_fetch.fake": fake}), \
                mock.patch.object(refresh, "load_snapshot", return_value=old), \
                mock.patch.object(refresh, "write_snapshot", side_effect=lambda name, payload: written.update(payload)), \
                mock.patch("builtins.print"):
            self.assertEqual(refresh.refresh("fake"), (1, 1))
        values = {item["key"]: item["datasets"][0]["values"] for item in written["series"]}
        self.assertEqual(values, {"a": [5], "b": [2]})
        self.assertEqual(written["stale"][0]["kept_series"], ["b"])

    def test_sports_groups_reach_static_site_and_web_app_with_art(self):
        catalog = json.loads((ROOT / "data" / "catalog.json").read_text(encoding="utf-8"))
        static_index = json.loads((ROOT / "docs" / "api" / "indicators.json").read_text(encoding="utf-8"))
        group = next(category for category in catalog["categories"] if category["name"] == "Culture, Heritage & Sport")
        placed = {item["key"] for item in catalog["indicators"] if item["category"] == group["name"]}
        for name in GROUPS:
            with self.subTest(group=name):
                expected = {key for key, item in self.series.items() if item["meta"]["category"] == name}
                self.assertTrue(expected <= placed)
        for art in [group["art"]] + [subgroup["art"] for subgroup in group["subgroups"]]:
            self.assertTrue((ROOT / "frontend" / "public" / "art" / art).is_file(), art)
        self.assertTrue(any(item["category"] == group["name"] for item in static_index))
        explore = (ROOT / "frontend" / "src" / "pages" / "Explore.jsx").read_text(encoding="utf-8")
        self.assertIn("api.categories", explore)
        self.assertIn("api.indicators", explore)
        self.assertIn("data/sports.json", (ROOT / ".github" / "workflows" / "deploy-dashboard.yml").read_text(encoding="utf-8"))
        self.assertIn("Official sports data sources", (ROOT / "frontend" / "src" / "pages" / "Sources.jsx").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
