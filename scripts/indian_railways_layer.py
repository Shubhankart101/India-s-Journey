"""Indian Railways: a top-level group with seven subgroups built from official sources.

Static series are transcribed from the Ministry of Railways' *Indian Railways Year Book 2023-24* (Directorate of
Statistics & Economics, Railway Board) and PIB releases; the global comparison pulls live World Bank rail
indicators. If a live fetch fails the previous series is kept.
"""
from __future__ import annotations

from typing import Callable

try:
    from scripts.transport_common import meta, multi, ranked, single, with_fallback, wb_observations, WB_PAGE
except ImportError:  # run as a plain script from scripts/
    from transport_common import meta, multi, ranked, single, with_fallback, wb_observations, WB_PAGE

CATEGORY = "Indian Railways"
NETWORK, PASSENGERS, FREIGHT, FLEET, SAFETY, FINANCE, GLOBAL = (
    "Network & Electrification", "Passenger Services", "Freight Operations", "Rolling Stock & Operations",
    "Railway Safety", "Finance & Efficiency", "Global Rail Comparison",
)
YEAR_BOOK = ("https://rb.indianrailways.gov.in/public/ourOrganization/public/pdf/"
             "IR%20Year%20Book%202023-24-English_f937bf20_1762054799339.pdf")
PIB_FREIGHT = "https://pib.gov.in/PressReleasePage.aspx?PRID=2117417"
YB = "Ministry of Railways, Indian Railways Year Book 2023-24 (Directorate of Statistics & Economics, Railway Board)"

DECADES = ["1950-51", "1960-61", "1970-71", "1980-81", "1990-91", "2000-01", "2010-11", "2020-21", "2021-22", "2022-23", "2023-24"]
FY = ["2022-23", "2023-24"]

ROUTE_KM = [53596, 56247, 59790, 61240, 62367, 63028, 64173, 68103, 68043, 68584, 69181]
RUNNING_TRACK_KM = [59315, 63602, 71669, 75860, 78607, 81865, 87114, 100866, 102831, 106493, 109748]
TOTAL_TRACK_KM = [77609, 83706, 98546, 104480, 108858, 108706, 114037, 126611, 128305, 132310, 135207]
ELECTRIFIED_YEARS = ["1951", "1961", "1971", "1981", "1991", "2001", "2011", "2021", "2022", "2023", "2024"]
ELECTRIFIED_KM = [388, 748, 3706, 5345, 9968, 14856, 19607, 45772, 51804, 58074, 62253]

ZONE_ROUTE_KM = {
    "Central": 4275, "Eastern": 2841, "East Central": 4377, "East Coast": 3071, "Northern": 7406, "North Central": 3522,
    "North Eastern": 3492, "Northeast Frontier": 4348, "North Western": 5712, "Southern": 5092, "South Central": 6610,
    "South Eastern": 2749, "South East Central": 2541, "South Western": 3692, "Western": 6284, "West Central": 3124,
    "Metro Railway Kolkata": 45,
}
STATE_ROUTE_KM = {
    "Andhra Pradesh": 4016, "Arunachal Pradesh": 12, "Assam": 2571, "Bihar": 3959, "Chhattisgarh": 1222, "Goa": 69,
    "Gujarat": 5051, "Haryana": 1780, "Himachal Pradesh": 313, "Jharkhand": 2651, "Karnataka": 3647, "Kerala": 1048,
    "Madhya Pradesh": 5263, "Maharashtra": 5930, "Manipur": 56, "Meghalaya": 9, "Mizoram": 1, "Nagaland": 25,
    "Odisha": 2985, "Punjab": 2265, "Rajasthan": 6135, "Tamil Nadu": 4038, "Telangana": 2015, "Tripura": 265,
    "Uttarakhand": 346, "Uttar Pradesh": 8823, "West Bengal": 4161, "Chandigarh": 16, "Delhi": 188,
    "Jammu & Kashmir": 298, "Puducherry": 23,
}

PASSENGERS_TOTAL = [1284, 1594, 2431, 3613, 3858, 4833, 7651, 1250, 3519, 6396, 6905]
PASSENGERS_SUBURBAN = [412, 680, 1219, 2000, 2259, 2861, 4061, 917, 2169, 3792, 3981]
PASSENGERS_NON_SUBURBAN = [872, 914, 1212, 1613, 1599, 1972, 3590, 333, 1350, 2604, 2924]
PASSENGER_KM = [66517, 77665, 118120, 208558, 295644, 457022, 978508, 231126, 590217, 958919, 1064700]
PASSENGER_LEAD = [51.8, 48.7, 48.6, 57.7, 76.6, 94.6, 127.9, 184.8, 167.7, 149.9, 154.2]

FREIGHT_TONNES = [73.20, 119.80, 167.90, 195.90, 318.40, 473.50, 921.73, 1230.94, 1415.87, 1509.10, 1588.06]
FREIGHT_NTKM = [37565, 72333, 110696, 147652, 235785, 312371, 625723, 719762, 871816, 959566, 973968]
FREIGHT_LEAD = [513, 603, 659, 754, 741, 660, 679, 585, 616, 636, 613]
# Revenue-earning tonnes originating (millions), 2022-23 then 2023-24, from the Year Book freight table.
COMMODITIES = {
    "Coal": (727.24, 786.84), "Iron ore": (160.14, 180.95), "Cement": (143.93, 152.72),
    "Containers": (79.22, 84.76), "Pig iron & finished steel": (69.86, 75.77), "Fertilizers": (56.34, 58.92),
    "Foodgrains": (70.92, 51.44), "Mineral oil (POL)": (48.22, 49.88), "Raw material for steel": (28.15, 29.17),
    "Other goods": (125.08, 117.61),
}

ACCIDENT_YEARS = ["2019-20", "2020-21", "2021-22", "2022-23", "2023-24"]
ACCIDENTS = {
    "Derailments": [40, 17, 27, 36, 25], "Collisions": [5, 1, 2, 6, 6], "Fire in trains": [8, 3, 4, 4, 9],
    "Level-crossing accidents": [1, 1, 1, 1, 0], "Miscellaneous": [1, 0, 1, 1, 0],
}
ACCIDENT_RATE = [0.05, 0.03, 0.03, 0.03, 0.03]

PEERS = ("IND", "CHN", "USA", "RUS", "JPN", "DEU", "FRA", "GBR", "BRA", "AUS")
NAMES = {"IND": "India", "CHN": "China", "USA": "United States", "RUS": "Russia", "JPN": "Japan", "DEU": "Germany",
         "FRA": "France", "GBR": "United Kingdom", "BRA": "Brazil", "AUS": "Australia"}
LINE_PEERS = ("IND", "CHN", "USA", "RUS", "JPN")
LINE_COLORS = ("#ff9933", "#ff7b72", "#58a6ff", "#bc8cff", "#3fb950")
BENCHMARK = "2019"  # latest year that most peers report before the pandemic distortion


def _m(subgroup, title, subtitle, suffix, color="#ff9933", **explain):
    return meta(CATEGORY, subgroup, title, subtitle, suffix, color, **explain)


