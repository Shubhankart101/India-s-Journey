"""Water transport charts from official MoPSW, Sansad and World Bank sources."""
from __future__ import annotations
from typing import Callable
try:
    from scripts.transport_common import meta, multi, ranked, single, with_fallback, wb_observations, wb_url
except ImportError:
    from transport_common import meta, multi, ranked, single, with_fallback, wb_observations, wb_url

CATEGORY = "Water Transport & Shipping"
PORT, INLAND, COAST, PASSENGER, PERFORMANCE, GLOBAL = (
    "Port Cargo Traffic", "Inland Waterways", "Coastal Shipping", "Water Passenger Traffic",
    "Container & Port Performance", "Global Maritime Comparison")
SUBGROUPS = (PORT, INLAND, COAST, PASSENGER, PERFORMANCE, GLOBAL)
REPORT = "https://shipmin.gov.in/sites/default/files/Annual%20Report%202023-24_English.pdf"
REPORT_NAME = "Ministry of Ports, Shipping and Waterways, Annual Report 2023-24"
IWT_STATS = "https://shipmin.gov.in/sites/default/files/IWT%202022%2023%20APPROVED.pdf"
IWT_STATS_NAME = "MoPSW, Statistics of Inland Water Transport 2022-23"
SANSAD_PASSENGERS = "https://sansad.in/getFile/loksabhaquestions/annex/186/AU2182_FElOEb.pdf?source=pqals"
PIB_CRUISE = "https://pib.gov.in/PressReleaseIframePage.aspx?PRID=1974552"
IWT_PASSENGER_YEARS = ["2019", "2020", "2021", "2022", "2023"]
IWT_STATE_PASSENGERS = {
    "Assam": [8514.22, 6585.91, 1979.20, 4385.95, 3155.38],
    "Karnataka": [2158.00, 1617.00, 916.25, 928.02, 1283.79],
    "Kerala": [19739.08, 20535.31, 8874.78, 19224.53, 20262.39],
    "Maharashtra": [19291.70, 15922.30, 9106.53, 13667.60, 18724.02],
    "West Bengal": [106492.00, 116880.00, 126980.00, 136369.00, 29762.61],
}
CARGO_YEARS = ["2017-18", "2018-19", "2019-20", "2020-21", "2021-22", "2022-23", "2023-24"]
PORTS = ["Kolkata", "Haldia", "Paradip", "Visakhapatnam", "Chennai", "V.O. Chidambaranar", "Cochin",
         "New Mangalore", "Mormugao", "Jawaharlal Nehru", "Mumbai", "Deendayal (Kandla)", "Kamarajar (Ennore)"]
PORT_2223 = [17.052,48.608,135.362,73.750,48.949,38.041,35.255,41.417,17.334,83.861,63.608,137.561,43.507]
PORT_2324 = [16.856,49.536,145.379,81.090,51.598,41.402,36.315,45.707,20.615,85.817,67.261,132.374,45.277]
COMMODITIES = {
    "POL":[224.82,233.70,234.86,206.77,221.27,234.17,245.99],
    "Iron ore":[41.17,38.81,55.68,64.28,51.71,46.51,61.03],
    "Fertilisers & raw materials":[15.05,15.41,16.15,17.67,15.93,16.68,17.68],
    "Coal":[141.23,163.67,149.04,126.75,146.80,188.24,191.98],
    "Containerised cargo":[133.73,145.52,146.86,143.77,166.90,170.29,181.57],
    "Other cargo":[123.37,101.99,102.34,113.44,117.44,128.42,120.98],
}
CONTAINER_TEU = [9.14,9.88,8.79,9.61,11.22,11.45,12.31]
CAPACITY_YEARS = ["2001-02","2002-03","2003-04","2004-05","2005-06","2006-07","2007-08","2008-09",
                  "2009-10","2010-11","2011-12","2012-13","2013-14","2014-15","2015-16","2016-17",
                  "2017-18","2018-19","2019-20","2020-21","2021-22","2022-23","2023-24"]
PORT_CAPACITY = [343.95,362.75,389.50,397.50,456.20,504.75,532.07,574.77,616.73,670.13,689.83,744.91,
                 800.52,871.52,965.36,1065.83,1451.19,1514.09,1534.91,1560.61,1597.59,1617.39,1629.86]
PORT_TRAFFIC = [287.58,313.55,344.80,383.75,423.41,463.78,519.31,530.53,561.09,570.03,560.14,545.68,
                555.50,581.34,606.47,648.40,679.37,699.10,704.93,672.68,720.05,784.31,819.23]
