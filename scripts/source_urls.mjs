// Turns an indicator's source attribution (a URL or a free-text citation) into one absolute http(s) URL.
// Publisher homepages live in data/source_publishers.json so the Python audit can verify host/publisher agreement.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
export const publishers = JSON.parse(fs.readFileSync(path.join(root, 'data', 'source_publishers.json'), 'utf8')).publishers
  .map(entry => ({ ...entry, regex: new RegExp(entry.pattern, 'i') }));

const RBI_TABLE_ID_OFFSET = 23449;
const WORLD_BANK_CODE = /\b(?:[A-Z]{2}|GOV_WGI_[A-Z]{2})\.[A-Z0-9.]+/;
const URL_PATTERN = /https?:\/\/[^\s,;)"'<>]+/;

const tidy = url => url.replace(/[.,;:]+$/, '');

export const resolveSourceUrl = (sourceUrl, seriesSource = '') => {
  const raw = String(sourceUrl || '').trim();
  const text = String(seriesSource || raw).trim() || raw;
  if (/^https?:\/\/\S+$/.test(raw)) return tidy(raw);
  const label = raw || text;
  if (/^world bank/i.test(label)) {
    const code = label.match(WORLD_BANK_CODE);
    if (code) return `https://data.worldbank.org/indicator/${code[0]}${code[0].startsWith('GOV_') ? '' : '?locations=IN'}`;
  }
  const rbiTable = label.match(/^rbi handbook[^;]*?table\s+(\d+)/i);
  if (rbiTable) return `https://www.rbi.org.in/Scripts/PublicationsView.aspx?id=${RBI_TABLE_ID_OFFSET + Number(rbiTable[1])}`;
  const embedded = raw.match(URL_PATTERN) || text.match(URL_PATTERN);
  if (embedded) return tidy(embedded[0]);
  const match = publishers.find(entry => entry.url && entry.regex.test(label));
  return match ? match.url : '';
};
