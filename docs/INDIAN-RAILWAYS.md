# Indian Railways

Top-level dashboard group built by `scripts/indian_railways_layer.py`. Static series are transcribed from the Railway Board's Year Book 2023-24; global comparisons are live World Bank pulls. If a live pull fails, the previous value is kept.

## Sources and what they say

| Source | Used for |
|---|---|
| [Railway Board Year Book 2023-24](https://rb.indianrailways.gov.in/public/ourOrganization/public/pdf/IR%20Year%20Book%202023-24-English_f937bf20_1762054799339.pdf) | Route length 69,181 km (53,596 km in 1950-51); electrified route 62,253 km with 4,644 km added in 2023-24; 6,905 million passengers originating; 1,064,700 million passenger-km; 1,588.06 million tonnes of revenue-earning freight, 973,968 million net tonne-km, coal 49.55%; 40 consequential accidents; operating ratio 98.43%. Zone and State route-km each reconcile to 69,181. Also fleet, gauge, earnings and yield tables. |
| PIB releases | Freight loading to 2024-25. |
| [World Bank](https://data.worldbank.org/indicator/IS.RRS.GOOD.MT.K6) | `IS.RRS.GOOD.MT.K6` freight, `IS.RRS.PASG.KM` passenger-km, `IS.RRS.TOTL.KM` route length, for India and peers. Benchmark year 2019, because most countries stop reporting around then. |

## Subgroups

Network & Electrification, Passenger Services, Freight Operations, Rolling Stock & Operations, Railway Safety, Finance & Efficiency, Global Rail Comparison (38 charts). Art: scenes `rail-*`.