def _yb(table: str) -> str:
    text = table.lower()
    if "electrification" in text and "network" in text:
        pages = "Year Book 2023-24, pp. 60-62 and 74-78"
    elif "network" in text:
        pages = "Year Book 2023-24, pp. 60-62"
    elif "electrification" in text:
        pages = "Year Book 2023-24, pp. 74-78"
    elif "passenger business" in text and "freight operation" in text:
        pages = "Year Book 2023-24, pp. 22-45"
    elif "passenger business" in text:
        pages = "Year Book 2023-24, pp. 22-37"
    elif "freight operation" in text:
        pages = "Year Book 2023-24, pp. 38-45"
    elif "safety" in text:
        pages = "Year Book 2023-24, pp. 52-59"
    elif "selected financial ratio" in text:
        pages = "Year Book 2023-24, pp. 7-8"
    elif "key statistics" in text:
        pages = "Year Book 2023-24, p. 3"
    else:
        pages = "Year Book 2023-24, pp. 4-6"
    return f"{YB}: {table}; {pages}."


def _static() -> dict[str, Callable]:
    b: dict[str, Callable] = {}

    def add(key, fn):
        b[key] = lambda: fn(key)

    def share(part, whole):
        return [round(100 * value / total, 2) for value, total in zip(part, whole)]

    # ---- Network & Electrification
    add("rail_route_km", lambda k: single(k, DECADES, ROUTE_KM, source=YEAR_BOOK, unit="km",
        note=_yb("'The Network', route kilometres since 1950-51"),
        meta_=_m(NETWORK, "Route Length Since Independence", "Route kilometres of Indian Railways", " km",
                 what="Total route kilometres across all gauges, 1950-51 to 2023-24.",
                 read="The network grew by about 15,600 km over 73 years and stood at 69,181 km on 31 March 2024.",
                 why="Route length is the physical reach of the railway.")))
    add("rail_track_km", lambda k: multi(k, DECADES, [
        {"label": "Total track km", "values": TOTAL_TRACK_KM, "color": "#ff9933"},
        {"label": "Running track km", "values": RUNNING_TRACK_KM, "color": "#58a6ff"},
        {"label": "Route km", "values": ROUTE_KM, "color": "#3fb950"}], source=YEAR_BOOK, unit="km",
        note=_yb("'The Network', route, running track and total track kilometres"),
        meta_=_m(NETWORK, "Route vs Track Kilometres", "Doubling and multi-tracking since 1950-51", " km", "#58a6ff",
                 what="Route, running-track and total-track kilometres.",
                 read="Running track grew about 85% since 1950-51 against 29% for route length, which points to doubling and extra lines on existing corridors.",
                 why="Track length divided by route length shows how much of the network has more than one line.")))
    add("rail_electrified_km", lambda k: single(k, ELECTRIFIED_YEARS, ELECTRIFIED_KM, source=YEAR_BOOK, unit="km",
        chart="bar", note=_yb("'Electrification', cumulative electrified route kilometres"),
        meta_=_m(NETWORK, "Cumulative Electrified Route", "Electrified route kilometres, 1951 to 2024", " km", "#f6c344",
                 what="Cumulative electrified route kilometres in each year shown.",
                 read="Electrification more than tripled after 2011; a record 4,644 km was electrified in 2023-24, taking the total to 62,253 km, about 90% of the broad-gauge network.",
                 why="The Mission 100% Electrification policy aims to cut diesel imports and running costs.")))
    add("rail_gauge_mix", lambda k: single(k, ["Broad gauge (1,676 mm)", "Metre gauge", "Narrow gauge"], [66820, 1159, 1202],
        source=YEAR_BOOK, unit="km", chart="doughnut", note=_yb("'The Network', route length by gauge on 31 March 2024"),
        meta_=_m(NETWORK, "Route Length by Gauge (2023-24)", "Broad, metre and narrow gauge route kilometres", " km", "#58a6ff",
                 what="Route kilometres by track gauge on 31 March 2024.",
                 read="Broad gauge is 96.59% of the route and carried 100% of freight output and 99.96% of passenger-km.",
                 why="A single dominant gauge lets trains run end to end across the country.")))
    add("rail_zone_route_km", lambda k: ranked(k, ZONE_ROUTE_KM, source=YEAR_BOOK, unit="km",
        note=_yb("'The Network', route kilometres by zonal railway, 2023-24"),
        meta_=_m(NETWORK, "Route Kilometres by Zonal Railway (2023-24)", "Route length of the 16 zones plus Kolkata Metro", " km", "#3fb950",
                 what="Route kilometres under each of the 16 zonal railways and Metro Railway Kolkata.",
                 read="Northern Railway (7,406 km), South Central (6,610) and Western (6,284) run the longest networks.",
                 why="Zones are the operating units of Indian Railways.")))
    add("rail_state_route_km", lambda k: ranked(k, STATE_ROUTE_KM, source=YEAR_BOOK, unit="km",
        note=_yb("'The Network', state-wise route kilometres, 2023-24. States and territories not listed have no railway line"),
        meta_=_m(NETWORK, "Route Kilometres by State (2023-24)", "Railway route length in each state and union territory", " km", "#bc8cff",
                 what="Route kilometres within each state or union territory at the end of 2023-24.",
                 read="Uttar Pradesh (8,823 km), Rajasthan (6,135) and Maharashtra (5,930) have the longest networks; Mizoram has 1 km.",
                 why="State-wise length shows where rail access is deepest.")))

    add("rail_multiple_track_index", lambda k: single(k, DECADES,
        [round(track / route * 100, 2) for track, route in zip(RUNNING_TRACK_KM, ROUTE_KM)],
        source=YEAR_BOOK, unit="running-track km per 100 route-km", note=_yb("'The Network', route and running track kilometres"),
        meta_=_m(NETWORK, "Running Track per 100 Route-Km", "Running-track length relative to route length", " track km / 100 route-km", "#58a6ff",
                 what="Running-track kilometres for every 100 route-kilometres, calculated from the Year Book series.",
                 read=f"The ratio was {RUNNING_TRACK_KM[-1] / ROUTE_KM[-1] * 100:.2f} in 2023-24, versus {RUNNING_TRACK_KM[0] / ROUTE_KM[0] * 100:.2f} in 1950-51.",
                 why="It indicates how much additional track exists beyond a single route line.")))
    add("rail_route_net_additions", lambda k: single(k, DECADES[1:],
        [later - earlier for earlier, later in zip(ROUTE_KM, ROUTE_KM[1:])],
        source=YEAR_BOOK, unit="km", chart="bar", note=_yb("'The Network', route kilometres by benchmark year; each bar is the change from the preceding listed benchmark"),
        meta_=_m(NETWORK, "Route-Km Added Between Benchmarks", "Change in route length since the prior listed year", " km", "#3fb950",
                 what="Difference between each adjacent published route-kilometre benchmark.",
                 read=f"The listed route length increased by {ROUTE_KM[-1] - ROUTE_KM[0]:,} km from 1950-51 to 2023-24; the last interval added {ROUTE_KM[-1] - ROUTE_KM[-2]:,} km.",
                 why="The differences show when network expansion accelerated or slowed.")))
    add("rail_route_growth_index", lambda k: single(k, DECADES,
        [round(value / ROUTE_KM[0] * 100, 2) for value in ROUTE_KM],
        source=YEAR_BOOK, unit="1950-51 = 100", note=_yb("'The Network', route kilometres since 1950-51; index calculated from the published values"),
        meta_=_m(NETWORK, "Route Length Index", "Route kilometres indexed to 1950-51", " index", "#bc8cff",
                 what="Route kilometres as an index, with 1950-51 set to 100.",
                 read=f"The index reached {ROUTE_KM[-1] / ROUTE_KM[0] * 100:.1f} in 2023-24.",
                 why="An index makes long-run growth easier to compare.")))
    add("rail_electrified_route_share", lambda k: single(k, DECADES,
        share(ELECTRIFIED_KM, ROUTE_KM), source=YEAR_BOOK, unit="%", chart="bar",
        note=_yb("'Electrification' cumulative electrified route and 'The Network' route kilometres; share calculated for matching benchmark years"),
        meta_=_m(NETWORK, "Electrified Route Share", "Electrified kilometres as a share of route kilometres", "%", "#f6c344",
                 what="Cumulative electrified route kilometres divided by total route kilometres.",
                 read=f"The ratio was {ELECTRIFIED_KM[-1] / ROUTE_KM[-1] * 100:.2f}% in the 2023-24 benchmark.",
                 why="It tracks the reach of electrification across the network.")))

    # ---- Passenger Services
    add("rail_passengers_originating", lambda k: single(k, DECADES, PASSENGERS_TOTAL, source=YEAR_BOOK, unit="million",
        note=_yb("Passenger Business, Table I (passengers originating, suburban plus non-suburban)"),
        meta_=_m(PASSENGERS, "Passengers Originating", "Annual passenger journeys on Indian Railways", " million",
                 what="Passenger journeys that began on Indian Railways, in millions.",
                 read="Journeys fell to 1,250 million in 2020-21 (COVID-19) and recovered to 6,905 million in 2023-24, still below the 7,651 million of 2010-11.",
                 why="It is the headline demand measure for Indian Railways.")))
    add("rail_passenger_split", lambda k: multi(k, DECADES, [
        {"label": "Suburban", "values": PASSENGERS_SUBURBAN, "color": "#ff9933"},
        {"label": "Non-suburban", "values": PASSENGERS_NON_SUBURBAN, "color": "#58a6ff"}], source=YEAR_BOOK, unit="million",
        note=_yb("Passenger Business, Table I, suburban versus non-suburban journeys"),
        meta_=_m(PASSENGERS, "Suburban vs Non-Suburban Journeys", "Passengers originating by service type", " million", "#58a6ff",
                 what="Suburban (city commuter) and non-suburban (long-distance) passenger journeys.",
                 read="Suburban journeys were 3,981 million in 2023-24, 58% of the total.",
                 why="Commuter and long-distance services need different capacity.")))
    add("rail_passenger_km", lambda k: single(k, DECADES, PASSENGER_KM, source=YEAR_BOOK, unit="million passenger-km",
        note=_yb("Passenger Business, Table II (passenger kilometres)"),
        meta_=_m(PASSENGERS, "Passenger Kilometres", "Total distance travelled by rail passengers", " million passenger-km", "#3fb950",
                 what="Passenger-kilometres: each passenger multiplied by the distance travelled.",
                 read="Output reached 1,064,700 million passenger-km in 2023-24, about 16 times the 1950-51 level and above 2010-11.",
                 why="Passenger-km measures output; counting journeys alone ignores how far people travel.")))
    add("rail_passenger_lead", lambda k: single(k, DECADES, PASSENGER_LEAD, source=YEAR_BOOK, unit="km",
        note=_yb("Passenger Business, Table III (average lead of all passengers)"),
        meta_=_m(PASSENGERS, "Average Passenger Journey Length", "Average lead per passenger", " km", "#f6c344",
                 what="Average distance of a passenger journey, in kilometres.",
                 read="It rose from 51.8 km in 1950-51 to 154.2 km in 2023-24, with a peak of 184.8 km in 2020-21.",
                 why="A longer lead means a bigger share of travel is intercity rather than suburban.")))
    add("rail_passenger_mix", lambda k: single(k, ["Suburban", "Second class mail/express", "Second class ordinary", "Upper class"],
        [3981, 1871, 734, 319], source=YEAR_BOOK, unit="million", chart="doughnut",
        note=_yb("Passenger Business, Table I, 2023-24 journeys by service and class"),
        meta_=_m(PASSENGERS, "Passenger Journeys by Service (2023-24)", "Split of 6,905 million journeys", " million", "#ff7b72",
                 what="How 2023-24 passenger journeys split across suburban and non-suburban classes.",
                 read="Suburban is 57.7% of journeys, second-class mail/express 27.1%, second-class ordinary 10.6% and upper class 4.6%.",
                 why="Most journeys are suburban or second class.")))
    add("rail_trains_daily", lambda k: multi(k, FY, [
        {"label": "Passenger trains run daily", "values": [12541, 13198], "color": "#ff9933"},
        {"label": "Goods trains run daily", "values": [10388, 11724], "color": "#58a6ff"}], source=YEAR_BOOK, unit="trains", chart="bar",
        note=_yb("Other Important Statistics, Train Utilisation"),
        meta_=_m(PASSENGERS, "Trains Run Daily", "Passenger and goods trains on an average day", " trains", "#58a6ff",
                 what="Average number of passenger and goods trains run each day.",
                 read="Passenger trains per day grew 5.2% and goods trains 12.9% between 2022-23 and 2023-24.",
                 why="Train counts show how intensively the track is used.")))

    add("rail_passenger_suburban_share", lambda k: single(k, DECADES,
        share(PASSENGERS_SUBURBAN, PASSENGERS_TOTAL), source=YEAR_BOOK, unit="%", chart="bar",
        note=_yb("Passenger Business, Table I, suburban journeys divided by total journeys"),
        meta_=_m(PASSENGERS, "Suburban Share of Journeys", "Suburban journeys as a share of all passenger journeys", "%", "#ff9933",
                 what="Suburban passenger journeys divided by total passenger journeys for each year.",
                 read=f"Suburban journeys were {PASSENGERS_SUBURBAN[-1] / PASSENGERS_TOTAL[-1] * 100:.2f}% of the 2023-24 total.",
                 why="The share distinguishes commuter traffic from long-distance demand.")))
    add("rail_passenger_non_suburban_share", lambda k: single(k, DECADES,
        share(PASSENGERS_NON_SUBURBAN, PASSENGERS_TOTAL), source=YEAR_BOOK, unit="%", chart="bar",
        note=_yb("Passenger Business, Table I, non-suburban journeys divided by total journeys"),
        meta_=_m(PASSENGERS, "Non-Suburban Share of Journeys", "Non-suburban journeys as a share of all passenger journeys", "%", "#58a6ff",
                 what="Non-suburban passenger journeys divided by total passenger journeys for each year.",
                 read=f"Non-suburban journeys were {PASSENGERS_NON_SUBURBAN[-1] / PASSENGERS_TOTAL[-1] * 100:.2f}% of the 2023-24 total.",
                 why="This share tracks the long-distance portion of passenger traffic.")))
    add("rail_passenger_average_lead_calculated", lambda k: single(k, DECADES,
        [round(km / passengers, 2) for km, passengers in zip(PASSENGER_KM, PASSENGERS_TOTAL)],
        source=YEAR_BOOK, unit="km per journey", note=_yb("Passenger Business, Tables I and II; passenger-km divided by passengers originating"),
        meta_=_m(PASSENGERS, "Calculated Average Passenger Journey", "Passenger-km divided by passenger journeys", " km", "#3fb950",
                 what="Average journey length calculated from passenger-kilometres and journeys originating.",
                 read=f"The ratio was {PASSENGER_KM[-1] / PASSENGERS_TOTAL[-1]:.2f} km per journey in 2023-24; it is calculated independently of the reported average lead.",
                 why="It cross-checks the relationship between passenger volume and distance travelled.")))
    add("rail_passenger_km_index", lambda k: single(k, DECADES,
        [round(value / PASSENGER_KM[0] * 100, 2) for value in PASSENGER_KM],
        source=YEAR_BOOK, unit="1950-51 = 100", note=_yb("Passenger Business, Table II; passenger-kilometres indexed to 1950-51"),
        meta_=_m(PASSENGERS, "Passenger-Km Index", "Passenger-kilometres indexed to 1950-51", " index", "#bc8cff",
                 what="Passenger-kilometres as an index with 1950-51 set to 100.",
                 read=f"The index reached {PASSENGER_KM[-1] / PASSENGER_KM[0] * 100:.1f} in 2023-24.",
                 why="The index shows long-run growth in passenger transport work.")))

    # ---- Freight Operations
    add("rail_freight_tonnes", lambda k: single(k, DECADES, FREIGHT_TONNES, source=YEAR_BOOK, unit="million tonnes",
        note=_yb("Freight Operation, Table I (revenue-earning freight, tonnes originating, excluding Konkan Railway)"),
        meta_=_m(FREIGHT, "Freight Originating", "Revenue-earning tonnes loaded by Indian Railways", " million tonnes", "#ff9933",
                 what="Revenue-earning freight originating on Indian Railways, in million tonnes.",
                 read="From 73 million tonnes in 1950-51 to 1,588 million tonnes in 2023-24, about 21.7 times higher.",
                 why="Rail carries the bulk commodities (coal, ore, cement, foodgrains) that supply industry.")))
    add("rail_freight_ntkm", lambda k: single(k, DECADES, FREIGHT_NTKM, source=YEAR_BOOK, unit="million net tonne-km",
        note=_yb("Freight Operation, Table I (net tonne kilometres)"),
        meta_=_m(FREIGHT, "Freight Output (Net Tonne-Km)", "Tonnes moved multiplied by distance", " million NTKM", "#58a6ff",
                 what="Net tonne-kilometres: freight tonnage multiplied by distance moved.",
                 read="Output reached 973,968 million NTKM in 2023-24, about 26 times 1950-51.",
                 why="NTKM measures transport work; tonnes alone ignore haul length.")))
    add("rail_freight_lead", lambda k: single(k, DECADES, FREIGHT_LEAD, source=YEAR_BOOK, unit="km",
        note=_yb("Freight Operation, Table I (average lead of freight)"),
        meta_=_m(FREIGHT, "Average Freight Haul", "Average lead of a tonne of freight", " km", "#3fb950",
                 what="Average distance a tonne of freight is carried.",
                 read="Average haul peaked at 754 km in 1980-81 and was 613 km in 2023-24.",
                 why="Haul length affects wagon use and freight earnings per tonne.")))
    add("rail_freight_commodity_mix", lambda k: single(k, list(COMMODITIES), [v[1] for v in COMMODITIES.values()],
        source=YEAR_BOOK, unit="million tonnes", chart="doughnut", note=_yb("Freight Operation, commodity-wise loading 2023-24"),
        meta_=_m(FREIGHT, "Freight by Commodity (2023-24)", "Share of 1,588 million tonnes loaded", " million tonnes", "#ff7b72",
                 what="Revenue-earning freight by commodity group in 2023-24.",
                 read="Coal is 49.55% of loading (thermal power houses alone 38.19%), then iron ore 11.39%, cement 9.62% and containers 5.34%.",
                 why="Rail freight depends heavily on bulk coal.")))
    add("rail_freight_commodity_change", lambda k: multi(k, list(COMMODITIES), [
        {"label": "2022-23", "values": [v[0] for v in COMMODITIES.values()], "color": "#58a6ff"},
        {"label": "2023-24", "values": [v[1] for v in COMMODITIES.values()], "color": "#ff9933"}], source=YEAR_BOOK, unit="million tonnes", chart="bar",
        note=_yb("Freight Operation, commodity-wise loading 2022-23 vs 2023-24"),
        meta_=_m(FREIGHT, "Commodity Loading: 2022-23 vs 2023-24", "Tonnes loaded by commodity group", " million tonnes", "#ff9933",
                 what="Tonnes carried for each commodity group in the last two years.",
                 read="Coal added 59.6 million tonnes and iron ore 20.8 million; foodgrains fell by 19.5 million.",
                 why="Year-on-year changes show which commodities drove growth.")))
    add("rail_freight_loading_pib", lambda k: single(k, ["2020-21", "2023-24", "2024-25"], [1233, 1590.68, 1617.38],
        source=PIB_FREIGHT, unit="million tonnes", chart="bar",
        note=("Ministry of Railways via PIB: originating freight loading was 1,233 MT in 2020-21 (Lok Sabha reply, PIB release 2201815), "
              "1,590.68 MT in 2023-24 and 1,617.38 MT in 2024-25, up 1.68% (PIB release 2117417, 1 April 2025, opening freight-loading paragraph). "
              "These cover all originating loading, so they differ slightly from the Year Book's revenue-earning series."),
        meta_=_m(FREIGHT, "Freight Loading to 2024-25", "Originating loading, latest Ministry figures", " million tonnes", "#f6c344",
                 what="Total originating freight loading, from Ministry of Railways statements.",
                 read="Loading reached 1,617.38 million tonnes in 2024-25; the Ministry says this makes Indian Railways the second-largest freight carrier in the world.",
                 why="It extends the series past the Year Book's 2023-24 end year.")))

    add("rail_freight_commodity_share", lambda k: single(k, list(COMMODITIES),
        [round(values[1] / FREIGHT_TONNES[-1] * 100, 2) for values in COMMODITIES.values()],
        source=YEAR_BOOK, unit="% of revenue-earning tonnes", chart="doughnut",
        note=_yb("Freight Operation commodity table, 2023-24 loading as a share of the 1,588.06 million tonnes reported in Table I"),
        meta_=_m(FREIGHT, "Commodity Shares of Loading", "Commodity tonnes as a share of 2023-24 revenue-earning loading", "%", "#f6c344",
                 what="Each commodity group's reported loading divided by total revenue-earning tonnes originating.",
                 read=f"Coal accounted for {COMMODITIES['Coal'][1] / FREIGHT_TONNES[-1] * 100:.2f}% of 2023-24 revenue-earning loading.",
                 why="The shares show the commodity concentration of rail freight.")))
    add("rail_freight_commodity_growth_pct", lambda k: single(k, list(COMMODITIES),
        [round((current - prior) / prior * 100, 2) for prior, current in COMMODITIES.values()],
        source=YEAR_BOOK, unit="% change", chart="bar",
        note=_yb("Freight Operation commodity-wise loading table, 2022-23 to 2023-24; percentage changes calculated from table values"),
        meta_=_m(FREIGHT, "Commodity Loading Growth", "Percent change in tonnes loaded by commodity", "%", "#ff7b72",
                 what="Year-on-year percentage change in commodity loading between 2022-23 and 2023-24.",
                 read=f"Coal loading rose {((COMMODITIES['Coal'][1] - COMMODITIES['Coal'][0]) / COMMODITIES['Coal'][0] * 100):.2f}%; foodgrains changed by {((COMMODITIES['Foodgrains'][1] - COMMODITIES['Foodgrains'][0]) / COMMODITIES['Foodgrains'][0] * 100):.2f}%.",
                 why="Growth by commodity identifies which goods gained or lost loading.")))
    add("rail_freight_average_haul_calculated", lambda k: single(k, DECADES,
        [round(ntkm / tonnes, 2) for ntkm, tonnes in zip(FREIGHT_NTKM, FREIGHT_TONNES)],
        source=YEAR_BOOK, unit="km", note=_yb("Freight Operation, Table I; net tonne-kilometres divided by revenue-earning tonnes"),
        meta_=_m(FREIGHT, "Calculated Average Freight Haul", "Net tonne-km divided by originating tonnes", " km", "#3fb950",
                 what="Average freight haul calculated by dividing net tonne-kilometres by tonnes originating.",
                 read=f"The calculated average haul was {FREIGHT_NTKM[-1] / FREIGHT_TONNES[-1]:.2f} km in 2023-24.",
                 why="The quotient ties freight volume to the distance moved.")))
    add("rail_freight_loading_benchmark_change", lambda k: single(k, DECADES[1:],
        [current - previous for previous, current in zip(FREIGHT_TONNES, FREIGHT_TONNES[1:])],
        source=YEAR_BOOK, unit="million tonnes", chart="bar",
        note=_yb("Freight Operation, Table I; change between adjacent listed originating-tonnage benchmarks"),
        meta_=_m(FREIGHT, "Freight Loading Change Between Benchmarks", "Change in originating tonnes since the prior listed year", " million tonnes", "#58a6ff",
                 what="Difference in revenue-earning tonnes originating between adjacent listed benchmark years.",
                 read=f"Loading increased by {FREIGHT_TONNES[-1] - FREIGHT_TONNES[-2]:.2f} million tonnes between 2022-23 and 2023-24.",
                 why="The changes reveal the varying scale of long-run growth.")))

    # ---- Rolling Stock & Operations
    add("rail_locomotive_mix", lambda k: single(k, ["Electric", "Diesel", "Steam"], [10675, 4397, 38],
        source=YEAR_BOOK, unit="locomotives", chart="doughnut", note=_yb("Other Important Statistics, locomotives on 31 March 2024"),
        meta_=_m(FLEET, "Locomotives by Traction (2023-24)", "15,110 locomotives by type", " locomotives", "#f6c344",
                 what="Locomotive fleet by traction type on 31 March 2024.",
                 read="Electric locomotives are 70.7% of the fleet; 38 steam locomotives remain.",
                 why="Fleet mix follows the electrification of the route.")))
    add("rail_locomotive_change", lambda k: multi(k, ["Electric", "Diesel", "Steam"], [
        {"label": "2022-23", "values": [9565, 4730, 39], "color": "#58a6ff"},
        {"label": "2023-24", "values": [10675, 4397, 38], "color": "#ff9933"}], source=YEAR_BOOK, unit="locomotives", chart="bar",
        note=_yb("Other Important Statistics, number of locomotives (2022-23 revised)"),
        meta_=_m(FLEET, "Locomotive Fleet: 2022-23 vs 2023-24", "Locomotives by traction type", " locomotives", "#ff9933",
                 what="Number of electric, diesel and steam locomotives in the last two years.",
                 read="Electric locomotives grew by 1,110 while diesel fell by 333.",
                 why="Shows the shift from diesel to electric traction year by year.")))
    add("rail_coach_fleet", lambda k: multi(k, ["Passenger carriages", "Other coaching vehicles", "EMU/MEMU coaches"], [
        {"label": "2022-23", "values": [66369, 11419, 11913], "color": "#58a6ff"},
        {"label": "2023-24", "values": [66687, 13022, 12229], "color": "#ff9933"}], source=YEAR_BOOK, unit="coaches", chart="bar",
        note=_yb("Other Important Statistics, number of coaches (2022-23 revised)"),
        meta_=_m(FLEET, "Coach Fleet: 2022-23 vs 2023-24", "Passenger and other coaching vehicles", " coaches", "#58a6ff",
                 what="Coaches by type; the total was 91,948 in 2023-24 including rail cars.",
                 read="Other coaching vehicles grew fastest, by 14%; passenger carriages grew 0.5%.",
                 why="Coach numbers limit how many passengers can be carried.")))
    add("rail_wagon_fleet", lambda k: single(k, FY, [315103, 327991], source=YEAR_BOOK, unit="wagons", chart="bar",
        note=_yb("Other Important Statistics, number of wagons (2022-23 revised)"),
        meta_=_m(FLEET, "Wagon Fleet", "Freight wagons owned by Indian Railways", " wagons", "#3fb950",
                 what="Total wagons owned by Indian Railways.",
                 read="The fleet grew by 12,888 wagons (4.1%) to 327,991.",
                 why="Wagon availability caps freight loading.")))
    add("rail_wagon_turnround", lambda k: single(k, FY, [4.70, 5.11], source=YEAR_BOOK, unit="days", chart="bar",
        note=_yb("Other Important Statistics, Wagon Utilisation (broad gauge)"),
        meta_=_m(FLEET, "Wagon Turn-Round Time", "Days for a wagon to complete a loading cycle", " days", "#ff7b72",
                 what="Average days for a broad-gauge wagon to complete one loading cycle.",
                 read="Turn-round lengthened from 4.70 to 5.11 days.",
                 why="A shorter turn-round lets the same fleet carry more freight.")))
    add("rail_goods_load", lambda k: multi(k, ["Average net load", "Average gross load"], [
        {"label": "2022-23", "values": [1738, 2918], "color": "#58a6ff"},
        {"label": "2023-24", "values": [1899, 3085], "color": "#ff9933"}], source=YEAR_BOOK, unit="tonnes", chart="bar",
        note=_yb("Other Important Statistics, goods train utilisation (broad gauge, all traction). Average goods-train speed fell from 30.8 to 25.0 km/h over the same year"),
        meta_=_m(FLEET, "Average Goods Train Load", "Net and gross load per goods train", " tonnes", "#ff9933",
                 what="Average net and gross load of a broad-gauge goods train.",
                 read="Net load per train rose 9.3% to 1,899 tonnes, while average goods-train speed fell to 25.0 km/h.",
                 why="Heavier trains move more per path, but slower speeds lengthen transit times.")))

    add("rail_locomotive_traction_share", lambda k: multi(k, FY, [
        {"label": kind, "values": [round(value / total * 100, 2) for value, total in zip(values, [15334, 15110])],
         "color": color} for kind, values, color in (
             ("Electric", [9565, 10675], "#ff9933"), ("Diesel", [4730, 4397], "#58a6ff"),
             ("Steam", [39, 38], "#8b949e"))], source=YEAR_BOOK, unit="% of locomotive fleet", chart="bar",
        note=_yb("Other Important Statistics, locomotive counts by traction on 31 March 2023 and 31 March 2024; shares calculated from category totals"),
        meta_=_m(FLEET, "Locomotive Fleet by Traction Share", "Electric, diesel and steam shares", "%", "#f6c344",
                 what="Locomotive counts by traction as a share of all reported electric, diesel and steam locomotives.",
                 read=f"Electric locomotives were {10675 / (10675 + 4397 + 38) * 100:.2f}% of the listed fleet in 2023-24.",
                 why="Shares make the traction transition comparable despite fleet growth.")))
    add("rail_coach_category_share", lambda k: multi(k, FY, [
        {"label": kind, "values": [round(values[i] / (66369 + 11419 + 11913 if i == 0 else 66687 + 13022 + 12229) * 100, 2)
                                    for i in range(2)], "color": color}
        for kind, values, color in (("Passenger carriages", [66369, 66687], "#ff9933"),
                                    ("Other coaching vehicles", [11419, 13022], "#58a6ff"),
                                    ("EMU/MEMU coaches", [11913, 12229], "#3fb950"))],
        source=YEAR_BOOK, unit="% of listed coach categories", chart="bar",
        note=_yb("Other Important Statistics, number of coaches by category, 2022-23 revised and 2023-24; shares calculated over the three listed categories"),
        meta_=_m(FLEET, "Share of Listed Coach Categories", "Composition of the three reported coach groups", "%", "#58a6ff",
                 what="Share of passenger carriages, other coaching vehicles and EMU/MEMU coaches among those listed categories.",
                 read=f"Passenger carriages were {66687 / (66687 + 13022 + 12229) * 100:.2f}% of the listed 2023-24 categories.",
                 why="Category shares show how the reported coaching fleet is composed.")))
    add("rail_daily_goods_train_share", lambda k: single(k, FY,
        [round(goods / (goods + passenger) * 100, 2) for goods, passenger in zip([10388, 11724], [12541, 13198])],
        source=YEAR_BOOK, unit="% of passenger and goods trains", chart="bar",
        note=_yb("Other Important Statistics, daily passenger and goods trains run; goods share calculated from the two reported totals"),
        meta_=_m(FLEET, "Goods Trains as Share of Daily Trains", "Goods trains among reported passenger and goods trains", "%", "#3fb950",
                 what="Goods trains run daily divided by the combined daily passenger and goods train counts.",
                 read=f"Goods trains made up {11724 / (11724 + 13198) * 100:.2f}% of the two reported train groups in 2023-24.",
                 why="The mix compares passenger and freight operating intensity.")))
    add("rail_goods_load_utilisation_pct", lambda k: single(k, FY,
        [round(net / gross * 100, 2) for net, gross in zip([1738, 1899], [2918, 3085])],
        source=YEAR_BOOK, unit="% of gross tonnes", chart="bar",
        note=_yb("Other Important Statistics, average net and gross goods-train loads; net-to-gross ratios calculated from the reported values"),
        meta_=_m(FLEET, "Average Net Load as Share of Gross Load", "Net tonnes per goods train relative to gross tonnes", "%", "#bc8cff",
                 what="Average net goods-train load divided by average gross load.",
                 read=f"The net-to-gross ratio was {1899 / 3085 * 100:.2f}% in 2023-24.",
                 why="The ratio shows the share of average gross train weight represented by payload.")))

    # ---- Safety
    add("rail_accidents_by_type", lambda k: multi(k, ACCIDENT_YEARS, [
        {"label": label, "values": values, "color": color} for (label, values), color in zip(ACCIDENTS.items(), ("#ff7b72", "#ff9933", "#f6c344", "#58a6ff", "#8b949e"))],
        source=YEAR_BOOK, unit="accidents", chart="bar", note=_yb("Safety, consequential train accidents by type, including Konkan Railway"),
        meta_=_m(SAFETY, "Consequential Train Accidents by Type", "Accidents per year, 2019-20 to 2023-24", " accidents", "#ff7b72",
                 what="Consequential train accidents split into derailments, collisions, fires, level-crossing and other accidents.",
                 read="Derailments are the largest category (25 of 40 in 2023-24); fire accidents rose to 9.",
                 why="Type-wise counts show where safety work matters most.")))
    add("rail_accidents_total", lambda k: single(k, ACCIDENT_YEARS, [55, 22, 35, 48, 40], source=YEAR_BOOK, unit="accidents", chart="bar",
        note=_yb("Safety, total consequential train accidents including Konkan Railway"),
        meta_=_m(SAFETY, "Total Consequential Train Accidents", "Accidents per year", " accidents", "#ff7b72",
                 what="Total consequential train accidents.",
                 read="40 in 2023-24, against 55 in 2019-20 and 48 in 2022-23.",
                 why="Raw counts show how many serious incidents occurred.")))
    add("rail_accident_rate", lambda k: single(k, ACCIDENT_YEARS, ACCIDENT_RATE, source=YEAR_BOOK, unit="per million train-km", chart="bar",
        note=_yb("Safety, accidents per million train kilometres, the Year Book's principal safety index"),
        meta_=_m(SAFETY, "Accidents per Million Train-Km", "Accident rate normalised for traffic", " per million train-km", "#f6c344",
                 what="Consequential accidents divided by million train-kilometres run.",
                 read="The rate has held at 0.03 since 2020-21, against 0.05 in 2019-20.",
                 why="A rate shows safety per unit of traffic, unlike a raw count.")))
    add("rail_accident_mix", lambda k: single(k, ["Derailments", "Fire in trains", "Collisions"], [25, 9, 6], source=YEAR_BOOK, unit="accidents", chart="doughnut",
        note=_yb("Safety, 2023-24: 40 consequential accidents; none at level crossings or miscellaneous"),
        meta_=_m(SAFETY, "Accident Types (2023-24)", "Composition of 40 consequential accidents", " accidents", "#ff7b72",
                 what="Share of each accident type among the 40 consequential accidents in 2023-24.",
                 read="Derailments are 62.5%, fires 22.5% and collisions 15%.",
                 why="Shows which accident types dominate.")))

    add("rail_derailment_collision_trend", lambda k: single(k, ACCIDENT_YEARS,
        [derailments + collisions for derailments, collisions in zip(ACCIDENTS["Derailments"], ACCIDENTS["Collisions"])],
        source=YEAR_BOOK, unit="accidents", chart="bar",
        note=_yb("Safety, consequential train accidents table; derailments plus collisions calculated from the listed types"),
        meta_=_m(SAFETY, "Derailments and Collisions", "Combined derailment and collision counts", " accidents", "#ff7b72",
                 what="Yearly derailment and collision counts added together from the consequential-accident table.",
                 read=f"There were {ACCIDENTS['Derailments'][-1] + ACCIDENTS['Collisions'][-1]} derailments and collisions in 2023-24.",
                 why="These two accident types together account for a large share of consequential incidents.")))
    add("rail_derailment_share_pct", lambda k: single(k, ACCIDENT_YEARS,
        share(ACCIDENTS["Derailments"], [sum(values[i] for values in ACCIDENTS.values()) for i in range(len(ACCIDENT_YEARS))]),
        source=YEAR_BOOK, unit="% of consequential accidents", chart="bar",
        note=_yb("Safety, consequential train accidents table; derailments divided by each year's total"),
        meta_=_m(SAFETY, "Derailments as Share of Consequential Accidents", "Derailments divided by all listed consequential accidents", "%", "#f6c344",
                 what="Derailments as a percentage of all consequential train accidents listed for each year.",
                 read=f"Derailments accounted for {ACCIDENTS['Derailments'][-1] / sum(values[-1] for values in ACCIDENTS.values()) * 100:.2f}% of consequential accidents in 2023-24.",
                 why="The share distinguishes the leading accident type from the overall count.")))
    add("rail_accident_yoy_change_pct", lambda k: single(k, ACCIDENT_YEARS[1:],
        [round((current - previous) / previous * 100, 2) for previous, current in zip([sum(v[i] for v in ACCIDENTS.values()) for i in range(5)], [sum(v[i] for v in ACCIDENTS.values()) for i in range(5)][1:])],
        source=YEAR_BOOK, unit="% change", chart="bar",
        note=_yb("Safety, consequential train accidents table; year-on-year changes calculated from the sum of listed accident types"),
        meta_=_m(SAFETY, "Year-on-Year Accident Count Change", "Percent change in consequential accident totals", "%", "#58a6ff",
                 what="Year-on-year percentage change in the sum of the five reported accident categories.",
                 read=f"The total changed by {(sum(v[-1] for v in ACCIDENTS.values()) - sum(v[-2] for v in ACCIDENTS.values())) / sum(v[-2] for v in ACCIDENTS.values()) * 100:.2f}% between 2022-23 and 2023-24.",
                 why="Year-on-year change shows direction as well as scale.")))

    # ---- Finance & Efficiency
    add("rail_revenue_expenses", lambda k: multi(k, ["Revenue", "Expenses", "Net revenue (before dividend)"], [
        {"label": "2022-23", "values": [239982.56, 235655.78, 2517.38], "color": "#58a6ff"},
        {"label": "2023-24", "values": [255272.63, 250893.61, 3259.68], "color": "#ff9933"}], source=YEAR_BOOK, unit="Rs crore", chart="bar",
        note=_yb("Key Statistics, financial results"),
        meta_=_m(FINANCE, "Railway Revenue and Expenses", "Rs crore, 2022-23 and 2023-24", " Rs crore", "#ff9933",
                 what="Total revenue, expenses and net revenue of Indian Railways.",
                 read="Revenue rose 6.4% to Rs 2.55 lakh crore; expenses rose 6.5%, leaving Rs 3,260 crore of net revenue.",
                 why="Net revenue is small relative to turnover.")))
    add("rail_earnings", lambda k: multi(k, ["Passenger earnings", "Freight earnings"], [
        {"label": "2022-23", "values": [63416.85, 160158.48], "color": "#58a6ff"},
        {"label": "2023-24", "values": [70693.32, 165880.58], "color": "#ff9933"}], source=YEAR_BOOK, unit="Rs crore", chart="bar",
        note=_yb("Passenger Business and Freight Operation, earnings (freight excludes demurrage and wharfage)"),
        meta_=_m(FINANCE, "Passenger vs Freight Earnings", "Earnings by business, Rs crore", " Rs crore", "#58a6ff",
                 what="Earnings from passenger and freight services.",
                 read="Passenger earnings grew 11.5% and freight 3.6%; freight is 70% of the two combined.",
                 why="Freight is the larger earner.")))
    add("rail_financial_ratios", lambda k: multi(k, ["Operating ratio", "Working ratio", "Operating ratio with subsidy", "Goods operating ratio", "Coaching operating ratio"], [
        {"label": "2022-23", "values": [98.10, 90.92, 80.40, 66.97, 180.82], "color": "#58a6ff"},
        {"label": "2023-24", "values": [98.43, 91.31, 81.10, 67.55, 177.69], "color": "#ff9933"}], source=YEAR_BOOK, unit="%", chart="bar",
        note=_yb("Some Selected Financial Ratio"),
        meta_=_m(FINANCE, "Operating and Working Ratios", "Expenses as a percentage of earnings", "%", "#f6c344",
                 what="Operating ratio is expenditure as a share of earnings; lower is better.",
                 read="The overall ratio was 98.43%. Goods runs at 67.55% while coaching is 177.69%, meaning Rs 1.78 is spent for every Re 1 earned from passengers.",
                 why="The ratio shows how much of each rupee earned is left for investment.")))
    add("rail_yield", lambda k: multi(k, ["Passenger yield (paise per passenger-km)", "Freight yield (paise per net tonne-km)"], [
        {"label": "2022-23", "values": [66.13, 166.91], "color": "#58a6ff"},
        {"label": "2023-24", "values": [66.40, 170.31], "color": "#ff9933"}], source=YEAR_BOOK, unit="paise", chart="bar",
        note=_yb("Some Selected Financial Ratio, earning/yield ratios based on apportioned earning"),
        meta_=_m(FINANCE, "Passenger and Freight Yield", "Average revenue per unit of traffic", " paise", "#3fb950",
                 what="Average revenue per passenger-km and per net tonne-km.",
                 read="Passenger yield was 66.40 paise per passenger-km and freight 170.31 paise per net tonne-km.",
                 why="Yield compares what the railway earns on each unit of traffic.")))
    add("rail_earnings_mix_share", lambda k: multi(k, FY, [
        {"label": "Passenger earnings", "values": [round(value / total * 100, 2) for value, total in
            zip([63416.85, 70693.32], [63416.85 + 160158.48, 70693.32 + 165880.58])], "color": "#58a6ff"},
        {"label": "Freight earnings", "values": [round(value / total * 100, 2) for value, total in
            zip([160158.48, 165880.58], [63416.85 + 160158.48, 70693.32 + 165880.58])], "color": "#ff9933"}],
        source=YEAR_BOOK, unit="% of passenger and freight earnings", chart="bar",
        note=_yb("Passenger Business and Freight Operation earnings table; shares calculated over those two earning streams"),
        meta_=_m(FINANCE, "Passenger and Freight Earnings Shares", "Share of combined passenger and freight earnings", "%", "#58a6ff",
                 what="Passenger and freight earnings as percentages of the two categories' combined earnings.",
                 read=f"Freight represented {165880.58 / (70693.32 + 165880.58) * 100:.2f}% of combined passenger and freight earnings in 2023-24.",
                 why="The shares show the relative contribution of the two main traffic earnings streams.")))
    add("rail_net_revenue_margin_pct", lambda k: single(k, FY,
        [round(net / revenue * 100, 2) for net, revenue in zip([2517.38, 3259.68], [239982.56, 255272.63])],
        source=YEAR_BOOK, unit="% of total revenue", chart="bar",
        note=_yb("Key Statistics, financial results; net revenue divided by total revenue"),
        meta_=_m(FINANCE, "Net Revenue Margin", "Net revenue as a share of total revenue", "%", "#3fb950",
                 what="Reported net revenue divided by total railway revenue for each year.",
                 read=f"Net revenue was {3259.68 / 255272.63 * 100:.2f}% of total revenue in 2023-24.",
                 why="The margin shows the net result relative to the scale of railway earnings.")))
    add("rail_financial_growth_rates", lambda k: single(k, ["Revenue", "Expenses"],
        [round((255272.63 / 239982.56 - 1) * 100, 2), round((250893.61 / 235655.78 - 1) * 100, 2)],
        source=YEAR_BOOK, unit="% change, 2022-23 to 2023-24", chart="bar",
        note=_yb("Key Statistics, financial results; growth rates calculated from reported total revenue and expenses"),
        meta_=_m(FINANCE, "Revenue and Expense Growth", "Year-on-year change in railway revenue and expenses", "%", "#f6c344",
                 what="Percentage change in reported total revenue and total expenses from 2022-23 to 2023-24.",
                 read=f"Revenue increased {(255272.63 / 239982.56 - 1) * 100:.2f}%; expenses increased {(250893.61 / 235655.78 - 1) * 100:.2f}%.",
                 why="Comparing the two growth rates shows whether expenses grew faster than revenue.")))

    return b


