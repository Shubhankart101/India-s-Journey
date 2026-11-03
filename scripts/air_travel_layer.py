"""Air Travel & Civil Aviation: a top-level group with six subgroups built from official sources.

Static series are transcribed from the Airports Authority of India *Annual Report 2023-24* and Ministry of Civil
Aviation statements (Lok Sabha reply of 4 December 2025 and the ministry's performance summary); the global
comparison pulls live World Bank / ICAO air-transport indicators. If a live fetch fails the previous series is kept.
"""
from __future__ import annotations

from typing import Callable

try:
    from scripts.transport_common import meta, multi, ranked, single, with_fallback, wb_observations, WB_PAGE
except ImportError:  # run as a plain script from scripts/
    from transport_common import meta, multi, ranked, single, with_fallback, wb_observations, WB_PAGE

CATEGORY = "Air Travel & Civil Aviation"
GROWTH, GLOBAL, TRAFFIC, AIRPORTS, CARGO, FINANCE = (
    "Air Passenger Growth", "Global Aviation Comparison", "Domestic vs International", "Airports & UDAN",
    "Air Cargo", "AAI Finance & Investment",
)
AAI_REPORT = "https://www.aai.aero/sites/default/files/AAI%20AR_2024_ENG_05.12.2024.pdf"
MOCA = "https://www.civilaviation.gov.in/our-performance"
LOK_SABHA = "https://www.sansad.in/getFile/loksabhaquestions/annex/186/AU861_6WIzEa.pdf?source=pqals"
AAI = "Airports Authority of India, Annual Report 2023-24"

FY = ["2022-23", "2023-24"]
AAI_YEARS = ["2018-19", "2019-20", "2020-21", "2021-22", "2022-23", "2023-24"]
AAI_MOVEMENTS = [2605.96, 2587.05, 1196.74, 1757.11, 2508.32, 2677.59]  # thousand, all Indian airports
AAI_REVENUE = [14132.96, 12837.44, 4867.04, 6841.29, 12172.35, 15979.83]
AAI_PBT = [3683.99, 3817.06, -2767.01, 32.76, 3963.75, 6214.00]
AAI_PAT = [2271.44, 1985.09, -1962.06, 8.76, 2972.05, 4651.31]
AAI_CAPEX_ACTUAL = [4297.44, 4713.49, 4350.00, 3724.34, 5175.00, 5335.00]
AAI_CAPEX_PLAN = [4195.07, 4950.00, 4364.94, 4500.00, 5000.00, 4000.00]

PEERS = ("IND", "CHN", "USA", "JPN", "GBR", "DEU", "FRA", "BRA", "AUS", "ARE", "RUS")
NAMES = {"IND": "India", "CHN": "China", "USA": "United States", "JPN": "Japan", "GBR": "United Kingdom",
         "DEU": "Germany", "FRA": "France", "BRA": "Brazil", "AUS": "Australia", "ARE": "United Arab Emirates", "RUS": "Russia"}
LINE_PEERS = ("IND", "CHN", "USA", "JPN", "GBR")
LINE_COLORS = ("#ff9933", "#ff7b72", "#58a6ff", "#bc8cff", "#3fb950")
BENCHMARK = "2023"  # latest year every compared country reports


def _m(subgroup, title, subtitle, suffix, color="#ff9933", **explain):
    return meta(CATEGORY, subgroup, title, subtitle, suffix, color, **explain)


def _aai(table: str) -> str:
    return f"{AAI}: {table}."


