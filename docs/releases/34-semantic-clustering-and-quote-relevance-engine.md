# Release 34: Semantic Indicator Clustering, Accurate Multi-Theater Section Titling & Quote Relevance Engine

- **Commit:** [`HEAD`](https://github.com/Shubhankart101/India-s-Journey)
- **Date:** 2026-11-15
- **Scope:** All 13 Categories, 137 Subgroups, 3,081 Indicators, and Subgroup Long-Form Articles

---

## Executive Summary

Release 34 addresses two major content quality issues across the long-form articles of all groups and subgroups in India's Journey:
1. **Elimination of Quote-to-Indicator Mismatches:** Previously, a global pull quote computed from the highest percentage shift across the entire subgroup was injected at the end of Section 2 via `quoteAfterSection={1}`. In subgroups like `Health Spending & Disease Burden`, this caused an immunisation quote (*"Measles Immunisation rose from 1% in 1985 to 97% in 2024, a shift of 96 percentage points."*) to be displayed directly underneath an unrelated line chart (*"Smoking Prevalence"*). This release resolves this by setting `quoteAfterSection={-1}`, properly elevating the lead pull quote to the hero header where it serves as the executive summary for the topic, while prioritizing headline indicators from Section 1.
2. **Semantic Clustering & Accurate Multi-Theater Section Titling:** Previously, indicators were blindly sliced into equal numerical slices using naive array chunking, and section titles were stamped with formulaic templates using only the first indicator's stem (`"{stem}: the headline view"`). In `Insurgency & Militancy`, this caused a section titled *"North East insurgency fatalities: the headline view"* to contain North East fatalities, North East incidents, Jammu & Kashmir insurgency deaths, Jammu & Kashmir terror incidents, and Punjab militancy historical fatalities. Release 34 introduces a comprehensive semantic clustering engine with dedicated multi-theater recipes and composite title synthesis, ensuring indicators belong together and section headings truthfully describe every series in the section.

---

## Key Improvements & Technical Architecture

### 1. Thematic Indicator Clustering Engine (`scripts/subgroup_articles.py`)
- **Multi-Theater & Diverse Subgroup Recipes:** Defined `CUSTOM_SUBGROUP_CLUSTERS` for multi-theater and diverse domains:
  - **`Insurgency & Militancy`:** Separated into 6 coherent, dedicated sections:
    1. *North East Insurgency: Fatalities, Incidents & Trajectory* (`northeast_insurgency_fatalities`, `northeast_insurgency_incidents`, `northeast_fatalities_by_period`)
    2. *Jammu & Kashmir and Punjab Militancy: Conflict Trajectories & Incidents* (`kashmir_insurgency_fatalities`, `kashmir_terror_incidents`, `kashmir_fatalities_by_period`, `khalistan_insurgency_historical`, `khalistan_fatalities_by_period`)
    3. *Left-Wing Extremism: Annual Fatalities & Force Casualties* (`lwe_incidents`, `lwe_civilian_casualties`, `lwe_security_force_casualties`, `lwe_perpetrator_casualties`, `lwe_casualties_cumulative`)
    4. *Left-Wing Extremism: Period Trajectories & Recent Civilian Toll* (`lwe_casualties_latest`, `lwe_civilian_casualties_by_period`)
    5. *Left-Wing Extremism: Affected Districts & Violent Incidents* (`lwe_affected_districts`, `lwe_most_affected_districts`, `lwe_violent_incidents`, `lwe_fatalities`, `lwe_civilians_killed`)
    6. *Left-Wing Extremism: Surrenders, Security Operations & Infrastructure* (`lwe_attacks_economic_infrastructure`, `lwe_maoist_surrenders`, `lwe_security_buildup`, `lwe_roads_towers`)
  - **`Health Spending & Disease Burden`:** Re-clustered into 4 thematic pillars:
    1. *Health Expenditure, Public Financing & Out-of-Pocket Spending* (`current_health_spending`, `government_health_spending_per_capita`, `wb_government_health_share`, `wb_health_financing_mix`, `wb_health_spending_split`)
    2. *Drinking Water, Sanitation Access & Healthcare Capacity* (`basic_water_access`, `basic_sanitation_access`, `safely_managed_drinking_water`, `physicians_density`, `wb_hospital_beds`)
    3. *Communicable Diseases: Tuberculosis, Vector-Borne Cases & Mortality* (`wb_tb_incidence`, `wb_malaria_incidence`, `mospi_malaria_cases`, `mospi_dengue_cases`, `wb_causes_of_death`)
    4. *Immunisation Coverage, Child Nutrition & Preventable Risk Factors* (`wb_dpt_immunization`, `wb_measles_immunisation`, `wb_undernourishment`, `wb_child_stunting`, `wb_smoking`)
  - **`Coal, Oil & Gas`**, **`Defence Budget, Production & Exports`**, **`Heritage & Visitor Trends`**, **`Terrorism, Conflict & Displacement`**, **`Indus Valley Civilisation`**, and **`Empires of Ancient India`**.
- **Generic Semantic Affinity Clustering:** Across all remaining subgroups, grouping respects contiguous domain affinity, ensuring 1 to 5 charts per section and between $\min(3, N)$ and 6 sections per subgroup.

### 2. Composite Title Synthesis (`synthesize_section_title`)
- Detects the topic distribution across indicators in each section:
  - **Single Shared Topic:** Formulates focused headings like `"{topic}: Key Trends & Indicators"`.
  - **Two Topics:** Generates inclusive joint headings like `"{topic1} & {topic2}: Core Measures"`.
  - **Three Topics:** Synthesizes `"{topic1}, {topic2} & {topic3}"`.
  - **Diverse Metrics:** Formats `"{stems[0]} and Related Measures"`.
- Eliminates deceptive single-stem titles where unrelated series were hidden under a title claiming only the first indicator.

### 3. Hero Pull Quote Alignment & Rogue Injection Removal
- In `frontend/src/components/SubgroupPage.jsx`, switched `quoteAfterSection={-1}`.
- The global pull quote (`article.pullQuote`) renders strictly in `<header className="subgroup-article-hero">` right below the headline and dek, providing an overarching executive summary.
- Updated `scripts/subgroup_articles.py` to prioritize facts from the first (headline) section so that the lead quote always addresses the primary subject of the article (e.g. Government Health Spending for Health, rather than a secondary measles indicator).

---

## Verification & Test Results

| Test Suite | Commands | Result | Notes |
|---|---|---|---|
| **Python Unit Tests** | `python -m unittest discover tests` | **100 Passed** (100%) | Covers all 100 test cases across feed, layers, models, and migrations |
| **Explainer & Subgroup Tests** | `python -m pytest tests/test_subgroup_articles.py tests/test_group_explainers.py` | **6 Passed** (100%) | Validates section cleanliness, unique keys, valid ranges (1-5 keys, 3-6 sections), distinct Devanagari verses |
| **Frontend Vitest Suite** | `npm.cmd --prefix frontend test -- --run` | **131 Passed** (100%) | Covers React 19 views, maps, SubgroupPage, SubgroupArticle, and atlases |
| **Frontend Production Build** | `npm.cmd --prefix frontend run build` | **Passed** | Clean compilation of Vite production bundle into `frontend/dist` |
| **Static Build Verification** | `npm.cmd --prefix frontend run build:static` | **Passed** | 3,081 indicators and 1,457 articles compiled into `docs/build` |

---

## Deployment & Verification Instructions

1. **Rebuild Explainers:** Run `python scripts/build_explainers.py` to compile `frontend/src/data/group-explainers.json`.
2. **Rebuild Static Dashboard:** Run `npm.cmd --prefix frontend run build:static` to compile client assets into `docs/build/`.
3. **Verify Tests:** Run `python -m unittest discover tests` and `npm.cmd --prefix frontend test -- --run`.
