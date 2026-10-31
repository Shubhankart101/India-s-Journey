import { screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it } from 'vitest';
import { categories, detail, json, mockApi, page, renderApp, summary } from './helpers.jsx';

const stats = { indicators: 691, live_indicators: 691, radial_indicators: 264, categories: 13, subgroups: 58, articles: 2, data_points: 17571, source_generated_at: '2026-05-01T00:00:00Z', last_refresh: null };
const articles = page([{ title: 'Budget explainer', url: 'https://example.com/a', published: '', published_at: '2026-04-01T00:00:00Z', publisher: 'Polity and Policy', kind: 'polity_policy', is_featured: false }]);

describe('Layout and Home', () => {
  it('renders stats, group tiles with art and latest articles', async () => {
    mockApi({ '/api/stats/': stats, '/api/categories/': categories, '/api/articles/': articles });
    renderApp('/');
    expect(await screen.findByText('691')).toBeInTheDocument();
    const tile = await screen.findByRole('link', { name: /subgroups\s*Economic/ });
    expect(tile).toHaveAttribute('href', '/explore?category=economic');
    expect(tile.style.getPropertyValue('--tile-art')).toContain('/art/parliament.svg');
    expect(await screen.findByRole('link', { name: 'Budget explainer' })).toHaveAttribute('rel', 'noopener noreferrer');
  });

  it('cycles the hero backdrop through group scenes with selectable dots', async () => {
    mockApi({ '/api/stats/': stats, '/api/categories/': categories, '/api/articles/': articles });
    const { container } = renderApp('/');
    expect(await screen.findByRole('link', { name: /Now showing\s*Economic/ })).toHaveAttribute('href', '/explore?category=economic');
    const backdrop = container.querySelector('.hero .art-backdrop');
    expect(backdrop).toHaveAttribute('aria-hidden', 'true');
    expect(backdrop).toHaveAttribute('data-art', 'parliament.svg');
    const dot = screen.getByRole('button', { name: 'Show Elections scene' });
    expect(dot).toHaveAttribute('aria-pressed', 'false');
    await userEvent.click(dot);
    expect(dot).toHaveAttribute('aria-pressed', 'true');
    expect(backdrop).toHaveAttribute('data-art', 'eci-building.svg');
    expect(screen.getByRole('link', { name: /Now showing\s*Elections/ })).toHaveAttribute('href', '/explore?category=elections');
    await waitFor(() => expect(backdrop.querySelectorAll('img')).toHaveLength(2));
    expect([...backdrop.querySelectorAll('img')].map(img => img.getAttribute('src'))).toEqual(['/art/parliament.svg', '/art/eci-building.svg']);
  });

  it('has desktop navigation and a mobile tab bar', async () => {
    mockApi({ '/api/stats/': stats, '/api/categories/': [], '/api/articles/': page([]) });
    renderApp('/');
    const primary = screen.getByRole('navigation', { name: 'Primary' });
    const mobile = screen.getByRole('navigation', { name: 'Mobile' });
    for (const nav of [primary, mobile]) {
      expect(within(nav).getAllByRole('link')).toHaveLength(5);
    }
    expect(screen.getByRole('link', { name: 'Sign in' })).toHaveAttribute('href', '/login');
  });

  it('shows a retry button when the API fails', async () => {
    let attempts = 0;
    mockApi({
      '/api/stats/': stats,
      '/api/articles/': page([]),
      '/api/categories/': () => (attempts++ === 0 ? json({ detail: 'Server exploded' }, 500) : categories),
    });
    renderApp('/');
    await userEvent.click(await screen.findByRole('button', { name: 'Try again' }));
    expect(await screen.findByRole('link', { name: /Elections/ })).toBeInTheDocument();
  });

  it('renders the 404 page for unknown routes', async () => {
    mockApi();
    renderApp('/nowhere');
    expect(await screen.findByText('This page wandered off.')).toBeInTheDocument();
  });
});