def _static() -> dict[str, Callable]:
    b: dict[str, Callable] = {}

    def add(key, fn):
        b[key] = lambda: fn(key)

    # ---- Domestic vs International (AAI traffic at all Indian airports)
    add("air_aai_passengers", lambda k: multi(k, ["Domestic", "International", "Total"], [
        {"label": "2022-23", "values": [270.34, 56.94, 327.28], "color": "#58a6ff"},
        {"label": "2023-24", "values": [306.79, 69.64, 376.43], "color": "#ff9933"}], source=AAI_REPORT, unit="million", chart="bar",
        note=_aai("Board's Report, traffic handled at all Indian airports. Passengers are counted as movements, arrivals plus departures"),
        meta_=_m(TRAFFIC, "Passengers Handled: Domestic vs International", "All Indian airports, 2022-23 and 2023-24", " million", "#ff9933",
                 what="Passenger traffic handled at all Indian airports, split between domestic and international.",
                 read="Total traffic grew 15.0% to 376.43 million; international grew 22.3% against 13.5% for domestic.",
                 why="International traffic was still catching up after COVID-19, so it grew faster.")))
    add("air_aai_movements", lambda k: multi(k, ["Domestic", "International", "Total"], [
        {"label": "2022-23", "values": [2143.27, 365.05, 2508.32], "color": "#58a6ff"},
        {"label": "2023-24", "values": [2252.42, 425.17, 2677.59], "color": "#ff9933"}], source=AAI_REPORT, unit="thousand", chart="bar",
        note=_aai("Board's Report, aircraft movements at all Indian airports"),
        meta_=_m(TRAFFIC, "Aircraft Movements: Domestic vs International", "Takeoffs and landings, thousands", " thousand", "#58a6ff",
                 what="Aircraft movements (takeoffs and landings) at all Indian airports.",
                 read="Movements grew 6.7% to 2,677.59 thousand, slower than passengers: international movements rose 16.5%, domestic 5.1%.",
                 why="Passengers growing faster than movements means aircraft are flying fuller or larger.")))
    add("air_aai_passenger_mix", lambda k: single(k, ["Domestic", "International"], [306.79, 69.64], source=AAI_REPORT, unit="million", chart="doughnut",
        note=_aai("Board's Report, 2023-24 passengers at all Indian airports"),
        meta_=_m(TRAFFIC, "Domestic vs International Passengers (2023-24)", "Share of 376.43 million passengers", " million", "#3fb950",
                 what="Domestic and international share of 2023-24 airport passenger traffic.",
                 read="Domestic is 81.5% and international 18.5%.",
                 why="India's air market is predominantly domestic.")))
    add("air_aai_movement_mix", lambda k: single(k, ["Domestic", "International"], [2252.42, 425.17], source=AAI_REPORT, unit="thousand", chart="doughnut",
        note=_aai("Board's Report, 2023-24 aircraft movements at all Indian airports"),
        meta_=_m(TRAFFIC, "Domestic vs International Movements (2023-24)", "Share of 2,677.59 thousand movements", " thousand", "#ff7b72",
                 what="Domestic and international share of 2023-24 aircraft movements.",
                 read="Domestic is 84.1% and international 15.9%.",
                 why="International flights carry more passengers per movement than domestic ones.")))
    add("air_scheduled_carried", lambda k: multi(k, ["Scheduled domestic", "Scheduled international"], [
        {"label": "2023-24", "values": [153.7, 66.8], "color": "#58a6ff"},
        {"label": "2024-25", "values": [165.5, 74.14], "color": "#ff9933"}], source=MOCA, unit="million", chart="bar",
        note=(f"Ministry of Civil Aviation performance summary ({MOCA}) and Lok Sabha reply of 4 December 2025 ({LOK_SABHA}): "
              "165.5 million domestic and 74.14 million international passengers on scheduled flights in 2024-25, against 153.7 and 66.8 million in 2023-24. "
              "These count passengers carried by scheduled airlines, so they are lower than AAI's movement-based totals."),
        meta_=_m(TRAFFIC, "Scheduled Passengers Carried to 2024-25", "Passengers on scheduled airlines, Ministry of Civil Aviation", " million", "#ff9933",
                 what="Passengers carried on scheduled domestic and international flights.",
                 read="Scheduled domestic passengers grew 7.7% to 165.5 million in 2024-25; international rose to 74.14 million.",
                 why="Brings the passenger series up to 2024-25, past the AAI report's year.")))

    # ---- Air Passenger Growth
    add("air_aai_movements_trend", lambda k: single(k, AAI_YEARS, AAI_MOVEMENTS, source=AAI_REPORT, unit="thousand",
        note=_aai("Performance at a Glance, aircraft movements at AAI-reporting airports, six years"),
        meta_=_m(GROWTH, "Aircraft Movements Since 2018-19", "Aircraft movements, thousands", " thousand", "#ff9933",
                 what="Aircraft movements reported by AAI each year.",
                 read="Movements fell to 1,196.74 thousand in 2020-21 and reached 2,677.59 thousand in 2023-24, above the 2018-19 level of 2,605.96 thousand.",
                 why="Shows the COVID-19 collapse and the full recovery of flying.")))

    # ---- Airports & UDAN
    add("air_operational_airports", lambda k: single(k, ["2014", "2024 (AAI report)", "2025 (Ministry)"], [74, 157, 164],
        source=LOK_SABHA, unit="airports", chart="bar",
        note=(f"Operational airports including heliports and water aerodromes: 74 in 2014 and 164 in 2025 (Ministry of Civil Aviation, Lok Sabha reply of 4 December 2025); "
              f"157 as at the date of the AAI Annual Report 2023-24 Board's Report ({AAI_REPORT})."),
        meta_=_m(AIRPORTS, "Operational Airports", "Airports, heliports and water aerodromes", " airports", "#58a6ff",
                 what="Number of operational airports, heliports and water aerodromes.",
                 read="The count more than doubled from 74 in 2014 to 164 in 2025.",
                 why="More airports bring air service to more districts.")))
    add("air_aai_airport_network", lambda k: single(k, ["AAI-operated", "PPP", "Joint venture (Delhi, Mumbai)"], [125, 6, 2],
        source=AAI_REPORT, unit="airports", chart="doughnut",
        note=_aai("Board's Report: AAI manages 133 airports, of which 8 are under private control: DIAL and MIAL as joint ventures and Ahmedabad, Jaipur, Lucknow, Guwahati, Thiruvananthapuram and Mangalore as PPPs"),
        meta_=_m(AIRPORTS, "Airports Managed by AAI", "Operating model of AAI's 133 airports", " airports", "#bc8cff",
                 what="How the 133 airports under AAI's management are operated.",
                 read="125 are run directly by AAI, 6 by public-private partnerships and 2 by joint-venture companies (Delhi, Mumbai).",
                 why="Shows how much of airport operations has moved to private operators.")))
    add("air_udan_passengers", lambda k: single(k, ["31 Mar 2023", "31 Mar 2024", "31 Dec 2025"], [117, 136, 159],
        source=AAI_REPORT, unit="lakh", chart="bar",
        note=(f"Cumulative passengers carried under RCS-UDAN: 117 lakh up to 31 March 2023 and 136 lakh up to 31 March 2024 ({AAI}); "
              f"more than 159 lakh as at 31 December 2025 (Ministry of Civil Aviation, {MOCA})."),
        meta_=_m(AIRPORTS, "UDAN Passengers Carried (Cumulative)", "Passengers on RCS-UDAN flights, lakh", " lakh", "#ff9933",
                 what="Cumulative passengers carried on flights under the Regional Connectivity Scheme (UDAN).",
                 read="The total passed 159 lakh by December 2025, up from 117 lakh in March 2023.",
                 why="Measures the reach of regional flying on subsidised routes.")))
    add("air_udan_routes", lambda k: single(k, ["31 Mar 2024", "31 Dec 2025"], [559, 657], source=AAI_REPORT, unit="routes", chart="bar",
        note=(f"RCS-UDAN routes operationalised: 559 connecting 84 airports at 31 March 2024 ({AAI}); "
              f"657 routes and 93 airports at 31 December 2025 (Ministry of Civil Aviation, {MOCA})."),
        meta_=_m(AIRPORTS, "UDAN Routes Operationalised", "Cumulative RCS-UDAN routes", " routes", "#3fb950",
                 what="Cumulative routes started under the Regional Connectivity Scheme.",
                 read="Operational routes rose from 559 to 657 and the airports served from 84 to 93.",
                 why="UDAN is the policy lever for small-city connectivity.")))
    add("air_udan_flights", lambda k: single(k, ["31 Mar 2023", "31 Mar 2024", "31 Dec 2025"], [2.24, 2.62, 3.34],
        source=AAI_REPORT, unit="lakh", chart="bar",
        note=(f"Cumulative RCS-UDAN flights operated: 2.24 lakh up to 31 March 2023 and 2.62 lakh up to 31 March 2024 ({AAI}); "
              f"about 3.34 lakh at 31 December 2025 (Ministry of Civil Aviation, {MOCA})."),
        meta_=_m(AIRPORTS, "UDAN Flights Operated (Cumulative)", "Flights under RCS-UDAN, lakh", " lakh", "#f6c344",
                 what="Cumulative flights operated under UDAN.",
                 read="Flights rose from 2.24 lakh to about 3.34 lakh between March 2023 and December 2025.",
                 why="Flights complement the passenger count to show service frequency.")))

    # ---- Air Cargo
    add("air_aai_freight", lambda k: multi(k, ["Domestic", "International", "Total"], [
        {"label": "2022-23", "values": [1282.26, 1864.54, 3146.80], "color": "#58a6ff"},
        {"label": "2023-24", "values": [1320.16, 2045.52, 3365.68], "color": "#ff9933"}], source=AAI_REPORT, unit="thousand tonnes", chart="bar",
        note=_aai("Board's Report, freight handled at all Indian airports"),
        meta_=_m(CARGO, "Air Freight: Domestic vs International", "Freight handled, thousand tonnes", " thousand tonnes", "#58a6ff",
                 what="Air freight handled at all Indian airports.",
                 read="Total freight grew 7.0% to 3,365.68 thousand tonnes; international freight grew 9.7% and domestic 3.0%.",
                 why="Air cargo carries high-value goods and links India to world trade.")))
    add("air_aai_freight_mix", lambda k: single(k, ["International", "Domestic"], [2045.52, 1320.16], source=AAI_REPORT, unit="thousand tonnes", chart="doughnut",
        note=_aai("Board's Report, 2023-24 freight at all Indian airports"),
        meta_=_m(CARGO, "Air Freight Mix (2023-24)", "Share of 3,365.68 thousand tonnes", " thousand tonnes", "#ff7b72",
                 what="International and domestic share of air freight in 2023-24.",
                 read="International freight is 60.8% and domestic 39.2%, the reverse of passenger traffic.",
                 why="Cargo is more export-driven than passenger flying.")))
    add("air_cargo_decade", lambda k: single(k, ["2014-15", "2023-24 (AAI)", "2024-25 (Ministry)"], [2.53, 3.37, 3.72],
        source=MOCA, unit="million tonnes", chart="bar",
        note=(f"Air cargo handled: 2.53 million tonnes in 2014-15 and 3.72 million tonnes in 2024-25 (Ministry of Civil Aviation, {MOCA}); "
              f"3.37 million tonnes (3,365.68 thousand) in 2023-24 from the AAI Annual Report."),
        meta_=_m(CARGO, "Air Cargo Handled Over a Decade", "Million tonnes", " million tonnes", "#f6c344",
                 what="Air cargo handled at Indian airports.",
                 read="Cargo rose from 2.53 million tonnes in 2014-15 to 3.72 million tonnes in 2024-25, up 47%.",
                 why="A ten-year view shows structural growth beyond the COVID-19 swing.")))

    # ---- AAI Finance & Investment
    add("air_aai_profit", lambda k: multi(k, AAI_YEARS, [
        {"label": "Revenue", "values": AAI_REVENUE, "color": "#ff9933"},
        {"label": "Profit before tax", "values": AAI_PBT, "color": "#3fb950"},
        {"label": "Profit after tax", "values": AAI_PAT, "color": "#58a6ff"}], source=AAI_REPORT, unit="Rs crore",
        note=_aai("Performance at a Glance, income and profit"),
        meta_=_m(FINANCE, "AAI Revenue and Profit", "Rs crore, 2018-19 to 2023-24", " Rs crore", "#ff9933",
                 what="Revenue and profit of the Airports Authority of India.",
                 read="Revenue fell to Rs 4,867 crore and AAI lost Rs 1,962 crore after tax in 2020-21; in 2023-24 revenue was Rs 15,980 crore and profit after tax Rs 4,651 crore.",
                 why="AAI's finances track air traffic closely.")))
    add("air_aai_capex", lambda k: multi(k, AAI_YEARS, [
        {"label": "Plan outlay", "values": AAI_CAPEX_PLAN, "color": "#58a6ff"},
        {"label": "Actual capital expenditure", "values": AAI_CAPEX_ACTUAL, "color": "#ff9933"}], source=AAI_REPORT, unit="Rs crore", chart="bar",
        note=_aai("Performance at a Glance, annual plan outlay and actual capital expenditure"),
        meta_=_m(FINANCE, "AAI Capital Expenditure vs Plan", "Rs crore, 2018-19 to 2023-24", " Rs crore", "#58a6ff",
                 what="AAI's planned and actual capital expenditure.",
                 read="Actual spend was Rs 5,335 crore in 2023-24 against a plan outlay of Rs 4,000 crore.",
                 why="Capital expenditure builds terminals, runways and air navigation capacity.")))
    return b


