// Mirrors formatMagnitude in docs/app.js: USD figures use the international system
// (thousand/million/billion), everything else uses the Indian system (lakh/crore).
const USD_PATTERN = /\bUSD\b|US dollars?|international \$/i;
const DECLARED_UNIT = /thousand|million|lakh|gwh|mt|tonnes|usd\/barrel|usd bn|inr bn|inr cr|sipri tiv|incidents|attacks|deaths|cases|females/i;

export const isUsd = suffix => USD_PATTERN.test(String(suffix || '').trim());
export const localeFor = suffix => (isUsd(suffix) ? 'en-US' : 'en-IN');

export function formatMagnitude(value, suffix = '') {
  if (value === null || value === undefined || value === '' || !Number.isFinite(Number(value))) return '—';
  const number = Number(value);
  const unitSuffix = String(suffix || '').trim();
  const locale = localeFor(unitSuffix);
  const withSuffix = text => `${text}${unitSuffix ? ` ${unitSuffix}` : ''}`;
  const plain = number.toLocaleString(locale, { maximumFractionDigits: 2 });
  if (DECLARED_UNIT.test(unitSuffix)) return withSuffix(plain);
  const units = locale === 'en-US'
    ? [[1e12, 'trillion'], [1e9, 'billion'], [1e6, 'million'], [1e3, 'thousand']]
    : [[1e12, 'lakh crore'], [1e7, 'crore'], [1e5, 'lakh'], [1e3, 'thousand']];
  const unit = units.find(([threshold]) => Math.abs(number) >= threshold);
  if (!unit) return withSuffix(plain);
  return withSuffix(`${(number / unit[0]).toLocaleString(locale, { maximumFractionDigits: 2 })} ${unit[1]}`);
}

// Short axis ticks: 1.2B / 3.4Cr style.
export function formatAxis(value, suffix = '') {
  const number = Number(value);
  if (!Number.isFinite(number)) return '';
  const usd = isUsd(suffix);
  const units = usd ? [[1e12, 'T'], [1e9, 'B'], [1e6, 'M'], [1e3, 'K']] : [[1e12, 'L Cr'], [1e7, 'Cr'], [1e5, 'L'], [1e3, 'K']];
  const unit = units.find(([threshold]) => Math.abs(number) >= threshold);
  const locale = usd ? 'en-US' : 'en-IN';
  if (!unit) return number.toLocaleString(locale, { maximumFractionDigits: 2 });
  return `${(number / unit[0]).toLocaleString(locale, { maximumFractionDigits: 1 })}${unit[1]}`;
}

export function formatDate(value) {
  if (!value) return '';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  return date.toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' });
}

export function seriesStats(values) {
  const numbers = (values || []).map(Number).filter((value, index) => values[index] !== null && Number.isFinite(value));
  if (!numbers.length) return null;
  const first = numbers[0];
  const last = numbers[numbers.length - 1];
  return {
    count: numbers.length,
    min: Math.min(...numbers),
    max: Math.max(...numbers),
    mean: numbers.reduce((sum, value) => sum + value, 0) / numbers.length,
    first,
    last,
    change: first === 0 ? null : ((last - first) / Math.abs(first)) * 100,
  };
}

export const isRadial = type => type === 'pie' || type === 'doughnut';

const NON_ADDITIVE = /%|rate|index|ratio|per\b|per-|score|average|share|growth|yoy|change|years|°|days|density|expectancy/i;

// Same rules as the static site: native pies, plus additive categorical bars that can be shown as a pie.
export function chartModes({ chart_type: chartType = 'line', labels = [], datasets = [], suffix = '', title = '', scope = '', category = '' }) {
  const values = datasets.length === 1 ? datasets[0].values || [] : [];
  const numbers = values.filter(value => value !== null && Number.isFinite(Number(value))).map(Number);
  const nativeRadial = isRadial(chartType);
  const additive = datasets.length === 1 && labels.length >= 2 && labels.length <= 80
    && !labels.some(label => /^\d{4}/.test(String(label)))
    && (['state', 'category'].includes(scope) || chartType === 'bar')
    && !NON_ADDITIVE.test(`${suffix} ${title}`)
    && numbers.every(value => value >= 0) && numbers.filter(value => value > 0).length >= 2;
  const barType = nativeRadial ? 'bar' : chartType;
  if (!nativeRadial && !additive) return { modes: [chartType], initial: chartType };
  const radialType = nativeRadial ? chartType : 'doughnut';
  const preferPie = nativeRadial || (additive && ['Elections', 'U.S. Elections'].includes(category));
  return { modes: [radialType, barType], initial: preferPie ? radialType : barType };
}
