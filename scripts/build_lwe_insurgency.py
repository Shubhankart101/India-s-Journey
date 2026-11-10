#!/usr/bin/env python3
"""Build data/lwe-insurgency.json: Maoist / Left-Wing Extremism indices.

Sources (all read in full; only labelled or quoted figures are used):
  PIB  - "Naxal-Free India: Integrated Strategies Defeated Left-Wing Extremism", 1 Aug 2026 (Ministry of Home Affairs).
  ORF  - "Reclaiming the Heartland: India's Success in Countering the Maoist Insurgency", 2026.
  ICFS - "Closing the Red Corridor" by Shruti Kapil, 2026.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data' / 'lwe-insurgency.json'

PIB = 'https://static.pib.gov.in/WriteReadData/specificdocs/documents/2026/aug/doc202681940501.pdf'
ORF = 'https://www.orfonline.org/research/reclaiming-the-heartland-india-s-success-in-countering-the-maoist-insurgency'
ICFS = 'https://icfs.org.uk/wp-content/uploads/2026/10/Closing-The-Red-Corridor_Oct-26.pdf'
PIB_NAME = 'Press Information Bureau'
ICFS_NAME = 'International Centre for Sustainability and Futures'

PIB_DOC = 'PIB backgrounder "Naxal-Free India: Integrated Strategies Defeated Left-Wing Extremism" (Ministry of Home Affairs, 1 August 2026)'
ICFS_DOC = 'ICFS "Closing the Red Corridor" (Shruti Kapil, 2026)'
ORF_DOC = 'ORF "Reclaiming the Heartland: India\'s Success in Countering the Maoist Insurgency" (2026)'

SECURITY = ('Crime & Security', 'Maoism / LWE')


def make(key, title, subtitle, labels, values, publisher, url, note, explain, placement=SECURITY,
         color='#f85149', suffix='', chart='bar', frequency='Selected years', horizontal=False, unit=''):
    series = {
        'labels': labels, 'values': values, 'chartType': chart,
        'source': f'{publisher} ({url})', 'source_url': url, 'note': note,
        'meta': {'title': title, 'subtitle': subtitle, 'frequency': frequency, 'color': color, 'suffix': suffix,
                 'category': placement[0], 'subgroup': placement[1], 'explain': explain},
    }
    if unit:
        series['unit'] = unit
    if horizontal:
        series['indexAxis'] = 'y'
    return key, series


def build():
    surrender_years = [str(year) for year in range(2004, 2026)] + ['2026 (to 30 Mar)']
    surrenders = [368, 1231, 1278, 390, 400, 150, 266, 394, 445, 283, 676, 570, 1442, 685, 644, 440, 475, 736, 376, 496, 881, 2337, 709]
    return dict([
        make('lwe_affected_districts', 'Districts affected by Left-Wing Extremism',
             'Approximate number of LWE-affected districts, peak to 2024',
             ['2011-12', '2014', 'Apr 2018', 'Jul 2021', 'Apr 2024'], [223, 126, 90, 70, 38],
             ICFS_NAME, ICFS,
             f'{ICFS_DOC}, Figure 5 and text (223 districts at peak, 126 in 2014, 38 in April 2024); ORF "Reclaiming the Heartland" gives the same 223 districts for 2011-12. The 2018 (about 90) and 2021 (about 70) values are read from an unlabelled chart and are approximate. The sources disagree on the 2026 count (PIB reports none, ORF and ICFS report two), so 2026 is not plotted.',
             {'what': 'How many districts the Ministry of Home Affairs treated as affected by Maoist violence at successive reviews, from the 2011-12 peak.',
              'read': 'The count fell from 223 to 126 by 2014 and to 38 by April 2024; the 2018 and 2021 points are approximate.',
              'why': 'The district count is the official yardstick for how far the Red Corridor has shrunk.'},
             color='#f85149', suffix=' districts', frequency='Selected reviews'),
        make('lwe_most_affected_districts', 'Most-affected LWE districts',
             'Districts classed as most affected by Left-Wing Extremism',
             ['2014', '2026'], [35, 0], PIB_NAME, PIB,
             f'{PIB_DOC}: 35 most-affected districts in 2014 and none by 2026.',
             {'what': 'Districts in the most severely affected category.', 'read': 'The count went from 35 in 2014 to zero in 2026.',
              'why': 'These districts drove most of the violence and received the heaviest security deployment.'},
             color='#f85149', suffix=' districts', frequency='2014 and 2026'),
        make('lwe_violent_incidents', 'Naxal-related violent incidents',
             'Incidents in 2010, 2014 and 2026 (to 29 July)',
             ['2010', '2014', '2026 (to 29 Jul)'], [1936, 870, 33], PIB_NAME, PIB,
             f'{PIB_DOC}. 2026 is a part-year figure as on 29 July 2026. The decade 2004-14 recorded 17,542 violent incidents in total.',
             {'what': 'Violent incidents attributed to Left-Wing Extremism in three reference years.', 'read': '2010 was the deadliest year; 2026 shows 33 incidents so far.',
              'why': 'The headline measure of how violent the insurgency has been.'},
             suffix=' incidents'),
        make('lwe_fatalities', 'Naxal-related fatalities',
             'Total fatalities in 2010, 2014 and 2026 (to 29 July)',
             ['2010', '2014', '2026 (to 29 Jul)'], [1005, 310, 11], PIB_NAME, PIB,
             f'{PIB_DOC}. 2026 is a part-year figure as on 29 July 2026. Over 2004-14 the report counts 1,913 security-force deaths and 5,019 civilian deaths.',
             {'what': 'Deaths of civilians, security forces and cadres in LWE-related violence.', 'read': 'Fatalities fell from 1,005 in 2010 to 310 in 2014 and 11 in 2026 so far.',
              'why': 'Fatalities show the human cost behind the incident counts.'},
             suffix=' deaths'),
        make('lwe_civilians_killed', 'Civilians killed by Maoists',
             'Civilian deaths in 2010, 2014 and 2024',
             ['2010', '2014', '2024'], [720, 222, 121], ICFS_NAME, ICFS,
             f'{ICFS_DOC}, Figure 8 (Ministry of Home Affairs data). PIB confirms 720 civilian deaths in 2010.',
             {'what': 'Civilians killed in Maoist violence in three reference years.', 'read': 'Civilian deaths fell by more than 80 percent between 2010 and 2024.',
              'why': 'Civilian safety is the clearest sign of state control in the affected districts.'},
             suffix=' deaths'),
        make('lwe_attacks_economic_infrastructure', 'Maoist attacks on economic infrastructure',
             'Attacks on roads, rail, telecom and other infrastructure',
             ['2010', '2014', '2024'], [365, 100, 25], ICFS_NAME, ICFS,
             f'{ICFS_DOC}, Figure 8 (Ministry of Home Affairs data).',
             {'what': 'Incidents of Maoist damage to economic infrastructure.', 'read': 'Attacks fell from 365 in 2010 to 25 in 2024.',
              'why': 'Roads, towers and rail lines are what opened the interior to development.'},
             suffix=' attacks'),
        make('lwe_maoist_surrenders', 'Maoists surrendering each year',
             'Cadres who surrendered, 2004 to March 2026',
             surrender_years, surrenders, ICFS_NAME, ICFS,
             f'{ICFS_DOC}, Figure 9 (labelled annual data). 2026 covers 1 January to 30 March only. The PIB backgrounder reports 3,927 surrenders between 2024 and March 2026.',
             {'what': 'Maoist cadres who laid down arms in each year.', 'read': 'Surrenders spiked in 2005-06 and 2016 and reached 2,337 in 2025.',
              'why': 'Surrender trends show whether rehabilitation policy is eroding the insurgency from within.'},
             color='#ff9933', suffix=' surrenders', chart='bar', frequency='Annual'),
        make('lwe_security_buildup', 'Security build-up in LWE areas',
             'Fortified police stations, new CAPF camps and night-landing helipads',
             ['Fortified police stations before 2014', 'Fortified police stations in 2026', 'New CAPF camps (7 years)', 'Night-landing helipads'],
             [66, 663, 408, 68], PIB_NAME, PIB,
             f'{PIB_DOC}. The ICFS report quotes about 361 new camps, so the PIB figure is used.',
             {'what': 'Counts of security infrastructure built in LWE-affected areas.', 'read': 'Fortified police stations rose from 66 to 663.',
              'why': 'Forward bases are what allowed forces to hold territory after clearing it.'},
             color='#58a6ff', suffix='', horizontal=True),
        make('lwe_roads_towers', 'Roads and mobile towers built in LWE areas',
             'Road length (km) and towers commissioned',
             ['Roads under RRP and RCPLWEA (km)', 'Mobile towers commissioned'], [15189, 9497],
             PIB_NAME, PIB,
             f'{PIB_DOC}. ICFS quotes more than 9,600 towers; the PIB figure is used. In Bastar alone the PIB reports 3,240 km of roads and 889 towers.',
             {'what': 'Roads built under the Road Requirement Plan and the Road Connectivity Project for LWE areas, and mobile towers commissioned.', 'read': 'The two bars use different units: kilometres of road and number of towers.',
              'why': 'Connectivity ends isolation and lets the state reach villages the Maoists once controlled.'},
             color='#3fb950', horizontal=True),
        make('lwe_village_mobile_connectivity', 'Mobile connectivity in LWE-affected villages',
             'Villages with mobile coverage out of villages in LWE areas',
             ['Villages with mobile connectivity', 'Villages in LWE areas'], [44728, 46592],
             PIB_NAME, PIB,
             f'{PIB_DOC}: 44,728 of 46,592 villages covered (96 percent).',
             {'what': 'How many villages in LWE-affected areas have mobile coverage.', 'read': 'About 96 percent of villages are covered.',
              'why': 'Mobile coverage supports tip-offs, welfare delivery and digital payments.'},
             color='#3fb950', placement=('Innovation & Technology', 'Digital Technology Adoption'), suffix=' villages'),
        make('lwe_financial_inclusion', 'Financial inclusion in LWE-affected areas',
             'Banking access added between April 2015 and March 2026',
             ['Bank branches', 'ATMs', 'Banking correspondents', 'Post offices'], [1804, 1321, 74720, 6025],
             PIB_NAME, PIB,
             f'{PIB_DOC}: financial-inclusion additions between April 2015 and March 2026.',
             {'what': 'New bank branches, ATMs, banking correspondents and post offices in LWE-affected districts.', 'read': 'Banking correspondents account for the bulk of new touchpoints.',
              'why': 'Access to banks and payments is part of the development half of the strategy.'},
             color='#ff9933', placement=('Payments & Digital Banking', 'Financial Inclusion & Credit Depth'), horizontal=True),
        make('lwe_education_skilling', 'Schools and skilling in LWE-affected areas',
             'Eklavya schools, ITIs and skill development centres',
             ['EMRS sanctioned', 'EMRS functional', 'ITIs', 'Skill development centres'], [259, 179, 47, 49],
             PIB_NAME, PIB,
             f'{PIB_DOC}. ICFS quotes 46 ITIs; the PIB figure is used.',
             {'what': 'Eklavya Model Residential Schools (EMRS) and skilling institutes in LWE districts.', 'read': '179 of 259 sanctioned EMRS are functional.',
              'why': 'Schools and skills offer an alternative to recruitment by armed groups.'},
             color='#bc8cff', placement=('Social', 'Education'), horizontal=True),
        make('lwe_central_funding', 'Central funding for LWE schemes',
             'Funds released or sanctioned under four schemes',
             ['Special Central Assistance (since 2017)', 'Special Infrastructure Scheme (sanctioned)', 'Security Related Expenditure (since 2014-15)', 'Civic Action Programme (since 2014)'],
             [4289.20, 1761, 3805.04, 221.88], PIB_NAME, PIB,
             f'{PIB_DOC}. Rupees crore; cumulative amounts over different periods, so the bars are not like for like.',
             {'what': 'Central funds under the Special Central Assistance, Special Infrastructure and Security Related Expenditure schemes and the Civic Action Programme.', 'read': 'Cumulative figures over different periods.',
              'why': 'Shows how the Centre financed both policing and development.'},
             color='#e3b341', placement=('Union Budget', 'Expenditure'), suffix=' crore', horizontal=True),
    ])


def main():
    payload = {
        'generated_at_utc': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'source': f'{PIB}; {ORF}; {ICFS}',
        'series': build(),
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    print(f'wrote {OUT} with {len(payload["series"])} series')


if __name__ == '__main__':
    main()
