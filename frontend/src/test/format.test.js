import { describe, expect, it } from 'vitest';
import { changeSeries, chartModes, formatAxis, formatDate, formatMagnitude, isUsd, linearTrend, parseExplainer, seriesStats } from '../format.js';

describe('analysis helpers', () => {
  it('computes relative change or percentage-point change', () => {
    expect(changeSeries([100, 110, null, 99])).toEqual([null, 10, null, null]);
    expect(changeSeries([5, 7.5], true)).toEqual([null, 2.5]);
    expect(changeSeries([0, 4])).toEqual([null, null]);
  });

  it('fits a least-squares trend line', () => {
    const trend = linearTrend([1, 3, null, 7]);
    expect(trend.slope).toBeCloseTo(2);
    expect(trend.r2).toBeCloseTo(1);
    expect(trend.line).toEqual([1, 3, 5, 7]);
    expect(linearTrend([1, 2])).toBeNull();
  });

  it('splits explainer paragraphs from other notes', () => {
    expect(parseExplainer('What it shows — A.\n\nWhy it matters — B.\n\nNote.')).toEqual({ explain: { what: 'A.', why: 'B.' }, paragraphs: ['Note.'] });
    expect(parseExplainer('Plain.')).toEqual({ explain: null, paragraphs: ['Plain.'] });
  });
});

describe('formatMagnitude', () => {
  it('uses the international system for USD values', () => {
    expect(formatMagnitude(2_500_000_000, ' USD')).toBe('2.5 billion USD');
    expect(formatMagnitude(1_200_000, 'US dollars')).toBe('1.2 million US dollars');
    expect(formatMagnitude(3.4e12, 'current USD')).toBe('3.4 trillion current USD');
  });

  it('uses the Indian system for everything else', () => {
    expect(formatMagnitude(25_000_000, ' people')).toBe('2.5 crore people');
    expect(formatMagnitude(150_000, '')).toBe('1.5 lakh');
    expect(formatMagnitude(2e12, ' INR')).toBe('2 lakh crore INR');
    expect(formatMagnitude(1234567.891, '')).toBe('12.35 lakh');
  });

  it('keeps declared units as plain grouped numbers', () => {
    expect(formatMagnitude(1234567, ' tonnes')).toBe('12,34,567 tonnes');
    expect(formatMagnitude(1234567, ' USD bn')).toBe('1,234,567 USD bn');
  });

  it('handles small, negative and missing values', () => {
    expect(formatMagnitude(6.5, '%')).toBe('6.5 %');
    expect(formatMagnitude(-2_000_000, '')).toBe('-20 lakh');
    expect(formatMagnitude(null)).toBe('—');
    expect(formatMagnitude('abc')).toBe('—');
  });
});

describe('helpers', () => {
  it('detects USD suffixes', () => {
    expect(isUsd(' USD')).toBe(true);
    expect(isUsd('international $')).toBe(true);
    expect(isUsd(' INR cr')).toBe(false);
  });

  it('formats short axis ticks in each number system', () => {
    expect(formatAxis(2_500_000_000, ' USD')).toBe('2.5B');
    expect(formatAxis(25_000_000, '')).toBe('2.5Cr');
    expect(formatAxis(42, '')).toBe('42');
    expect(formatAxis('x', '')).toBe('');
  });

  it('formats dates and tolerates bad input', () => {
    expect(formatDate('2026-04-02T08:00:00Z')).toMatch(/2026/);
    expect(formatDate('')).toBe('');
    expect(formatDate('not a date')).toBe('not a date');
  });

  it('computes summary statistics ignoring nulls', () => {
    expect(seriesStats([10, null, 5, 20])).toMatchObject({ count: 3, min: 5, max: 20, first: 10, last: 20, change: 100 });
    expect(seriesStats([null, null])).toBeNull();
    expect(seriesStats([0, 5]).change).toBeNull();
  });
});

describe('chartModes', () => {
  it('offers pie and bar for native pies, preferring the pie', () => {
    expect(chartModes({ chart_type: 'doughnut', labels: ['A', 'B'], datasets: [{ values: [1, 2] }] })).toEqual({ modes: ['doughnut', 'bar'], initial: 'doughnut' });
  });

  it('lets additive categorical bars switch to a pie', () => {
    const result = chartModes({ chart_type: 'bar', labels: ['A', 'B', 'C'], datasets: [{ values: [1, 2, 3] }], suffix: ' seats', title: 'Seats' });
    expect(result).toEqual({ modes: ['doughnut', 'bar'], initial: 'bar' });
  });

  it('prefers pies for additive election charts', () => {
    const result = chartModes({ chart_type: 'bar', labels: ['A', 'B'], datasets: [{ values: [1, 2] }], category: 'Elections' });
    expect(result.initial).toBe('doughnut');
  });

  it('keeps rates, time series and negative values out of pies', () => {
    expect(chartModes({ chart_type: 'bar', labels: ['A', 'B'], datasets: [{ values: [1, 2] }], suffix: '%' }).modes).toEqual(['bar']);
    expect(chartModes({ chart_type: 'bar', labels: ['2020', '2021'], datasets: [{ values: [1, 2] }] }).modes).toEqual(['bar']);
    expect(chartModes({ chart_type: 'bar', labels: ['A', 'B'], datasets: [{ values: [-1, 2] }] }).modes).toEqual(['bar']);
    expect(chartModes({ chart_type: 'line', labels: ['A', 'B'], datasets: [{ values: [1, 2] }] }).modes).toEqual(['line']);
  });
});
