import { screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it } from 'vitest';
import { mockApi, page, renderApp, summary } from './helpers.jsx';

const comparePayload = {
  labels: ['2022', '2023', '2024'],
  series: [
    { key: 'gdp_growth', title: 'Real GDP growth', suffix: '%', color: '#ff9933', category: 'Economic', subgroup: 'Macro', chart_type: 'line', values: [7, 8, 6] },
    { key: 'exports_usd', title: 'Exports', suffix: ' USD', color: '#3fb950', category: 'Economic', subgroup: 'Trade', chart_type: 'line', values: [null, 400e9, 500e9] },
  ],
  missing: [],
};

describe('Compare', () => {
  it('loads indicators from the URL and shows latest values', async () => {
    const { calls } = mockApi({ '/api/compare/': comparePayload });
    renderApp('/compare?keys=gdp_growth,exports_usd');
    expect(await screen.findByTestId('chart')).toHaveAttribute('data-datasets', '2');
    expect(calls.find(call => call.path === '/api/compare/').params.get('keys')).toBe('gdp_growth,exports_usd');
    const table = screen.getByRole('table');
    expect(within(table).getByText('500 billion USD (2024)')).toBeInTheDocument();
    expect(screen.getByText(/Units differ/)).toBeInTheDocument();
  });

  it('rebases to 100 and stores the choice in the URL', async () => {
    mockApi({ '/api/compare/': comparePayload });
    renderApp('/compare?keys=gdp_growth,exports_usd');
    await screen.findByTestId('chart');
    await userEvent.click(screen.getByRole('checkbox', { name: 'Rebase to 100' }));
    const values = JSON.parse(screen.getByTestId('chart').getAttribute('data-values'));
    expect(values[0][0]).toBe(100);
    expect(values[1][2]).toBe(125);
    expect(screen.getByTestId('location')).toHaveTextContent('normalise=1');
  });

  it('removes a series and adds one through search', async () => {
    mockApi({
      '/api/compare/': url => ({ ...comparePayload, series: comparePayload.series.filter(item => url.searchParams.get('keys').split(',').includes(item.key)) }),
      '/api/indicators/': page([summary({ key: 'exports_usd', title: 'Exports' })]),
    });
    renderApp('/compare?keys=gdp_growth,exports_usd');
    await userEvent.click(await screen.findByRole('button', { name: 'Remove Exports' }));
    await waitFor(() => expect(screen.getByTestId('location')).toHaveTextContent('/compare?keys=gdp_growth'));
    await userEvent.type(screen.getByRole('searchbox', { name: 'Add an indicator to compare' }), 'exp');
    await userEvent.click(await screen.findByRole('button', { name: /Exports/ }));
    await waitFor(() => expect(decodeURIComponent(screen.getByTestId('location').textContent)).toBe('/compare?keys=gdp_growth,exports_usd'));
  });

  it('explains how to start when nothing is selected', async () => {
    mockApi();
    renderApp('/compare');
    expect(await screen.findByText(/Nothing to compare yet/)).toBeInTheDocument();
  });

  it('uses the compare tray when the URL has no keys', async () => {
    localStorage.setItem('ij-compare', JSON.stringify([{ key: 'gdp_growth', title: 'Real GDP growth' }]));
    mockApi({ '/api/compare/': { ...comparePayload, series: comparePayload.series.slice(0, 1) } });
    renderApp('/compare');
    await waitFor(() => expect(screen.getByTestId('location')).toHaveTextContent('/compare?keys=gdp_growth'));
    expect(await screen.findByTestId('chart')).toBeInTheDocument();
  });

  it('renders AI correlation and decoupling synthesis when comparing indicators', async () => {
    mockApi({
      '/api/compare/': comparePayload,
      '/api/ai/compare-insights/': {
        keys: ['gdp_growth', 'exports_usd'],
        count: 2,
        summary: 'Comparing 2 indicators: Real GDP growth and Exports exhibit strong correlation.',
        correlations: [
          {
            pair: ['gdp_growth', 'exports_usd'],
            titles: ['Real GDP growth', 'Exports'],
            r: 0.82,
            strength: 'Strong positive co-movement',
            sample_size: 15,
            start_year: '2010',
            end_year: '2024',
          },
        ],
        decouplings: [
          {
            year: '2020',
            label: '2020',
            event: 'COVID-19 pandemic nationwide lockdown shock',
            observation: 'Real GDP growth shifted by -5.8% while Exports moved by -1.2%.',
          },
        ],
        takeaways: [
          'Strong synchrony: Real GDP growth and Exports exhibit tight co-movement (r = +0.82).',
          'Key structural decoupling observed in 2020 (COVID-19 shock).',
        ],
      },
    });
    renderApp('/compare?keys=gdp_growth,exports_usd');
    expect(await screen.findByText('AI Cross-Series Correlation & Decoupling Synthesis')).toBeInTheDocument();
    expect(screen.getByText('r = +0.82')).toBeInTheDocument();
    expect(screen.getByText(/Strong synchrony: Real GDP growth and Exports/)).toBeInTheDocument();
    expect(screen.getByText(/2020: COVID-19 pandemic nationwide lockdown shock/)).toBeInTheDocument();
  });
});

