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
    _more(add)
    return b


TN = "https://www.aai.aero/en/business-opportunities/aai-traffic-news"
AR2425 = "https://www.aai.aero/sites/default/files/Final_AAi_Annual%20Report_English_29%20jan.pdf"
AR2223 = "https://www.aai.aero/sites/default/files/AAI_AR_2023_ENG_LARGE.pdf"
RS2260 = "https://www.sansad.in/getFile/annex/266/AU2260_TGQhJU.pdf?source=pqars"
LS4389 = "https://sansad.in/getFile/loksabhaquestions/annex/184/AU4389_JWASE8.pdf?source=pqals"
RS2419 = "https://sansad.in/getFile/annex/268/AU2419_Xi4vXl.pdf?source=pqars"
LS2858 = "https://www.sansad.in/getFile/loksabhaquestions/annex/182/AU2858_wclCg4.pdf?source=pqals"
TN_NOTE = "AAI Traffic News, March 2026 report and annexures (April-March 2025-26 against 2024-25)"
AR25 = "Airports Authority of India, Annual Report 2024-25"

# Airport-wise traffic, (2025-26, 2024-25): AAI Traffic News March 2026, top ten airports by 2025-26 value.
AIRPORT_MOVEMENTS = {
    "Delhi": (473540, 468822), "Mumbai": (331756, 330063), "Bengaluru": (279971, 267852),
    "Hyderabad": (207900, 202151), "Chennai": (158702, 156126), "Kolkata": (142261, 148888),
    "Ahmedabad": (103475, 101119), "Kochi": (71722, 72091), "Pune": (71523, 68830), "Guwahati": (47439, 45984),
}
AIRPORT_PASSENGERS = {
    "Delhi": (78701971, 79259890), "Mumbai": (55290095, 55122422), "Bengaluru": (44470035, 41875620),
    "Hyderabad": (30483885, 29482396), "Chennai": (23017324, 22411290), "Kolkata": (21102741, 21831118),
    "Ahmedabad": (13822287, 13427697), "Kochi": (11302552, 11140778), "Pune": (11005988, 10457694),
    "Guwahati": (6622784, 6160157),
}
AIRPORT_INTL_PAX = {
    "Delhi": (21549460, 21561977), "Mumbai": (16347263, 15598554), "Bengaluru": (7227399, 5834155),
    "Chennai": (6142731, 5855344), "Hyderabad": (5463102, 5048572), "Kochi": (5330796, 5242146),
    "Kozhikode": (2920143, 2965957), "Thiruvananthapuram": (2490985, 2344298), "Ahmedabad": (2416259, 2232203),
    "Kolkata": (2298213, 2419466),
}
AIRPORT_DOM_PAX = {
    "Delhi": (57152511, 57697913), "Mumbai": (38942832, 39523868), "Bengaluru": (37242636, 36041465),
    "Hyderabad": (25020783, 24433824), "Kolkata": (18804528, 19411652), "Chennai": (16874593, 16555946),
    "Ahmedabad": (11406028, 11195494), "Pune": (10666184, 10204966), "Guwahati": (6547535, 6101855),
    "Kochi": (5971756, 5898632),
}
AIRPORT_FREIGHT = {  # tonnes
    "Delhi": (1148337.6, 1109519.9), "Mumbai": (927499.4, 889900.1), "Bengaluru": (532012.0, 502509.0),
    "Chennai": (422515.9, 379154.1), "Hyderabad": (182440.0, 165868.3), "Kolkata": (168244.8, 165617.9),
    "Ahmedabad": (136535.9, 118922.3), "Kochi": (68074.6, 61999.7), "Pune": (54711.9, 42293.2),
    "Guwahati": (30164.3, 26606.7),
}
AIRPORT_INTL_FREIGHT = {  # tonnes
    "Delhi": (739779.4, 729784.8), "Mumbai": (694919.1, 654756.4), "Bengaluru": (336545.0, 321283.5),
    "Chennai": (329865.0, 295359.5), "Hyderabad": (110275.5, 98825.0), "Ahmedabad": (63538.6, 51286.9),
    "Kochi": (51930.5, 46836.3), "Kolkata": (51849.5, 51694.7), "Kozhikode": (17754.8, 21222.7),
    "Thiruvananthapuram": (17379.0, 19697.6),
}
NATIONAL_2526 = {"passengers": 420089356, "movements": 2906241, "freight_t": 3964346.6}

CATEGORIES = ["International airports", "PPP international", "JV international", "State govt/private international",
              "Customs airports", "Domestic airports", "State govt/private domestic"]
CAT_PAX = ([85308380, 39380469, 224690440, 6620823, 36980270, 25032851, 2076123],
           [86651348, 39317650, 221119226, 5385392, 35067865, 22635401, 1909229])
CAT_MOV = ([601453, 282760, 1400379, 47330, 265547, 261884, 46888],
           [619087, 293733, 1376410, 38293, 257235, 260069, 41982])
CAT_FREIGHT = [692101.0, 240493.2, 2871261.2, 3524.1, 121815.0, 23441.4, 11710.7]  # tonnes, 2025-26

REGIONS = ["Eastern", "North East", "Northern", "Southern", "Western"]
REG_PAX = ([44367927, 12104183, 117851736, 136762385, 109003125], [42665718, 11617782, 120010782, 131215424, 106576405])
REG_MOV = ([323295, 94518, 763192, 957398, 767838], [311369, 96021, 787068, 937102, 755249])
REG_FREIGHT = ([222821.8, 46818.1, 1239040.3, 1280756.8, 1174909.5], [213158.9, 42524.3, 1192435.7, 1188579.7, 1096638.5])
REG_INTL_PAX = [2570589, 75249, 24595644, 33348741, 20051273]
REG_DOM_PAX = [41797338, 12028934, 93256092, 103413644, 88951852]

# State table, 2025-26: (movements total, intl pax, domestic pax, intl freight t, domestic freight t)
STATES = {
    "Andaman & Nicobar": (15481, 1031, 1815454, 0.0, 9326.7), "Andhra Pradesh": (62877, 144191, 6084020, 0.0, 6179.7),
    "Arunachal Pradesh": (2949, 0, 221481, 0.0, 25.8), "Assam": (59176, 75249, 7990305, 4.0, 32189.8),
    "Bihar": (40771, 91104, 5589574, 0.0, 11887.4), "Chandigarh": (26395, 173044, 3753475, 0.0, 14512.6),
    "Chhattisgarh": (24559, 0, 2865706, 0.0, 5588.5), "Dadra & Nagar Haveli and Daman & Diu": (3250, 0, 127659, 0.0, 0.0),
    "Delhi": (473615, 21549460, 57152536, 739779.5, 408558.1), "Goa": (76238, 575695, 10927765, 2194.4, 6763.9),
    "Gujarat": (151383, 2623988, 16075487, 63538.6, 85026.9), "Haryana": (474, 0, 9559, 0.0, 0.0),
    "Himachal Pradesh": (4374, 0, 192727, 0.0, 0.0), "Jammu & Kashmir": (32962, 5128, 4750752, 197.7, 10252.6),
    "Jharkhand": (22647, 0, 3093669, 0.0, 7747.0), "Karnataka": (319187, 7998825, 40050613, 338369.9, 196288.9),
    "Kerala": (139158, 11715315, 9571229, 90503.6, 19634.7), "Ladakh": (8360, 0, 1070313, 0.0, 1627.4),
    "Lakshadweep": (3774, 0, 136680, 0.0, 0.0), "Madhya Pradesh": (59345, 66541, 6641807, 0.0, 14100.5),
    "Maharashtra": (481297, 16785049, 55525047, 704151.9, 299133.4), "Manipur": (10542, 0, 1366765, 0.0, 6271.9),
    "Meghalaya": (1890, 0, 96716, 0.0, 0.0), "Mizoram": (4154, 0, 428701, 0.0, 1221.1),
    "Nagaland": (4558, 0, 386791, 0.0, 1309.1), "Odisha": (47462, 153473, 5448723, 55.8, 9579.3),
    "Puducherry": (1497, 0, 102635, 0.0, 0.0), "Punjab": (20637, 997408, 2070199, 1844.5, 1816.2),
    "Rajasthan": (70907, 575461, 8376570, 2144.1, 26677.1), "Tamil Nadu": (220077, 8027308, 22437315, 340700.2, 106639.8),
    "Telangana": (210828, 5463102, 25031152, 110275.5, 72164.6), "Tripura": (11249, 0, 1538175, 0.0, 5796.5),
    "Uttar Pradesh": (99504, 1295143, 13573576, 6263.4, 23464.5), "Uttarakhand": (22289, 0, 1960472, 0.0, 1902.7),
    "West Bengal": (172375, 2324981, 22984212, 51849.5, 126787.7),
}

HY = ["2018-19", "2019-20", "2020-21", "2021-22", "2022-23", "2023-24", "2024-25", "2025-26"]
H_MOV_I = [452.641, 431.853, 134.824, 211.836, 365.048, 425.17, 465.119, 481.280]  # thousand
H_MOV_D = [2153.323, 2155.201, 1061.916, 1545.276, 2143.267, 2252.42, 2421.690, 2424.961]
H_PAX_I = [69.480768, 66.543642, 10.128283, 22.088224, 56.939661, 69.64, 77.38, 80.64]  # million
H_PAX_D = [275.218965, 274.507009, 105.2515, 166.803217, 270.339475, 306.79, 334.70, 339.45]
H_PAX_T = [344.699733, 341.050651, 115.379783, 188.891441, 327.279136, 376.43, 412.09, 420.09]
H_FR_I = [2200.187, 2003.123, 1521.424, 1961.112, 1864.544, 2045.52, 2325.0955, 2451.8724]  # thousand tonnes
H_FR_D = [1361.714, 1325.506, 952.487, 1179.690, 1282.257, 1320.16, 1408.2415, 1512.4742]
H_FR_T = [3561.901, 3328.629, 2473.911, 3140.802, 3146.801, 3365.68, 3733.337, 3964.3466]

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep"]
M_PAX = {"total": ([38.63, 35.08, 34.51, 33.83, 36.98, 33.39, 30.63, 31.01, 30.10],
                   [37.13, 34.91, 36.09, 35.76, 35.38, 34.02, 32.14, 32.85, 31.98]),
         "intl": ([7.76, 6.59, 5.34, 5.56, 6.15, 6.15, 6.33, 6.40, 6.10], [7.24, 6.40, 6.54, 6.63, 6.76, 6.45, 6.63, 6.67, 6.37]),
         "dom": ([30.87, 28.49, 29.17, 28.27, 30.83, 27.24, 24.30, 24.61, 24.00],
                 [29.89, 28.51, 29.55, 29.13, 28.62, 27.57, 25.51, 26.18, 25.61])}