TURNAROUND = [82.61,50.12,41.61,65.86,44.92,51.36,33.40,40.44,65.61,26.00,62.97,54.24,44.37]
BERTH_OUTPUT = [5365,13698,33014,13687,18728,15401,25963,19218,17772,28648,11152,18217,27197]
WB_PEERS = ("IND","CHN","SGP","USA","ARE","KOR","NLD","DEU","JPN","MYS","VNM","BRA","AUS")
WB_NAMES = dict(zip(WB_PEERS,["India","China","Singapore","United States","United Arab Emirates","Korea, Rep.",
                              "Netherlands","Germany","Japan","Malaysia","Vietnam","Brazil","Australia"]))
WB_CODES = {"container":"IS.SHP.GOOD.TU", "connectivity":"IS.SHP.GCNW.XQ"}
WB_COLORS = ("#ff9933","#ff7b72","#58a6ff","#bc8cff","#3fb950","#f6c344","#39c5bb","#f778ba",
             "#a5d6ff","#ffa657","#d2a8ff","#7ee787","#ff9bce")


def _m(group, title, subtitle, suffix, what, read, why, color="#ff9933"):
    return meta(CATEGORY, group, title, subtitle, suffix, color, what=what, read=read, why=why)


def _note(ref, basis=""):
    return f"{REPORT_NAME}, {ref}. {basis}".strip()


def _one(key, group, title, subtitle, labels, values, unit, ref, what, read, why, chart=None, basis=""):
    return single(key, labels, values, source=REPORT, unit=unit, chart=chart, note=_note(ref, basis),
                  meta_=_m(group, title, subtitle, unit, what, read, why))


def _external_one(key, title, subtitle, labels, values, unit, source, note, what, read, why, chart=None):
    return single(key, labels, values, source=source, unit=unit, chart=chart, note=note,
                  meta_=_m(PASSENGER, title, subtitle, unit, what, read, why))


