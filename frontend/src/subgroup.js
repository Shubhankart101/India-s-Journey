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
          title: "Urban Planning & Orthogonal Grid Metrology",
          text: "Every major Harappan city was laid out on an aligned orthogonal grid with strict cardinal orientations, establishing the earliest planned urban topologies in human history. Standardized kiln-fired and sun-dried bricks adhering to a precise 4:2:1 dimensional ratio (typically 28 × 14 × 7 cm) were deployed across hundreds of settlements spanning more than 1.5 million square kilometres, from Shortugai along the Amu Darya in northern Afghanistan to Daimabad in Maharashtra.\n\nCivic architects divided urban centres into distinct fortified citadels (upper cities) raised on colossal mud-brick plinths and expansive lower towns where residential quarters and artisan workshops congregated. Wide arterial boulevards measuring up to 10 metres across intersected at right angles, designed to accommodate bullock traffic and municipal cargo transit while creating systematic residential blocks that housed populations exceeding 40,000 in metropolises such as Mohenjo-daro and Harappa.",
          keys: ["ivc_urban_settlement_area"]
        },
        {
          title: "Hydraulic Civil Engineering, Drainage & The Great Bath",
          text: "The hydraulic civil engineering of the Indus Valley Civilisation achieved public sanitation standards unheralded in the ancient Near East and unsurpassed until imperial Rome two millennia later. Domestic bathrooms in multi-storey brick residences featured sloped terracotta flooring draining into vertical terracotta chutes embedded within exterior walls, which fed into covered street drains engineered with gentle gradients and covered with removable limestone inspection slabs for silt desilting.\n\nAt Mohenjo-daro, the Great Bath represents the earliest public water-purification reservoir in antiquity, engineered with precision-dressed bricks laid in header-and-stretcher bonds sealed with bitumen waterproofing and flanked by private bathing cubicles. Meanwhile, the hyper-arid coastal metropolis of Dholavira in the Rann of Kutch developed sixteen monumental stone-cut rock reservoirs and masonry check dams along the seasonal Manhar and Mansar channels, capable of storing over 250,000 cubic metres of rain runoff to sustain the desert citadel through multi-year droughts.",
          keys: ["ivc_hydraulic_drainage_capacity"]
        },
        {
          title: "Standardized Metrology & Cubical Chert Weights",
          text: "Commercial exchanges throughout the Harappan realm were regulated by an extraordinarily uniform, state-wide metrological framework based on finely polished cubical chert weights sourced primarily from the Rohri quarries of Sindh. The metrology employed a hybrid binary-decimal numerical progression: lower denominations scaled as 1, 2, 4, 8, 16, 32, and 64 (where the base unit 16 corresponded to approximately 13.64 grams), while higher denominations shifted to decimal multiples (160, 200, 320, 640, up to 12,800 units).\n\nExcavations at Lothal and Kalibangan have also yielded precision ivory and shell measuring scales featuring equidistant linear divisions calibrated to approximately 1.704 millimetres and 33.5 millimetres (the Harappan foot and cubit), demonstrating mathematical rigor in architectural proportioning and land boundary surveys.",
          keys: ["ivc_steatite_seals_by_site"]
        },
        {
          title: "Long-Distance Maritime Trade Corridors to Meluhha",
          text: "Indus merchant guilds operated long-distance maritime corridors extending over 2,500 kilometres across the Arabian Sea and Persian Gulf, connecting Lothal, Suktagendor, and Prabhas Patan with intermediate trading entrepôts at Bahrain (Dilmun) and Oman (Magan), and terminating at the Mesopotamian riverports of Ur, Kish, and Lagash. Mesopotamian cuneiform administrative tablets from the Akkadian King Sargon (c. 2334–2279 BCE) proudly boast of merchant ships from 'Meluhha'—the Sumerian exonym for the Indus realm—docking directly along the Euphrates wharves.\n\nExports from Meluhha included finely bleached cotton textiles (the earliest exported cotton in antiquity), ebony, lapis lazuli from Badakhshan, prime timber, ivory combs, and distinctive etched carnelian beads crafted through alkaline heating techniques unique to Gujarat. In return, Indus ports imported copper ingots, Mesopotamian wool, frankincense, tin, and silver bullions, fostering an integrated Bronze Age trans-oceanic economic sphere.",
          keys: ["ivc_international_trade_distance"]
        },
        {
          title: "Glyptic Art, Steatite Seals & Animal Iconography",
          text: "Over 4,000 carved steatite stamp seals represent the apex of Harappan glyptic craftsmanship, functioning as administrative identity credentials, ownership marks on merchandise bales, and symbolic badges of authority. Seals were carved in intaglio using micro-chisels and glazed through high-temperature baking into a white porcelain-like steatite surface, predominantly featuring a single animal in profile beneath a short inscription in the undeciphered Indus script.\n\nThe iconic unicorn—a mythical single-horned bovine accompanied by a ritual standard or incense burner—accounts for over 65% of all seal motifs, suggesting a prominent administrative or cultic elite. Other frequently depicted fauna include the humped zebu bull, Asian elephant, Bengal tiger, rhinoceros, water buffalo, and composite mythological creatures, reflecting deep ecological intimacy with the riverine floodplains.",
          keys: ["ivc_steatite_seals_by_site"]
        },
        {
          title: "Sign Concordance, Positional Syntax & Undeciphered Script Corpus",
          text: "The Indus script survives in approximately 4,000 distinct inscriptions on stamp seals, copper tablets, terracotta tokens, pottery graffiti, and the monumental 10-character Dholavira signboard discovered near the citadel's northern gateway. Comprising approximately 417 distinct signs according to the Mahadevan Concordance (and roughly 400 signs in Asko Parpola's Corpus), the sign count strongly indicates a logo-syllabic writing system rather than a pure alphabetic or logographic script.\n\nStatistical entropy analyses reveal structured syntactic rules: texts are written predominantly right-to-left (as demonstrated by sign cramping on left margins), with specific signs exhibiting rigid positional preferences. Notably, Sign M-342 (the Jar or Vessel glyph) appears over 1,390 times—almost exclusively as the terminal leftmost character—indicating that it acted as a grammatical case marker, patronymic suffix, or genitive possessive inflection.",
          keys: ["ivc_top_script_signs_frequency"]
        },
        {
          title: "Agrarian Foundations & Multi-Crop Riverine Ecology",
          text: "The staggering scale of Harappan urbanism was underpinned by surplus agrarian production cultivated across the hyper-fertile silt plains of the Indus, Saraswati-Ghaggar-Hakra, and coastal Gujarat river basins. Paleobotanical evidence confirms that Harappan farmers practiced a sophisticated multi-cropping strategy exploiting both the summer Southwest monsoon (Kharif) and winter moisture (Rabi) cycles.\n\nWinter harvests yielded large surpluses of emmer wheat, six-row barley, peas, chickpeas, and mustard, while summer crops in the Saurashtra peninsula pioneered the cultivation of drought-hardy millets (bajra, jowar, and ragi) alongside indigenous cotton (Gossypium arboreum) and rice. Enormous public granary complexes at Harappa and Mohenjo-daro, elevated on sloped timber air-duct platforms to prevent dampness, served as state grain reserves that buffered urban populations against seasonal droughts.",
          keys: ["ivc_radiocarbon_phases"]
        },
        {
          title: "Hydro-Climatic Shifts, De-Urbanization & Cultural Continuity",
          text: "Between 1900 and 1500 BCE, the mature urban phase transitioned into the Post-Urban (Late Harappan) era, characterized not by sudden apocalyptic warfare, but by gradual socio-ecological restructuring triggered by hydro-climatic shifts. Speleothem and paleoclimatic records indicate a multi-century weakening of the Indian summer monsoon and the progressive desiccation of the Ghaggar-Hakra river system, which rendered massive centralized urban water-harvesting systems unsustainable.\n\nAs metropolitan populations dispersed eastward into the wetter agrarian valleys of the Ganga-Yamuna Doab and southward into the Deccan plateau, writing, monumental brick architecture, and standardized weights gradually waned. However, fundamental Harappan technologies—including bullock cart geometry, bronze casting via the lost-wax (cire-perdue) technique, binary weighing traditions, holy water purification rituals, and symbolic motifs—persisted seamlessly, forming the bedrock of India's classical historical civilizations.",
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
  const subgroup = group?.article.subgroups.find(item => item.name === subgroupName || slugify(item.name) === subSlug || (subSlug.includes('metro') && slugify(item.name).includes('metro')))
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