def _global(get_json: Callable[[str], object]) -> dict[str, Callable]:
    cache: dict[str, dict] = {}

    def fetch(code):
        if code not in cache:
            cache[code] = wb_observations(get_json, PEERS, code)
        return cache[code]

    def line(key, code, title, subtitle, suffix, scale, what, why):
        def build():
            observed = fetch(code)
            years = sorted({y for iso in LINE_PEERS for y in observed.get(iso, {})}, key=int)
            data = [{"label": NAMES[iso], "color": LINE_COLORS[i],
                     "values": [round(observed[iso][y] / scale, 3) if y in observed[iso] else None for y in years]}
                    for i, iso in enumerate(LINE_PEERS) if iso in observed]
            return multi(key, years, data, source=WB_PAGE.format(code=code), unit=suffix,
                         note=f"World Bank indicator {code}, compiled from national railway data (UIC / ITF). Gaps are years a country did not report.",
                         meta_=_m(GLOBAL, title, subtitle, suffix, "#ff9933", what=what, why=why,
                                  read="India is the orange line; compare its trajectory with each peer."))
        return key, build

    def line_all(key, code, title, subtitle, suffix, scale, what, why):
        def build():
            observed = fetch(code)
            years = sorted({year for iso in PEERS for year in observed.get(iso, {})}, key=int)
            datasets = [{"label": NAMES[iso], "values": [
                round(observed[iso][year] / scale, 3) if year in observed[iso] else None for year in years]}
                for iso in PEERS if observed.get(iso)]
            return multi(key, years, datasets, source=WB_PAGE.format(code=code), unit=suffix,
                         note=f"World Bank indicator {code}, all requested countries, annual observations; gaps indicate unreported country-years.",
                         meta_=_m(GLOBAL, title, subtitle, suffix,
                                  what=what, read="Compare the indexed annual series across the ten selected rail systems.", why=why))
        return key, build

    def common_cross(key, code, title, subtitle, suffix, scale, chart, what, why):
        def build():
            observed = fetch(code)
            years = sorted({year for rows in observed.values() for year in rows}, key=int, reverse=True)
            benchmark = None
            at = {}
            for year in years:
                current = {NAMES[iso]: rows[year] / scale for iso, rows in observed.items()
                           if iso in NAMES and year in rows}
                if "India" in current and len(current) >= 4:
                    benchmark, at = year, current
                    break
            if benchmark is None:
                raise ValueError(f"too few countries with a common year for {key}")
            order = [name for name, _ in sorted(at.items(), key=lambda item: -item[1])]
            rank = order.index("India") + 1
            return ranked(key, at, source=WB_PAGE.format(code=code), unit=suffix, chart=chart,
                          note=f"World Bank indicator {code}; {benchmark} is the latest year with India and at least three peers reporting.",
                          meta_=_m(GLOBAL, f"{title} ({benchmark})", subtitle, suffix, "#58a6ff",
                                   what=what, read=f"India ranks {rank} of {len(at)} countries in {benchmark}.", why=why))
        return key, build

    def cross(key, code, title, subtitle, suffix, scale, chart, what, why):
        def build():
            at = {NAMES[iso]: rows[BENCHMARK] / scale for iso, rows in fetch(code).items() if BENCHMARK in rows}
            if "India" not in at or len(at) < 4:
                raise ValueError(f"too few countries for {key}")
            order = [name for name, _ in sorted(at.items(), key=lambda item: -item[1])]
            rank = order.index("India") + 1
            return ranked(key, at, source=WB_PAGE.format(code=code), unit=suffix, chart=chart,
                          note=(f"World Bank indicator {code}, {BENCHMARK} (latest year most compared countries report). "
                                f"India ranks {rank} of {len(at)} countries shown."),
                          meta_=_m(GLOBAL, f"{title} ({BENCHMARK})", subtitle, suffix, "#58a6ff", what=what, why=why,
                                   read=f"India ranks {rank} of {len(at)} countries in this comparison."))
        return key, build

    specs = [
        line("rail_wb_freight_trend", "IS.RRS.GOOD.MT.K6", "Rail Freight: India vs Peers", "Goods transported by railway", " billion tonne-km", 1e3,
             "Freight moved by rail, in billion tonne-kilometres.", "Rail freight volume is a core measure of industrial transport capacity."),
        line("rail_wb_passenger_trend", "IS.RRS.PASG.KM", "Rail Passengers: India vs Peers", "Passenger-kilometres carried by railway", " billion passenger-km", 1e3,
             "Passengers carried by rail, in billion passenger-kilometres.", "Passenger-km shows how much a country relies on rail for travel."),
        line("rail_wb_route_trend", "IS.RRS.TOTL.KM", "Rail Network Length: India vs Peers", "Total rail route", " thousand km", 1e3,
             "Total rail lines in operation, in thousand route-kilometres.", "Network length measures physical reach."),
        cross("rail_wb_freight_rank", "IS.RRS.GOOD.MT.K6", "Rail Freight Ranking", "Goods transported by railway", " billion tonne-km", 1e3, "bar",
              "Freight moved by rail, billion tonne-km.", "Ranks India's freight output against large rail systems."),
        cross("rail_wb_freight_share", "IS.RRS.GOOD.MT.K6", "Share of Rail Freight Among Peers", "Peer share of rail freight", " billion tonne-km", 1e3, "doughnut",
              "Each country's share of the peer group's rail freight.", "Shows India's weight in global rail freight."),
        cross("rail_wb_passenger_rank", "IS.RRS.PASG.KM", "Rail Passenger-Km Ranking", "Passenger-km carried by railway", " billion passenger-km", 1e3, "bar",
              "Rail passenger-kilometres.", "Ranks India's rail passenger output."),
        cross("rail_wb_passenger_share", "IS.RRS.PASG.KM", "Share of Rail Passenger-Km Among Peers", "Peer share of rail passenger-km", " billion passenger-km", 1e3, "doughnut",
              "Each country's share of the peer group's rail passenger-km.", "Shows India's weight in passenger rail."),
        cross("rail_wb_route_rank", "IS.RRS.TOTL.KM", "Rail Network Ranking", "Total rail route", " thousand km", 1e3, "bar",
              "Total rail route length, thousand km.", "Ranks the size of India's network."),
        line_all("rail_wb_freight_all_peer_trend", "IS.RRS.GOOD.MT.K6", "Rail Freight: Ten-System Trend", "Goods transported by railway", " billion tonne-km", 1e3,
                 "Freight moved by rail, billion tonne-kilometres for all ten selected countries.", "The wider peer set provides context beyond the five largest systems."),
        line_all("rail_wb_passenger_all_peer_trend", "IS.RRS.PASG.KM", "Rail Passenger-Km: Ten-System Trend", "Passenger-kilometres carried by railway", " billion passenger-km", 1e3,
                 "Passenger-kilometres moved by rail for all ten selected countries.", "The wider peer set provides context beyond the five largest systems."),
        line_all("rail_wb_route_all_peer_trend", "IS.RRS.TOTL.KM", "Rail Network: Ten-System Trend", "Total rail route", " thousand km", 1e3,
                 "Total rail route length for all ten selected countries, in thousand kilometres.", "The wider peer set provides context beyond the five largest systems."),
        common_cross("rail_wb_freight_latest_common_rank", "IS.RRS.GOOD.MT.K6", "Latest Common-Year Rail Freight Ranking", "Goods transported by railway", " billion tonne-km", 1e3, "bar",
                     "Freight moved by rail, billion tonne-kilometres.", "Ranks India against peers for the latest common year with sufficient reports."),
        common_cross("rail_wb_passenger_latest_common_rank", "IS.RRS.PASG.KM", "Latest Common-Year Rail Passenger Ranking", "Passenger-kilometres carried by railway", " billion passenger-km", 1e3, "bar",
                     "Rail passenger-kilometres.", "Ranks India against peers for the latest common year with sufficient reports."),
        common_cross("rail_wb_route_latest_common_rank", "IS.RRS.TOTL.KM", "Latest Common-Year Rail Network Ranking", "Total rail route", " thousand km", 1e3, "bar",
                     "Total rail route length, thousand km.", "Ranks India against peers for the latest common year with sufficient reports."),
    ]
    return dict(specs)


def build_indian_railways_layer(get_json: Callable[[str], object], previous: dict[str, dict]) -> dict[str, dict]:
    builders = _static()
    builders.update(_global(get_json))
    return with_fallback(builders, previous)