describe('Account features', () => {
  it('renders sign-in page with Google and Microsoft OAuth options', async () => {
    mockApi({
      '/api/auth/me/': { authenticated: false, user: null },
      '/api/auth/providers/': [
        { id: 'google', name: 'Google', login_url: '/accounts/google/login/' },
        { id: 'microsoft', name: 'Microsoft (Outlook)', login_url: '/accounts/microsoft/login/' },
      ],
    });
    renderApp('/login');
    expect(await screen.findByRole('heading', { name: 'Sign in' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Continue with Google/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Continue with Microsoft/i })).toBeInTheDocument();
  });

  it('displays user profile and sign out button when authenticated', async () => {
    mockApi({
      '/api/auth/me/': { authenticated: true, user: { username: 'asha', first_name: 'Asha', email: 'asha@example.com' } },
    });
    renderApp('/login');
    expect(await screen.findByRole('heading', { name: 'Signed in' })).toBeInTheDocument();
    expect(screen.getAllByText('Asha').length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText('asha@example.com')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Sign out' })).toBeInTheDocument();
  });
});

describe('Articles', () => {
  it('filters articles by publisher and paginates', async () => {
    const { calls } = mockApi({
      '/api/stats/': { indicators: 691, subgroups: 58, last_refresh: '2026-05-01T00:00:00Z' },
      '/api/articles/': url => {
        const pageNumber = url.searchParams.get('page');
        const kind = url.searchParams.get('kind') || 'all';
        return page([{ title: `${kind} article page ${pageNumber}`, url: `https://example.com/${kind}/${pageNumber}`, published_at: null, published: '', publisher: 'X', kind }], {
          next: pageNumber === '1' ? 'more' : null,
        });
      },
    });
    renderApp('/articles');
    expect(await screen.findByText('all article page 1')).toBeInTheDocument();
    await userEvent.click(screen.getByRole('button', { name: 'Load more' }));
    expect(await screen.findByText('all article page 2')).toBeInTheDocument();
    expect(screen.getByText('all article page 1')).toBeInTheDocument();
    await userEvent.selectOptions(screen.getByRole('combobox', { name: 'Publisher' }), 'pew');
    expect(await screen.findByText('pew article page 1')).toBeInTheDocument();
    expect(screen.queryByText('all article page 2')).not.toBeInTheDocument();
    // The Sources acknowledgement asks for three articles per publisher; the About list pages by 20.
    const aboutCalls = calls.filter(call => call.path === '/api/articles/' && call.params.get('page_size') !== '3');
    expect(aboutCalls.length).toBeGreaterThan(0);
    expect(aboutCalls.every(call => call.params.get('page_size') === '20')).toBe(true);
  });
});
