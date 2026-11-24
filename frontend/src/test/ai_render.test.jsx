import { fireEvent, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it } from 'vitest';
import { mockApi, renderApp } from './helpers.jsx';

describe('AI Hub Rendering', () => {
  it('renders /ai without crashing', async () => {
    mockApi({
      '/api/stats/': { indicators: 691 },
      '/api/categories/': [],
      '/api/indicators/': { count: 0, results: [] },
      '/api/ai/simulate/': { success: true },
      '/api/ai/correlate/': { correlation: 0.8 },
      '/api/ai/regimes/': { regimes: [] },
      '/api/ai/policy-query/': { answer: 'Policy synthesis' },
    });

    renderApp('/ai');

    await waitFor(() => {
      const broken = screen.queryByText(/This page hit an unexpected error/i);
      if (broken) {
        throw new Error('AiPage crashed and showed Unexpected Error boundary!');
      }
    }, { timeout: 3000 });
  });

  it('switches AI Hub workbenches, applies shock presets, and closes indicator picker on Escape', async () => {
    mockApi({
      '/api/stats/': { indicators: 691 },
      '/api/categories/': [],
      '/api/indicators/gdp_growth/': {
        key: 'gdp_growth',
        title: 'Real GDP Growth',
        category: 'Economy',
        subgroup: 'Growth',
        suffix: '%',
        color: '#2997ff',
        labels: ['2021', '2022', '2023'],
        datasets: [{ label: 'GDP', values: [9.1, 7.2, 7.6] }],
      },
      '/api/compare/': {
        labels: ['2021', '2022', '2023'],
        series: [
          { key: 'gdp_growth', title: 'Real GDP Growth', suffix: '%', values: [9.1, 7.2, 7.6] },
          { key: 'capital_formation_gdp', title: 'Gross Capital Formation', suffix: '%', values: [31.2, 31.8, 32.1] },
        ],
      },
      '/api/ai/compare-insights/': {
        keys: ['gdp_growth', 'capital_formation_gdp'],
        count: 2,
        correlations: [{ pair: ['gdp_growth', 'capital_formation_gdp'], titles: ['Real GDP Growth', 'Gross Capital Formation'], r: 0.85, strength: 'Strong', sample_size: 3 }],
        decouplings: [],
        takeaways: [],
      },
      '/api/ai/insights/gdp_growth/': {
        key: 'gdp_growth',
        title: 'Real GDP Growth',
        metrics: { peak: { label: '2021', value: 9.1 }, trough: { label: '2022', value: 7.2 }, latest: { label: '2023', value: 7.6 }, delta: -1.5, unit: '%' },
        takeaways: [],
      },
      '/api/indicators/': { count: 1, results: [{ key: 'upi', title: 'UPI Volume', category: 'Payments', subgroup: 'DPI', suffix: 'Cr', is_live: true }] },
    });

    renderApp('/ai');

    const triggers = await screen.findAllByRole('button', { name: /▼ Change/ });
    await userEvent.click(triggers[0]);
    expect(screen.getByPlaceholderText(/Search 3,082 indicators/)).toBeInTheDocument();
    fireEvent.keyDown(document, { key: 'Escape' });
    expect(screen.queryByPlaceholderText(/Search 3,082 indicators/)).not.toBeInTheDocument();

    await userEvent.click(screen.getByRole('button', { name: /Policy Stress Simulator/ }));
    expect(screen.getByRole('heading', { name: /Macroeconomic Policy Stress/ })).toBeInTheDocument();
    await userEvent.click(screen.getByRole('button', { name: /Global Stagflation Shock/ }));
    expect(screen.getByText('+50 bps')).toBeInTheDocument();
    expect(screen.getByText('$110 / bbl')).toBeInTheDocument();

    await userEvent.click(screen.getByRole('button', { name: /Regime Shift Radar/ }));
    expect(screen.getByRole('heading', { name: /Macroeconomic Regime Shift/ })).toBeInTheDocument();
  });
});