def _static_builders():
    b = {}
    def add(key, fn): b[key] = lambda: fn(key)
    port_ref = "§2.12 and Table ‘Commodity-wise Cargo Traffic at Major Ports’, printed p.16"
    add("water_major_port_cargo_rank", lambda k: ranked(k, dict(zip(PORTS,PORT_2324)), source=REPORT,
        unit="million tonnes", note=_note("Table ‘Performance of Major Ports’, printed p.51; provisional 2023-24"),
        meta_=_m(PORT,"Cargo Handled by Major Port (2023-24)","Ranked port throughput; provisional values","million tonnes",
                 "Total cargo handled at each of the 13 major ports in 2023-24.",
                 "Deendayal handled 132.374 million tonnes; Kolkata handled 16.856 million tonnes.",
                 "Shows where major-port freight activity is concentrated.")))
    add("water_major_port_cargo_two_years", lambda k: multi(k,PORTS,[
        {"label":"2022-23 actual","values":PORT_2223,"color":"#58a6ff"},
        {"label":"2023-24 provisional","values":PORT_2324,"color":"#ff9933"}],source=REPORT,unit="million tonnes",chart="bar",
        note=_note("Table ‘Performance of Major Ports’, printed p.51; 2022-23 actual and 2023-24 provisional"),
        meta_=_m(PORT,"Major Port Cargo: Year-on-Year","Million tonnes by port","million tonnes",
                 "Actual 2022-23 and provisional 2023-24 cargo handled by each major port.",
                 "The 13 port values sum to 819.227 million tonnes in 2023-24.","Compares port-level traffic year over year.")))
    add("water_major_port_cargo_share", lambda k: single(k,PORTS,PORT_2324,source=REPORT,unit="million tonnes",chart="doughnut",
        note=_note("Table ‘Performance of Major Ports’, printed p.51; 2023-24 provisional values; shares are within the 13 listed ports"),
        meta_=_m(PORT,"Major-Port Cargo Share by Port","2023-24 composition","million tonnes",
                 "Each port's contribution to major-port cargo.","Port values sum to 819.227 million tonnes.",
                 "Shows relative contribution of each major port.")))
    add("water_major_port_cargo_history", lambda k: _one(k,PORT,"Major-Port Cargo Throughput","All major ports, 2017-18 to 2023-24",CARGO_YEARS,
        [679.37,699.10,704.93,672.68,720.05,784.31,819.23],"million tonnes",port_ref,
        "Annual total cargo handled at major ports.","Throughput reached 819.23 MMT in 2023-24, up from 784.31 MMT.",
        "Puts the latest year in long-run context."))
    add("water_major_nonmajor_cargo", lambda k: multi(k,["2022-23","2023-24"],[
        {"label":"Major ports","values":[784.31,819.23],"color":"#ff9933"},
        {"label":"Non-major ports (derived)","values":[649.88,720.77],"color":"#58a6ff"},
        {"label":"All ports","values":[1434.19,1540.0],"color":"#3fb950"}],source=REPORT,unit="million tonnes",chart="bar",
        note=_note("§2.11, ‘Cargo Traffic at Indian Ports’, printed p.16; non-major values are derived as all-port less major-port traffic; 2023-24 all-port traffic is approximate 1,540 MMT"),
        meta_=_m(PORT,"Major and Non-Major Port Cargo","All-port, major-port and derived residuals","million tonnes",
                 "All-port traffic and reported major-port totals; non-major values are residuals.",
                 "Derived non-major traffic is 649.88 MMT in 2022-23 and approximately 720.77 MMT in 2023-24; the latter inherits rounding from 1,540 MMT.",
                 "Separates the major-port system without presenting the residual as a directly reported statistic.")))
    add("water_major_nonmajor_share", lambda k: single(k,["Major ports","Non-major ports (derived)"],[819.23,720.77],
        source=REPORT,unit="million tonnes",chart="doughnut",
        note=_note("§2.11, printed p.16; non-major ports = approximate 1,540 MMT all-port total less 819.23 MMT major-port total"),
        meta_=_m(PORT,"Major vs Non-Major Port Share","Approximate 2023-24 composition","million tonnes",
                 "Reported major-port cargo and a derived non-major-port residual.",
                 "Approximately 819.23 MMT major and 720.77 MMT non-major; the latter is derived from rounded all-port data.",
                 "Shows a transparent estimate of cargo distribution across port categories.")))
    add("water_commodity_trends", lambda k: multi(k,CARGO_YEARS,[{"label":n,"values":v} for n,v in COMMODITIES.items()],
        source=REPORT,unit="million tonnes",note=_note(port_ref),
        meta_=_m(PORT,"Major-Port Cargo by Commodity","Six groups, 2017-18 to 2023-24","million tonnes",
                 "POL, iron ore, fertilisers/raw materials, coal, containerised cargo, and other cargo.",
                 "2023-24 totals: POL 245.99 MMT, coal 191.98 MMT, containerised cargo 181.57 MMT.",
                 "Shows how port freight composition changes over time.")))
    add("water_commodity_mix", lambda k: single(k,list(COMMODITIES),[v[-1] for v in COMMODITIES.values()],
        source=REPORT,unit="million tonnes",chart="doughnut",note=_note(port_ref,"2023-24 column."),
        meta_=_m(PORT,"Major-Port Commodity Mix (2023-24)","Share of reported 819.23 MMT","million tonnes",
                 "Six reported major-port cargo groups.","The six groups sum to 819.23 MMT.","Compares the latest commodity composition.")))
    commodities = [
        ("pol_cargo","POL","POL at Major Ports","POL includes crude, products and LPG/LNG."),
        ("coal_cargo","Coal","Coal Cargo at Major Ports","Coal includes thermal, coking and other coal."),
        ("iron_ore_cargo","Iron ore","Iron Ore Cargo at Major Ports","Iron ore includes fines and pellets."),
        ("fertilisers_cargo","Fertilisers & raw materials","Fertilisers and Raw Materials at Major Ports","F&FRM includes dry and liquid fertilisers and raw materials."),
        ("containerised_cargo","Containerised cargo","Containerised Cargo at Major Ports","Cargo weight is in million tonnes; TEUs are charted separately."),
        ("other_cargo","Other cargo","Other Cargo at Major Ports","Other cargo is the report's residual commodity group."),
    ]
    for suffix,name,title,basis in commodities:
        add("water_"+suffix,lambda k,n=name,t=title,x=basis:_one(k,PORT,t,"Million tonnes, 2017-18 to 2023-24",CARGO_YEARS,
            COMMODITIES[n],"million tonnes",port_ref,"Major-port cargo volume for "+n+".",
            f"{n} reached {COMMODITIES[n][-1]:.2f} MMT in 2023-24. {x}","Tracks this freight stream over time."))
    add("water_container_teu_trend",lambda k:_one(k,PORT,"Major-Port Container Throughput","Container traffic, million TEUs",CARGO_YEARS,
        CONTAINER_TEU,"million TEUs",port_ref,"Container throughput at major ports in million TEUs.",
        "Major ports handled 12.31 million TEUs in 2023-24, compared with 11.45 million in 2022-23.",
        "TEUs measure container traffic independently of container cargo weight."))
    add("water_major_port_capacity_traffic",lambda k:multi(k,CAPACITY_YEARS,[
        {"label":"Rated capacity","values":PORT_CAPACITY,"color":"#58a6ff"},
        {"label":"Traffic handled","values":PORT_TRAFFIC,"color":"#ff9933"}],source=REPORT,unit="million tonnes",
        note=_note("Table ‘Capacity at Major Ports’, printed p.52; 2016-17 uses reported capacity, excluding the separately footnoted re-rated figure"),
        meta_=_m(PORT,"Major-Port Capacity vs Traffic","2001-02 to 2023-24","million tonnes",
                 "Rated annual capacity alongside major-port cargo handled.","Reported 2023-24 capacity was 1,629.86 MMT versus traffic of 819.23 MMT.",
                 "Shows installed capacity relative to freight volume.")))
    add("water_major_port_capacity_utilization",lambda k:_one(k,PORT,"Major-Port Capacity Utilisation","Traffic as a share of rated capacity",CAPACITY_YEARS,
        [round(x/y*100,2) for x,y in zip(PORT_TRAFFIC,PORT_CAPACITY)],"percent",
        "Table ‘Capacity at Major Ports’, printed p.52; ratio calculated as traffic / capacity × 100",
        "Annual major-port traffic divided by rated capacity.",f"Calculated utilisation was {PORT_TRAFFIC[-1]/PORT_CAPACITY[-1]*100:.2f}% in 2023-24.",
        "A derived ratio compares actual throughput with rated capacity."))
    add("water_inland_waterways_cargo",lambda k:_one(k,INLAND,"Cargo on National Waterways","Rounded annual traffic, 2022-23 to 2023-24",["2022-23","2023-24"],
        [126,133],"million tonnes","Score Card—Inland Waterways, printed p.3; values are rounded; overview reports 133 MMTPA",
        "Cargo handled on National Waterways, as rounded in the MoPSW scorecard.",
        "The scorecard shows 126 MMT in 2022-23 and 133 MMT in 2023-24.","Tracks inland freight using Ministry-published rounded totals."))
    add("water_national_waterways_status",lambda k:_one(k,INLAND,"National Waterways: Notified and Operational","Status reported for 2023-24",["Notified","Operational"],
        [111,24],"waterways","MoPSW report overview, printed p.2; national waterways snapshot",
        "Counts of notified National Waterways and those described as operational.",
        "The snapshot lists 111 notified and 24 operational National Waterways.","Distinguishes statutory notification from operational service.",chart="bar"))
    add("water_nw_investment",lambda k:_one(k,INLAND,"Capital Expenditure in National Waterways","MoPSW scorecard, 2022-23 to 2023-24",["2022-23","2023-24"],
        [1010,544],"INR crore","Score Card—Inland Waterways, printed p.3; Investment (CAPEX) in NWs",
        "Capital expenditure in National Waterways.","The scorecard shows INR 1,010 crore and INR 544 crore, respectively.",
        "Tracks annual public capital investment in inland-waterway development."))
    add("water_river_cruise_operational_nws",lambda k:_one(k,INLAND,"Operational NWs for River Cruise","MoPSW scorecard, 2022-23 to 2023-24",["2022-23","2023-24"],
        [10,9],"waterways","Score Card—Inland Waterways, printed p.3; Operational NWs for river cruise",
        "National Waterways reported operational for river-cruise service.","The count was 10 in 2022-23 and 9 in 2023-24.",
        "Tracks the report's river-cruise operational category."))
    add("water_iwai_network_cargo_growth",lambda k:_one(k,INLAND,"National Waterways Cargo Index","2022-23 = 100; derived from rounded totals",["2022-23","2023-24"],
        [100.0,round(133/126*100,1)],"index","Score Card—Inland Waterways, printed p.3; derived index with 2022-23 as base",
        "Index of rounded cargo handled on National Waterways, with 2022-23 set to 100.",
        f"The index is {round(133/126*100,1)} in 2023-24 from rounded values 133 and 126 MMT.",
        "Makes the relative change in inland cargo easier to compare."))
    add("water_coastal_cargo",lambda k:_one(k,COAST,"Coastal Cargo Handled","Rounded scorecard totals, 2022-23 to 2023-24",["2022-23","2023-24"],
        [151,162],"million tonnes","Score Card—Ports, printed p.3; Coastal Cargo Handled (MMTPA)",
        "Coastal cargo handled, as rounded in the Ministry Ports scorecard.","The scorecard reports 151 MMT in 2022-23 and 162 MMT in 2023-24.",
        "Tracks domestic coastal freight handled by ports."))
    add("water_coastal_cargo_share",lambda k:_one(k,COAST,"Coastal Cargo Relative to All-Port Throughput","Calculated from rounded scorecard totals",["2022-23","2023-24"],
        [round(151/1434.19*100,2),round(162/1540*100,2)],"percent",
        "Score Card—Ports, printed p.3 and §2.11, printed p.16; ratio of rounded coastal and all-port figures",
        "Rounded coastal cargo divided by all-port cargo throughput.",
        f"Calculated ratio: {151/1434.19*100:.2f}% and {162/1540*100:.2f}%; the 2023-24 all-port figure is approximately 1,540 MMT.",
        "Provides context for coastal cargo relative to total port cargo; source totals differ in precision."))
    add("water_flagged_vessels",lambda k:_one(k,COAST,"Indian-Flagged Ships and Vessels","MoPSW scorecard, 2022-23 to 2023-24",["2022-23","2023-24"],
        [1523,1526],"vessels","Score Card—Shipping, printed p.3; No. of Indian Flagged Ships / Vessels",
        "Number of ships and vessels under the Indian flag.","The reported count increased from 1,523 to 1,526.",
        "Tracks the Indian-flagged vessel register; this is a count, not gross tonnage."))
    add("water_seafarers",lambda k:_one(k,COAST,"Employed Indian Seafarers","Rounded scorecard figures",["2022-23","2023-24"],
        [2.58,2.85],"lakh seafarers","Score Card—Shipping, printed p.3; Employed Indian Seafarers (in Lakhs)",
        "Employed Indian seafarers, in lakhs.","The scorecard shows 2.58 lakh and 2.85 lakh.",
        "Indicates the workforce supporting India's maritime sector."))
    add("water_shipbuilding_tonnage",lambda k:_one(k,COAST,"Ships Built in India: Gross Tonnage","MoPSW scorecard, 2022-23 to 2023-24",["2022-23","2023-24"],
        [22213,26412],"gross tonnes","Score Card—Shipping, printed p.3; No. of ships built in India (GT)",
        "Gross tonnage of ships built in India.","Reported output rose from 22,213 GT to 26,412 GT.",
        "GT provides a size-adjusted measure of domestic shipbuilding output."))
    add("water_ocean_cruise_passengers",lambda k:multi(k,["Annual-report snapshot"],[{"label":"Ocean cruise passengers","values":[471000],"color":"#58a6ff"}],
        source=REPORT,unit="passengers",chart="bar",note=_note("Year at a Glance overview, printed p.2; reports 4.71 lakh passengers and 227 calls, but does not state the observation period on this snapshot; lakh converted to count"),
        meta_=_m(PASSENGER,"Ocean Cruise Passengers - Annual Report Snapshot","Reference period not separately stated","passengers",
                 "Passengers on ocean cruise calls in the Ministry overview.","The snapshot reports 4.71 lakh passengers; it does not identify a separate observation period.",
                 "Preserves the official reported count without assigning an unstated year.")))
    add("water_ocean_cruise_calls",lambda k:multi(k,["Annual-report snapshot"],[{"label":"Ocean cruise calls","values":[227],"color":"#ff9933"}],
        source=REPORT,unit="calls",chart="bar",note=_note("Year at a Glance overview, printed p.2; Ocean Cruise Calls snapshot; observation period not stated"),
        meta_=_m(PASSENGER,"Ocean Cruise Calls - Annual Report Snapshot","Reference period not separately stated","calls",
                 "Ocean cruise ship calls in the Ministry overview.","The snapshot reports 227 calls; it does not identify a separate observation period.",
                 "Complements the passenger count without assigning an unstated year.")))
    add("water_national_waterway_passenger_history", lambda k:_external_one(k,
        "Passenger Traffic on National Waterways", "National total, 2023-24 and 2024-25", ["2023-24", "2024-25"],
        [1.61, 7.64], "crore passengers", SANSAD_PASSENGERS,
        "Lok Sabha Unstarred Question 2182, answered 12 December 2025, part (a); National Waterways passenger traffic reported as 1.61 crore and 7.64 crore.",
        "Total passenger traffic recorded on India's National Waterways.",
        "The Ministry's answer reports 1.61 crore in 2023-24 and 7.64 crore in 2024-25.",
        "Adds the latest nationwide passenger movement figures directly reported to Parliament.", chart="bar"))
    add("water_inland_passenger_state_trends", lambda k:multi(k,IWT_PASSENGER_YEARS,[
        {"label":state,"values":values} for state,values in IWT_STATE_PASSENGERS.items()],source=IWT_STATS,
        unit="thousand passengers",chart="line",
        note=f"{IWT_STATS_NAME}, Table 3.2, printed p.62; state-government reports for table years 2019-2023; passenger totals in thousands. Bihar/other states with unavailable, zero, or repeated rows are excluded.",
        meta_=_m(PASSENGER,"Inland-Waterway Passenger Trends by State","State-government reports, table years 2019-2023","thousand passengers",
                 "Passenger totals carried by inland water vessels in the five states with usable annual series.",
                 "West Bengal's table-reported count is highest among the displayed states in 2022; its 2023 entry is 29,762.61 thousand. The source labels the table year basis 'Year Ending 31st March 2023'.",
                 "Shows state-reported passenger movement over time while omitting rows that are unavailable or marked as repeated.")))
    for state,values in IWT_STATE_PASSENGERS.items():
        slug=state.lower().replace(" ","_")
        add(f"water_{slug}_inland_passengers",lambda k,s=state,v=values:_external_one(k,
            f"{s} Inland-Waterway Passengers", "State-government reported totals, table years 2019-2023",
            IWT_PASSENGER_YEARS, v, "thousand passengers", IWT_STATS,
            f"{IWT_STATS_NAME}, Table 3.2, printed p.62; {s} row; passenger totals in thousands. The table labels its year basis 'Year Ending 31st March 2023'.",
            f"Passengers carried by inland water vessels in {s}, as reported by the State Government.",
            f"The source records {v[-1]:,.2f} thousand passengers for table year 2023.",
            "Adds a state-level historical series while retaining the source's units and year labels."))
    ranked_state_data={"West Bengal":29762.61,"Kerala":20262.39,"Maharashtra":18724.02,
                       "Assam":3155.38,"Karnataka":1283.79,"Uttar Pradesh":23.86}
    add("water_inland_passenger_state_rank_2023", lambda k:ranked(k,ranked_state_data,source=IWT_STATS,
        unit="thousand passengers",note=f"{IWT_STATS_NAME}, Table 3.2, printed p.62; year 2023, i.e. latest table year; state-government reports. States with unavailable or previous-year-repeated data are omitted.",
        meta_=_m(PASSENGER,"State-Reported Inland-Waterway Passengers","2023 table year; reporting states only","thousand passengers",
                 "Passenger totals for states with a reported, non-repeated 2023 value.",
                 "West Bengal reports 29,762.61 thousand and Uttar Pradesh 23.86 thousand; Bihar and Odisha are omitted because the table flags their FY2022-23 information as unavailable/repeated.",
                 "Compares only state observations that the source reports for the latest table year.")))
    add("water_ocean_cruise_passenger_history", lambda k:_external_one(k,
        "Ocean Cruise Passengers", "Reported comparison years, 2013-14 and 2022-23", ["2013-14", "2022-23"],
        [0.84, 4.72], "lakh passengers", PIB_CRUISE,
        "PIB release PRID 1974552, 3 November 2023; reports 84,000 ocean-cruise passengers in 2013-14 and 4.72 lakh in 2022-23.",
        "Passenger totals handled on ocean cruise calls at Indian ports.",
        "The release reports growth from 84,000 in 2013-14 to 4.72 lakh in 2022-23.",
        "Adds a year-separated cruise passenger comparison from the Ministry's official statement."))
    add("water_ocean_cruise_call_history", lambda k:_external_one(k,
        "Ocean Cruise Ship Calls", "Reported comparison years, 2013-14 and 2022-23", ["2013-14", "2022-23"],
        [102, 227], "calls", PIB_CRUISE,
        "PIB release PRID 1974552, 3 November 2023; reports 102 cruise ship calls in 2013-14 and 227 in 2022-23.",
        "Ocean cruise ship port calls in the reported years.",
        "The release reports 102 calls in 2013-14 and 227 in 2022-23.",
        "Separates vessel calls from passenger volumes rather than inferring passenger counts per call."))
    add("water_river_cruise_passengers",lambda k:_one(k,PASSENGER,"Overnight River Cruise Passengers","MoPSW scorecard, 2022-23 to 2023-24",["2022-23","2023-24"],
        [9606,11431],"passengers","Score Card—Inland Waterways, printed p.3; Overnight River Cruise Passengers",
        "Overnight river-cruise passenger numbers.","Passengers rose from 9,606 to 11,431.","Tracks passenger activity on inland river-cruise services."))
    add("water_international_ferry_route_launch",lambda k:multi(k,["2023-24"],[{"label":"Passenger ferry route launched","values":[1],"color":"#3fb950"}],
        source=REPORT,unit="route launch",chart="bar",note=_note("§1.8, ‘International Passenger Ferry Service (India and Sri Lanka)’, printed p.8; Nagapattinam–Kankesanthurai service flagged off 14 October 2023"),
        meta_=_m(PASSENGER,"International Passenger Ferry Service Launch","Nagapattinam–Kankesanthurai, 2023-24","route launch",
                 "One international passenger ferry route inauguration reported for 2023-24.",
                 "The service was flagged off on 14 October 2023; value counts the launch, not passengers or sailings.",
                 "Documents the reported international passenger-ferry service.")))
    add("water_port_turnaround_rank",lambda k:ranked(k,dict(zip(PORTS,TURNAROUND)),source=REPORT,unit="hours",
        note=_note("Table ‘Average Turn Round Time’, printed p.52; 2023-24 provisional; time measured from pilot boarding to deboarding"),
        meta_=_m(PERFORMANCE,"Average Vessel Turnaround by Major Port","2023-24 provisional","hours",
                 "Average vessel turnaround time for each major port.","Jawaharlal Nehru recorded 26.00 hours; Kolkata 82.61; all-ports average 48.06.",
                 "Measures vessel time in port from pilot boarding to deboarding.")))
    add("water_port_turnaround_history",lambda k:_one(k,PERFORMANCE,"Average Vessel Turnaround Time","All major ports, 2022-23 to 2023-24",["2022-23","2023-24"],
        [52.90,48.06],"hours","Table ‘Average Turn Round Time’, printed pp.52-53; all-ports total, 2023-24 provisional",
        "Average vessel turnaround at all major ports.","The average fell from 52.90 to 48.06 hours.","Lower turnaround means less time spent by vessels in port."))
    add("water_container_ship_turnaround",lambda k:_one(k,PERFORMANCE,"Container-Ship Turnaround Time","Major sea ports, 2022-23 to 2023-24",["2022-23","2023-24"],
        [30.10,30.12],"hours","Table ‘Average Turn Round Time’, printed p.53; container ships",
        "Average turnaround of container ships at major sea ports.","Container ship turnaround was 30.10 and 30.12 hours.",
        "Separates container-vessel turnaround from the all-vessel average."))
    add("water_ship_berth_output_rank",lambda k:ranked(k,dict(zip(PORTS,BERTH_OUTPUT)),source=REPORT,unit="tonnes per ship berth day",
        note=_note("Table ‘Average Output per Ship Berth Day’, printed p.53; 2023-24 provisional"),
        meta_=_m(PERFORMANCE,"Cargo Output per Ship Berth Day by Port","2023-24 provisional","tonnes per berth day",
                 "Cargo tonnes per ship berth day at each major port.","Paradip recorded 33,014 tonnes; all-ports total was 18,925.",
                 "Normalizes cargo-handling productivity by vessel berth time.")))
    add("water_ship_berth_output_history",lambda k:_one(k,PERFORMANCE,"Average Output per Ship Berth Day","All major ports, 2022-23 to 2023-24",["2022-23","2023-24"],
        [17605,18925],"tonnes per ship berth day","Table ‘Average Output per Ship Berth Day’, printed p.53; all-ports total",
        "Average cargo output per ship berth day.","The all-ports average rose from 17,605 to 18,925 tonnes.",
        "Higher output indicates greater average cargo-handling productivity."))
    return b


