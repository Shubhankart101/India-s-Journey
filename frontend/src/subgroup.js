import { api } from './api.js';
import explainers from './data/group-explainers.json';
import { mapPoints } from './components/IndiaMap.jsx';

export const slugify = value => String(value ?? '').toLowerCase().replace(/&/g, ' and ').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
export const MIN_MAP_STATES = 10;

const IVC_SUBGROUP_NAME = "The Indus Valley Civilisation Comprehensive Excavation Map";

const IVC_GROUP_ARTICLE = {
  headline: "The Bronze Age Metropolis of the Indus",
  dek: "Across 1.5 million square kilometres from the Oxus to the Arabian Sea, the Harappan world pioneered grid-iron urban planning, sanitary hydraulics, standard metrology, oceanic seafaring, and an enigmatic undeciphered script.",
  sources: [
    "Archaeological Survey of India (ASI) Centennial Excavation Reports",
    "Corpus of Indus Seals and Inscriptions (CISI, Vols 1–3, Asko Parpola & Jagat Pati Joshi)",
    "The Indus Script: Texts, Concordance and Tables (Iravatham Mahadevan, ASI 1977)",
    "The Indus Civilization: A Contemporary Perspective (Gregory L. Possehl, 2002)"
  ],
  subgroups: [
    {
      name: IVC_SUBGROUP_NAME,
      headline: "The Indus Valley Civilisation Comprehensive Excavation Map, Urbanism & Script",
      dek: "49 cataloged excavations across 9 countries with exact GPS coordinates, excavated structures, material culture, script decipherment concordance, and peer-reviewed monograph citations.",
      pullQuote: "The sanitation and civic architecture of Harappan cities was unmatched anywhere in antiquity until imperial Rome two millennia later.",
      sources: [
        "Archaeological Survey of India (ASI)",
        "Corpus of Indus Seals and Inscriptions (CISI)",
        "Harappa Archaeological Research Project (HARP)"
      ],
      sections: [
        {
          title: "Urban Planning & Hydraulic Genius",
          text: "Every major Harappan city was laid out on an aligned orthogonal grid with cardinal orientations. Standardized fired bricks with a strict 4:2:1 dimensional ratio were utilized across hundreds of settlements spanning thousands of kilometres.",
          keys: ["ivc_urban_settlement_area"]
        },
        {
          title: "Standardized Metrology & Glyptic Art",
          text: "Indus weights followed a binary system in lower denominations (1, 2, 4, 8, 16, 32, 64) and decimal in higher denominations (160, 200, 320, 640), accurate to fractions of a gram.",
          keys: ["ivc_steatite_seals_by_site"]
        },
        {
          title: "Long-Distance Maritime Trade Corridors",
          text: "Indus merchant guilds sailed over 2,500 km across the Arabian Sea, trading textiles, timber, ivory, and etched carnelian for Mesopotamian wool, tin, and silver.",
          keys: ["ivc_international_trade_distance"]
        },
        {
          title: "Sign Concordance & Positional Entropy",
          text: "Sign M-342 (the Jar/Vessel sign) occurs over 1,390 times, almost exclusively at the terminal (leftmost) position of texts, functioning as an inflectional or patronymic suffix.",
          keys: ["ivc_top_script_signs_frequency"]
        },
        {
          title: "Settlement Transitions Across Eras",
          text: "From the Kot Diji and Amri early phases to the Mature urban climax and Ochre Coloured Pottery (OCP) / Painted Grey Ware (PGW) transitions, the Harappan legacy formed the deep substrate of Indian history.",
          keys: ["ivc_radiocarbon_phases"]
        }
      ]
    }
  ]
};

export function articleFor(categoryName, subgroupName) {
  const normCat = slugify(categoryName);
  if ((normCat.includes('indus') && !normCat.includes('industry')) || normCat.includes('harapp')) {
    const subgroup = IVC_GROUP_ARTICLE.subgroups.find(item => item.name === subgroupName || slugify(item.name) === slugify(subgroupName))
      || IVC_GROUP_ARTICLE.subgroups[0];
    return { group: IVC_GROUP_ARTICLE, subgroup };
  }
  const group = explainers.groups.find(item => item.name === categoryName || slugify(item.name) === normCat || (normCat.includes('empires') && slugify(item.name).includes('empires')));
  const subSlug = slugify(subgroupName);
  const subgroup = group?.article.subgroups.find(item => item.name === subgroupName || slugify(item.name) === subSlug)
    || group?.article.subgroups[0];
  return { group: group?.article, subgroup };
}

export async function loadSubgroupIndicators(categorySlug, subgroupSlug, signal) {
  const items = [];
  for (let page = 1; page < 6; page += 1) {
    const data = await api.indicators({ category: categorySlug, subgroup: subgroupSlug, page_size: 100, page }, signal);
    items.push(...data.results);
    if (!data.next) break;
  }
  return items;
}

export const stemOf = title => String(title || '').replace(/\s+[\u2014\u2013-]\s+map$/i, '').trim();

// "Birth rate by State/UT (2023) — map" -> { base: "Birth rate by State/UT", period: "2023" }
export function splitMetric(title) {
  const text = stemOf(title);
  const match = text.match(/^(.*?)\s*\(([^()]*\d[^()]*)\)\s*$/);
  return match && match[1] ? { base: match[1].trim(), period: match[2].trim() } : { base: text, period: '' };
}

// Map metrics the geometry can draw; the same measure published for several periods becomes one metric with a period switch.
export function buildMetrics(indicators, stateNames) {
  const metrics = [];
  const byBase = new Map();
  indicators.filter(item => item.chart_type === 'map').forEach(indicator => {
    const preview = indicator.preview || {};
    const points = mapPoints(preview.labels || [], preview.datasets?.[0]?.values || [], stateNames);
    if (points.size < MIN_MAP_STATES) return;
    const { base, period } = splitMetric(indicator.title);
    const entry = { key: indicator.key, period, indicator, points };
    if (byBase.has(base)) byBase.get(base).entries.push(entry);
    else {
      const metric = { id: indicator.key, base, suffix: indicator.suffix, entries: [entry] };
      byBase.set(base, metric);
      metrics.push(metric);
    }
  });
  return metrics;
}

export function rankOf(points, name) {
  const value = points.get(name);
  if (value === undefined) return null;
  const sorted = [...points.values()].sort((a, b) => b - a);
  const middle = Math.floor(sorted.length / 2);
  const median = sorted.length % 2 ? sorted[middle] : (sorted[middle - 1] + sorted[middle]) / 2;
  return { value, rank: sorted.indexOf(value) + 1, total: sorted.length, median };
}

export const ordinal = number => {
  const tens = number % 100;
  const suffix = tens >= 11 && tens <= 13 ? 'th' : ({ 1: 'st', 2: 'nd', 3: 'rd' }[number % 10] || 'th');
  return `${number}${suffix}`;
};
