import { fireEvent, screen, waitFor, within } from '@testing-library/react';
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
    const latest = (await screen.findByRole('heading', { name: 'Latest analysis' })).closest('section');
    expect(await within(latest).findByRole('link', { name: 'Budget explainer' })).toHaveAttribute('rel', 'noopener noreferrer');
  });

  it('shows the intro shared with the static site without repeating the Sources acknowledgement', async () => {
    mockApi({
      '/api/stats/': stats,
      '/api/categories/': categories,
      '/api/articles/': articles,
    });
    renderApp('/');
    expect(screen.getByRole('heading', { level: 1, name: 'India, in perspective.' })).toBeInTheDocument();
    expect(screen.getByText(/A thousand signals\. One changing nation\./)).toBeInTheDocument();
    expect(screen.queryByRole('region', { name: 'The writing that inspired this atlas' })).not.toBeInTheDocument();
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

  it('shows mini indices with sparklines for the group on screen', async () => {
    const elections = summary({ key: 'turnout', title: 'Voter turnout', category: 'Elections', category_slug: 'elections', suffix: '%', preview: { labels: ['2014', '2019', '2024'], datasets: [{ label: 'Turnout', values: [66.4, 67.4, 65.8] }] } });
    const { calls } = mockApi({
      '/api/stats/': stats,
      '/api/categories/': categories,
      '/api/articles/': articles,
      '/api/indicators/': url => page(url.searchParams.get('category') === 'elections'
        ? [elections]
        : [summary({ source: 'World Bank', source_url: 'https://data.worldbank.org/' }), summary({ key: 'seat_pie', chart_type: 'doughnut' }), summary({ key: 'gdp_level', title: 'GDP level', suffix: ' USD', preview: { labels: ['2022', '2023', '2024'], datasets: [{ label: 'GDP', values: [3e12, 3.5e12, 3.85e12] }] } })]),
    });
    renderApp('/');
    const strip = await screen.findByRole('list', { name: 'Headline Economic indicators' });
    const links = within(strip).getAllByRole('link');
    const chartLinks = links.filter(link => link.classList.contains('mini-index-main'));
    expect(chartLinks.map(link => link.getAttribute('href'))).toEqual(['/indicator/gdp_growth', '/indicator/gdp_level']);
    expect(chartLinks[0]).toHaveTextContent('6.5 %');
    expect(chartLinks[0]).toHaveTextContent('▼ −1.7 pp');
    expect(chartLinks[1]).toHaveTextContent('3.85 trillion USD');
    expect(chartLinks[1]).toHaveTextContent('▲ +10.0%');
    expect(within(strip).getByRole('link', { name: 'data.worldbank.org · Source ↗' })).toHaveAttribute('href', 'https://data.worldbank.org/');
    expect(strip.querySelectorAll('svg.mini-spark polyline')).toHaveLength(2);
    expect(calls.some(call => call.path === '/api/indicators/' && call.params.get('live') === 'true')).toBe(true);
    await userEvent.click(screen.getByRole('button', { name: 'Show Elections scene' }));
    const next = await screen.findByRole('list', { name: 'Headline Elections indicators' });
    expect(within(next).getByRole('link')).toHaveAttribute('href', '/indicator/turnout');
  });

  it('falls back to latest-snapshot share tiles for groups without trends', async () => {
    const seats = summary({
      key: 'seat_share', title: 'Seat share', chart_type: 'doughnut', category: 'Elections', category_slug: 'elections', suffix: ' seats',
      preview: { labels: ['BJP', 'INC', 'SP', 'TMC', 'DMK', 'Others'], datasets: [{ label: 'Seats', values: [240, 99, 37, 29, 22, 116] }] },
    });
    const ranking = summary({ key: 'state_rank', scope: 'state', category_slug: 'elections', chart_type: 'bar', preview: { labels: ['A', 'B'], datasets: [{ label: 'x', values: [1, 2] }] } });
    mockApi({ '/api/stats/': stats, '/api/categories/': [categories[1], categories[0]], '/api/articles/': articles, '/api/indicators/': page([ranking, seats]) });
    const { container } = renderApp('/');
    const strip = await screen.findByRole('list', { name: 'Headline Elections indicators' });
    const tile = within(strip).getByRole('link');
    expect(tile).toHaveAttribute('href', '/indicator/seat_share');
    expect(tile).toHaveTextContent('44.2%');
    expect(tile).toHaveTextContent('BJP');
    expect(container.querySelectorAll('.mini-share span')).toHaveLength(4);
  });

  it('has desktop navigation and a mobile tab bar', async () => {
    mockApi({ '/api/stats/': stats, '/api/categories/': [], '/api/articles/': page([]) });
    renderApp('/');
    const primary = screen.getByRole('navigation', { name: 'Primary' });
    const mobile = screen.getByRole('navigation', { name: 'Mobile' });
    for (const nav of [primary, mobile]) {
      expect(within(nav).getAllByRole('link')).toHaveLength(6);
    }
    expect(within(primary).getByRole('link', { name: 'API' })).toHaveAttribute('href', '/api');
    expect(screen.queryByRole('link', { name: 'Sign in' })).not.toBeInTheDocument();
    expect(screen.queryByRole('link', { name: 'Saved' })).not.toBeInTheDocument();
  });

  it('shows Django and static API resources without the general site chrome', async () => {
    mockApi();
    renderApp('/api');
    expect(await screen.findByRole('heading', { name: 'API & endpoint explorer' })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Open Swagger UI' })).toHaveAttribute('href', '/api/docs/');
    expect(screen.getByRole('link', { name: 'Open static JSON API explorer' })).toHaveAttribute(
      'href',
      'https://indiasjourney.netlify.app/api.html',
    );
    expect(screen.queryByRole('navigation', { name: 'Primary' })).not.toBeInTheDocument();
    expect(screen.queryByRole('contentinfo')).not.toBeInTheDocument();
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
    expect(await screen.findByRole('link', { name: /subgroups\s*Elections/ })).toBeInTheDocument();
  });

  it('adds a subgroup marquee, typewriter topics and a back-to-top button', async () => {
    mockApi({ '/api/stats/': stats, '/api/categories/': categories, '/api/articles/': articles });
    const { container } = renderApp('/');
    const featured = await screen.findByRole('navigation', { name: 'Featured subgroups' });
    expect(within(featured).getByRole('link', { name: 'Macro Overview' })).toHaveAttribute('href', '/explore?category=economic&subgroup=macro-overview');
    const more = screen.getByRole('navigation', { name: 'More subgroups' });
    expect(within(more).getByRole('link', { name: 'Indian Elections' })).toHaveAttribute('href', '/explore?category=elections&subgroup=indian-elections');
    // The looping duplicate copy is hidden from assistive tech and the tab order.
    const copy = featured.querySelector('.marquee-group[aria-hidden="true"] a');
    expect(copy).toHaveAttribute('tabindex', '-1');
    expect(screen.getByText(/GDP and inflation, UPI payments/)).toHaveClass('sr-only');
    expect(container.querySelector('.hero-orbs')).toHaveAttribute('aria-hidden', 'true');
    expect(container.querySelector('.scroll-progress')).toBeInTheDocument();
    const top = screen.getByRole('button', { name: 'Back to top', hidden: true });
    expect(top).toHaveAttribute('tabindex', '-1');
  });

  it('renders the 404 page for unknown routes', async () => {
    mockApi();
    renderApp('/nowhere');
    expect(await screen.findByText('This page wandered off.')).toBeInTheDocument();
  });
});

describe('Sources', () => {
  it('shows a standalone searchable source directory without the Explore page', async () => {
    const indicators = [
      summary({
        key: 'gdp_growth',
        title: 'Real GDP growth',
        source_url: 'https://data.worldbank.org/indicator/NY.GDP.MKTP.KD.ZG',
      }),
      summary({
        key: 'cpi',
        title: 'CPI inflation',
        source_url: 'https://www.mospi.gov.in/',
      }),
      summary({
        key: 'wb_lending_rate',
        title: 'Bank lending interest rate',
        source_url: 'World Bank API FR.INR.LEND',
      }),
      summary({
        key: 'report_source',
        title: 'Annual report citation',
        source: 'Ministry annual report',
        source_url: '',
      }),
    ];
    const { calls } = mockApi({
      '/api/indicators/': url => {
        const pageNumber = Number(url.searchParams.get('page') || 1);
        return page(pageNumber === 1 ? indicators.slice(0, 1) : indicators.slice(1), {
          next: pageNumber === 1 ? '/api/indicators/?page=2' : null,
          count: indicators.length,
        });
      },
      '/api/articles/': page([]),
    });
    renderApp('/sources');

    expect(await screen.findByRole('heading', { name: 'Sources & references' })).toBeInTheDocument();
    expect(screen.getByRole('region', { name: 'The writing that inspired this atlas' })).toBeInTheDocument();
    expect(await screen.findByText('Real GDP growth')).toBeInTheDocument();
    expect(await screen.findByText('CPI inflation')).toBeInTheDocument();
    expect(await screen.findByText('Bank lending interest rate')).toBeInTheDocument();
    expect(screen.getByText('World Bank API FR.INR.LEND')).toBeInTheDocument();
    expect(await screen.findByText('Annual report citation')).toBeInTheDocument();
    expect(screen.getByText('Ministry annual report')).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /data\.worldbank\.org · Open source/ })).toHaveAttribute(
      'href',
      indicators[0].source_url,
    );
    expect(screen.getAllByRole('link', { name: 'View graph' })[0]).toHaveAttribute('href', '/indicator/gdp_growth');
    expect(screen.getByText('4 graphs')).toBeInTheDocument();
    expect(screen.getByText('Public data publishers, project references & tools')).toBeInTheDocument();
    expect(screen.getByText('Original background illustrations')).toBeInTheDocument();
    fireEvent.change(screen.getByLabelText('Find an indicator, publisher or URL'), { target: { value: 'mospi' } });
    await waitFor(() => expect(screen.queryByText('Real GDP growth')).not.toBeInTheDocument());
    expect(screen.getByText('CPI inflation')).toBeInTheDocument();
    expect(calls.filter(call => call.path === '/api/indicators/')).toHaveLength(2);
    expect(screen.queryByText('Every indicator, one search away.')).not.toBeInTheDocument();
    expect(screen.getAllByRole('link', { name: 'Sources' }).every(link => link.getAttribute('href') === '/sources')).toBe(true);
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
    expect(await screen.findByTestId('chart')).toHaveAttribute('data-type', 'doughnut');
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

  it('shows an illustrated tile grid for groups and subgroups', async () => {
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
    await userEvent.click(within(subgroups).getByText('← All groups').closest('button'));
    await waitFor(() => expect(screen.getByTestId('location')).toHaveTextContent(/^\/explore$/));
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
    expect(within(tray).getAllByRole('listitem')).toHaveLength(4);
    await userEvent.click(within(tray).getByRole('button', { name: 'Remove Indicator b from compare' }));
    expect(tray).toHaveTextContent('3 selected');
    expect(within(tray).getByRole('link', { name: 'Compare' })).toHaveAttribute('href', '/compare?keys=a,c,d');
    expect(screen.getAllByRole('button', { name: '+ Compare' }).every(button => !button.disabled)).toBe(true);
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

  it('switches to period-on-period change and overlays a trend line', async () => {
    mockApi({ 'GET /api/indicators/gdp_growth/': detail() });
    renderApp('/indicator/gdp_growth');
    await screen.findByTestId('chart');
    await userEvent.click(screen.getByRole('button', { name: '↗ Trend' }));
    expect(screen.getByTestId('chart')).toHaveAttribute('data-datasets', '2');
    expect(screen.getByText(/R² /)).toBeInTheDocument();
    await userEvent.click(screen.getByRole('button', { name: 'Δ Change' }));
    expect(screen.getByTestId('chart')).toHaveAttribute('data-values', JSON.stringify([[null, 1.2, -1.7]]));
    expect(screen.getByText(/percentage points/)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: '↗ Trend' })).toBeDisabled();
  });

  it('renders explainer tiles from structured details', async () => {
    mockApi({ 'GET /api/indicators/gdp_growth/': detail({ details: 'What it shows — Output.\n\nHow to read it — Higher is faster.\n\nWhy it matters — Jobs.\n\nExtra note.' }) });
    renderApp('/indicator/gdp_growth');
    expect(await screen.findByRole('heading', { name: 'What it shows' })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Why it matters' }).nextSibling).toHaveTextContent('Jobs.');
    expect(screen.getByText('Extra note.')).toBeInTheDocument();
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

  it('does not expose account-only save controls', async () => {
    mockApi({ 'GET /api/indicators/gdp_growth/': detail() });
    renderApp('/indicator/gdp_growth');
    await screen.findByRole('heading', { name: 'Real GDP growth' });
    expect(screen.queryByRole('button', { name: /save/i })).not.toBeInTheDocument();
    expect(screen.getByRole('button', { name: '+ Compare' })).toBeInTheDocument();
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