M_FREIGHT = {"total": ([324.69, 328.61, 343.31, 347.56, 364.45, 364.29, 372.26, 369.88, 372.27],
                       [299.17, 278.69, 343.38, 316.36, 329.79, 315.27, 335.92, 333.21, 332.10]),
             "intl": ([201.13, 204.39, 208.13, 220.70, 226.38, 231.74, 239.53, 240.41, 243.13],
                      [185.51, 173.88, 221.31, 197.80, 205.07, 194.15, 208.49, 208.12, 204.40]),
             "dom": ([123.56, 124.22, 135.18, 126.86, 138.07, 132.55, 132.73, 129.47, 129.14],
                     [113.66, 104.81, 122.07, 118.56, 124.72, 121.12, 127.43, 125.09, 127.70])}
M_MOV_TOTAL = ([253.0, 231.6, 242.94, 241.1, 254.17, 228.76, 213.26, 223.91, 216.3],
               [249.45, 232.67, 256.94, 248.06, 249.37, 239.74, 228.72, 230.27, 231.24])
APR_SEP = {"Passengers": (196.24, 202.14), "Freight": (2192.38, 1962.65), "Aircraft movements": (1377.29, 1427.55)}

# Domestic passengers by airline, calendar 2023 and 2024: Lok Sabha AU4389 annexure.
AIRLINE_DOM = {
    "IndiGo": (91937895, 99903855), "Air India": (14274483, 19441183), "Vistara": (13846669, 13220757),
    "Akasa Air": (6229350, 7374382), "Air India Express": (479753, 7042504), "AIX Connect": (10893476, 6101602),
    "SpiceJet": (8390024, 6008185), "Alliance Air": (1641286, 1431638), "Star Air": (329910, 631391),
    "Fly91": (0, 127178), "India One Air": (19541, 27342), "FlyBig": (210589, 15488), "Go Air": (3787926, 0),
}
AIRLINE_DOM_TOTAL = (152040902, 161325505)
QTR_DOM = ([37512597, 38589565, 36769252, 39169488], [39146377, 40201177, 39144140, 42833811])
# 2024-25 provisional (to October 2024), (domestic, international): Rajya Sabha AU2260.
AIRLINE_FY25 = {
    "IndiGo": (57622296, 7768709), "Air India": (10507802, 5081130), "Vistara": (8963542, 1653341),
    "Air India Express": (3594119, 3491909), "Akasa Air": (4262116, 165859), "SpiceJet": (2974878, 850229),
    "AIX Connect": (3760720, 0), "Alliance Air": (832743, 17243), "Star Air": (377210, 0), "Fly91": (81289, 0),
    "India One Air": (14304, 0), "FlyBig": (11491, 0),
}
AIRLINE_FY25_TOTAL = (93002510, 19028420)
OTP_2024 = {"IndiGo": 71.4, "Vistara": 72.4, "AIX Connect": 73.0, "Akasa Air": 73.3, "SpiceJet": 52.3, "Alliance Air": 53.6}
CANCEL_2024 = {"IndiGo": 1.3, "Vistara": 0.8, "AIX Connect": 0.7, "Akasa Air": 0.4, "SpiceJet": 2.1, "Alliance Air": 4.2}
OTP_2025 = {"IndiGo": 82.4, "Akasa Air": 79.5, "Air India Group": 76.1, "SpiceJet": 59.2, "Alliance Air": 58.1}
CANCEL_2025 = {"IndiGo": 0.9, "Akasa Air": 0.3, "Air India Group": 0.9, "SpiceJet": 2.1, "Alliance Air": 4.9}

UDAN_YEARS = ["2017-18", "2018-19", "2019-20", "2020-21", "2021-22", "2022-23", "2023-24", "2024-25 (to 30 Jun)"]
UDAN_PHASE1 = [297.49, 512.42, 700.18, 615.51, 441.47, 800.92, 619.85, 45.55]
UDAN_PHASE2 = [0, 0, 0, 0, 0, 0, 32.48, 6.11]
UDAN_EXPENDITURE_TOTAL = 4071.98
UDAN_VGF_YEARS = ["2017-18", "2018-19", "2019-20", "2020-21", "2021-22", "2022-23", "2023-24 (provisional)", "2024-25 (to 31 Jul)"]
UDAN_VGF = [42.35, 138.07, 681.28, 325.60, 625.94, 787.37, 777.14, 134.54]
UDAN_VGF_TOTAL = 3512.29
UDAN_ROUTES = {"Routes awarded": 870, "Routes operationalised": 579, "Routes discontinued early": 106}
AAI_NETWORK = {"AAI operational airports": 113, "International operations": 38, "Civil enclaves": 29, "Under private control": 8}

# Performance at a Glance, AAI Annual Reports 2019-20, 2020-21 and 2024-25 (2014-15 to 2024-25).
DEC = ["2014-15", "2015-16", "2016-17", "2017-18", "2018-19", "2019-20", "2020-21", "2021-22", "2022-23", "2023-24", "2024-25"]
D_MOV = [1603, 1793, 2049, 2324.55, 2605.96, 2587.05, 1196.74, 1757.11, 2508.32, 2677.59, 2887.05]  # thousand
D_PAX = [78895, 92817, 113021, 136731.39, 158793.1, 158332.38, 58467.96, 91157.16, 149874.64, 166414.12, 183672.26]  # thousand, AAI airports
D_CARGO = [681, 724, 808, 920.26, 942.32, 909.56]  # thousand tonnes, 2014-15 to 2019-20
D_EMP = [17465, 17370, 17484, 17536, 17487, 17364, 16780, 16158, 16023, 16078, 16251]
D_MOV_EMP = [92, 103, 117, 133, 149, 149, 71, 109, 157, 167, 178]
D_REV_EMP = [5325, 6232, 7173, 7400, 8082, 7393, 2901, 4234, 7597, 9939, 12706]  # Rs thousand
D_REV = [9284.98, 10824.50, 12542.01, 12976.96, 14132.96, 12837.44, 4867.04, 6841.29, 12172.35, 15979.83, 20648.25]
D_EXP = [6493.57, 7127.15, 7984.40, 8560.02, 10448.97, 9020.38, 7634.05, 6808.53, 8208.60, 9765.83, 10992.79]
D_PBT = [2791.41, 3697.35, 4557.61, 4416.94, 3683.99, 3817.06, -2767.01, 32.76, 3963.75, 6214.00, 9655.46]
D_PAT = [1959.22, 2537.36, 3115.93, 2801.64, 2271.44, 1985.09, -1962.06, 8.76, 2972.05, 4651.31, 7233.28]
D_CAPEX = [1399.87, 1757, 2054, 2504.38, 4297.44, 4713.49, 4350, 3724.34, 5175, 5335, 5568.55]
D_NETWORTH = [11416.61, 13037.81, 15028.66, 14827.45, 14386.45, 15413.19, 12762.38, 12132.59, 15661.86, 18917.78, 23981.07]
D_CWIP = [1442.22, 1601.00, 1661.25, 1574.65, 3183.06, 4849.38, 7248.09, 7691.85, 9367.65, 4934.20, 6068.64]
D_LOANS = [1287.40, 545.21, 39.78, 37.43, 37.16, 91.56, 1897.21, 3151.94, 2385.29, 2396.53, 2171.31]
D_DIVIDEND = [391.85, 761.21, 934.78, 840.50, 765.46, 818.57, 0, 0, 891.62, 1395.39, 2169.99]

FY7 = HY[:7]  # 2018-19 to 2024-25
CAPEX_FUNDING = {
    "Internal resources": [3704.12, 4230.76, 1817.86, 606.24, 3059.74, 4715.34, 5151.41],
    "NEC grant": [0, 22.636, 2.07, 4.50, 4.18, 1.29, 0],
    "RCS grant": [282.61, 454.514, 630, 900, 507.39, 432.18, 413.19],
    "Budgetary support": [118.20, 0.978, 29.99, 190, 221.93, 44.43, 0],
    "Commercial borrowings": [0, 0, 1828.07, 1277.29, 1314.35, 0, 0],
    "Others": [192.51, 4.598, 42.01, 746.31, 67.41, 141.76, 3.95],
}
FY5 = HY[:5]  # revenue mix, 2018-19 to 2022-23
REVENUE_MIX = {
    "Air navigation services": [3702.18, 3592.95, 1587.62, 2379.96, 3550.35],
    "Airport services": [4491.59, 3718.05, 1291.21, 1674.04, 2913.12],
    "Non-aeronautical": [1842.85, 1887.74, 885.84, 912.09, 1257.02],
    "JVC lease": [3050.07, 3063.01, 483.50, 1038.04, 3020.55],
    "PPP concession fees": [0, 0, 87.25, 329.59, 683.86],
    "Other income": [1046.27, 575.69, 531.63, 507.57, 747.45],
}
NON_AERO = [1842.85, 1887.74, 885.84, 912.09, 1257.02, 1640.37, 1910.59]  # 2018-19 to 2024-25
PPP_FEES = [87.25, 329.59, 683.86, 982.83, 3192.75]  # 2020-21 to 2024-25; 2024-25 includes 2,231.80 under-recovery
OPS_REVENUE = [12261.75, 4335.42, 6333.72, 11424.90, 14962.76, 19472.54]  # 2019-20 to 2024-25
OTHER_INCOME = [575.69, 531.62, 507.57, 747.45, 1017.07, 1175.71]
COSTS = {"Operating costs": [7082.16, 8018.13], "Finance costs": [97.38, 141.61], "Depreciation": [2586.29, 2833.05]}  # 2023-24, 2024-25


def _pct(new, old):
    return (new / old - 1) * 100


def _lead(points, suffix, d=1):
    items = sorted(points.items(), key=lambda kv: -kv[1])
    total = sum(v for _, v in items)
    (a, av), (z, zv) = items[0], items[-1]
    share = "" if suffix.strip() == "%" else f" ({av / total * 100:.1f}% of the {len(items)} shown)"
    return f"{a} leads at {av:,.{d}f}{suffix}{share}; {z} is lowest at {zv:,.{d}f}{suffix}."


def _top(points, n=10):
    return dict(sorted(points.items(), key=lambda kv: -kv[1])[:n])


