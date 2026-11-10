import { render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it, vi } from 'vitest';
import MapSelector, { choropleth } from '../components/MapSelector.jsx';
import SubgroupArticle from '../components/SubgroupArticle.jsx';
import { stateKey } from '../components/IndiaMap.jsx';
import { mockApi, page, renderApp, summary } from './helpers.jsx';

vi.mock('../components/LazyChart.jsx', () => ({
  default: ({ title }) => <div role="img" aria-label={`Chart: ${title}`} />,
}));

const NAMES = ['Kerala', 'Goa', 'Punjab', 'Bihar', 'Assam', 'Gujarat', 'Odisha', 'Haryana', 'Sikkim', 'Tripura'];
const geometry = { viewBox: '0 0 100 100', states: Object.fromEntries(NAMES.map((name, index) => [name, `M${index * 8} 0h6v6z`])) };

describe('SubgroupArticle extensions', () => {
  it('renders a callout lead, an inline pull quote, chip sources and the closing slot', () => {
    render(<MemoryRouter><SubgroupArticle
      headline="Guide"
      dek="Intro."
      kicker="Group · Subgroup"
      lead={<p>Lead callout</p>}
      sections={[{ title: 'One', text: 'a' }, { title: 'Two', text: 'b' }, { title: 'Three', text: 'c' }]}
      quote="A memorable fact."
      quoteAfterSection={1}
      verse={{ tradition: 'T', lang: 'en', text: 'Verse text', english: 'Verse text', source: 'Src' }}
      after={<p>All charts</p>}
      sources={[{ name: 'Publisher A', url: 'https://a.example' }]}
      chipSources
    /></MemoryRouter>);
    expect(screen.getByText('Group · Subgroup')).toBeInTheDocument();
    expect(screen.getByText('Lead callout')).toBeInTheDocument();
    expect(screen.getByText('A memorable fact.')).toBeInTheDocument();
    expect(screen.getByText('Publisher A')).toBeInTheDocument();
    expect(screen.getByText('All charts')).toBeInTheDocument();
    expect(screen.getByText('03')).toBeInTheDocument();
  });
});

describe('MapSelector', () => {
  const regions = new Map([
    [stateKey('Kerala'), { fill: 'red', summary: '94%', to: '/x/kerala' }],
    [stateKey('Goa'), { summary: 'No figure' }],
  ]);

  it('lists every region, links only those with a page and selects from the map', async () => {
    const onSelect = vi.fn();
    render(<MemoryRouter><MapSelector geometry={geometry} regions={regions} heading="Pick one" ariaLabel="Map" onSelect={onSelect} /></MemoryRouter>);
    const list = screen.getByRole('navigation', { name: /Choose a State/ });
    expect(within(list).getAllByText(/./, { selector: 'strong' })).toHaveLength(NAMES.length);
    expect(within(list).getByRole('link', { name: /Kerala/ })).toHaveAttribute('href', '/x/kerala');
    expect(within(list).queryByRole('link', { name: /Goa/ })).not.toBeInTheDocument();
    await userEvent.click(screen.getByRole('button', { name: /^Kerala\./ }));
    expect(onSelect).toHaveBeenCalledWith('/x/kerala', 'Kerala');
    await userEvent.click(screen.getByRole('button', { name: /^Goa\./ }));
    expect(onSelect).toHaveBeenCalledTimes(1);
  });

  it('builds quintile fills from a point map', () => {
    const { edges, fillOf } = choropleth(new Map(NAMES.map((name, index) => [name, index])));
    expect(edges.length).toBeGreaterThan(0);
    expect(fillOf(0)).not.toEqual(fillOf(9));
    expect(fillOf(undefined)).toBeUndefined();
  });
});

describe('map subgroup and region page', () => {
  const categories = [{
    name: 'India in Maps', slug: 'india-in-maps', order: 0, title: 'India in maps', description: '', badges: [], art: 'parliament.svg', indicator_count: 3, live_count: 3,
    subgroups: [{ name: 'Payments & Banking Maps', slug: 'payments-banking-maps', order: 0, title: 'Payments & Banking Maps', description: 'Health by State.', art: 'parliament.svg', indicator_count: 3, live_count: 3 }],
  }];
  const mapIndicator = (key, title, offset) => summary({
    key, title, category: 'India in Maps', category_slug: 'india-in-maps', subgroup: 'Payments & Banking Maps', subgroup_slug: 'payments-banking-maps', chart_type: 'map', suffix: '%',
    latest_value: 50, preview: { labels: NAMES, datasets: [{ label: title, values: NAMES.map((_, index) => index * 3 + offset) }] },
  });
  const items = [
    mapIndicator('literacy_2011', 'Literacy by State/UT (2011) — map', 1),
    mapIndicator('literacy_2021', 'Literacy by State/UT (2021) — map', 5),
    mapIndicator('births_2023', 'Birth rate by State/UT (2023) — map', 2),
  ];
  const routes = () => mockApi({
    '/api/categories/': categories,
    '/api/indicators/': page(items),
    '/maps/india-states.json': geometry,
  });

  it('shows the map selector with measure and period switches', async () => {
    routes();
    renderApp('/explore/india-in-maps/payments-banking-maps');
    expect(await screen.findByRole('heading', { level: 1, name: /Payments/ })).toBeInTheDocument();
    expect(await screen.findByRole('combobox', { name: 'Measure shown on the map' })).toBeInTheDocument();
    expect(screen.getByRole('group', { name: 'Period' })).toBeInTheDocument();
    await userEvent.click(screen.getByRole('link', { name: /^Kerala/ }));
    await waitFor(() => expect(screen.getByTestId('location')).toHaveTextContent('/explore/india-in-maps/payments-banking-maps/kerala'));
  });

  it('opens a per-state article with ranks and a back link', async () => {
    routes();
    renderApp('/explore/india-in-maps/payments-banking-maps/kerala');
    expect(await screen.findByRole('heading', { level: 1, name: /Kerala/ })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /Payments/ })).toBeInTheDocument();
    expect(await screen.findByText(/Where Kerala stands/)).toBeInTheDocument();
    expect(screen.getAllByRole('table')[0]).toHaveTextContent('Literacy by State/UT');
  });

  it('keeps distinct charts per article section', async () => {
    mockApi({
      '/api/categories/': [{ ...categories[0], name: 'Economic', slug: 'economic', subgroups: [{ ...categories[0].subgroups[0], name: 'Trade', slug: 'trade', title: 'Trade' }] }],
      '/api/indicators/': page([summary({ key: 'a', title: 'Exports' }), summary({ key: 'b', title: 'Imports' })]),
    });
    renderApp('/explore/economic/trade');
    expect(await screen.findByRole('heading', { level: 1, name: 'Trade' })).toBeInTheDocument();
    const figures = await screen.findAllByRole('img', { name: 'Chart: Exports' });
    expect(figures).toHaveLength(1);
  });
});
