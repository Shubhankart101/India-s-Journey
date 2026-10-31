import { screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it } from 'vitest';
import { json, mockApi, page, renderApp, summary } from './helpers.jsx';

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
});

describe('Accounts', () => {
  it('signs in and returns to the requested page', async () => {
    document.cookie = 'csrftoken=tok';
    mockApi({
      'POST /api/auth/login/': { authenticated: true, user: { id: 1, username: 'asha', saved_count: 0 } },
      'GET /api/saved/': [],
    });
    renderApp('/login?next=/saved');
    await userEvent.type(await screen.findByLabelText('Username'), 'asha');
    await userEvent.type(screen.getByLabelText('Password'), 'Strong-pass-123');
    await userEvent.click(screen.getByRole('button', { name: 'Sign in' }));
    await waitFor(() => expect(screen.getByTestId('location')).toHaveTextContent(/^\/saved$/));
    expect(await screen.findByText(/No saved charts yet/)).toBeInTheDocument();
    expect(screen.getByText('Hi, asha')).toBeInTheDocument();
  });

  it('shows login errors', async () => {
    document.cookie = 'csrftoken=tok';
    mockApi({ 'POST /api/auth/login/': json({ detail: 'Invalid username or password.' }, 400) });
    renderApp('/login');
    await userEvent.type(await screen.findByLabelText('Username'), 'asha');
    await userEvent.type(screen.getByLabelText('Password'), 'wrong');
    await userEvent.click(screen.getByRole('button', { name: 'Sign in' }));
    expect(await screen.findByRole('alert')).toHaveTextContent('Invalid username or password.');
  });

  it('validates matching passwords before registering', async () => {
    const { calls } = mockApi();
    renderApp('/register');
    await userEvent.type(await screen.findByLabelText('Username'), 'ravi');
    await userEvent.type(screen.getByLabelText('Password'), 'Strong-pass-123');
    await userEvent.type(screen.getByLabelText('Confirm password'), 'different');
    await userEvent.click(screen.getByRole('button', { name: 'Create account' }));
    expect(screen.getByRole('alert')).toHaveTextContent('Passwords do not match.');
    expect(calls.some(call => call.path === '/api/auth/register/')).toBe(false);
  });

  it('registers a new account and surfaces server validation', async () => {
    document.cookie = 'csrftoken=tok';
    let attempt = 0;
    mockApi({
      'POST /api/auth/register/': () => (attempt++ === 0
        ? json({ password: ['This password is too common.'] }, 400)
        : json({ authenticated: true, user: { id: 2, username: 'ravi', saved_count: 0 } }, 201)),
      'GET /api/saved/': [],
    });
    renderApp('/register');
    await userEvent.type(await screen.findByLabelText('Username'), 'ravi');
    await userEvent.type(screen.getByLabelText('Password'), 'password1');
    await userEvent.type(screen.getByLabelText('Confirm password'), 'password1');
    await userEvent.click(screen.getByRole('button', { name: 'Create account' }));
    expect(await screen.findByRole('alert')).toHaveTextContent('password: This password is too common.');
    await userEvent.click(screen.getByRole('button', { name: 'Create account' }));
    expect(await screen.findByText('Hi, ravi')).toBeInTheDocument();
  });

  it('signs out from the header', async () => {
    document.cookie = 'csrftoken=tok';
    mockApi({
      '/api/auth/me/': { authenticated: true, user: { id: 1, username: 'asha' } },
      'POST /api/auth/logout/': { authenticated: false, user: null },
      '/api/stats/': { indicators: 1, radial_indicators: 0, categories: 1, data_points: 3 },
      '/api/categories/': [],
      '/api/articles/': page([]),
    });
    renderApp('/');
    await userEvent.click(await screen.findByRole('button', { name: 'Sign out' }));
    expect(await screen.findByRole('link', { name: 'Sign in' })).toBeInTheDocument();
  });

  it('redirects anonymous visitors away from saved charts', async () => {
    mockApi();
    renderApp('/saved');
    await waitFor(() => expect(screen.getByTestId('location')).toHaveTextContent('/login?next=/saved'));
  });

  it('lists and removes saved charts', async () => {
    document.cookie = 'csrftoken=tok';
    mockApi({
      '/api/auth/me/': { authenticated: true, user: { id: 1, username: 'asha' } },
      'GET /api/saved/': [{ key: 'gdp_growth', note: '', created_at: '2026-05-01T00:00:00Z', indicator: summary() }],
      'DELETE /api/saved/gdp_growth/': { ok: true, status: 204, json: async () => null },
    });
    renderApp('/saved');
    expect(await screen.findByRole('heading', { name: 'Real GDP growth' })).toBeInTheDocument();
    await userEvent.click(screen.getByRole('button', { name: 'Remove Real GDP growth' }));
    expect(await screen.findByText(/No saved charts yet/)).toBeInTheDocument();
  });
});

describe('About', () => {
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
    renderApp('/about');
    expect(await screen.findByText('all article page 1')).toBeInTheDocument();
    await userEvent.click(screen.getByRole('button', { name: 'Load more' }));
    expect(await screen.findByText('all article page 2')).toBeInTheDocument();
    expect(screen.getByText('all article page 1')).toBeInTheDocument();
    await userEvent.selectOptions(screen.getByRole('combobox', { name: 'Publisher' }), 'pew');
    expect(await screen.findByText('pew article page 1')).toBeInTheDocument();
    expect(screen.queryByText('all article page 2')).not.toBeInTheDocument();
    expect(calls.filter(call => call.path === '/api/articles/').every(call => call.params.get('page_size') === '20')).toBe(true);
  });
});