def _global(get_json: Callable[[str], object]) -> dict[str, Callable]:
    cache: dict[str, dict] = {}

    def fetch(code):
        if code not in cache:
            cache[code] = wb_observations(get_json, PEERS, code)
        return cache[code]

    def line(key, code, title, subtitle, suffix, scale, subgroup, what, why):
        def build():
            observed = fetch(code)
            years = sorted({y for iso in LINE_PEERS for y in observed.get(iso, {})}, key=int)
            data = [{"label": NAMES[iso], "color": LINE_COLORS[i],
                     "values": [round(observed[iso][y] / scale, 3) if y in observed[iso] else None for y in years]}
                    for i, iso in enumerate(LINE_PEERS) if iso in observed]
            return multi(key, years, data, source=WB_PAGE.format(code=code), unit=suffix,
                         note=f"World Bank indicator {code}, compiled from ICAO civil-aviation statistics for carriers registered in each country. Gaps are years a country did not report.",
                         meta_=_m(subgroup, title, subtitle, suffix, "#ff9933", what=what, why=why,
                                  read="India is the orange line; compare its trajectory with each peer."))
        return key, build

    def india(key, code, title, subtitle, suffix, scale, subgroup, what, why):
        def build():
            rows = fetch(code)["IND"]
            years = sorted(rows, key=int)
            values = [round(rows[y] / scale, 3) for y in years]
            low = min(range(len(values)), key=values.__getitem__)
            return single(key, years, values, source=WB_PAGE.format(code=code), unit=suffix,
                          note=f"World Bank indicator {code}, compiled from ICAO civil-aviation statistics for Indian-registered carriers.",
                          meta_=_m(subgroup, title, subtitle, suffix, "#ff9933", what=what, why=why,
                                   read=f"From {values[0]:,.1f} in {years[0]} to {values[-1]:,.1f} in {years[-1]}; the lowest point was {values[low]:,.1f} in {years[low]}."))
        return key, build

    def cross(key, code, title, subtitle, suffix, scale, chart, subgroup, what, why, per=None):
        def build():
            data = fetch(code)
            if per:
                pop = fetch("SP.POP.TOTL")
                at = {NAMES[i]: data[i][BENCHMARK] / pop[i][BENCHMARK] * per for i in data if BENCHMARK in data[i] and BENCHMARK in pop.get(i, {})}
            else:
                at = {NAMES[i]: rows[BENCHMARK] / scale for i, rows in data.items() if BENCHMARK in rows}
            if "India" not in at or len(at) < 4:
                raise ValueError(f"too few countries for {key}")
            rank = [n for n, _ in sorted(at.items(), key=lambda item: -item[1])].index("India") + 1
            return ranked(key, at, source=WB_PAGE.format(code=code), unit=suffix, chart=chart,
                          note=f"World Bank indicator {code}, {BENCHMARK}. India ranks {rank} of {len(at)} countries shown.",
                          meta_=_m(subgroup, f"{title} ({BENCHMARK})", subtitle, suffix, "#58a6ff", what=what, why=why,
                                   read=f"India ranks {rank} of {len(at)} countries in this comparison."))
        return key, build

    wb_pax, wb_dep, wb_cargo = "IS.AIR.PSGR", "IS.AIR.DPRT", "IS.AIR.GOOD.MT.K1"

    specs = [
        india("air_wb_india_passengers", wb_pax, "Air Passengers Carried by Indian Carriers", "Passengers on Indian-registered airlines", " million", 1e6, GROWTH,
              "Passengers carried by air by carriers registered in India, domestic and international, in millions.",
              "A long annual series shows how quickly Indian aviation has grown and how COVID-19 disrupted it."),
        line("air_wb_passengers_trend", wb_pax, "Air Passengers: India vs Peers", "Passengers carried by registered carriers", " million", 1e6, GROWTH,
             "Air passengers carried by each country's airlines, in millions.", "Compares India's growth path with the largest aviation markets."),
        line("air_wb_departures_trend", wb_dep, "Aircraft Departures: India vs Peers", "Departures by registered carriers", " million", 1e6, GROWTH,
             "Take-offs by each country's registered carriers, in millions.", "Departures measure how often aircraft fly, not just how many people travel."),
        cross("air_wb_passengers_per_100", wb_pax, "Air Passengers per 100 People", "Passengers carried relative to population", " per 100 people", 1, "bar", GROWTH,
              "Air passengers carried divided by population.", "Per-person figures show how far air travel has spread beyond big markets.", per=100),
        cross("air_wb_passengers_rank", wb_pax, "Air Passengers Ranking", "Passengers carried by registered carriers", " million", 1e6, "bar", GLOBAL,
              "Passengers carried by each country's airlines, in millions.", "Ranks India among major aviation markets."),
        cross("air_wb_passengers_share", wb_pax, "Share of Air Passengers Among Peers", "Peer share of passengers carried", " million", 1e6, "doughnut", GLOBAL,
              "Each country's share of the peer group's air passengers.", "Shows India's weight in global air travel."),
        cross("air_wb_departures_rank", wb_dep, "Aircraft Departures Ranking", "Departures by registered carriers", " million", 1e6, "bar", GLOBAL,
              "Take-offs by each country's airlines, in millions.", "Ranks India on flight frequency."),
        cross("air_wb_departures_share", wb_dep, "Share of Aircraft Departures Among Peers", "Peer share of departures", " million", 1e6, "doughnut", GLOBAL,
              "Each country's share of the peer group's departures.", "Shows India's weight in global flying."),
        line("air_wb_freight_trend", wb_cargo, "Air Freight: India vs Peers", "Freight carried by registered carriers", " million tonne-km", 1e6, CARGO,
             "Air freight in million tonne-kilometres.", "Air freight tracks high-value trade."),
        cross("air_wb_freight_rank", wb_cargo, "Air Freight Ranking", "Freight carried by registered carriers", " million tonne-km", 1e6, "bar", CARGO,
              "Air freight in million tonne-kilometres.", "Ranks India's air cargo output."),
        cross("air_wb_freight_share", wb_cargo, "Share of Air Freight Among Peers", "Peer share of air freight", " million tonne-km", 1e6, "doughnut", CARGO,
              "Each country's share of the peer group's air freight.", "Shows India's weight in global air cargo."),
    ]
    return dict(specs)


def build_air_travel_layer(get_json: Callable[[str], object], previous: dict[str, dict]) -> dict[str, dict]:
    builders = _static()
    builders.update(_global(get_json))
    return with_fallback(builders, previous)
