# Air Travel & Civil Aviation

Top-level dashboard group built by `scripts/air_travel_layer.py`. Static series are transcribed from official documents; the global comparisons are live World Bank pulls (ICAO data). If a live pull fails, the previous value is kept.

## Sources and what they say

| Source | Used for |
|---|---|
| [AAI Annual Report 2023-24](https://www.aai.aero/sites/default/files/AAI%20AR_2024_ENG_05.12.2024.pdf) | Traffic at all Indian airports: 376.43 million passengers (domestic 306.79, international 69.64), 2,677.59 thousand aircraft movements, 3,365.68 thousand tonnes of freight in 2023-24 (2022-23: 327.28 million, 2,508.32 thousand, 3,146.80 thousand). AAI manages 133 airports (8 privately run). Revenue Rs 15,979.83 crore, profit after tax Rs 4,651.31 crore, capital expenditure Rs 5,335 crore in 2023-24. UDAN: 559 routes, 84 airports, 136 lakh passengers at 31 March 2024. |
| [Ministry of Civil Aviation](https://www.civilaviation.gov.in/our-performance) and Lok Sabha reply of 4 December 2025 | 164 operational airports in 2025 (74 in 2014); scheduled passengers carried 165.5 million domestic and 74.14 million international in 2024-25 (153.7 and 66.8 million in 2023-24); cargo 3.72 million tonnes in 2024-25 (2.53 in 2014-15); UDAN 657 routes, 93 airports, 159 lakh passengers at 31 December 2025. |
| [World Bank](https://data.worldbank.org/indicator/IS.AIR.PSGR) (ICAO) | `IS.AIR.PSGR` passengers, `IS.AIR.DPRT` departures, `IS.AIR.GOOD.MT.K1` freight, `SP.POP.TOTL` population, for India and ten peers. Benchmark year 2023. |

**Basis caution:** AAI counts passengers handled at airports (arrivals plus departures); the Ministry counts passengers carried by scheduled airlines. They are shown on separate charts and are not comparable.

## Subgroups

Air Passenger Growth, Global Aviation Comparison, Domestic vs International, Airports & UDAN, Air Cargo, AAI Finance & Investment (27 charts). Art: `scripts/generate_art.py` scenes `air-*`.