def _benchmark(observations):
    by_year = {}
    for country, values in observations.items():
        for year, value in values.items(): by_year.setdefault(str(year),{})[country] = value
    if not by_year: raise ValueError("World Bank returned no usable observations")
    year = max(by_year,key=lambda y:(len(by_year[y]),int(y)))
    return year,by_year[year]


def _world_bank_builders(get_json):
    cache = {}
    def observations(code):
        if code not in cache:
            try: cache[code] = wb_observations(get_json,WB_PEERS,code)
            except Exception as exc: cache[code] = exc
        result=cache[code]
        if isinstance(result,Exception): raise result
        return result
    def source(code): return wb_url(WB_PEERS,code)
    builders={}
    specs=[("container",WB_CODES["container"],"Container port traffic","TEUs","peer-set share, not global share"),
           ("connectivity",WB_CODES["connectivity"],"Liner shipping connectivity index","index points","peer-set index composition, not market share")]
    for slug,code,title,unit,share_note in specs:
        def trend(code=code,slug=slug,title=title,unit=unit):
            key=f"water_wb_{slug}_trend"; obs=observations(code)
            countries=[c for c in WB_PEERS if obs.get(c)]
            years=sorted({str(y) for c in countries for y in obs[c]},key=int)
            if not years: raise ValueError(f"No values for {code}")
            data=[{"label":WB_NAMES[c],"values":[obs[c].get(y) for y in years],"color":WB_COLORS[WB_PEERS.index(c)]} for c in countries]
            return multi(key,years,data,source=source(code),unit=unit,
                note=f"World Bank World Development Indicators API, indicator {code}; annual peer-country observations.",
                meta_=_m(GLOBAL,f"{title}: India and Peers","Annual observations",unit,
                    f"{title} for India and the listed maritime comparison economies.",
                    f"Trend includes {len(countries)} reporting peers; absent years remain blank, not imputed.",
                    "Compares India's long-run maritime performance with peer economies."))
        def rank(code=code,slug=slug,title=title,unit=unit):
            key=f"water_wb_{slug}_rank"; year,points=_benchmark(observations(code))
            ordered=sorted(points.items(),key=lambda x:(-x[1],WB_PEERS.index(x[0])))
            if len(ordered)<2: raise ValueError(f"Fewer than two countries for {code} in {year}")
            rank=1+sum(value>points["IND"] for value in points.values()) if "IND" in points else None
            read=f"At the widest-coverage year {year}, India ranks {rank} of {len(points)} available countries." if rank else f"Widest-coverage year is {year}; India has no value."
            return single(key,[WB_NAMES[c] for c,v in ordered],[v for c,v in ordered],source=source(code),unit=unit,chart="bar",horizontal=True,
                note=f"World Bank WDI API, {code}; ranked values use widest-coverage year {year}, including only countries reporting that year.",
                meta_=_m(GLOBAL,f"{title}: Peer Ranking",f"{year}, descending",unit,
                    f"Country ranking by {title} for the year with the widest peer coverage.",read,
                    "Uses one common year to avoid comparing different reporting periods."))
        def share(code=code,slug=slug,title=title,unit=unit,share_note=share_note):
            key=f"water_wb_{slug}_share"; year,points=_benchmark(observations(code))
            if len(points)<2 or any(v<0 for v in points.values()) or sum(points.values())<=0:
                raise ValueError(f"No valid peer-set shares for {code} in {year}")
            countries=sorted(points,key=lambda c:(-points[c],WB_PEERS.index(c)))
            india_share=points.get("IND",0)/sum(points.values())*100
            return single(key,[WB_NAMES[c] for c in countries],[points[c] for c in countries],source=source(code),unit=unit,chart="doughnut",
                note=f"World Bank WDI API, {code}; {year} values; doughnut normalises only the listed countries, not the entire world.",
                meta_=_m(GLOBAL,f"{title}: Peer-Set Composition",f"{year}; {share_note}",unit,
                    f"{title} for peer countries with values in {year}.",
                    f"India is {india_share:.1f}% of the displayed peer-set values in {year}; this is {share_note}.",
                    "Shows relative distribution among listed countries without implying a global total."))
        builders[f"water_wb_{slug}_trend"]=trend
        builders[f"water_wb_{slug}_rank"]=rank
        builders[f"water_wb_{slug}_share"]=share
    return builders


def build_water_transport_layer(get_json: Callable[[str],object], previous: dict[str,dict]) -> dict[str,dict]:
    """Build official water-transport series, retaining previous values on source failures."""
    builders=_static_builders()
    builders.update(_world_bank_builders(get_json))
    return with_fallback(builders,previous)
