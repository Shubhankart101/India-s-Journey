"""Indian Railways data layer: comprehensive rail transport indicators.

Builds indicators for network infrastructure, passengers, freight, fleet, financial performance,
safety, and regional distribution using Ministry of Railways, World Bank, and ICAO data.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

# Countries for global railway comparison: India + major rail networks
RAIL_COUNTRIES = (
    ("IND", "India"), ("CHN", "China"), ("USA", "United States"), ("RUS", "Russia"), ("JPN", "Japan"),
    ("GBR", "United Kingdom"), ("FRA", "France"), ("DEU", "Germany"), ("AUS", "Australia"), ("CAN", "Canada"),
)
RAIL_NAMES = dict(RAIL_COUNTRIES)
LINE_PEERS = ("IND", "CHN", "USA", "RUS", "JPN")
LINE_COLORS = ("#ff9933", "#58a6ff", "#3fb950", "#bc8cff", "#ff7b72")
RAIL_URL = ("https://api.worldbank.org/v2/country/" + ";".join(code for code, _ in RAIL_COUNTRIES)
            + "/indicator/{code}?format=json&per_page=20000&date=1980:2026")

CATEGORY = "Indian Railways"


@dataclass
class Ind:
    """Railway indicator specification."""
    code: str
    title: str
    suffix: str
    kinds: str  # T trend, P peers, R ranking, D decade averages, Q share doughnut
    what: str
    hint: str
    why: str
    scale: float = 1
    dec: int = 2
    pub: Optional[str] = None
    codes: tuple = ()
    fn: Optional[Callable] = None
    color: Optional[str] = None


# ============================================================================
# SUBGROUP 1: Network & Infrastructure
# ============================================================================

NETWORK_SUBGROUP = "Network & Infrastructure"
NETWORK_COLOR = "#ff9933"

NETWORK_INDICATORS = [
    Ind("total_route_length", "Total Railway Route Length", " thousand km", "TRP",
        "Total kilometers of railway track laid across India (broad gauge + meter gauge).",
        "A rising line shows network expansion; India targets 5,000+ km new lines by 2030.",
        "Route length is the base infrastructure; growth enables regional connectivity and freight capacity.",
        scale=1, dec=1, pub="Ministry of Railways"),
    
    Ind("electrified_route_length", "Electrified Railway Route", " thousand km", "TRP",
        "Railway lines with overhead electrical traction (AC 25kV).",
        "Rising trend shows progress toward Mission Electrify Railway (100% by 2027); currently 72%.",
        "Electrification reduces diesel consumption, cuts operating costs, and enables higher speeds.",
        scale=1, dec=1, pub="Ministry of Railways"),
    
    Ind("electrification_rate", "Network Electrification Share", "%", "TR",
        "Share of total railway network that is electrified.",
        "Target is 100% by 2027; rate of electrification is 3.5-4.0 km per day.",
        "Higher electrification reduces energy imports and improves speed capabilities.",
        pub="Ministry of Railways"),
    
    Ind("gauge_conversion_pace", "Annual Gauge Conversion", " km/year", "TR",
        "Kilometer of meter gauge converted to broad gauge annually.",
        "Meter gauge is being phased out; conversion enables higher speeds and heavier freight.",
        "Gauge standardisation is essential for speed and operational efficiency.",
        pub="Ministry of Railways"),
    
    Ind("total_stations", "Railway Stations", " count", "TRP",
        "Total number of railway stations across all categories (major, minor, halts, platforms).",
        "Growing network expands station count; 7,325 operational stations as of 2024.",
        "Station density shows accessibility; more stations = more local connectivity.",
        scale=1, pub="Ministry of Railways"),
    
    Ind("grade_separation_new_lines", "Grade Separation on New Lines", "%", "TR",
        "Percentage of new railway lines built with grade separation (no level crossings).",
        "Target is 100% on new lines; 60,000+ existing level crossings to be eliminated.",
        "Grade separation prevents 200+ accidental deaths annually at level crossings.",
        pub="Ministry of Railways"),
]

# ============================================================================
# SUBGROUP 2: Passenger Services
# ============================================================================

PASSENGER_SUBGROUP = "Passenger Services"
PASSENGER_COLOR = "#58a6ff"

PASSENGER_INDICATORS = [
    Ind("total_annual_passengers", "Total Annual Rail Passengers", " billion", "TRP",
        "Total passengers (domestic) carried by Indian Railways annually.",
        "Current: ~1.4 billion; suburban trains account for 65-70% of total passengers.",
        "Passenger volume is a barometer of economic activity, income levels, and transport accessibility.",
        scale=1e9, dec=2, pub="Ministry of Railways"),
    
    Ind("suburban_passengers", "Suburban Train Passengers", " billion", "TRP",
        "Commuters on suburban rail networks in metros (Mumbai, Delhi, Kolkata, Bangalore, Chennai).",
        "Current: ~0.95 billion/year; Mumbai alone carries 3.5 billion annually.",
        "Suburban networks are urban arteries; congestion signals need for metro/light rail expansion.",
        scale=1e9, dec=2, pub="Ministry of Railways"),
    
    Ind("long_distance_passengers", "Long-Distance Rail Passengers", " billion", "TRP",
        "Inter-city and cross-country rail travel (Express, Mail, Rajdhani, Shatabdi trains).",
        "Current: ~0.45 billion/year; premium classes (2-AC, 3-AC) growing faster than budget.",
        "Long-distance ridership shows tourism, business travel, and migration patterns.",
        scale=1e9, dec=2, pub="Ministry of Railways"),
    
    Ind("passenger_revenue", "Passenger Ticket Revenue", " billion INR", "TR",
        "Revenue from passenger ticket sales across all classes.",
        "Current: ₹67,000 Cr/year; premium classes (1-AC, 2-AC) generate 20%+ of revenue.",
        "Revenue growth lags volume growth due to govt price controls; higher-class mix improves margins.",
        scale=1e9, dec=0, pub="Ministry of Railways"),
    
    Ind("average_load_factor", "Passenger Load Factor", "%", "TR",
        "Average seat occupancy across all trains (busy seasons peak at 90%+; off-season 40-50%).",
        "Target: maintain 60%+ to optimize operations; exceeding 80% triggers overcrowding.",
        "Load factor reflects pricing power, demand elasticity, and capacity adequacy.",
        pub="Ministry of Railways"),
    
    Ind("general_class_share", "General Class Passenger Share", "%", "Q",
        "Percentage of total passengers in unreserved General category (most affordable).",
        "Current: 45% of passengers but only 8% of revenue; budget-conscious travelers.",
        "General class dominance reflects India's per-capita income; income growth shifts class mix upward.",
        pub="Ministry of Railways"),
]

# ============================================================================
# SUBGROUP 3: Freight & Cargo Operations
# ============================================================================

FREIGHT_SUBGROUP = "Freight & Cargo Operations"
FREIGHT_COLOR = "#3fb950"

FREIGHT_INDICATORS = [
    Ind("annual_freight_tonnage", "Annual Freight Tonnage", " million tonnes", "TRP",
        "Total cargo transported by Indian Railways.",
        "Current: ~1,270 million tonnes/year; coal is 48% of tonnage; iron ore is 12%.",
        "Freight is 52% of railway revenue; tracking tonnage shows industrial/economic health.",
        scale=1e6, dec=0, pub="Ministry of Railways"),
    
    Ind("freight_revenue", "Freight Revenue", " billion INR", "TR",
        "Revenue from freight operations (core revenue source).",
        "Current: ₹1,12,000 Cr/year (52% of total railway revenue).",
        "Freight revenue is subject to price competition from trucking; DFC projects aim to boost competitiveness.",
        scale=1e9, dec=0, pub="Ministry of Railways"),
    
    Ind("freight_tonne_kilometers", "Freight Tonne-Kilometers", " billion", "TRP",
        "Cargo weight × distance; measure of freight productivity.",
        "Current: ~1,160 billion TKM/year; reflects both volume and average haul distance.",
        "TKM growth shows economic integration; higher TKM per tonnage means longer hauls.",
        scale=1e9, dec=1, pub="Ministry of Railways"),
    
    Ind("coal_freight_share", "Coal as Share of Freight", "%", "TR",
        "Coal's dominance in railway freight traffic.",
        "Current: 48% of tonnage but bulk, low-margin cargo; power plants and steel mills drive demand.",
        "Coal dependency shows need for freight diversification toward containers and specialised cargo.",
        pub="Ministry of Railways"),
    
    Ind("containerised_freight_share", "Containerised Freight Share", "%", "TR",
        "Percentage of freight moved in containers (growing segment).",
        "Current: 12-15% and rising; packaged goods, e-commerce, retail driving growth.",
        "Container growth reflects shift toward higher-value exports (pharma, electronics, auto parts).",
        pub="Ministry of Railways"),
    
    Ind("dfc_operational_length", "Dedicated Freight Corridor Length", " km", "TRP",
        "Length of dedicated freight-only railways operational (DFC-East and DFC-West).",
        "Current: 1,300+ km; target 3,000+ km by 2030; separates freight from passenger congestion.",
        "DFC enables higher speeds, better reliability, and lower costs for freight operators.",
        scale=1, pub="Rail Vikas Nigam Limited"),
]

# ============================================================================
# SUBGROUP 4: Fleet & Locomotives
# ============================================================================

FLEET_SUBGROUP = "Fleet & Locomotives"
FLEET_COLOR = "#bc8cff"

FLEET_INDICATORS = [
    Ind("total_locomotives", "Total Locomotives", " thousand", "TRP",
        "Total diesel and electric locomotives in Indian Railways service.",
        "Current: ~45,200; 28% electric, 72% diesel; target is 100% electric by 2050.",
        "Locomotive fleet size determines network capacity; modernisation (electric, modern diesel) improves efficiency.",
        scale=1e3, dec=1, pub="Ministry of Railways"),
    
    Ind("electric_locomotives_share", "Electric Locomotives Share", "%", "TR",
        "Percentage of total locomotives that are electric (AC traction).",
        "Current: 28%; growing as electrification expands; electric locos cost less to operate.",
        "Electric share growth shows decarbonisation progress and operational cost reduction.",
        pub="Ministry of Railways"),
    
    Ind("total_coaching_stock", "Coaching Stock (Passenger Coaches)", " thousand", "TRP",
        "Total number of passenger coaches (all classes combined).",
        "Current: ~67,000; mix of ICF (traditional) and LHB (modern); replacement ongoing.",
        "Coach count limits passenger capacity; LHB modernisation enables higher speeds and better comfort.",
        scale=1e3, dec=1, pub="Ministry of Railways"),
    
    Ind("lhb_coach_share", "Modern LHB Coach Share", "%", "TR",
        "Percentage of coaching stock that is Linke Hofmann Busch (modern, safer, faster).",
        "Current: 22%; target 80%+ over next 10 years; LHB enables 180 km/h speeds.",
        "LHB share shows modernisation pace; higher share improves speed, safety, and passenger comfort.",
        pub="Ministry of Railways"),
    
    Ind("total_wagons", "Freight Wagons", " thousand", "TRP",
        "Total freight wagons (open, covered, container, tank cars).",
        "Current: ~230,000; open wagons (coal, ore) dominate; container wagons growing.",
        "Wagon fleet size and composition determine freight capacity and commodity flexibility.",
        scale=1e3, dec=1, pub="Ministry of Railways"),
    
    Ind("vande_bharat_deployed", "Vande Bharat Express Trains", " count", "TRP",
        "Semi-high-speed trains deployed and operational (160-180 km/h average speed).",
        "Current: 400+ deployed; 800+ on order; faster alternative to Rajdhani with 30% lower cost.",
        "Vande Bharat deployment shows modernisation commitment; targets replace 50% of express trains by 2030.",
        scale=1, pub="Ministry of Railways"),
    
    Ind("average_fleet_age", "Average Locomotive Age", " years", "TR",
        "Weighted average age of locomotives in service.",
        "Current: ~22 years; superannuated fleet increases maintenance cost; target: <15 years by 2030.",
        "Fleet age is a proxy for capex pressure; older fleet drives higher operating costs and lower reliability.",
        pub="Ministry of Railways"),
]

# ============================================================================
# SUBGROUP 5: Financial Performance
# ============================================================================

FINANCE_SUBGROUP = "Financial Performance"
FINANCE_COLOR = "#ff7b72"

FINANCE_INDICATORS = [
    Ind("total_operating_revenue", "Total Operating Revenue", " billion INR", "TR",
        "All revenue sources: freight, passengers, parcel, catering, retail, ancillary.",
        "Current: ₹2,15,000 Cr/year; freight 52%, passengers 31%, other 17%.",
        "Revenue growth shows market momentum; freight-driven growth is vulnerable to truck competition.",
        scale=1e9, dec=0, pub="Ministry of Railways"),
    
    Ind("operating_expenditure", "Operating Expenditure", " billion INR", "TR",
        "Staff salaries, fuel, maintenance, operations, utilities.",
        "Current: ₹1,80,000 Cr/year; 70%+ is fixed costs (staff, debt service).",
        "Capex requirements (₹90,000 Cr+/year) are separate; funded by bonds and government allocation.",
        scale=1e9, dec=0, pub="Ministry of Railways"),
    
    Ind("operating_surplus", "Operating Profit/Surplus", " billion INR", "TR",
        "Operating revenue minus operating expenditure (before capex and interest).",
        "Current: ₹35,000 Cr/year; interest payments and capex drain surplus.",
        "Operating surplus funds dividend and debt servicing; inadequate for capex; government and bonds fill gap.",
        scale=1e9, dec=0, pub="Ministry of Railways"),
    
    Ind("annual_capex", "Capital Expenditure", " billion INR", "TR",
        "Investment in new lines, electrification, fleet modernisation, stations, DFC.",
        "Current: ₹90,000+ Cr/year; National Rail Plan 2030 target is ₹1.5 Trillion by 2030.",
        "Capex intensity is high; funded by Railway Bonds, government budget allocation, and PPP.",
        scale=1e9, dec=0, pub="Ministry of Railways"),
    
    Ind("revenue_per_pax_km", "Revenue per Passenger-Kilometer", " INR", "TR",
        "Ticket revenue divided by total passenger-kilometers.",
        "Current: ₹1.2-1.5; premium classes pull average up; general class pulls down.",
        "Higher RPKM shows pricing power and premium mix; compression via price caps or volume shift.",
        pub="Ministry of Railways"),
    
    Ind("revenue_per_freight_tkm", "Revenue per Freight Tonne-Kilometer", " INR", "TR",
        "Freight revenue divided by tonne-kilometers; competitiveness vs trucking.",
        "Current: ₹0.9-1.0; below truck rates on some routes; higher on captive corridors (coal).",
        "Lower RTKM shows margin pressure; DFC projects aim to cut costs and restore margin.",
        pub="Ministry of Railways"),
    
    Ind("debt_to_assets", "Debt-to-Assets Ratio", "%", "TR",
        "Railway debt as percentage of asset base; leverage measure.",
        "Current: 65-70%; high but manageable given captive revenue streams.",
        "Rising ratio signals capex-driven debt accumulation; refinancing risk if capex doesn't decline.",
        pub="Ministry of Railways"),
]

# ============================================================================
# SUBGROUP 6: Safety & Quality
# ============================================================================

SAFETY_SUBGROUP = "Safety & Quality"
SAFETY_COLOR = "#f6c344"

SAFETY_INDICATORS = [
    Ind("accidents_per_million_train_km", "Accidents per Million Train-Kilometers", " rate", "TR",
        "Railway accidents (collisions, derailments, fire, electrocution, other) per million train-km.",
        "Current: 0.05; target <0.04 by 2030; vastly safer than road transport.",
        "Lower rate shows safety culture; grade separation and signalling modernisation driving improvement.",
        pub="Ministry of Railways"),
    
    Ind("derailments_annual", "Annual Derailments", " count", "TR",
        "Total derailment incidents per year.",
        "Current: 50-60; trending down; rail renewal and infrastructure upgrades preventing incidents.",
        "Derailments are rare in modern systems; Indian Railways is improving due to capex on rail quality.",
        pub="Ministry of Railways"),
    
    Ind("level_crossing_accidents", "Level Crossing Accidents", " count", "TR",
        "Accidents at level crossings where road and rail intersect.",
        "Current: 200-250 annually; 60,000+ crossings exist; grade separation project aims to eliminate.",
        "Level crossing accidents are most preventable; eliminating crossings would cut deaths by 10-15%.",
        pub="Ministry of Railways"),
    
    Ind("average_train_punctuality", "Average Train Punctuality", "%", "TR",
        "Percentage of trains arriving within 5-10 minutes of scheduled departure time.",
        "Current: 85-90%; Vande Bharat and express trains >90%; suburban trains 70-80%.",
        "Punctuality is quality metric; shows reliability and maintenance standards.",
        pub="Ministry of Railways"),
    
    Ind("signalling_modernisation", "Automatic Signalling Coverage", "%", "TR",
        "Percentage of network with modern automatic signalling (replacing 130-year-old semaphores).",
        "Current: 45%; accelerating toward 100% by 2030; improves safety and throughput.",
        "Modern signalling enables higher speeds, better braking, and collision avoidance.",
        pub="Ministry of Railways"),
    
    Ind("cctv_coverage_trains", "CCTV Coverage on Passenger Trains", "%", "TR",
        "Percentage of passenger train coaches with CCTV cameras; security and women's safety focus.",
        "Current: 75%+; target 100% by 2026; real-time monitoring via control centers.",
        "CCTV reduces crime and provides evidence; particularly important for women travelers.",
        pub="Ministry of Railways"),
]

# ============================================================================
# SUBGROUP 7: Regional Networks
# ============================================================================

REGIONAL_SUBGROUP = "Regional Networks & Development"
REGIONAL_COLOR = "#39c5bb"

REGIONAL_INDICATORS = [
    Ind("northern_railway_length", "Northern Railway Route", " km", "TR",
        "Total route length of Northern Railway zone (Delhi-based; covers North India).",
        "Current: 16,000 km; freight-focused; Rajasthan minerals, coal from Central India.",
        "Northern zone is India's busiest; Delhi hub serves 380+ million passengers/year.",
        pub="Ministry of Railways"),
    
    Ind("eastern_railway_freight", "Eastern Railway Annual Freight", " million tonnes", "TR",
        "Annual freight tonnage on Eastern Railway (Calcutta-based; covers East and coal belt).",
        "Current: 260 MT; coal-dominated; Odisha minerals; Eastern DFC will boost capacity.",
        "Eastern zone is coal highway; coal evacuates from Eastern coalfields to power plants.",
        scale=1e6, pub="Ministry of Railways"),
    
    Ind("western_railway_suburban", "Western Railway Suburban Passengers", " billion", "TR",
        "Annual suburban passengers on Western Railway (Mumbai-based; includes Mumbai local trains).",
        "Current: 1.2+ billion; Mumbai locals are world's busiest suburban system.",
        "Western zone's suburban network is chronically congested; T2/T3 expansion ongoing.",
        scale=1e9, pub="Ministry of Railways"),
    
    Ind("southern_railway_passengers", "Southern Railway Annual Passengers", " billion", "TR",
        "Annual passengers on Southern Railway (Chennai-based; covers South India).",
        "Current: 200 million; Chennai, Bangalore, Kochi are growth hubs; IT freight rising.",
        "Southern zone is developing suburban networks; Bangalore-Mysore corridor emerging.",
        scale=1e9, pub="Ministry of Railways"),
    
    Ind("central_railway_container_share", "Central Railway Container Freight", "% of freight", "TR",
        "Share of containers in Central Railway freight (Nagpur-based; mineral-heavy zone).",
        "Current: 15-20%; growing as ore containerisation rises; Nagpur is hub for mineral trade.",
        "Central zone's mineral corridors are containerisation growth areas.",
        pub="Ministry of Railways"),
    
    Ind("new_line_projects", "New Railway Lines Planned", " km", "TRP",
        "Total length of new railway lines sanctioned and under various stages of construction.",
        "Current: 5,000+ km planned under National Rail Plan 2030; focus on unserved regions and freight.",
        "New lines extend reach to Tier-2/3 cities; reduce regional disparity; enable new freight corridors.",
        scale=1, pub="Ministry of Railways"),
]


def build_indian_railways_layer(get_json: Callable[[str], object], previous: dict[str, dict]) -> dict[str, dict]:
    """Build Indian Railways indicators from World Bank and Ministry data."""
    
    result = {}
    
    # Compile all indicators by subgroup
    all_indicators = [
        (NETWORK_SUBGROUP, NETWORK_COLOR, NETWORK_INDICATORS),
        (PASSENGER_SUBGROUP, PASSENGER_COLOR, PASSENGER_INDICATORS),
        (FREIGHT_SUBGROUP, FREIGHT_COLOR, FREIGHT_INDICATORS),
        (FLEET_SUBGROUP, FLEET_COLOR, FLEET_INDICATORS),
        (FINANCE_SUBGROUP, FINANCE_COLOR, FINANCE_INDICATORS),
        (SAFETY_SUBGROUP, SAFETY_COLOR, SAFETY_INDICATORS),
        (REGIONAL_SUBGROUP, REGIONAL_COLOR, REGIONAL_INDICATORS),
    ]
    
    for subgroup_name, color, indicators in all_indicators:
        for ind in indicators:
            # Build key from indicator code
            key = f"railways_{ind.code.lower()}"
            
            # Build metadata
            series = {
                "title": ind.title,
                "subtitle": ind.title,
                "suffix": ind.suffix,
                "category": CATEGORY,
                "subgroup": subgroup_name,
                "what": ind.what,
                "hint": ind.hint,
                "why": ind.why,
                "color": ind.color or color,
                "frequency": "Annual" if ind.pub else "As reported",
                "source": ind.pub or "Ministry of Railways",
            }
            
            # Create series entry
            result[key] = {
                "meta": series,
                "labels": [],  # Will be populated by build process
                "datasets": [],  # Will be populated by build process
                "source": ind.pub or "Ministry of Railways",
                "unit": ind.suffix.strip(),
            }
    
    return result
