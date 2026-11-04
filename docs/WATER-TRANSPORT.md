# Water Transport & Shipping

Top-level dashboard group. Built by `scripts/water_transport_layer.py` from Ministry of Ports, Shipping and Waterways, Indian Ports Association, IWAI and DG Shipping documents, PIB and live World Bank indicators (container port traffic, liner shipping connectivity). Covers freight and passenger traffic by water. Series that could not be read from an official document are omitted. If a live pull fails, the previous value is kept.

## Subgroups (43 charts)

| Subgroup | Charts |
|---|---|
| Port Cargo Traffic | 17 |
| Inland Waterways | 5 |
| Coastal Shipping | 5 |
| Water Passenger Traffic | 5 |
| Container & Port Performance | 5 |
| Global Maritime Comparison | 6 |

## Source documents used

| Source | Charts |
|---|---|
| <https://shipmin.gov.in/sites/default/files/Annual%20Report%202023-24_English.pdf> | 37 |
| <https://api.worldbank.org/v2/country/IND;CHN;SGP;USA;ARE;KOR;NLD;DEU;JPN;MYS;VNM;BRA;AUS/indicator/IS.SHP.GOOD.TU?format=json&per_page=5000&date=1990:2025> | 3 |
| <https://api.worldbank.org/v2/country/IND;CHN;SGP;USA;ARE;KOR;NLD;DEU;JPN;MYS;VNM;BRA;AUS/indicator/IS.SHP.GCNW.XQ?format=json&per_page=5000&date=1990:2025> | 3 |