describe('Explore', () => {
  it('loads indicators and syncs filters with the URL', async () => {
    const { calls } = mockApi({
      '/api/categories/': categories,
      '/api/indicators/': url => (url.searchParams.get('category') === 'elections'
        ? page([summary({ key: 'seat_share', title: 'Seat share', category: 'Elections', subgroup: 'Indian Elections', chart_type: 'doughnut' })])
        : page([summary()])),
    });
    renderApp('/explore');
    expect(await screen.findByRole('heading', { name: 'Real GDP growth' })).toBeInTheDocument();
    expect(screen.getByText('6.5 %')).toBeInTheDocument();

    await userEvent.selectOptions(screen.getByRole('combobox', { name: 'Group' }), 'elections');
    expect(await screen.findByRole('heading', { name: 'Seat share' })).toBeInTheDocument();
    expect(screen.getByTestId('location')).toHaveTextContent('/explore?category=elections');
    expect(screen.getByRole('heading', { level: 1, name: 'Elections' })).toBeInTheDocument();
    expect(screen.getByTestId('chart')).toHaveAttribute('data-type', 'doughnut');
    expect(calls.some(call => call.path === '/api/indicators/' && call.params.get('category') === 'elections')).toBe(true);
  });

  it('debounces search into the q parameter', async () => {
    const { calls } = mockApi({ '/api/categories/': categories, '/api/indicators/': page([summary()]) });
    renderApp('/explore');
    await screen.findByRole('heading', { name: 'Real GDP growth' });
    await userEvent.type(screen.getByRole('searchbox', { name: 'Search indicators' }), 'coal');
    await waitFor(() => expect(screen.getByTestId('location')).toHaveTextContent('/explore?q=coal'));
    const searches = calls.filter(call => call.path === '/api/indicators/' && call.params.get('q'));
    expect(searches.map(call => call.params.get('q'))).toEqual(['coal']);
  });

  it('shows illustrated picture rails for groups and subgroups', async () => {
    mockApi({ '/api/categories/': categories, '/api/indicators/': page([summary()]) });
    const { container } = renderApp('/explore');
    const groups = await screen.findByRole('list', { name: 'Groups' });
    const electionsCard = within(groups).getByText('Elections').closest('button');
    expect(electionsCard.style.getPropertyValue('--card-art')).toContain('/art/eci-building.svg');
    await userEvent.click(within(groups).getByText('Economic').closest('button'));
    await waitFor(() => expect(screen.getByTestId('location')).toHaveTextContent('/explore?category=economic'));

    const subgroups = await screen.findByRole('list', { name: 'Subgroups' });
    const trade = within(subgroups).getByText('Trade').closest('button');
    expect(trade.style.getPropertyValue('--card-art')).toContain('/art/rail-station.svg');
    expect(trade).toHaveAttribute('aria-pressed', 'false');
    await userEvent.click(trade);
    await waitFor(() => expect(screen.getByTestId('location')).toHaveTextContent('subgroup=trade'));
    expect(trade).toHaveAttribute('aria-pressed', 'true');
    expect(container.querySelector('.page-hero .art-backdrop')).toHaveAttribute('data-art', 'rail-station.svg');
  });

  it('reads filters from a deep link and can clear them', async () => {
    mockApi({ '/api/categories/': categories, '/api/indicators/': page([summary()]) });
    renderApp('/explore?category=economic&subgroup=trade&q=gdp');
    expect(await screen.findByRole('heading', { level: 1, name: 'Trade' })).toBeInTheDocument();
    expect(screen.getByRole('searchbox', { name: 'Search indicators' })).toHaveValue('gdp');
    await userEvent.click(screen.getByRole('button', { name: 'Clear filters' }));
    await waitFor(() => expect(screen.getByTestId('location')).toHaveTextContent(/^\/explore$/));
    expect(screen.getByRole('searchbox', { name: 'Search indicators' })).toHaveValue('');
  });

  it('appends the next page with load more', async () => {
    mockApi({
      '/api/categories/': categories,
      '/api/indicators/': url => (url.searchParams.get('page') === '2'
        ? page([summary({ key: 'inflation', title: 'Inflation' })], { count: 2 })
        : page([summary()], { count: 2, next: '/api/indicators/?page=2' })),
    });
    renderApp('/explore');
    await userEvent.click(await screen.findByRole('button', { name: /Load more \(1 left\)/ }));
    expect(await screen.findByRole('heading', { name: 'Inflation' })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Real GDP growth' })).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /Load more/ })).not.toBeInTheDocument();
  });

  it('shows an empty state', async () => {
    mockApi({ '/api/categories/': categories, '/api/indicators/': page([]) });
    renderApp('/explore?q=zzz');
    expect(await screen.findByText(/No indicators match/)).toBeInTheDocument();
  });

  it('adds cards to the compare tray, capped at four', async () => {
    const many = ['a', 'b', 'c', 'd', 'e'].map(key => summary({ key, title: `Indicator ${key}` }));
    mockApi({ '/api/categories/': categories, '/api/indicators/': page(many) });
    renderApp('/explore');
    const buttons = await screen.findAllByRole('button', { name: '+ Compare' });
    for (const button of buttons.slice(0, 4)) await userEvent.click(button);
    const tray = screen.getByRole('complementary', { name: 'Compare tray' });
    expect(tray).toHaveTextContent('4 selected');
    expect(within(tray).getByRole('link', { name: 'Compare' })).toHaveAttribute('href', '/compare?keys=a,b,c,d');
    expect(screen.getByRole('button', { name: '+ Compare' })).toBeDisabled();
    await userEvent.click(within(tray).getByRole('button', { name: 'Clear' }));
    expect(screen.queryByRole('complementary', { name: 'Compare tray' })).not.toBeInTheDocument();
  });
});

describe('Indicator detail', () => {
  it('renders the full chart, stats, notes, source and downloads', async () => {
    mockApi({ 'GET /api/indicators/gdp_growth/': detail() });
    renderApp('/indicator/gdp_growth');
    expect(await screen.findByRole('heading', { level: 1, name: 'Real GDP growth' })).toBeInTheDocument();
    expect(await screen.findByTestId('chart')).toHaveAttribute('data-labels', JSON.stringify(['2022', '2023', '2024']));
    expect(screen.getByText('Second paragraph.')).toBeInTheDocument();
    expect(screen.getByRole('link', { name: '⇩ CSV' })).toHaveAttribute('href', '/api/indicators/gdp_growth/download/?format=csv');
    expect(screen.getByRole('link', { name: '⇩ JSON' })).toHaveAttribute('href', '/api/indicators/gdp_growth/download/?format=json');
    expect(screen.getByRole('link', { name: /Open official source/ })).toHaveAttribute('href', 'https://data.worldbank.org/');
    expect(screen.getByRole('link', { name: 'Next →' })).toHaveAttribute('href', '/indicator/inflation');
    expect(screen.getByText('Highest').nextSibling).toHaveTextContent('8.2 %');
    expect(document.title).toBe("Real GDP growth · India's Journey");
  });

  it('filters the chart by year range', async () => {
    mockApi({ 'GET /api/indicators/gdp_growth/': detail() });
    renderApp('/indicator/gdp_growth');
    await screen.findByTestId('chart');
    await userEvent.selectOptions(screen.getByRole('combobox', { name: 'From year' }), '2023');
    expect(screen.getByTestId('chart')).toHaveAttribute('data-labels', JSON.stringify(['2023', '2024']));
    await userEvent.selectOptions(screen.getByRole('combobox', { name: 'To year' }), '2022');
    expect(screen.getByRole('combobox', { name: 'From year' })).toHaveValue('2022');
  });

  it('switches between pie and bar for categorical data', async () => {
    mockApi({
      'GET /api/indicators/seat_share/': detail({
        key: 'seat_share', title: 'Seat share', chart_type: 'doughnut', suffix: ' seats', category: 'Elections',
        labels: ['BJP', 'INC'], datasets: [{ label: 'Seats', values: [240, 99] }], latest_label: 'INC', latest_value: 99,
      }),
    });
    renderApp('/indicator/seat_share');
    expect(await screen.findByTestId('chart')).toHaveAttribute('data-type', 'doughnut');
    expect(screen.queryByRole('combobox', { name: 'From year' })).not.toBeInTheDocument();
    await userEvent.click(screen.getByRole('button', { name: '▥ Bar' }));
    expect(screen.getByTestId('chart')).toHaveAttribute('data-type', 'bar');
    expect(screen.getByRole('button', { name: '▥ Bar' })).toHaveAttribute('aria-pressed', 'true');
  });

  it('shows the data table on demand', async () => {
    mockApi({ 'GET /api/indicators/gdp_growth/': detail() });
    renderApp('/indicator/gdp_growth');
    await userEvent.click(await screen.findByRole('button', { name: 'Show data table' }));
    const table = screen.getByRole('table');
    expect(within(table).getAllByRole('row')).toHaveLength(4);
    expect(within(table).getByText('8.2 %')).toBeInTheDocument();
  });

  it('sends anonymous users to sign in when saving', async () => {
    mockApi({ 'GET /api/indicators/gdp_growth/': detail() });
    renderApp('/indicator/gdp_growth');
    await userEvent.click(await screen.findByRole('button', { name: '☆ Save' }));
    await waitFor(() => expect(screen.getByTestId('location')).toHaveTextContent('/login?next=/indicator/gdp_growth'));
    expect(await screen.findByRole('heading', { name: 'Sign in', level: 1 })).toBeInTheDocument();
  });

  it('saves and unsaves for signed-in users', async () => {
    document.cookie = 'csrftoken=tok';
    const { calls } = mockApi({
      '/api/auth/me/': { authenticated: true, user: { id: 1, username: 'asha', saved_count: 0 } },
      'GET /api/indicators/gdp_growth/': detail(),
      'POST /api/saved/': json({ key: 'gdp_growth' }, 201),
      'DELETE /api/saved/gdp_growth/': { ok: true, status: 204, json: async () => null },
    });
    renderApp('/indicator/gdp_growth');
    await screen.findByText('Hi, asha');
    await userEvent.click(await screen.findByRole('button', { name: '☆ Save' }));
    expect(await screen.findByRole('button', { name: '★ Saved' })).toHaveAttribute('aria-pressed', 'true');
    await userEvent.click(screen.getByRole('button', { name: '★ Saved' }));
    expect(await screen.findByRole('button', { name: '☆ Save' })).toBeInTheDocument();
    expect(calls.filter(call => call.method !== 'GET').map(call => call.method)).toEqual(['POST', 'DELETE']);
  });

  it('shows a friendly message for unknown indicators', async () => {
    mockApi();
    renderApp('/indicator/missing');
    expect(await screen.findByText('That indicator does not exist.')).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'Try again' })).not.toBeInTheDocument();
  });

  it('shows pending indicators without a chart', async () => {
    mockApi({ 'GET /api/indicators/pending/': detail({ key: 'pending', is_live: false, error: 'Source blocked automated access', labels: [], datasets: [] }) });
    renderApp('/indicator/pending');
    expect(await screen.findByText('Source blocked automated access')).toBeInTheDocument();
    expect(screen.queryByTestId('chart')).not.toBeInTheDocument();
  });
});
