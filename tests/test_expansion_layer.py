import unittest

from scripts import expansion_layer as layer

CATEGORIES = (
    "Economic", "Industry Trends & Performance", "Mining & Natural Resources", "Payments & Digital Banking",
    "State Performance & Regional Health", "Public Health & Epidemiology", "Social", "Environment & Climate",
    "Agriculture & Food", "Defence & Strategic", "Crime & Security", "Tourism & Heritage",
)
FORBIDDEN = {
    "Farm Inputs", "Crop Production", "Livestock & Fisheries", "North East Insurgency", "Jammu & Kashmir Insurgency",
    "Punjab Militancy & Security", "Violence & Crime", "Maoism / LWE", "Terrorism", "Defence Budget & Modernization",
    "Defence Exports & Production", "Strategic Stockpiles & Capabilities", "Macroeconomics",
    "Per Capita Income & Wealth", "Manufacturing & Industrial Growth", "Trade & External", "Monetary Policy",
    "Production & Commodities", "Media & Publications", "Markets", "Fiscal & Union Budget", "Climate & Weather",
    "Forests & Land", "Pollution & Waste", "Disasters & Extremes", "Energy Transition", "Infrastructure Development",
    "Food Processing & Consumer Goods", "Heavy Industry & Metals", "Automobiles & Transport Equipment",
    "Chemicals, Pharma & Electronics", "Industrial Output Monitor (IIP)", "Metallic Minerals & Ores",
    "Energy Minerals & Fuel", "Non-Metallic & Industrial Minerals", "Mineral Exports & Trade",
    "Mining Output Monitor (IIP)", "Mineral Price Monitor (WPI)", "UPI & Digital Payments", "Card Spends & Ecosystem",
    "Digital Financial Index", "State Banking & Credit", "Regional Rural Banks", "Pensions & Social Security",
    "Mortality & Lifespan Milestones", "Disease Burden & Epidemiology", "Health Infrastructure & Spending",
    "State Health Outcomes", "State Health Infrastructure", "Nutrition & Food Security", "Demographics", "Welfare",
    "Employment & Poverty", "Education", "Gender & Population", "Higher Education", "State Financial Health & GSDP",
    "State Infrastructure & Services", "State Industrial & Manufacturing Hubs", "State Welfare & Scheme Coverage",
    "State Socio-Demographic Milestones", "State Economy & Industry", "International Visitor Trends",
    "World Heritage Sites", "Global Tourism Comparison",
}


def fake_payload(code, countries=layer.NAMES, years=range(2000, 2021)):
    rows = []
    for c_index, iso in enumerate(countries):
        for year in years:
            rows.append({"countryiso3code": iso, "date": str(year),
                         "value": (10.0 + c_index * 3 + (year - 2000) * 0.5 + len(code) % 7) * 1e10})
    return [{"page": 1}, rows]


class ExpansionLayerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.calls = []

        def fake(url):
            cls.calls.append(url)
            code = url.split("/indicator/")[1].split("?")[0]
            return fake_payload(code)

        cls.series = layer.build_expansion_layer(fake, {})

    def test_every_category_has_two_subgroups_with_six_series(self):
        counts = {}
        for item in self.series.values():
            meta = item["meta"]
            counts.setdefault(meta["category"], {}).setdefault(meta["subgroup"], 0)
            counts[meta["category"]][meta["subgroup"]] += 1
        self.assertEqual(set(counts), set(CATEGORIES))
        for category in CATEGORIES:
            big = [name for name, count in counts[category].items() if count >= 6]
            self.assertGreaterEqual(len(big), 2, category)
            self.assertGreaterEqual(sum(counts[category].values()), 12, category)
        self.assertGreaterEqual(len(self.series), 150)

    def test_new_subgroups_are_declared_unique_and_not_forbidden(self):
        self.assertEqual(set(layer.NEW_SUBGROUPS), set(CATEGORIES))
        names = [name for names in layer.NEW_SUBGROUPS.values() for name in names]
        self.assertEqual(len(names), len(set(names)))
        self.assertFalse(set(names) & FORBIDDEN)
        for category, subgroups in layer.NEW_SUBGROUPS.items():
            self.assertGreaterEqual(len(subgroups), 2, category)
        built = {(i["meta"]["category"], i["meta"]["subgroup"]) for i in self.series.values()}
        declared = {(c, s) for c, names in layer.NEW_SUBGROUPS.items() for s in names}
        self.assertEqual(built, declared)

    def test_meta_and_explain(self):
        required = {"title", "subtitle", "frequency", "color", "suffix", "category", "subgroup", "explain"}
        explains = set()
        for key, item in self.series.items():
            self.assertTrue(key.startswith("xp_"), key)
            self.assertFalse(key.startswith("xp_innov_"), key)
            self.assertTrue(required <= set(item["meta"]), key)
            explain = item["meta"]["explain"]
            for part in ("what", "read", "why"):
                self.assertTrue(explain.get(part), f"{key} {part}")
            explains.add((explain["what"], explain["read"]))
            self.assertIn("World Bank API", item["source"])
            self.assertTrue(item["note"].startswith(item["note"].split(" Source:")[0]))
            self.assertIn("latest year", item["note"])
        self.assertEqual(len(explains), len(self.series))

    def test_labels_and_values_align(self):
        for key, item in self.series.items():
            if "datasets" in item:
                if key.endswith("_peers"):
                    self.assertEqual(item["datasets"][0]["label"], "India", key)
                    self.assertEqual(item["datasets"][0]["color"], "#ff9933", key)
                for dataset in item["datasets"]:
                    self.assertEqual(len(dataset["values"]), len(item["labels"]), key)
            else:
                self.assertEqual(len(item["values"]), len(item["labels"]), key)
                self.assertTrue(all(v is not None for v in item["values"]), key)

    def test_chart_kinds(self):
        rank = self.series["xp_ne_gdi_totl_zs_rank"]
        self.assertEqual((rank["chartType"], rank["indexAxis"], rank["scope"]), ("bar", "y", "category"))
        self.assertIn("India ranks", rank["note"])
        share = self.series["xp_fi_res_totl_cd_share"]
        self.assertEqual((share["chartType"], share["scope"]), ("doughnut", "category"))
        pie = self.series["xp_sector_value_added_pie"]
        self.assertAlmostEqual(sum(pie["values"]), 100, delta=0.1)
        self.assertIn("datasets", self.series["xp_ne_gdi_totl_zs_peers"])
        self.assertIn("datasets", self.series["xp_water_urban_rural_multi"])

    def test_each_url_fetched_once_and_wgi_source(self):
        self.assertEqual(len(self.calls), len(set(self.calls)))
        wgi = [url for url in self.calls if "GOV_WGI_" in url]
        self.assertTrue(wgi)
        self.assertTrue(all("source=3" in url for url in wgi))

    def test_previous_retained_on_failure(self):
        keep = {"xp_ne_gdi_totl_zs_trend": {"labels": ["2000"], "values": [1.0], "meta": {"title": "kept"}}}

        def failing(url):
            raise RuntimeError("offline")

        result = layer.build_expansion_layer(failing, keep)
        self.assertEqual(result, keep)

    def test_empty_payload_is_dropped_not_fatal(self):
        def empty(url):
            return [{"page": 1}, None]

        self.assertEqual(layer.build_expansion_layer(empty, {}), {})


if __name__ == "__main__":
    unittest.main()
