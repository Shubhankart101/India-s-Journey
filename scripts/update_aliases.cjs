const fs = require('fs');
const aliases = JSON.parse(fs.readFileSync('frontend/src/data/legacy-aliases.json', 'utf8'));

const ivcSub = 'The Indus Valley Civilisation Comprehensive Excavation Map';
const empSub = 'Empires of Ancient India: Dynastic Atlases, Battles & Inscriptions';

const ivcOldSubs = [
  'Metropolises & Major Urban Centers',
  'Artifacts, Statuary & Material Culture',
  'Maritime Trade & International Artifacts',
  'Indus Script & Alphabet Decoding',
  'Chronology, Settlement Geography & Legacy',
  'metropolises-major-urban-centers',
  'artifacts-statuary-material-culture',
  'maritime-trade-international-artifacts',
  'indus-script-alphabet-decoding',
  'chronology-settlement-geography-legacy'
];

ivcOldSubs.forEach(sub => {
  aliases.subgroups['Indus Valley Civilisation|' + sub] = { group: 'Indus Valley Civilisation', subgroup: ivcSub };
  aliases.subgroups['indus-valley-civilisation|' + sub] = { group: 'Indus Valley Civilisation', subgroup: ivcSub };
});

const empOldSubs = [
  '16 Mahajanapadas & Early Republics',
  'Magadha Ascendancy: Haryanka, Shishunaga & Nanda',
  "Alexander the Great's Campaign & Macedonian Limit",
  'Mauryan Empire & Pan-Indian Hegemony',
  'Post-Mauryan & Indo-Greek Kingdoms',
  'Satavahana Empire & Deccan Maritime Ascendancy',
  'Kushan Empire & The Silk Road Synthesis',
  'Gupta Empire: Classical Golden Age',
  'Vardhana Empire of Harsha',
  'Classical Southern Dynasties: Chola, Chera, Pandya & Pallava',
  '16-mahajanapadas-early-republics',
  'magadha-ascendancy-haryanka-shishunaga-nanda',
  'alexander-the-great-s-campaign-macedonian-limit',
  'mauryan-empire-pan-indian-hegemony',
  'post-mauryan-indo-greek-kingdoms',
  'satavahana-empire-deccan-maritime-ascendancy',
  'kushan-empire-the-silk-road-synthesis',
  'gupta-empire-classical-golden-age',
  'vardhana-empire-of-harsha',
  'classical-southern-dynasties-chola-chera-pandya-pallava'
];

empOldSubs.forEach(sub => {
  aliases.subgroups['Empires of Ancient India|' + sub] = { group: 'Empires of Ancient India', subgroup: empSub };
  aliases.subgroups['empires-of-ancient-india|' + sub] = { group: 'Empires of Ancient India', subgroup: empSub };
});

fs.writeFileSync('frontend/src/data/legacy-aliases.json', JSON.stringify(aliases, null, 2) + '\n');
console.log('Successfully updated legacy-aliases.json with ancient subgroup aliases.');
