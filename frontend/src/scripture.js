import data from './data/scripture-verses.json';

export const TRADITIONS = ['Hindu', 'Buddhist', 'Jain', 'Sikh'];
export const VERSES = data.verses;
export const GROUP_THEMES = data.GROUP_THEMES;

// FNV-1a, 32-bit. Keep identical to docs/scripture.js.
export function fnv1a(text) {
  let hash = 0x811c9dc5;
  for (let i = 0; i < text.length; i += 1) {
    hash ^= text.charCodeAt(i);
    hash = Math.imul(hash, 0x01000193) >>> 0;
  }
  return hash >>> 0;
}

export function candidatesFor(group, verses = VERSES, groupThemes = GROUP_THEMES) {
  const themes = groupThemes[group];
  if (!themes || !themes.length) return verses;
  const pool = verses.filter(verse => verse.themes.some(theme => themes.includes(theme)));
  return pool.length ? pool : verses;
}

export function pickVerse(key, group, avoidId = '', verses = VERSES, groupThemes = GROUP_THEMES) {
  const pool = candidatesFor(group, verses, groupThemes);
  const text = String(key);
  const tradition = TRADITIONS[fnv1a(text) % TRADITIONS.length];
  const ofTradition = pool.filter(verse => verse.tradition === tradition);
  let options = ofTradition.length ? ofTradition : pool;
  if (avoidId && options.length > 1) options = options.filter(verse => verse.id !== avoidId);
  return options[fnv1a(`${text}#${tradition}`) % options.length];
}

// Subgroup explainers use "group/subgroup" and never repeat the previous subgroup's verse.
export function pickSubgroupVerse(group, subgroup, subgroupNames = []) {
  const index = subgroupNames.indexOf(subgroup);
  const previous = index > 0 ? subgroupNames[index - 1] : '';
  const avoid = previous ? pickVerse(`${group}/${previous}`, group) : pickVerse(group, group);
  return pickVerse(`${group}/${subgroup}`, group, avoid.id);
}
