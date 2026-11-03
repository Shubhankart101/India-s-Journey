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
    return f"{YB}: {table}."


def _static() -> dict[str, Callable]:
    b: dict[str, Callable] = {}

    def add(key, fn):
        b[key] = lambda: fn(key)

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
              "1,590.68 MT in 2023-24 and 1,617.38 MT in 2024-25, up 1.68% (PIB release 2117417, 1 April 2025). "
              "These cover all originating loading, so they differ slightly from the Year Book's revenue-earning series."),
        meta_=_m(FREIGHT, "Freight Loading to 2024-25", "Originating loading, latest Ministry figures", " million tonnes", "#f6c344",
                 what="Total originating freight loading, from Ministry of Railways statements.",
                 read="Loading reached 1,617.38 million tonnes in 2024-25; the Ministry says this makes Indian Railways the second-largest freight carrier in the world.",
                 why="It extends the series past the Year Book's 2023-24 end year.")))

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
    ]
    return dict(specs)


def build_indian_railways_layer(get_json: Callable[[str], object], previous: dict[str, dict]) -> dict[str, dict]:
    builders = _static()
    builders.update(_global(get_json))
    return with_fallback(builders, previous)