def _more(add):
    def R(key, sub, title, subtitle, suffix, pts, src, note, what, why, chart="bar", color="#58a6ff", d=1, read=None):
        pts = {k: round(v, 3) for k, v in pts.items()}
        add(key, lambda k: ranked(k, pts, source=src, unit=suffix, note=note, chart=chart,
                                  meta_=_m(sub, title, subtitle, suffix, color, what=what, why=why,
                                           read=read or _lead(pts, suffix, d))))

    def S(key, sub, title, subtitle, suffix, labels, values, src, note, what, why, read, chart=None, color="#ff9933"):
        add(key, lambda k: single(k, labels, values, source=src, unit=suffix, note=note, chart=chart,
                                  meta_=_m(sub, title, subtitle, suffix, color, what=what, why=why, read=read)))

    def M(key, sub, title, subtitle, suffix, labels, datasets, src, note, what, why, read, chart=None, color="#ff9933"):
        add(key, lambda k: multi(k, labels, datasets, source=src, unit=suffix, note=note, chart=chart,
                                 meta_=_m(sub, title, subtitle, suffix, color, what=what, why=why, read=read)))

    def pair(table, scale):
        return {n: v[0] / scale for n, v in table.items()}

    def two_year(table, scale):
        return [{"label": "2024-25", "values": [round(v[1] / scale, 3) for v in table.values()], "color": "#58a6ff"},
                {"label": "2025-26", "values": [round(v[0] / scale, 3) for v in table.values()], "color": "#ff9933"}]

    def growth(table):
        return {n: _pct(v[0], v[1]) for n, v in table.items()}

    pax_growth = growth(AIRPORT_PASSENGERS)
    best, worst = max(pax_growth, key=pax_growth.get), min(pax_growth, key=pax_growth.get)
    top_pax = sum(v[0] for v in AIRPORT_PASSENGERS.values())
    hist_yoy = [_pct(H_PAX_T[i], H_PAX_T[i - 1]) for i in range(1, len(HY))]
    ppm = [p / m for p, m in zip(H_PAX_T, [i + d for i, d in zip(H_MOV_I, H_MOV_D)])]  # million / thousand = thousand per movement
    mon_yoy = [_pct(c, p) for c, p in zip(*M_PAX["total"])]
    hi, lo = max(range(9), key=mon_yoy.__getitem__), min(range(9), key=mon_yoy.__getitem__)
    cat_growth = growth(dict(zip(CATEGORIES, zip(*CAT_PAX))))
    cum = {k: _pct(*v) for k, v in APR_SEP.items()}

    # ---- Air Passenger Growth
    R("air_top10_airport_passengers", GROWTH, "Busiest Airports by Passengers (2025-26)", "Top ten airports, million passengers", " million",
      {n: v[0] / 1e6 for n, v in AIRPORT_PASSENGERS.items()}, TN,
      f"{TN_NOTE}: airport-wise passenger traffic (domestic plus international). Mumbai, Bengaluru and Hyderabad are the JV airports MIAL, BIAL and GHIAL.",
      "Total passengers (arrivals plus departures) at the ten busiest Indian airports in April-March 2025-26.",
      "Passenger traffic is concentrated at a few hub airports, which sets where capacity is needed.", d=2,
      read=f"Delhi leads with {AIRPORT_PASSENGERS['Delhi'][0] / 1e6:.1f} million; the ten airports together handle {top_pax / NATIONAL_2526['passengers'] * 100:.1f}% of all {NATIONAL_2526['passengers'] / 1e6:.1f} million passengers.")
    M("air_top10_airport_pax_yoy", GROWTH, "Busiest Airports: 2024-25 vs 2025-26", "Million passengers", " million", list(AIRPORT_PASSENGERS),
      two_year(AIRPORT_PASSENGERS, 1e6), TN, f"{TN_NOTE}: airport-wise passenger traffic for the ten busiest airports.",
      "Passengers at each of the ten busiest airports in two consecutive years.", "Shows which hubs are growing and which are flat.",
      f"{best} added the most in percentage terms ({pax_growth[best]:+.1f}%); {worst} changed {pax_growth[worst]:+.1f}%.", chart="bar")
    R("air_airport_pax_growth_pct", GROWTH, "Passenger Growth by Airport (2025-26)", "Change over 2024-25, top ten airports", "%",
      pax_growth, TN, f"{TN_NOTE}: airport-wise passengers, percentage change computed from the two years.",
      "Year-on-year change in passengers at the ten busiest airports.", "Separates fast-growing airports from mature or congested ones.",
      color="#3fb950", d=1,
      read=f"{best} grew fastest at {pax_growth[best]:+.1f}%; {worst} was weakest at {pax_growth[worst]:+.1f}%; Delhi changed {pax_growth['Delhi']:+.1f}%.")
    M("air_category_pax_yoy", GROWTH, "Passengers by Airport Category", "2024-25 vs 2025-26, million", " million", CATEGORIES,
      [{"label": "2024-25", "values": [round(v / 1e6, 3) for v in CAT_PAX[1]], "color": "#58a6ff"},
       {"label": "2025-26", "values": [round(v / 1e6, 3) for v in CAT_PAX[0]], "color": "#ff9933"}], TN,
      f"{TN_NOTE}, Annexure I: traffic by airport category.",
      "Passengers handled by each AAI airport category: AAI international, PPP, JV, state/private, customs and domestic airports.",
      "Shows whether growth comes from the big JV hubs or from smaller airports.",
      f"JV international airports handled {CAT_PAX[0][2] / 1e6:.1f} million ({CAT_PAX[0][2] / sum(CAT_PAX[0]) * 100:.1f}%); state/private international airports grew fastest ({cat_growth['State govt/private international']:+.1f}%).",
      chart="bar", color="#58a6ff")
    M("air_monthly_passengers", GROWTH, "Monthly Passengers: 2026 vs 2025", "January to September, million", " million", MONTHS,
      [{"label": "2025", "values": M_PAX["total"][1], "color": "#58a6ff"}, {"label": "2026", "values": M_PAX["total"][0], "color": "#ff9933"}],
      TN, "AAI monthly Traffic News reports, January to September 2026 (month of 2026 against the same month of 2025), total passengers.",
      "Total monthly passengers at Indian airports, compared with the same month a year earlier.", "Shows the seasonal pattern and whether growth is holding up.",
      f"January 2026 was {M_PAX['total'][0][0]:.2f} million ({mon_yoy[0]:+.1f}% on a year earlier); by September it was {M_PAX['total'][0][8]:.2f} million ({mon_yoy[8]:+.1f}%).")
    S("air_monthly_passengers_yoy", GROWTH, "Monthly Passenger Growth, 2026", "Change on same month of 2025", "%", MONTHS,
      [round(x, 2) for x in mon_yoy], TN, "AAI monthly Traffic News reports, January to September 2026; percentage change computed from the reported monthly totals.",
      "Year-on-year change in total passengers for each month.", "Reveals the turning point from growth to decline.",
      f"Strongest month was {MONTHS[hi]} ({mon_yoy[hi]:+.1f}%); weakest was {MONTHS[lo]} ({mon_yoy[lo]:+.1f}%).", chart="bar", color="#3fb950")
    S("air_apr_sep_change", GROWTH, "April-September 2026-27 vs 2025-26", "Cumulative change, passengers, freight and movements", "%",
      list(cum), [round(v, 2) for v in cum.values()], TN, "AAI Traffic News, September 2026: cumulative April-September 2026-27 against April-September 2025-26 "
      f"(passengers {APR_SEP['Passengers'][0]} vs {APR_SEP['Passengers'][1]} million; freight {APR_SEP['Freight'][0]:,} vs {APR_SEP['Freight'][1]:,} thousand tonnes; movements {APR_SEP['Aircraft movements'][0]:,} vs {APR_SEP['Aircraft movements'][1]:,} thousand).",
      "Half-year change in passengers, air freight and aircraft movements.", "Contrasts a cargo boom with softer passenger traffic.",
      f"Freight is {cum['Freight']:+.1f}% while passengers are {cum['Passengers']:+.1f}% and movements {cum['Aircraft movements']:+.1f}%.", chart="bar", color="#bc8cff")
    S("air_history_passengers", GROWTH, "Passengers at Indian Airports, 2018-19 to 2025-26", "Total domestic plus international, million", " million", HY, H_PAX_T,
      AR2223, "AAI Annual Reports 2019-20 to 2022-23 (Board's Report, traffic at all Indian airports) for 2018-19 to 2022-23; AAI Annual Report 2023-24 for 2023-24; AAI Traffic News March 2026 for 2024-25 and 2025-26.",
      "Total passengers handled at all Indian airports each financial year.", "The pandemic collapse and recovery in one series.",
      f"From {H_PAX_T[0]:.1f} million in 2018-19 to a low of {H_PAX_T[2]:.1f} million in 2020-21, then {H_PAX_T[-1]:.1f} million in 2025-26.")
    S("air_history_passengers_yoy", GROWTH, "Yearly Passenger Growth, 2019-20 to 2025-26", "Change on previous financial year", "%", HY[1:],
      [round(x, 2) for x in hist_yoy], AR2223, "Computed from the total passengers series: AAI Annual Reports 2019-20 to 2023-24 and AAI Traffic News March 2026.",
      "Year-on-year growth in total airport passengers.", "Shows the size of the 2020-21 collapse and the 2021-22 rebound.",
      f"Traffic fell {hist_yoy[1]:.1f}% in 2020-21, rebounded {hist_yoy[2]:+.1f}% in 2021-22 and grew {hist_yoy[-1]:+.1f}% in 2025-26.", chart="bar", color="#3fb950")
    S("air_passengers_per_movement", GROWTH, "Passengers per Aircraft Movement", "Average passengers on each takeoff or landing", " passengers", HY,
      [round(x * 1000, 1) for x in ppm], AR2223, "Computed: total passengers divided by total aircraft movements, from AAI Annual Reports 2019-20 to 2023-24 and AAI Traffic News March 2026.",
      "Average passengers handled per aircraft movement across all airports (includes cargo and non-scheduled movements).", "Rising loads signal larger aircraft and fuller flights.",
      f"{ppm[0] * 1000:.0f} in 2018-19, {ppm[2] * 1000:.0f} in 2020-21 and {ppm[-1] * 1000:.0f} in 2025-26.", color="#39c5bb")
    S("air_aai_airports_passenger_decade", GROWTH, "Passengers at AAI-Managed Airports, 2014-15 to 2024-25", "Million", " million", DEC,
      [round(x / 1000, 2) for x in D_PAX], AR2425, f"{AR25}: Performance at a Glance (passenger movements at AAI airports; excludes JVC, state and private airports). Earlier years from AAI Annual Reports 2019-20 and 2020-21.",
      "Passengers at airports run by AAI itself, over eleven years.", "A long baseline showing growth at AAI's own network.",
      f"From {D_PAX[0] / 1000:.1f} million in 2014-15 to {D_PAX[-1] / 1000:.1f} million in 2024-25, {D_PAX[-1] / D_PAX[0]:.1f} times.", color="#58a6ff")
    S("air_aai_movements_decade", GROWTH, "Aircraft Movements, 2014-15 to 2024-25", "Thousand, all Indian airports", " thousand", DEC, D_MOV, AR2425,
      f"{AR25}: Performance at a Glance (aircraft movements); earlier years from AAI Annual Reports 2019-20 and 2020-21.",
      "Takeoffs and landings at Indian airports over eleven years.", "Movements are the flight-activity counterpart of passenger traffic.",
      f"From {D_MOV[0]:,.0f} thousand in 2014-15 to {D_MOV[-1]:,.0f} thousand in 2024-25; the 2020-21 low was {D_MOV[6]:,.0f} thousand.", color="#39c5bb")

    # ---- Domestic vs International
    M("air_history_passengers_split", TRAFFIC, "Domestic vs International Passengers, 2018-19 to 2025-26", "Million", " million", HY,
      [{"label": "Domestic", "values": H_PAX_D, "color": "#58a6ff"}, {"label": "International", "values": H_PAX_I, "color": "#ff9933"}], AR2223,
      "AAI Annual Reports 2019-20 to 2023-24 (Board's Report traffic tables) and AAI Traffic News March 2026 (2024-25 and 2025-26).",
      "Domestic and international passengers at all Indian airports, financial years.", "Shows how differently the two segments fell and recovered.",
      f"International fell to {H_PAX_I[2]:.1f} million in 2020-21 (from {H_PAX_I[0]:.1f}) and reached {H_PAX_I[-1]:.1f} million in 2025-26; domestic reached {H_PAX_D[-1]:.1f} million.")
    M("air_history_movements_split", TRAFFIC, "Domestic vs International Aircraft Movements", "Thousand, 2018-19 to 2025-26", " thousand", HY,
      [{"label": "Domestic", "values": H_MOV_D, "color": "#58a6ff"}, {"label": "International", "values": H_MOV_I, "color": "#ff9933"}], AR2223,
      "AAI Annual Reports 2019-20 to 2023-24 and AAI Traffic News March 2026, aircraft movements at all Indian airports.",
      "Domestic and international takeoffs and landings by financial year.", "Movement counts show real flight activity regardless of seat size.",
      f"International movements are {H_MOV_I[-1]:.0f} thousand in 2025-26, {_pct(H_MOV_I[-1], H_MOV_I[0]):+.1f}% against 2018-19; domestic {_pct(H_MOV_D[-1], H_MOV_D[0]):+.1f}%.", color="#58a6ff")
    intl_share = [i / t * 100 for i, t in zip(H_PAX_I, H_PAX_T)]
    S("air_international_share_trend", TRAFFIC, "International Share of Passengers", "% of all airport passengers", "%", HY, [round(x, 2) for x in intl_share],
      AR2223, "Computed from international and total passengers in AAI Annual Reports 2019-20 to 2023-24 and AAI Traffic News March 2026.",
      "International passengers as a share of all passengers.", "Tracks how quickly international travel regains its pre-pandemic weight.",
      f"{intl_share[0]:.1f}% in 2018-19, {intl_share[2]:.1f}% in 2020-21 and {intl_share[-1]:.1f}% in 2025-26.", color="#ff7b72")
    R("air_top10_intl_passengers", TRAFFIC, "Busiest International Airports (2025-26)", "International passengers, million", " million",
      {n: v[0] / 1e6 for n, v in AIRPORT_INTL_PAX.items()}, TN, f"{TN_NOTE}: airport-wise international passengers.",
      "International passengers at the ten busiest international gateways.", "International traffic is concentrated at metro and Kerala airports.", d=2)
    R("air_top10_domestic_passengers", TRAFFIC, "Busiest Domestic Airports (2025-26)", "Domestic passengers, million", " million",
      {n: v[0] / 1e6 for n, v in AIRPORT_DOM_PAX.items()}, TN, f"{TN_NOTE}: airport-wise domestic passengers.",
      "Domestic passengers at the ten busiest airports.", "Domestic traffic is dominated by the metros plus Pune and Guwahati.", d=2)
    states_intl = _top({n: v[1] / 1e6 for n, v in STATES.items()}, 10)
    R("air_state_intl_passengers", TRAFFIC, "International Passengers by State (2025-26)", "Top ten states, million", " million", states_intl, TN,
      f"{TN_NOTE}, Annexure VI: state-wise traffic (international passengers).", "International passengers by the state in which the airport is located.",
      "Shows which states are India's international gateways.", d=2, color="#ff9933")
    reg_split = [{"label": "International", "values": [round(v / 1e6, 3) for v in REG_INTL_PAX], "color": "#ff9933"},
                 {"label": "Domestic", "values": [round(v / 1e6, 3) for v in REG_DOM_PAX], "color": "#58a6ff"}]
    southern_share = REG_INTL_PAX[3] / sum(REG_INTL_PAX) * 100
    M("air_region_intl_domestic", TRAFFIC, "Domestic vs International Passengers by Region", "AAI regions, 2025-26, million", " million", REGIONS, reg_split, TN,
      f"{TN_NOTE}, Annexure V: region-wise traffic.", "Passengers in each AAI region split into domestic and international.",
      "Shows the regional balance between domestic and overseas travel.", f"Southern region has {southern_share:.1f}% of international passengers; North East is almost entirely domestic.", chart="bar")
    M("air_monthly_intl_dom_passengers", TRAFFIC, "Monthly Domestic and International Passengers", "2025 vs 2026, million", " million", MONTHS,
      [{"label": "Domestic 2025", "values": M_PAX["dom"][1], "color": "#58a6ff"}, {"label": "Domestic 2026", "values": M_PAX["dom"][0], "color": "#ff9933"},
       {"label": "International 2025", "values": M_PAX["intl"][1], "color": "#39c5bb"}, {"label": "International 2026", "values": M_PAX["intl"][0], "color": "#ff7b72"}],
      TN, "AAI monthly Traffic News reports, January to September 2026 against the same months of 2025.",
      "Monthly domestic and international passengers, this year and last.", "Shows which segment drives the monthly changes.",
      f"September 2026: domestic {M_PAX['dom'][0][8]:.2f} million ({_pct(M_PAX['dom'][0][8], M_PAX['dom'][1][8]):+.1f}%), international {M_PAX['intl'][0][8]:.2f} million ({_pct(M_PAX['intl'][0][8], M_PAX['intl'][1][8]):+.1f}%).")
    dom24 = {n: v[1] for n, v in AIRLINE_DOM.items() if v[1]}
    R("air_airline_domestic_2024", TRAFFIC, "Domestic Passengers by Airline (2024)", "Calendar year 2024, million", " million",
      {n: v / 1e6 for n, v in dom24.items()}, LS4389, "Lok Sabha Unstarred Question 4389 (27 March 2025), Ministry of Civil Aviation: domestic passengers carried by each scheduled airline, 2023 and 2024.",
      "Domestic passengers carried by each Indian scheduled airline in 2024.", "Airline concentration shapes fares and capacity.", d=2,
      read=f"IndiGo carried {dom24['IndiGo'] / 1e6:.1f} million, {dom24['IndiGo'] / AIRLINE_DOM_TOTAL[1] * 100:.1f}% of the {AIRLINE_DOM_TOTAL[1] / 1e6:.1f} million total.")
    share_top = _top(dom24, 6)
    share = {n: v / 1e6 for n, v in share_top.items()}
    share["Others"] = (AIRLINE_DOM_TOTAL[1] - sum(share_top.values())) / 1e6
    R("air_airline_market_share_2024", TRAFFIC, "Domestic Airline Market Share (2024)", "Share of 161.3 million domestic passengers", " million", share, LS4389,
      "Lok Sabha Unstarred Question 4389 (27 March 2025): airline-wise domestic passengers; shown are the six largest airlines and all others combined (grand total from the annexure).",
      "Each airline's share of domestic passengers in 2024.", "Market share shows how competitive the domestic market is.", chart="doughnut", d=2,
      read=f"IndiGo holds {dom24['IndiGo'] / AIRLINE_DOM_TOTAL[1] * 100:.1f}% and Air India {dom24['Air India'] / AIRLINE_DOM_TOTAL[1] * 100:.1f}%.")
    both = {n: _pct(v[1], v[0]) for n, v in AIRLINE_DOM.items() if v[0] >= 1_000_000 and v[1]}
    R("air_airline_growth_2024", TRAFFIC, "Airline Domestic Passenger Growth (2024 vs 2023)", "Airlines with over 1 million passengers in 2023", "%", both, LS4389,
      "Lok Sabha Unstarred Question 4389: percentage change computed from each airline's 2023 and 2024 domestic passengers (airlines under 1 million in 2023 or absent in 2024 are left out).",
      "Year-on-year change in each large airline's domestic passengers.", "Shows which airlines gained and lost domestic traffic.",
      color="#3fb950", read=f"Air India grew {both['Air India']:+.1f}%, IndiGo {both['IndiGo']:+.1f}% and SpiceJet {both['SpiceJet']:+.1f}%.")
    M("air_domestic_quarterly", TRAFFIC, "Domestic Passengers by Quarter", "2023 vs 2024, million", " million", ["Jan-Mar", "Apr-Jun", "Jul-Sep", "Oct-Dec"],
      [{"label": "2023", "values": [round(v / 1e6, 3) for v in QTR_DOM[0]], "color": "#58a6ff"}, {"label": "2024", "values": [round(v / 1e6, 3) for v in QTR_DOM[1]], "color": "#ff9933"}],
      LS4389, "Lok Sabha Unstarred Question 4389: quarterly domestic passengers, grand totals for 2023 and 2024.",
      "Domestic passengers in each calendar quarter.", "Shows the winter peak in October-December.",
      f"2024 total {sum(QTR_DOM[1]) / 1e6:.1f} million, {_pct(sum(QTR_DOM[1]), sum(QTR_DOM[0])):+.1f}% on 2023; the October-December quarter was highest at {QTR_DOM[1][3] / 1e6:.1f} million.", chart="bar")
    intl25 = {n: v[1] / 1e6 for n, v in AIRLINE_FY25.items() if v[1]}
    R("air_airline_international_fy25", TRAFFIC, "International Passengers by Airline (2024-25)", "Provisional, up to October 2024, million", " million", intl25, RS2260,
      "Rajya Sabha Unstarred Question 2260 (16 December 2024), Ministry of Civil Aviation: operator-wise domestic and international passengers for 2024-25 (provisional).",
      "International passengers carried by Indian airlines in 2024-25.", "Shows how concentrated overseas flying is among a few carriers.", d=2, color="#ff9933",
      read=f"IndiGo carried {intl25['IndiGo']:.1f} million of {AIRLINE_FY25_TOTAL[1] / 1e6:.1f} million; Air India group airlines carried {intl25['Air India'] + intl25['Air India Express']:.1f} million.")
    R("air_otp_2024", TRAFFIC, "On-Time Performance by Airline (2024)", "% of flights on time", "%", OTP_2024, RS2419,
      "Rajya Sabha Unstarred Question 2419 (11 August 2025), Ministry of Civil Aviation: on-time performance of scheduled airlines, calendar 2024.",
      "Share of flights that left on schedule, by airline.", "Punctuality is a core passenger-experience measure.", color="#3fb950", d=1)
    R("air_otp_2025", TRAFFIC, "On-Time Performance by Airline (2025 to 30 June)", "% of flights on time", "%", OTP_2025, RS2419,
      "Rajya Sabha Unstarred Question 2419: on-time performance, January to 30 June 2025; Air India Group includes Air India Express.",
      "Share of flights that left on schedule in the first half of 2025.", "Shows whether punctuality has improved since 2024.", color="#3fb950", d=1)
    R("air_cancellation_2024", TRAFFIC, "Flight Cancellation Rate by Airline (2024)", "% of scheduled flights cancelled", "%", CANCEL_2024, RS2419,
      "Rajya Sabha Unstarred Question 2419: cancellation rates of scheduled airlines, calendar 2024.", "Share of scheduled flights cancelled.",
      "High cancellation rates mark weaker regional operators.", color="#ff7b72", d=1)
    R("air_cancellation_2025", TRAFFIC, "Flight Cancellation Rate by Airline (2025 to 30 June)", "% of scheduled flights cancelled", "%", CANCEL_2025, RS2419,
      "Rajya Sabha Unstarred Question 2419: cancellation rates, January to 30 June 2025; Air India Group includes Air India Express.",
      "Share of scheduled flights cancelled in the first half of 2025.", "Compares reliability across airlines.", color="#ff7b72", d=1)

    # ---- Airports & UDAN
    R("air_top10_airport_movements", AIRPORTS, "Busiest Airports by Aircraft Movements (2025-26)", "Takeoffs and landings, thousand", " thousand",
      {n: v[0] / 1e3 for n, v in AIRPORT_MOVEMENTS.items()}, TN, f"{TN_NOTE}: airport-wise aircraft movements.",
      "Aircraft movements at the ten busiest Indian airports.", "Movements show runway load, the binding constraint at hubs.", d=1, color="#39c5bb")
    R("air_category_passenger_share", AIRPORTS, "Passengers by Airport Category (2025-26)", "Share of 420.09 million passengers", " million",
      {n: v / 1e6 for n, v in zip(CATEGORIES, CAT_PAX[0])}, TN, f"{TN_NOTE}, Annexure I: traffic by airport category.",
      "Which kinds of airport handle India's passengers.", "Private JV hubs dominate traffic while most airports are small.", chart="doughnut", d=1,
      read=f"JV international airports handle {CAT_PAX[0][2] / sum(CAT_PAX[0]) * 100:.1f}%; domestic and state-run domestic airports together only {(CAT_PAX[0][5] + CAT_PAX[0][6]) / sum(CAT_PAX[0]) * 100:.1f}%.")
    M("air_category_movements", AIRPORTS, "Aircraft Movements by Airport Category", "2024-25 vs 2025-26, thousand", " thousand", CATEGORIES,
      [{"label": "2024-25", "values": [round(v / 1e3, 3) for v in CAT_MOV[1]], "color": "#58a6ff"}, {"label": "2025-26", "values": [round(v / 1e3, 3) for v in CAT_MOV[0]], "color": "#ff9933"}],
      TN, f"{TN_NOTE}, Annexure I: aircraft movements by airport category.", "Takeoffs and landings by airport category.", "Shows where flying activity is growing.",
      f"JV international airports had {CAT_MOV[0][2] / 1e3:,.0f} thousand movements ({_pct(CAT_MOV[0][2], CAT_MOV[1][2]):+.1f}%).", chart="bar", color="#39c5bb")
    R("air_region_passenger_share", AIRPORTS, "Passengers by AAI Region (2025-26)", "Share of 420.09 million passengers", " million",
      dict(zip(REGIONS, [v / 1e6 for v in REG_PAX[0]])), TN, f"{TN_NOTE}, Annexure V: region-wise traffic.",
      "Passenger traffic by AAI region.", "Shows the regional balance of air travel.", chart="doughnut", d=1,
      read=f"Southern region handles {REG_PAX[0][3] / sum(REG_PAX[0]) * 100:.1f}% and Northern {REG_PAX[0][2] / sum(REG_PAX[0]) * 100:.1f}%; North East {REG_PAX[0][1] / sum(REG_PAX[0]) * 100:.1f}%.")
    reg_mov = {n: _pct(a, b) for n, a, b in zip(REGIONS, *REG_MOV)}
    R("air_region_movement_growth", AIRPORTS, "Aircraft Movement Growth by Region (2025-26)", "Change on 2024-25", "%", reg_mov, TN,
      f"{TN_NOTE}, Annexure V: region-wise aircraft movements; percentage change computed.", "Change in aircraft movements by AAI region.",
      "Shows which regions are adding flight activity.", color="#3fb950", d=1,
      read=f"Eastern grew {reg_mov['Eastern']:+.1f}% while Northern changed {reg_mov['Northern']:+.1f}% and North East {reg_mov['North East']:+.1f}%.")
    states_pax = _top({n: (v[1] + v[2]) / 1e6 for n, v in STATES.items()}, 10)
    R("air_state_passengers", AIRPORTS, "Passengers by State (2025-26)", "Top ten states, million", " million", states_pax, TN,
      f"{TN_NOTE}, Annexure VI: state-wise traffic (domestic plus international).", "Total passengers at airports in each state.",
      "Shows which states generate the most air travel.", d=1,
      read=f"Delhi leads with {states_pax['Delhi']:.1f} million; the top ten states handle {sum(states_pax.values()) / (NATIONAL_2526['passengers'] / 1e6) * 100:.1f}% of national passengers.")
    top5 = _top({n: v[0] / 1e6 for n, v in AIRPORT_PASSENGERS.items()}, 5)
    top5["All other airports"] = NATIONAL_2526["passengers"] / 1e6 - sum(top5.values())
    R("air_top5_airport_share", AIRPORTS, "Top Five Airports' Share of Passengers (2025-26)", "Share of 420.09 million passengers", " million", top5, TN,
      f"{TN_NOTE}: airport-wise passengers against the all-India total of 420,089,356.", "How much of India's traffic the five busiest airports carry.",
      "Concentration drives the case for new airports.", chart="doughnut", d=1,
      read=f"The top five handle {sum(v for n, v in top5.items() if n != 'All other airports') / (NATIONAL_2526['passengers'] / 1e6) * 100:.1f}% of passengers; 140 other airports share the rest.")
    M("air_udan_spend", AIRPORTS, "UDAN Expenditure by Year", "Rs crore, Phase-I and Phase-II", " Rs crore", UDAN_YEARS,
      [{"label": "Phase-I", "values": UDAN_PHASE1, "color": "#ff9933"}, {"label": "Phase-II", "values": UDAN_PHASE2, "color": "#58a6ff"}], LS2858,
      "Lok Sabha Unstarred Question 2858 (8 August 2024), Ministry of Civil Aviation, Annexure: budget allocated and utilised under UDAN. Phase-I allocation Rs 4,500 crore, Phase-II Rs 1,000 crore.",
      "Money spent each year on reviving airports and heliports under UDAN.", "Shows the pace of regional airport investment.",
      f"Spending peaked at Rs {max(UDAN_PHASE1):,.2f} crore in 2022-23; cumulative expenditure is Rs {UDAN_EXPENDITURE_TOTAL:,.2f} crore.", chart="bar")
    S("air_udan_vgf", AIRPORTS, "UDAN Viability Gap Funding by Year", "Rs crore disbursed to airlines", " Rs crore", UDAN_VGF_YEARS, UDAN_VGF, LS2858,
      "Lok Sabha Unstarred Question 2858: VGF disbursed in RACFT from 2017 to 31 July 2024; 2023-24 is provisional, 2024-25 covers April-July.",
      "Subsidy paid to airlines to operate regional routes.", "VGF is the main running cost of the regional connectivity scheme.",
      f"Rs {max(UDAN_VGF):,.2f} crore was disbursed in 2022-23, the peak; the total to July 2024 is Rs {UDAN_VGF_TOTAL:,.2f} crore.", chart="bar", color="#bc8cff")
    R("air_udan_route_status", AIRPORTS, "UDAN Routes: Awarded, Operational, Discontinued", "As on 8 August 2024", " routes", UDAN_ROUTES, LS2858,
      "Lok Sabha Unstarred Question 2858: 870 valid routes awarded, 579 operationalised connecting 85 airports (13 heliports, 2 water aerodromes); 106 discontinued before the three-year tenure ended.",
      "Status of routes awarded under the Regional Connectivity Scheme.", "Many awarded routes never start or end early.", color="#ff7b72", d=0,
      read=f"{579 / 870 * 100:.1f}% of awarded routes are operational; 106 routes were discontinued early.")
    R("air_aai_network_breakdown", AIRPORTS, "AAI Operational Airports by Type", "Annual Report 2024-25", " airports", AAI_NETWORK, AR2425,
      f"{AR25}: Corporate overview, Operational AAI Airports (113 total; 29 civil enclaves, 38 with international operations and 8 under private control are out of the 113).",
      "Number of airports AAI operates and how many are civil enclaves, international or privately run.", "Shows the structure of AAI's network.", d=0, color="#39c5bb",
      read="Of 113 operational AAI airports, 38 handle international flights, 29 are civil enclaves in defence airfields and 8 are privately operated.")

    # ---- Air Cargo
    R("air_top10_airport_freight", CARGO, "Busiest Airports by Freight (2025-26)", "Thousand tonnes", " thousand tonnes",
      {n: v[0] / 1e3 for n, v in AIRPORT_FREIGHT.items()}, TN, f"{TN_NOTE}: airport-wise freight (domestic plus international).",
      "Air freight handled at the ten busiest cargo airports.", "Cargo is even more concentrated than passenger traffic.", d=1,
      read=f"Delhi handled {AIRPORT_FREIGHT['Delhi'][0] / 1e3:,.0f} thousand tonnes and Mumbai {AIRPORT_FREIGHT['Mumbai'][0] / 1e3:,.0f}: together {(AIRPORT_FREIGHT['Delhi'][0] + AIRPORT_FREIGHT['Mumbai'][0]) / (NATIONAL_2526['freight_t']) * 100:.1f}% of national freight.")
    fr_growth = growth(AIRPORT_FREIGHT)
    M("air_airport_freight_yoy", CARGO, "Airport Freight: 2024-25 vs 2025-26", "Thousand tonnes, top ten airports", " thousand tonnes", list(AIRPORT_FREIGHT),
      two_year(AIRPORT_FREIGHT, 1e3), TN, f"{TN_NOTE}: airport-wise freight.", "Freight at each of the ten busiest cargo airports in two years.",
      "Shows which cargo hubs are expanding.", f"Pune grew {fr_growth['Pune']:+.1f}% and Chennai {fr_growth['Chennai']:+.1f}%; Delhi {fr_growth['Delhi']:+.1f}%.", chart="bar")
    R("air_airport_freight_growth_pct", CARGO, "Freight Growth by Airport (2025-26)", "Change on 2024-25, top ten airports", "%", fr_growth, TN,
      f"{TN_NOTE}: percentage change computed from airport-wise freight.", "Year-on-year change in freight at the ten busiest cargo airports.",
      "Highlights fast-rising cargo airports.", color="#3fb950", d=1,
      read=f"Fastest: {max(fr_growth, key=fr_growth.get)} {max(fr_growth.values()):+.1f}%; slowest: {min(fr_growth, key=fr_growth.get)} {min(fr_growth.values()):+.1f}%.")
    R("air_top_intl_freight", CARGO, "International Freight by Airport (2025-26)", "Thousand tonnes", " thousand tonnes",
      {n: v[0] / 1e3 for n, v in AIRPORT_INTL_FREIGHT.items()}, TN, f"{TN_NOTE}, Annexure IV: international freight by airport.",
      "International air freight at the ten leading gateways.", "Most export and import cargo moves through four airports.", d=1,
      read=f"Delhi {AIRPORT_INTL_FREIGHT['Delhi'][0] / 1e3:,.0f}, Mumbai {AIRPORT_INTL_FREIGHT['Mumbai'][0] / 1e3:,.0f}, Bengaluru and Chennai lead; the top four are {sum(v[0] for n, v in list(AIRPORT_INTL_FREIGHT.items())[:4]) / (H_FR_I[-1] * 1e3) * 100:.1f}% of India's international freight.")
    R("air_category_freight_share", CARGO, "Freight by Airport Category (2025-26)", "Share of 3.96 million tonnes", " thousand tonnes",
      {n: v / 1e3 for n, v in zip(CATEGORIES, CAT_FREIGHT)}, TN, f"{TN_NOTE}, Annexure I: freight by airport category.",
      "Which airport categories carry India's air freight.", "Cargo is overwhelmingly handled by the JV hubs.", chart="doughnut", d=1,
      read=f"JV international airports handle {CAT_FREIGHT[2] / sum(CAT_FREIGHT) * 100:.1f}% of freight.")
    fr_reg = {n: _pct(a, b) for n, a, b in zip(REGIONS, *REG_FREIGHT)}
    M("air_region_freight", CARGO, "Freight by AAI Region", "2024-25 vs 2025-26, thousand tonnes", " thousand tonnes", REGIONS,
      [{"label": "2024-25", "values": [round(v / 1e3, 3) for v in REG_FREIGHT[1]], "color": "#58a6ff"}, {"label": "2025-26", "values": [round(v / 1e3, 3) for v in REG_FREIGHT[0]], "color": "#ff9933"}],
      TN, f"{TN_NOTE}, Annexure V: region-wise freight.", "Air freight in each AAI region.", "Shows regional cargo capacity.",
      f"Southern {REG_FREIGHT[0][3] / 1e3:,.0f} thousand tonnes ({fr_reg['Southern']:+.1f}%) and Northern {REG_FREIGHT[0][2] / 1e3:,.0f} ({fr_reg['Northern']:+.1f}%) lead.", chart="bar")
    state_fr = _top({n: (v[3] + v[4]) / 1e3 for n, v in STATES.items()}, 10)
    R("air_state_freight", CARGO, "Freight by State (2025-26)", "Top ten states, thousand tonnes", " thousand tonnes", state_fr, TN,
      f"{TN_NOTE}, Annexure VI: state-wise freight.", "Air freight handled in each state.", "Shows where cargo flows concentrate.", d=1,
      read=f"Delhi {state_fr['Delhi']:,.0f} and Maharashtra {state_fr['Maharashtra']:,.0f} thousand tonnes lead the table.")
    M("air_history_freight", CARGO, "Air Freight at Indian Airports, 2018-19 to 2025-26", "Thousand tonnes", " thousand tonnes", HY,
      [{"label": "International", "values": H_FR_I, "color": "#ff9933"}, {"label": "Domestic", "values": H_FR_D, "color": "#58a6ff"}], AR2223,
      "AAI Annual Reports 2019-20 to 2023-24 (Board's Report) and AAI Traffic News March 2026, freight at all Indian airports.",
      "International and domestic air freight by financial year.", "Cargo held up far better than passengers during the pandemic.",
      f"Total freight dipped to {H_FR_T[2]:,.0f} thousand tonnes in 2020-21 and reached {H_FR_T[-1]:,.0f} thousand tonnes in 2025-26, {_pct(H_FR_T[-1], H_FR_T[0]):+.1f}% against 2018-19.")
    fr_yoy = [_pct(H_FR_T[i], H_FR_T[i - 1]) for i in range(1, len(HY))]
    S("air_history_freight_yoy", CARGO, "Yearly Freight Growth, 2019-20 to 2025-26", "Change on previous financial year", "%", HY[1:], [round(x, 2) for x in fr_yoy], AR2223,
      "Computed from total freight: AAI Annual Reports 2019-20 to 2023-24 and AAI Traffic News March 2026.", "Year-on-year growth in air freight.",
      "Shows the cargo cycle through the pandemic.", f"Freight fell {fr_yoy[1]:.1f}% in 2020-21, rose {fr_yoy[2]:+.1f}% in 2021-22 and {fr_yoy[-1]:+.1f}% in 2025-26.", chart="bar", color="#3fb950")
    intl_fr_share = [i / t * 100 for i, t in zip(H_FR_I, H_FR_T)]
    S("air_international_freight_share", CARGO, "International Share of Air Freight", "% of all freight", "%", HY, [round(x, 2) for x in intl_fr_share], AR2223,
      "Computed from international and total freight: AAI Annual Reports 2019-20 to 2023-24 and AAI Traffic News March 2026.", "International freight as a share of all freight handled.",
      "International cargo is the bigger part of Indian air freight.", f"{intl_fr_share[0]:.1f}% in 2018-19 and {intl_fr_share[-1]:.1f}% in 2025-26.", color="#ff7b72")
    S("air_aai_cargo_2014_2020", CARGO, "Cargo at AAI Airports, 2014-15 to 2019-20", "Thousand tonnes", " thousand tonnes", DEC[:6], D_CARGO, AAI_REPORTS_URL,
      "AAI Annual Report 2019-20 and 2020-21, Performance at a Glance: cargo handled at AAI airports (later reports stop reporting this line).",
      "Cargo handled at airports operated by AAI.", "A pre-pandemic baseline for cargo at AAI's own network.",
      f"Rose from {D_CARGO[0]:.0f} to {D_CARGO[4]:.0f} thousand tonnes by 2018-19, then eased to {D_CARGO[5]:.0f}.", color="#58a6ff")
    M("air_monthly_freight", CARGO, "Monthly Air Freight: 2026 vs 2025", "January to September, thousand tonnes", " thousand tonnes", MONTHS,
      [{"label": "2025", "values": M_FREIGHT["total"][1], "color": "#58a6ff"}, {"label": "2026", "values": M_FREIGHT["total"][0], "color": "#ff9933"}], TN,
      "AAI monthly Traffic News reports, January to September 2026 against the same months of 2025, total freight.", "Total air freight handled each month.",
      "Shows whether the cargo boom is persistent.", f"September 2026 freight was {M_FREIGHT['total'][0][8]:.1f} thousand tonnes, {_pct(M_FREIGHT['total'][0][8], M_FREIGHT['total'][1][8]):+.1f}% on a year earlier.")
    M("air_monthly_freight_split", CARGO, "Monthly Freight: International vs Domestic", "2026, thousand tonnes", " thousand tonnes", MONTHS,
      [{"label": "International", "values": M_FREIGHT["intl"][0], "color": "#ff9933"}, {"label": "Domestic", "values": M_FREIGHT["dom"][0], "color": "#58a6ff"}], TN,
      "AAI monthly Traffic News reports, January to September 2026.", "International and domestic freight each month of 2026.", "International freight is growing the fastest.",
      f"International freight rose from {M_FREIGHT['intl'][0][0]:.0f} thousand tonnes in January to {M_FREIGHT['intl'][0][8]:.0f} in September.")
    top5f = _top({n: v[0] / 1e3 for n, v in AIRPORT_FREIGHT.items()}, 5)
    top5f["All other airports"] = NATIONAL_2526["freight_t"] / 1e3 - sum(top5f.values())
    R("air_top5_airport_freight_share", CARGO, "Top Five Airports' Share of Freight (2025-26)", "Share of 3.96 million tonnes", " thousand tonnes", top5f, TN,
      f"{TN_NOTE}: airport-wise freight against the national total of 3,964,346.6 tonnes.", "How much of India's freight the five busiest cargo airports carry.",
      "Cargo capacity is concentrated.", chart="doughnut", d=1,
      read=f"The top five handle {sum(v for n, v in top5f.items() if n != 'All other airports') / (NATIONAL_2526['freight_t'] / 1e3) * 100:.1f}% of freight.")

    # ---- AAI Finance & Investment
    pbt_margin = [p / r * 100 for p, r in zip(D_PBT, D_REV)]
    M("air_aai_decade_income", FINANCE, "AAI Income and Profit, 2014-15 to 2024-25", "Rs crore", " Rs crore", DEC,
      [{"label": "Revenue", "values": D_REV, "color": "#ff9933"}, {"label": "Expenditure", "values": D_EXP, "color": "#ff7b72"},
       {"label": "Profit before tax", "values": D_PBT, "color": "#3fb950"}, {"label": "Profit after tax", "values": D_PAT, "color": "#58a6ff"}], AR2425,
      f"{AR25}: Performance at a Glance; earlier years from AAI Annual Reports 2019-20 and 2020-21. Revenue less expenditure equals profit before tax in every year.",
      "AAI revenue, expenditure and profit over eleven years.", "Shows the pandemic loss and the record profits since.",
      f"Revenue reached Rs {D_REV[-1]:,.0f} crore and profit after tax Rs {D_PAT[-1]:,.0f} crore in 2024-25; 2020-21 was a Rs {-D_PAT[6]:,.0f} crore loss.", chart="bar")
    S("air_aai_pbt_margin", FINANCE, "AAI Pre-Tax Profit Margin", "Profit before tax as % of revenue", "%", DEC, [round(x, 2) for x in pbt_margin], AR2425,
      f"Computed from revenue and profit before tax, {AR25}: Performance at a Glance (and AAI Annual Reports 2019-20 and 2020-21).", "How much of each rupee of revenue turns into pre-tax profit.",
      "Margin shows efficiency beyond raw growth.", f"Margin was {pbt_margin[0]:.1f}% in 2014-15, {pbt_margin[6]:.1f}% in 2020-21 and {pbt_margin[-1]:.1f}% in 2024-25.", color="#3fb950")
    M("air_aai_capex_decade", FINANCE, "AAI Capital Expenditure, 2014-15 to 2024-25", "Rs crore, actual spend", " Rs crore", DEC,
      [{"label": "Actual capital expenditure", "values": D_CAPEX, "color": "#ff9933"}], AR2425,
      f"{AR25}: Performance at a Glance and Board's Report (capital expenditure Rs 5,568.55 crore in 2024-25); earlier years from AAI Annual Reports 2019-20 and 2020-21.",
      "AAI's actual capital expenditure every year.", "Capital expenditure builds terminals, runways and air navigation capacity.",
      f"Spending rose from Rs {D_CAPEX[0]:,.0f} crore to a record Rs {D_CAPEX[-1]:,.0f} crore, {D_CAPEX[-1] / D_CAPEX[0]:.1f} times.", chart="bar", color="#58a6ff")
    funded = {k: v for k, v in CAPEX_FUNDING.items()}
    M("air_aai_capex_funding", FINANCE, "How AAI Funds Its Capital Expenditure", "Rs crore by source, 2018-19 to 2024-25", " Rs crore", FY7,
      [{"label": k, "values": v} for k, v in funded.items()], AR2425,
      "AAI Annual Reports 2018-19 to 2024-25 (Board's Report, capital expenditure by source of funds). Sources sum to total actual capital expenditure in each year.",
      "Capital expenditure split by internal resources, grants, budget support and borrowing.", "Shows how reliant AAI is on its own cash.",
      f"Internal resources funded Rs {funded['Internal resources'][-1]:,.0f} crore in 2024-25; commercial borrowings were used in 2020-21 to 2022-23.", chart="bar")
    f2122 = {k: v[3] for k, v in funded.items()}
    R("air_aai_capex_funding_2021_22", FINANCE, "Capex Funding Mix (2021-22)", "Rs crore by source", " Rs crore", f2122, AR2223,
      "AAI Annual Report 2021-22 (Board's Report): capital expenditure by source of funds, total Rs 3,724.34 crore.", "Sources of AAI's capital spending in 2021-22.",
      "A pandemic year when internal resources fell and borrowing rose.", chart="doughnut", d=1,
      read=f"Commercial borrowings funded {f2122['Commercial borrowings'] / sum(f2122.values()) * 100:.1f}% against {f2122['Internal resources'] / sum(f2122.values()) * 100:.1f}% from internal resources.")
    S("air_aai_employees", FINANCE, "AAI Employees, 2014-15 to 2024-25", "Number of employees", " employees", DEC, D_EMP, AR2425,
      f"{AR25}: Performance at a Glance (employees); earlier years from AAI Annual Reports 2019-20 and 2020-21.", "AAI's workforce.", "Traffic has grown far faster than the workforce.",
      f"Staff {D_EMP[0]:,} in 2014-15 and {D_EMP[-1]:,} in 2024-25 while movements rose {_pct(D_MOV[-1], D_MOV[0]):.0f}%.", color="#58a6ff")
    S("air_aai_movements_per_employee", FINANCE, "Aircraft Movements per AAI Employee", "Productivity, 2014-15 to 2024-25", " movements", DEC, D_MOV_EMP, AR2425,
      f"{AR25}: Performance at a Glance (aircraft movements per employee).", "Annual movements handled per AAI employee.", "A simple productivity measure.",
      f"{D_MOV_EMP[0]} in 2014-15, {D_MOV_EMP[6]} in 2020-21 and {D_MOV_EMP[-1]} in 2024-25.", color="#39c5bb")
    S("air_aai_revenue_per_employee", FINANCE, "AAI Revenue per Employee", "Rs thousand, 2014-15 to 2024-25", " Rs thousand", DEC, D_REV_EMP, AR2425,
      f"{AR25}: Performance at a Glance (revenue per employee).", "Annual AAI revenue per employee.", "Shows financial productivity.",
      f"Rs {D_REV_EMP[0]:,} thousand in 2014-15 rising to Rs {D_REV_EMP[-1]:,} thousand in 2024-25.", color="#ff9933")
    M("air_aai_networth_wip", FINANCE, "AAI Net Worth and Capital Work-in-Progress", "Rs crore, 2014-15 to 2024-25", " Rs crore", DEC,
      [{"label": "Net worth", "values": D_NETWORTH, "color": "#3fb950"}, {"label": "Capital work-in-progress", "values": D_CWIP, "color": "#ff9933"}], AR2425,
      f"{AR25}: Performance at a Glance (net worth, capital WIP); earlier years from AAI Annual Reports 2019-20 and 2020-21.", "AAI's net worth and projects still under construction.",
      "Net worth shows financial strength; work-in-progress shows pending projects.", f"Net worth reached Rs {D_NETWORTH[-1]:,.0f} crore in 2024-25, up from Rs {D_NETWORTH[0]:,.0f} crore.")
    S("air_aai_dividend", FINANCE, "AAI Dividend Paid, 2014-15 to 2024-25", "Rs crore, including interim dividend", " Rs crore", DEC, D_DIVIDEND, AR2425,
      f"{AR25}: Performance at a Glance (dividend including interim). The report shows no dividend ('-') in 2020-21 and 2021-22, plotted as zero.", "Dividend AAI paid to the Government of India.",
      "Dividends are the Government's direct return from AAI.", f"Dividend reached Rs {D_DIVIDEND[-1]:,.0f} crore in 2024-25, with none in 2020-21 and 2021-22.", chart="bar", color="#bc8cff")
    S("air_aai_borrowings", FINANCE, "AAI Borrowings (Loans from Others)", "Rs crore, 2014-15 to 2024-25", " Rs crore", DEC, D_LOANS, AR2425,
      f"{AR25}: Performance at a Glance (loans - others).", "Loans AAI has outstanding from lenders other than the Government.", "Shows how AAI financed the pandemic years.",
      f"Peaked at Rs {max(D_LOANS):,.0f} crore in 2021-22 and stood at Rs {D_LOANS[-1]:,.0f} crore in 2024-25.", color="#ff7b72")
    M("air_aai_revenue_mix", FINANCE, "AAI Revenue by Source, 2018-19 to 2022-23", "Rs crore", " Rs crore", FY5, [{"label": k, "values": v} for k, v in REVENUE_MIX.items()], AR2223,
      "AAI Annual Report 2022-23 (Board's Report, income analysis) and earlier reports; components sum to total revenue within rounding.", "AAI revenue by source: navigation, airport services, non-aeronautical, JVC lease, PPP fees and other income.",
      "Shows how AAI earns its money and how it depends on lease income.", f"Air navigation services earned Rs {REVENUE_MIX['Air navigation services'][-1]:,.0f} crore in 2022-23; JVC lease Rs {REVENUE_MIX['JVC lease'][-1]:,.0f} crore.", chart="bar")
    mix22 = {k: v[-1] for k, v in REVENUE_MIX.items()}
    R("air_aai_revenue_mix_2022_23", FINANCE, "AAI Revenue Mix (2022-23)", "Share of Rs 12,172 crore", " Rs crore", mix22, AR2223,
      "AAI Annual Report 2022-23: income analysis; components sum to total revenue Rs 12,172.35 crore.", "Where AAI's 2022-23 revenue came from.",
      "A quarter of revenue is lease income from private airports.", chart="doughnut", d=1,
      read=f"Air navigation is {mix22['Air navigation services'] / sum(mix22.values()) * 100:.1f}% and JVC lease {mix22['JVC lease'] / sum(mix22.values()) * 100:.1f}% of revenue.")
    S("air_aai_non_aero_revenue", FINANCE, "AAI Non-Aeronautical Revenue", "Rs crore, 2018-19 to 2024-25", " Rs crore", FY7, NON_AERO, AR2425,
      f"AAI Annual Reports 2018-19 to 2022-23 (income analysis) and {AR25} (non-aeronautical revenue).", "Revenue from retail, parking, advertising and rentals at airports.",
      "Commercial income reduces reliance on aeronautical charges.", f"Rs {NON_AERO[-1]:,.0f} crore in 2024-25, {NON_AERO[-1] / NON_AERO[0]:.2f} times 2018-19.", color="#39c5bb")
    S("air_aai_ppp_fees", FINANCE, "AAI PPP Airport Concession Fees", "Rs crore, 2020-21 to 2024-25", " Rs crore", HY[2:7], PPP_FEES, AR2425,
      f"AAI Annual Reports 2020-21 to 2022-23 and {AR25} (revenue from PPP airports). The 2024-25 figure includes a one-time Rs 2,231.80 crore under-recovery from six PPP airports.",
      "Fees AAI receives from the six leased PPP airports.", "Shows how privatised airports feed AAI revenue.",
      f"Rs {PPP_FEES[0]:,.0f} crore in 2020-21 to Rs {PPP_FEES[-1]:,.0f} crore in 2024-25, boosted by the one-off recovery.", chart="bar", color="#bc8cff")
    M("air_aai_operating_vs_other_income", FINANCE, "AAI Operating Revenue vs Other Income", "Rs crore, 2019-20 to 2024-25", " Rs crore", HY[1:7],
      [{"label": "Revenue from operations", "values": OPS_REVENUE, "color": "#ff9933"}, {"label": "Other income", "values": OTHER_INCOME, "color": "#58a6ff"}], AR2425,
      f"AAI Annual Reports 2019-20 to 2024-25 (statement of profit and loss, {AR25}).", "AAI's operating revenue and other income.", "Most income is from operations.",
      f"Operating revenue Rs {OPS_REVENUE[-1]:,.0f} crore and other income Rs {OTHER_INCOME[-1]:,.0f} crore in 2024-25.", chart="bar")
    M("air_aai_cost_structure", FINANCE, "AAI Cost Structure", "Rs crore, 2023-24 and 2024-25", " Rs crore", list(COSTS),
      [{"label": "2023-24", "values": [v[0] for v in COSTS.values()], "color": "#58a6ff"}, {"label": "2024-25", "values": [v[1] for v in COSTS.values()], "color": "#ff9933"}], AR2425,
      f"{AR25}: Board's Report, expenditure analysis; the three heads sum to total expenditure (Rs 9,765.83 crore in 2023-24, Rs 10,992.79 crore in 2024-25).",
      "AAI's expenditure split into operating costs, finance costs and depreciation.", "Shows how costs grow with capital investment.",
      f"Operating costs are {COSTS['Operating costs'][1] / sum(v[1] for v in COSTS.values()) * 100:.1f}% of 2024-25 expenditure; depreciation rose {_pct(COSTS['Depreciation'][1], COSTS['Depreciation'][0]):.1f}%.", chart="bar")


