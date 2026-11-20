import { screen, waitFor } from '@testing-library/react';
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
      // Check if error boundary caught an error
      const broken = screen.queryByText(/This page hit an unexpected error/i);
      if (broken) {
        throw new Error('AiPage crashed and showed Unexpected Error boundary!');
      }
    }, { timeout: 3000 });
  });
});
