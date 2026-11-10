#!/usr/bin/env python3
"""Build data/niti-reports.json: state-wise indices from NITI Aayog reports.

Tables for MPI, EPI and the India Innovation Index are read from
scripts/niti_report_tables.json (transcribed from the report PDFs); the Health
Index, Fiscal Health Index and School Education Quality Index scores are listed
below with the table or figure they were read from.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data' / 'niti-reports.json'
TABLES = json.loads((ROOT / 'scripts' / 'niti_report_tables.json').read_text(encoding='utf-8'))

A_N = 'Andaman & Nicobar Islands'
DNH = 'Dadra & Nagar Haveli and Daman & Diu'
JK = 'Jammu & Kashmir'

URL_HEALTH = 'https://www.niti.gov.in/sites/default/files/2023-02/NITI-WB_Health_Index_Report_24-12-21.pdf'
URL_FHI = 'https://www.niti.gov.in/sites/default/files/2025-01/Fiscal_Health_Index_24012025_Final.pdf'
URL_MPI = 'https://www.niti.gov.in/sites/default/files/2023-08/India-National-Multidimentional-Poverty-Index-2023.pdf'
URL_SEQI = 'https://www.niti.gov.in/sites/default/files/2019-09/seqi_document.pdf'
URL_EPI = 'https://www.niti.gov.in/sites/default/files/2023-07/Export-Preparedness-Index-2022_0.pdf'
URL_III = 'https://www.niti.gov.in/node/388'

# Health Index Round IV (2019-20), Table e.1 larger states, e.4 smaller states, e.6 UTs: overall reference-year score.
HEALTH = {
    'Kerala': 82.20, 'Tamil Nadu': 72.42, 'Telangana': 69.96, 'Andhra Pradesh': 69.95, 'Maharashtra': 69.14,
    'Gujarat': 63.59, 'Himachal Pradesh': 63.17, 'Punjab': 58.08, 'Karnataka': 57.93, 'Chhattisgarh': 50.70,
    'Haryana': 49.26, 'Assam': 47.74, 'Jharkhand': 47.55, 'Odisha': 44.31, 'Uttarakhand': 44.21,
    'Rajasthan': 41.33, 'Madhya Pradesh': 36.72, 'Bihar': 31.00, 'Uttar Pradesh': 30.57,
    'Mizoram': 75.77, 'Tripura': 70.16, 'Sikkim': 55.53, 'Goa': 53.68, 'Meghalaya': 43.05,
    'Manipur': 34.26, 'Arunachal Pradesh': 33.91, 'Nagaland': 27.00,
    DNH: 66.19, 'Chandigarh': 62.53, 'Lakshadweep': 51.88, 'Puducherry': 50.83, 'Delhi': 49.85,
    JK: 47.00, A_N: 44.74,
}

# Fiscal Health Index FY2023 composite scores (18 states; Himalayan and North-Eastern states not covered).
FHI = {
    'Odisha': 67.8, 'Chhattisgarh': 55.2, 'Goa': 53.6, 'Jharkhand': 51.6, 'Gujarat': 50.5, 'Maharashtra': 50.3,
    'Uttar Pradesh': 45.9, 'Telangana': 43.6, 'Madhya Pradesh': 42.2, 'Karnataka': 40.8, 'Tamil Nadu': 29.2,
    'Rajasthan': 28.6, 'Bihar': 27.8, 'Haryana': 27.4, 'Kerala': 25.4, 'West Bengal': 21.8,
    'Andhra Pradesh': 20.9, 'Punjab': 10.7,
}

# SEQI overall score [2015-16 base year, 2016-17 reference year], read from the overall-performance figures.
SEQI = {
    'Kerala': [77.6, 82.2], 'Tamil Nadu': [63.2, 73.4], 'Haryana': [51.0, 69.5], 'Gujarat': [52.4, 63.0],
    'Himachal Pradesh': [58.1, 62.8], 'Maharashtra': [58.6, 62.5], 'Odisha': [47.8, 60.2], 'Rajasthan': [51.2, 59.4],
    'Punjab': [50.7, 59.1], 'Assam': [39.3, 56.1], 'Andhra Pradesh': [48.4, 56.1], 'Chhattisgarh': [48.4, 54.9],
    'Karnataka': [56.6, 52.9], 'Uttarakhand': [49.5, 48.1], 'Madhya Pradesh': [44.4, 47.2], JK: [34.8, 47.1],
    'Uttar Pradesh': [32.8, 46.5], 'Telangana': [34.7, 39.0], 'Bihar': [30.0, 37.3], 'Jharkhand': [28.5, 30.6],
    'Tripura': [48.5, 56.1], 'Goa': [45.6, 53.8], 'Manipur': [45.3, 46.9], 'Mizoram': [47.7, 46.5],
    'Sikkim': [43.9, 43.0], 'Meghalaya': [24.3, 38.4], 'Nagaland': [22.4, 35.9], 'Arunachal Pradesh': [30.4, 28.4],
    'Chandigarh': [70.0, 73.9], 'Delhi': [60.0, 69.9], 'Puducherry': [40.8, 55.1],
    A_N: [42.8, 44.2], 'Lakshadweep': [37.5, 42.8],
}
# Daman & Diu (34.0 -> 50.5) and Dadra & Nagar Haveli (29.9 -> 44.9) were reported separately, so they are left out.


def bar(key, title, subtitle, data, suffix, color, category, subgroup, publisher, url, note, explain,
        decimals=2, ascending=False, frequency='Reference year'):
    items = sorted(data.items(), key=lambda kv: kv[1], reverse=not ascending)
    return key, {
        'labels': [name for name, _ in items],
        'values': [round(value, decimals) for _, value in items],
        'chartType': 'bar', 'indexAxis': 'y', 'scope': 'state',
        'source': f'{publisher} ({url})',
        'source_url': url,
        'note': note,
        'meta': {
            'title': title, 'subtitle': subtitle, 'frequency': frequency, 'color': color, 'suffix': suffix,
            'category': category, 'subgroup': subgroup, 'explain': explain,
        },
    }


def build():
    series = dict([
        bar('niti_health_index_2019_20', 'NITI Health Index: overall score by state and UT',
            'Overall reference-year (2019-20) Health Index score out of 100',
            HEALTH, ' points', '#3fb950', 'Public Health & Epidemiology', 'State Health Outcomes', 'NITI Aayog', URL_HEALTH,
            'Healthy States, Progressive India: Health Index Round IV 2019-20 (NITI Aayog with the Ministry of Health and Family Welfare and the World Bank, Dec 2021), Tables e.1, e.4 and e.6. Larger states, smaller states and UTs are scored within their own category, so cross-category gaps are indicative.',
            {'what': 'The composite Health Index score for every state and UT in Round IV (reference year 2019-20), combining health outcomes, governance and information, and key inputs and processes.',
             'read': 'A longer bar means a better composite score. Kerala leads the larger states and Mizoram the smaller ones; Uttar Pradesh and Bihar are lowest among the larger states.',
             'why': 'Ranks states on a single yardstick so that reform and funding priorities can be targeted at the weakest health systems.'}),
        bar('niti_fhi_2023', 'NITI Fiscal Health Index: composite score by state (FY2023)',
            'Composite FHI score for 18 major states, higher is healthier',
            FHI, ' points', '#58a6ff', 'State Performance & Regional Health', 'State Financial Health & GSDP', 'NITI Aayog', URL_FHI,
            'Fiscal Health Index 2025, Annual Report for the Financial Year 2023 (NITI Aayog, January 2025). Himalayan and North-Eastern states are not covered. Composite of quality of expenditure, revenue mobilisation, fiscal prudence, debt index and debt sustainability.',
            {'what': 'NITI Aayog\'s composite score of state fiscal health for FY2023, built from five sub-indices on expenditure quality, revenue mobilisation, fiscal prudence, debt and debt sustainability.',
             'read': 'Odisha tops the index at 67.8; Punjab is lowest at 10.7. Scores compare states with each other rather than against a fixed norm.',
             'why': 'States account for about two-thirds of general government spending, so their balance sheets shape the national fiscal outlook.'},
            decimals=1, frequency='FY2023'),
        bar('niti_mpi_headcount_2019_21', 'National MPI: share of population multidimensionally poor, 2019-21',
            'Headcount ratio by state and UT, NFHS-5',
            {k: v[1] for k, v in TABLES['mpi'].items()}, '%', '#f85149', 'Social', 'Employment & Poverty', 'NITI Aayog', URL_MPI,
            'National Multidimensional Poverty Index: A Progress Review 2023 (NITI Aayog), headcount ratio table based on NFHS-5 (2019-21).',
            {'what': 'The share of people in each state and UT who are multidimensionally poor across health, education and standard-of-living indicators, according to NFHS-5 (2019-21).',
             'read': 'Bars are the headcount ratio in percent. Bihar, Jharkhand and Meghalaya are highest; Kerala, Goa and Puducherry are lowest.',
             'why': 'Captures deprivation in assets, schooling, nutrition and services that income-only poverty lines miss.'},
            frequency='NFHS-5 (2019-21)'),
        bar('niti_mpi_reduction_2015_16_to_2019_21', 'National MPI: fall in poverty headcount between NFHS-4 and NFHS-5',
            'Percentage-point reduction in headcount ratio, 2015-16 to 2019-21',
            {k: v[0] - v[1] for k, v in TABLES['mpi'].items()}, ' pp', '#3fb950', 'Social', 'Employment & Poverty', 'NITI Aayog', URL_MPI,
            'National Multidimensional Poverty Index: A Progress Review 2023 (NITI Aayog). Computed as the NFHS-4 (2015-16) headcount ratio minus the NFHS-5 (2019-21) headcount ratio from the report\'s table.',
            {'what': 'How many percentage points each state and UT cut its multidimensional poverty headcount between NFHS-4 and NFHS-5.',
             'read': 'Longer bars mean faster decline. Bihar, Madhya Pradesh and Uttar Pradesh gained the most; states that started low have little room to fall.',
             'why': 'Shows whether the poorest states are catching up.'},
            frequency='2015-16 to 2019-21'),
        bar('niti_mpi_people_escaped_2015_16_to_2019_21', 'National MPI: people who escaped poverty by state',
            'Number of people who left multidimensional poverty, 2015-16 to 2019-21',
            {k: v[2] for k, v in TABLES['mpi'].items()}, ' people', '#ff9933', 'Social', 'Employment & Poverty', 'NITI Aayog', URL_MPI,
            'National Multidimensional Poverty Index: A Progress Review 2023 (NITI Aayog); estimates use 2021 population projections by the Ministry of Health and Family Welfare. All-India total reported: 13,54,61,035 people.',
            {'what': 'The estimated number of people in each state and UT who moved out of multidimensional poverty between the two NFHS rounds.',
             'read': 'Uttar Pradesh, Bihar and Madhya Pradesh account for the largest absolute numbers because of their size and starting poverty.',
             'why': 'Turns percentage declines into numbers of people.'},
            decimals=0, frequency='2015-16 to 2019-21'),
        bar('niti_seqi_2016_17', 'NITI School Education Quality Index: overall score, 2016-17',
            'SEQI overall score out of 100 for states and UTs',
            {k: v[1] for k, v in SEQI.items()}, ' points', '#bc8cff', 'Social', 'Education', 'NITI Aayog', URL_SEQI,
            'School Education Quality Index (NITI Aayog, September 2019), overall-performance figures for large states, small states and UTs, reference year 2016-17. Values are read from chart data labels; the report text quotes slightly different figures for a few states.',
            {'what': 'The overall SEQI score covering learning outcomes, access, infrastructure and governance of school education in 2016-17.',
             'read': 'Kerala, Tamil Nadu and Chandigarh lead; Jharkhand and Bihar are at the bottom of the large states.',
             'why': 'Gives states an outcome-focused benchmark for school education policy.'},
            decimals=1, frequency='2016-17'),
        bar('niti_seqi_gain_2015_16_to_2016_17', 'NITI School Education Quality Index: change in score, 2015-16 to 2016-17',
            'Points gained or lost on the overall SEQI score',
            {k: v[1] - v[0] for k, v in SEQI.items()}, ' points', '#ff9933', 'Social', 'Education', 'NITI Aayog', URL_SEQI,
            'School Education Quality Index (NITI Aayog, September 2019), base year 2015-16 to reference year 2016-17, computed from the overall scores in the report figures.',
            {'what': 'Incremental SEQI change between the base year and the reference year.',
             'read': 'Haryana, Assam and Puducherry improved most; Karnataka, Uttarakhand, Mizoram and Sikkim slipped.',
             'why': 'Separates states that are improving quickly from those that merely start high.'},
            decimals=1, frequency='2015-16 to 2016-17'),
        bar('niti_epi_2022', 'NITI Export Preparedness Index: overall score by state and UT',
            'EPI 2022 overall score out of 100',
            TABLES['epi'], ' points', '#58a6ff', 'Economic', 'Trade & External', 'NITI Aayog', URL_EPI,
            'Export Preparedness Index 2022 (NITI Aayog with the Institute for Competitiveness), Overall Ranking table, pp. 108-109. Four pillars: policy, business ecosystem, export ecosystem and export performance.',
            {'what': 'How prepared each state and UT is to export, scored across policy, business ecosystem, export ecosystem and export performance.',
             'read': 'Tamil Nadu (80.89), Maharashtra, Karnataka and Gujarat lead; Himalayan states and small UTs trail.',
             'why': 'Exports depend on state-level logistics, policy and industry, so state scores show where capacity is missing.'},
            frequency='EPI 2022'),
        bar('niti_innovation_index_2021', 'India Innovation Index 2021: overall score by state and UT',
            'Overall innovation score, third edition',
            {k: v[0] for k, v in TABLES['innovation'].items()}, ' points', '#f0883e', 'Innovation & Technology', 'Global Innovation Benchmarks', 'NITI Aayog', URL_III,
            'India Innovation Index 2021 (NITI Aayog with the Institute for Competitiveness, July 2022), category-wise rankings and Appendix state scores. States are ranked within Major States, North-East and Hill States, and UTs and City States, so scores are not strictly comparable across groups.',
            {'what': 'The overall innovation score combining enablers (human capital, investment, knowledge workers, business environment, safety and legal environment) and performers (knowledge output and diffusion).',
             'read': 'Karnataka tops the major states, Manipur the North-East and hill states, and Chandigarh the UTs.',
             'why': 'Shows which regional ecosystems turn inputs into innovative output.'},
            frequency='III 2021'),
        bar('niti_innovation_enablers_2021', 'India Innovation Index 2021: enabler score by state and UT',
            'Enablers dimension score',
            {k: v[1] for k, v in TABLES['innovation'].items()}, ' points', '#f0883e', 'Innovation & Technology', 'Global Innovation Benchmarks', 'NITI Aayog', URL_III,
            'India Innovation Index 2021 (NITI Aayog with the Institute for Competitiveness), Appendix state scores, Enablers dimension.',
            {'what': 'The Enablers dimension: the inputs for innovation such as human capital, investment, knowledge workers, business environment and safety and legal environment.',
             'read': 'Manipur and Chandigarh are highest; Ladakh and Bihar are lowest.',
             'why': 'Compares the supporting conditions for innovation with what is actually produced.'},
            frequency='III 2021'),
        bar('niti_innovation_performers_2021', 'India Innovation Index 2021: performer score by state and UT',
            'Performers dimension score',
            {k: v[2] for k, v in TABLES['innovation'].items()}, ' points', '#f0883e', 'Innovation & Technology', 'Global Innovation Benchmarks', 'NITI Aayog', URL_III,
            'India Innovation Index 2021 (NITI Aayog with the Institute for Competitiveness), Appendix state scores, Performers dimension.',
            {'what': 'The Performers dimension: realised innovation output including knowledge output and knowledge diffusion.',
             'read': 'Delhi and Chandigarh lead, followed by Telangana and Karnataka among the large states.',
             'why': 'Shows which states convert inputs into results.'},
            frequency='III 2021'),
    ])
    return series


def main():
    payload = {
        'generated_at_utc': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'source': 'NITI Aayog reports (Health Index Round IV, Fiscal Health Index 2025, National MPI Progress Review 2023, School Education Quality Index 2019, Export Preparedness Index 2022, India Innovation Index 2021)',
        'series': build(),
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    print(f'wrote {OUT} with {len(payload["series"])} series')


if __name__ == '__main__':
    main()
