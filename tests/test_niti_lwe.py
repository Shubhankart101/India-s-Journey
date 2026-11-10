import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CATALOG = json.loads((ROOT / 'data' / 'catalog.json').read_text(encoding='utf-8'))
BY_KEY = {item['key']: item for item in CATALOG['indicators']}

EXPECTED = {
    'niti_health_index_2019_20': ('People, Health & Society', 'State Health Outcomes'),
    'niti_fhi_2023': ('Public Finance & States', 'State Finances & GSDP'),
    'niti_mpi_headcount_2019_21': ('People, Health & Society', 'Jobs, Poverty & Youth'),
    'niti_seqi_2016_17': ('People, Health & Society', 'Education'),
    'niti_epi_2022': ('Economy & Markets', 'Trade, Debt & Reserves'),
    'niti_innovation_index_2021': ('Industry, Energy & Technology', 'R&D & Global Innovation'),
    'lwe_affected_districts': ('Security, Justice & Defence', 'Insurgency & Militancy'),
    'lwe_violent_incidents': ('Security, Justice & Defence', 'Insurgency & Militancy'),
    'lwe_maoist_surrenders': ('Security, Justice & Defence', 'Insurgency & Militancy'),
    'lwe_financial_inclusion': ('Economy & Markets', 'Rural Banking & Financial Inclusion'),
    'lwe_village_mobile_connectivity': ('Industry, Energy & Technology', 'Digital Technology Adoption'),
    'lwe_education_skilling': ('People, Health & Society', 'Education'),
    'lwe_central_funding': ('Public Finance & States', 'Union Budget: Receipts, Spending & Deficits'),
}


@pytest.mark.parametrize('key,placement', EXPECTED.items())
def test_new_series_land_in_expected_group(key, placement):
    item = BY_KEY[key]
    assert (item['category'], item['subgroup']) == placement
    assert item['source_url'].startswith('https://')
    assert item['series']


@pytest.mark.parametrize('name', ['niti-reports.json', 'lwe-insurgency.json'])
def test_series_have_data_and_sources(name):
    series = json.loads((ROOT / 'data' / name).read_text(encoding='utf-8'))['series']
    assert series
    for key, item in series.items():
        assert item['labels'] and len(item['labels']) == len(item['values']), key
        assert all(isinstance(v, (int, float)) for v in item['values']), key
        assert item['source'].count('(') == item['source'].count(')'), key
        assert item['source_url'] in item['source'], key
        assert item['note'] and item['meta']['explain'], key


def test_state_tables_use_canonical_names_and_known_values():
    series = json.loads((ROOT / 'data' / 'niti-reports.json').read_text(encoding='utf-8'))['series']
    health = dict(zip(series['niti_health_index_2019_20']['labels'], series['niti_health_index_2019_20']['values']))
    assert health['Kerala'] == 82.2 and health['Uttar Pradesh'] == 30.57
    mpi = dict(zip(series['niti_mpi_headcount_2019_21']['labels'], series['niti_mpi_headcount_2019_21']['values']))
    assert mpi['Bihar'] == 33.76 and len(mpi) == 36
    epi = dict(zip(series['niti_epi_2022']['labels'], series['niti_epi_2022']['values']))
    assert epi['Tamil Nadu'] == 80.89
    assert 'Jammu & Kashmir' in epi and 'Jammu and Kashmir' not in epi


def test_lwe_headline_figures():
    series = json.loads((ROOT / 'data' / 'lwe-insurgency.json').read_text(encoding='utf-8'))['series']
    incidents = dict(zip(series['lwe_violent_incidents']['labels'], series['lwe_violent_incidents']['values']))
    assert incidents['2010'] == 1936 and incidents['2014'] == 870
    surrenders = dict(zip(series['lwe_maoist_surrenders']['labels'], series['lwe_maoist_surrenders']['values']))
    assert surrenders['2025'] == 2337