AAI_REPORTS_URL = "https://www.aai.aero/en/business-opportunities/investors-annual-reports"


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

    def world(code):
        # World aggregate needs its own request so the peer charts never see WLD.
        if "W" + code not in cache:
            cache["W" + code] = wb_observations(get_json, ("IND", "WLD"), code)
        return cache["W" + code]

    def share(key, code, title, what, why):
        def build():
            data = world(code)
            years = sorted(set(data.get("IND", {})) & set(data.get("WLD", {})), key=int)
            if len(years) < 2:
                raise ValueError(f"no India/world overlap for {code}")
            values = [round(data["IND"][y] / data["WLD"][y] * 100, 3) for y in years]
            top = max(range(len(values)), key=values.__getitem__)
            return single(key, years, values, source=WB_PAGE.format(code=code), unit="%",
                          note=f"World Bank indicator {code} (ICAO data): India's value divided by the world aggregate (WLD), computed for each year both are reported.",
                          meta_=_m(CARGO if code == wb_cargo else GLOBAL, title, "India as % of the world total", "%", "#ff9933", what=what, why=why,
                                   read=f"{values[0]:.2f}% in {years[0]}, a peak of {values[top]:.2f}% in {years[top]} and {values[-1]:.2f}% in {years[-1]}."))
        return key, build

    def recovery(key):
        def build():
            data = fetch(wb_pax)
            at = {NAMES[i]: rows["2023"] / rows["2019"] * 100 for i, rows in data.items() if "2023" in rows and "2019" in rows}
            if "India" not in at or len(at) < 4:
                raise ValueError("too few countries for recovery")
            rank = [n for n, _ in sorted(at.items(), key=lambda item: -item[1])].index("India") + 1
            return ranked(key, at, source=WB_PAGE.format(code=wb_pax), unit="% of 2019", chart="bar",
                          note=f"World Bank indicator {wb_pax}: 2023 passengers divided by 2019 passengers, computed. India ranks {rank} of {len(at)}.",
                          meta_=_m(GLOBAL, "Passenger Recovery: 2023 as % of 2019", "Registered-carrier passengers, 2019 = 100", "% of 2019", "#3fb950",
                                   what="Passengers carried in 2023 relative to the pre-pandemic year 2019.", why="Shows which aviation markets have fully recovered.",
                                   read=f"India stands at {at['India']:.1f}% of its 2019 level, rank {rank} of {len(at)}."))
        return key, build

    def index_lines(key):
        def build():
            data = fetch(wb_pax)
            years = [y for y in sorted({y for iso in LINE_PEERS for y in data.get(iso, {})}, key=int) if int(y) >= 2019]
            sets = [{"label": NAMES[iso], "color": LINE_COLORS[i],
                     "values": [round(data[iso][y] / data[iso]["2019"] * 100, 2) if y in data[iso] and "2019" in data[iso] else None for y in years]}
                    for i, iso in enumerate(LINE_PEERS) if iso in data and "2019" in data[iso]]
            if not sets or sets[0]["label"] != "India":
                raise ValueError("India missing for passenger index")
            last = next(v for v in reversed(sets[0]["values"]) if v is not None)
            return multi(key, years, sets, source=WB_PAGE.format(code=wb_pax), unit="2019 = 100",
                         note=f"World Bank indicator {wb_pax}: each country's passengers indexed to 2019 = 100, computed.",
                         meta_=_m(GROWTH, "Passenger Recovery Index, 2019 = 100", "Registered-carrier passengers", " (2019 = 100)", "#ff9933",
                                  what="Passengers carried each year relative to 2019.", why="Shows how quickly each market recovered and then outgrew 2019.",
                                  read=f"India is at {last:.1f} in {years[-1]}; the orange line is India."))
        return key, build

    def yoy(key):
        def build():
            rows = fetch(wb_pax)["IND"]
            years = [y for y in sorted(rows, key=int) if str(int(y) - 1) in rows]
            values = [round((rows[y] / rows[str(int(y) - 1)] - 1) * 100, 2) for y in years]
            if len(values) < 2:
                raise ValueError("too few years for growth")
            return single(key, years, values, source=WB_PAGE.format(code=wb_pax), unit="%", chart="bar",
                          note=f"World Bank indicator {wb_pax}: year-on-year change in passengers carried by Indian-registered carriers, computed.",
                          meta_=_m(GROWTH, "Growth in Passengers Carried by Indian Airlines", "Change on previous year", "%", "#3fb950",
                                   what="Annual percentage change in passengers carried by Indian carriers.", why="Shows the long-run growth rate and the pandemic shock.",
                                   read=f"Highest {max(values):+.1f}% in {years[values.index(max(values))]}; lowest {min(values):+.1f}% in {years[values.index(min(values))]}."))
        return key, build

    def per_departure(key):
        def build():
            pax, dep = fetch(wb_pax), fetch(wb_dep)
            at = {NAMES[i]: pax[i][BENCHMARK] / dep[i][BENCHMARK] for i in pax if BENCHMARK in pax[i] and BENCHMARK in dep.get(i, {}) and dep[i][BENCHMARK]}
            if "India" not in at or len(at) < 4:
                raise ValueError("too few countries for passengers per departure")
            rank = [n for n, _ in sorted(at.items(), key=lambda item: -item[1])].index("India") + 1
            return ranked(key, at, source=WB_PAGE.format(code=wb_dep), unit=" passengers", chart="bar",
                          note=f"World Bank indicators {wb_pax} and {wb_dep}, {BENCHMARK}: passengers carried divided by departures, computed. India ranks {rank} of {len(at)}.",
                          meta_=_m(GLOBAL, f"Passengers per Departure ({BENCHMARK})", "Average load per take-off", " passengers", "#58a6ff",
                                   what="Passengers carried by registered carriers divided by their departures.", why="Higher values mean larger aircraft or fuller flights.",
                                   read=f"India averages {at['India']:.0f} passengers per departure, rank {rank} of {len(at)}."))
        return key, build

    def cagr(key):
        def build():
            data = fetch(wb_pax)
            at = {NAMES[i]: ((rows["2023"] / rows["2013"]) ** 0.1 - 1) * 100 for i, rows in data.items() if "2023" in rows and "2013" in rows}
            if "India" not in at or len(at) < 4:
                raise ValueError("too few countries for growth")
            rank = [n for n, _ in sorted(at.items(), key=lambda item: -item[1])].index("India") + 1
            return ranked(key, at, source=WB_PAGE.format(code=wb_pax), unit="% a year", chart="bar",
                          note=f"World Bank indicator {wb_pax}: compound annual growth of passengers carried, 2013 to 2023, computed. India ranks {rank} of {len(at)}.",
                          meta_=_m(GROWTH, "Passenger Growth 2013-2023 (Annual Rate)", "Compound annual growth of passengers carried", "% a year", "#3fb950",
                                   what="Compound annual growth in passengers carried over ten years, including the pandemic.", why="Compares long-run growth across aviation markets.",
                                   read=f"India grew {at['India']:.1f}% a year, rank {rank} of {len(at)}."))
        return key, build

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
        share("air_wb_india_share_passengers", wb_pax, "India's Share of World Air Passengers",
              "India's passengers carried as a percentage of the world total.", "Shows India's rising weight in global aviation."),
        share("air_wb_india_share_freight", wb_cargo, "India's Share of World Air Freight",
              "India's air freight (tonne-km) as a percentage of the world total.", "Shows India's weight in global air cargo."),
        recovery("air_wb_recovery_2019"),
        index_lines("air_wb_passengers_index"),
        yoy("air_wb_india_passengers_yoy"),
        per_departure("air_wb_passengers_per_departure"),
        cagr("air_wb_passenger_cagr"),
        cross("air_wb_departures_per_million", wb_dep, "Departures per Million People", "Take-offs relative to population", " per million people", 1, "bar", GLOBAL,
              "Departures by registered carriers divided by population.", "Shows how intensively each country's population is served.", per=1e6),
        india("air_wb_india_departures", wb_dep, "Aircraft Departures by Indian Carriers", "Take-offs by Indian-registered airlines", " million", 1e6, GROWTH,
              "Departures by carriers registered in India, in millions.", "Departures track flight activity over time."),
        india("air_wb_india_freight", wb_cargo, "Air Freight by Indian Carriers", "Million tonne-km", " million tonne-km", 1e6, CARGO,
              "Air freight carried by Indian-registered carriers in million tonne-kilometres.", "A long run of Indian air-cargo output."),
    ]
    return dict(specs)


def build_air_travel_layer(get_json: Callable[[str], object], previous: dict[str, dict]) -> dict[str, dict]:
    builders = _static()
    builders.update(_global(get_json))
    return with_fallback(builders, previous)
