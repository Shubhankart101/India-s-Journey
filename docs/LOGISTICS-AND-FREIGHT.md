# Logistics & Freight

Top-level dashboard group. Built by `scripts/logistics_layer.py`. A cross-mode view that deliberately repeats rail, sea and air freight figures under its own `log_` keys (the modal groups keep theirs) and adds road freight and a Logistics Revenue subgroup. Sources: Railway Board, AAI, MoCA, MoRTH/NHAI, MoPSW, DPIIT/NCAER, NITI Aayog via PIB, World Bank. Road freight tonne-km is omitted because the World Bank has no observations for India; truck registrations, permits and operator revenue were skipped as unverified. Bases differ by mode (tonnes vs tonne-km) and each chart notes its own. If a live pull fails, the previous value is kept.

## Subgroups (43 charts)

| Subgroup | Charts |
|---|---|
| Road Freight | 8 |
| Rail Freight | 8 |
| Sea Freight | 9 |
| Air Freight | 4 |
| Modal Split & Comparison | 7 |
| Logistics Revenue | 7 |

## Source documents used

| Source | Charts |
|---|---|
| <https://rb.indianrailways.gov.in/public/ourOrganization/public/pdf/IR%20Year%20Book%202023-24-English_f937bf20_1762054799339.pdf> | 9 |
| <https://shipmin.gov.in/sites/default/files/Annual%20Report%202023-24_English.pdf> | 5 |
| <https://nhai.gov.in/nhai/sites/default/files/2025-09/NHAI-Annual_Report_2023-24_English.pdf> | 4 |
| <https://shipmin.gov.in/sites/default/files/UPDATE%20ON%20INDIAN%20PORT%20SECTOR%2031.03.2024.pdf> | 3 |
| <https://www.aai.aero/sites/default/files/AAI%20AR_2024_ENG_05.12.2024.pdf> | 3 |
| <https://pib.gov.in/PressReleasePage.aspx?PRID=2091508> | 2 |
| <https://pib.gov.in/PressReleaseIframePage.aspx?PRID=1993425&reg=3&lang=2> | 2 |
| <https://pib.gov.in/PressReleasePage.aspx?PRID=2111286&reg=48&lang=2> | 2 |
| <https://pib.gov.in/PressReleaseIframePage.aspx?PRID=2116158> | 2 |
| <https://www.dpiit.gov.in/static/uploads/2025/09/c0d7c33f0b737ed71728ff6c2a35f1e7.pdf> | 2 |
| <https://www.dpiit.gov.in/static/uploads/2025/07/54df328bcdceeff75188644557d2dacb.pdf> | 2 |
| <https://pib.gov.in/PressReleaseIframePage.aspx?PRID=2112843&reg=48&lang=2> | 1 |
| <https://data.worldbank.org/indicator/IS.RRS.GOOD.MT.K6?locations=IN> | 1 |
| <https://data.worldbank.org/indicator/IS.SHP.GOOD.TU?locations=IN> | 1 |
| <https://www.civilaviation.gov.in/our-performance> | 1 |
| <https://databank.worldbank.org/embed/LPI/id/154e8630> | 1 |
| <https://pib.gov.in/PressReleaseIframePage.aspx?PRID=2082758> | 1 |
| <https://pib.gov.in/PressReleaseIframePage.aspx?PRID=2113222> | 1 |
