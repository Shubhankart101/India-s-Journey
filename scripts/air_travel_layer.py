"""Air Travel & Civil Aviation indicators for India.

This layer builds air travel statistics from World Bank, IATA, and Ministry of Civil Aviation sources.
Includes domestic aviation, international aviation, airport infrastructure, and airline performance metrics.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

# Countries for global comparison: India + major aviation markets
COUNTRIES = (
    ("IND", "India"), ("CHN", "China"), ("USA", "United States"), ("JPN", "Japan"), ("DEU", "Germany"),
    ("GBR", "United Kingdom"), ("FRA", "France"), ("BRA", "Brazil"), ("AUS", "Australia"), ("ARE", "United Arab Emirates"),
)
NAMES = dict(COUNTRIES)
LINE_PEERS = ("IND", "CHN", "USA", "JPN", "GBR")
LINE_COLORS = ("#ff9933", "#58a6ff", "#3fb950", "#bc8cff", "#ff7b72")
URL = ("https://api.worldbank.org/v2/country/" + ";".join(code for code, _ in COUNTRIES)
       + "/indicator/{code}?format=json&per_page=20000&date=1980:2026")

CATEGORY, SUBGROUP = "Industry Trends & Performance", "Air Travel & Civil Aviation"


@dataclass
class Ind:
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


def build_air_travel_layer(get_json: Callable[[str], object], previous: dict[str, dict]) -> dict[str, dict]:
    """Build air travel indicators from World Bank and IATA data."""
    
    result = {}
    
    # 1. Air Passenger Traffic - Domestic and International
    indicators = [
        Ind("IS.AIR.PSGR", "Civil Aviation Passengers", " million", "TRP",
            "Total number of civil aviation passengers (domestic and international combined).",
            "Higher values show a growing aviation market; steeper trends signal rapid expansion.",
            "Passenger traffic is a barometer of economic growth, income levels, and market liberalisation.",
            scale=1e6, dec=1),
        
        Ind("IS.AIR.DPRT", "Aircraft Departures", " thousand", "TRP",
            "Total number of aircraft departures from airports (all civil aviation flights).",
            "Rising lines show increased flight frequency and connectivity.",
            "Departure growth precedes passenger growth; it signals network expansion and route opening.",
            scale=1e3, dec=1),
        
        Ind("air_passengers_growth", "Year-on-Year Passenger Growth", "%", "TR",
            "Annual growth rate of civil aviation passengers.",
            "Positive growth means the aviation market is expanding; negative shows contraction.",
            "Growth rates show elasticity of demand to income changes and policy reforms.",
            codes=("IS.AIR.PSGR",), fn=lambda passengers: None),  # Computed downstream
        
        Ind("air_passengers_per_1000", "Air Passengers per 1,000 People", " per 1,000", "TP",
            "Total civil aviation passengers divided by population (annual rate).",
            "Higher values show aviation is more embedded in daily life.",
            "Peer comparison reveals India's air travel penetration vs developed economies.",
            codes=("IS.AIR.PSGR", "SP.POP.TOTL"), fn=lambda p, pop: p / pop * 1000),
        
        Ind("IS.AIR.GOOD.MT.K1", "Air Cargo", " million tonne-km", "TRP",
            "Cargo carried by commercial air transport in millions of tonne-kilometers.",
            "Bigger numbers mean more freight moving by air; critical for pharmaceuticals and tech exports.",
            "Air cargo is India's fastest-growing export segment; tracking it shows global trade integration.",
            scale=1e6, dec=1, color="#ff7b72"),
        
        Ind("air_cargo_per_pop", "Air Cargo Intensity", " tonne-km per capita", "TR",
            "Air cargo volume per person, reflecting export orientation and pharma/tech sector strength.",
            "Rising trends show more high-value goods moving through Indian hubs.",
            "Cargo intensity benchmarks India's position in global supply chains.",
            codes=("IS.AIR.GOOD.MT.K1", "SP.POP.TOTL"), fn=lambda c, pop: c / pop),
    ]
    
    # 2. Aviation Market Share and Rankings
    def _ranked_chart(title: str, subtitle: str, codes: str, what: str, hint: str, why: str, suffix: str = " passengers") -> Ind:
        """Helper to create ranking-style indicators."""
        return Ind(f"air_rank_{codes.lower()}", title, suffix, "PR",
                  what, hint, why, pub=codes)
    
    # 3. Airport Infrastructure
    airport_indicators = [
        Ind("air_ports_count", "Major Airports", " count", "Q",
            "Number of major airports with scheduled commercial services.",
            "Bigger numbers mean more distributed air connectivity; slices show airport tier concentration.",
            "Airport network density shows how accessible air travel is across regions.",
            pub="Ministry of Civil Aviation, India"),
        
        Ind("airport_passengers_capacity", "Airport Passenger Capacity Utilization", "%", "TR",
            "Average utilization of passenger handling capacity across major Indian airports.",
            "Higher utilization shows airports running near maximum; spikes trigger expansion.",
            "Capacity utilization signals infrastructure bottlenecks and investment needs.",
            pub="Airports Authority of India (AAI)"),
    ]
    
    # Add all indicators
    for ind in indicators + airport_indicators:
        key = f"air_{ind.code.lower()}" if not ind.code.startswith("IS.AIR") else f"air_{ind.code.lower()}"
        series = {
            "title": ind.title,
            "subtitle": ind.title,
            "suffix": ind.suffix,
            "category": CATEGORY,
            "subgroup": SUBGROUP,
            "what": ind.what,
            "hint": ind.hint,
            "why": ind.why,
            "color": ind.color or "#ff9933",
            "frequency": "Annual" if "Annual" not in ind.what else "As reported",
        }
        result[key] = {"meta": series}
    
    return result
