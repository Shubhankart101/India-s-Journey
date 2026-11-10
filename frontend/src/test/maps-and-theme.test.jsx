import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import IndiaMap, { mapPoints, stateKey } from '../components/IndiaMap.jsx';
import ThemeSelect, { ContactLinks, GITHUB_URL, LINKEDIN_URL } from '../components/ThemeSelect.jsx';
import { chartModes } from '../format.js';
import { getTheme } from '../theme.js';

const geometry = {
  viewBox: '0 0 100 100',
  sourceUrl: 'https://github.com/datameet/maps',
  license: 'CC BY 2.5 IN',
  states: { Kerala: 'M0,0L10,0L10,10Z', Goa: 'M20,0L30,0L30,10Z', 'Jammu & Kashmir': 'M40,0L50,0L50,10Z', Bihar: 'M60,0L70,0L70,10Z' },
};

describe('India in Maps', () => {
  it('matches State/UT spellings to the outline names', () => {
    expect(stateKey('1. Orissa (P)')).toBe('orissa');
    const points = mapPoints(['Kerala', 'Orissa', 'Jammu and Kashmir', 'Goa', 'All India'], [3, 1, 2, null, 9], Object.keys(geometry.states));
    expect([...points.entries()]).toEqual([['Kerala', 3], ['Odisha', 1], ['Jammu & Kashmir', 2]]);
  });

  it('shades reported States/UTs and describes the extremes', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue({ ok: true, json: async () => geometry });
    const { container } = render(<IndiaMap title="Bank offices" labels={['Kerala', 'Goa', 'Bihar']} values={[10, 30, 20]} suffix=" offices" />);
    await screen.findByRole('button', { name: /^Kerala: 10/ });
    expect(container.querySelectorAll('path.has-value')).toHaveLength(3);
    expect(container.querySelector('path.no-value').getAttribute('aria-label')).toBe('Jammu & Kashmir: not reported');
    expect(container.querySelector('.india-map-readout').textContent).toMatch(/^Highest: Goa/);
  });

  it('pins a State/UT with rank and median, filters by legend band and search', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue({ ok: true, json: async () => geometry });
    const { container } = render(<IndiaMap title="Pin test" labels={['Kerala', 'Goa', 'Bihar']} values={[10, 30, 20]} />);
    const goa = await screen.findByRole('button', { name: /^Goa: 30/ });
    await userEvent.click(goa);
    expect(goa).toHaveAttribute('aria-pressed', 'true');
    const detail = container.querySelector('.india-map-detail');
    expect(detail.textContent).toMatch(/Rank1 of 3/);
    expect(detail.textContent).toMatch(/Median/);
    await userEvent.keyboard('{Escape}');
    expect(container.querySelector('.india-map-detail').textContent).toMatch(/Click a State/);
    await userEvent.click(container.querySelector('.india-map-bins button'));
    expect(container.querySelectorAll('path.is-dim').length).toBeGreaterThan(0);
    await userEvent.type(screen.getByPlaceholderText(/Find a State/), 'bih');
    expect(container.querySelectorAll('.india-map-list li button')).toHaveLength(1);
  });

  it('plays through periods when the data has a time series', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue({ ok: true, json: async () => geometry });
    const datasets = [{ label: '2021', values: [1, 2, 3] }, { label: '2022', values: [2, 3, 4] }];
    const { container } = render(<IndiaMap title="Years" labels={['Kerala', 'Goa', 'Bihar']} values={datasets[0].values} datasets={datasets} />);
    await screen.findByRole('slider', { name: 'Period' });
    expect(container.querySelector('.india-map-timebar output').textContent).toBe('2022');
    await userEvent.click(screen.getByRole('button', { name: /Play/ }));
    expect(container.querySelector('.india-map-timebar output').textContent).toBe('2021');
  });

  it('offers map and bar views for map indicators', () => {
    expect(chartModes({ chart_type: 'map', labels: ['Kerala'], datasets: [{ values: [1] }] })).toEqual({ modes: ['map', 'bar'], initial: 'map' });
  });
});

describe('Header controls', () => {
  it('switches between all ten modes with the pill radio group and arrow keys', async () => {
    render(<ThemeSelect />);
    const group = screen.getByRole('radiogroup', { name: 'Display mode' });
    const radios = within(group).getAllByRole('radio');
    expect(radios.map(radio => radio.getAttribute('aria-label'))).toEqual(
      ['Light', 'Dark', 'Newspaper', 'Pamphlet', 'Military', 'Parliamentary', 'Desi', 'Air Force', 'Navy', 'Police']);
    expect(radios.find(radio => radio.getAttribute('aria-checked') === 'true')).toHaveAttribute('value', getTheme());
    for (const name of ['Newspaper', 'Parliamentary', 'Desi', 'Air Force', 'Navy']) {
      await userEvent.click(screen.getByRole('radio', { name }));
      expect(screen.getByRole('radio', { name })).toHaveAttribute('aria-checked', 'true');
    }
    expect(document.documentElement.dataset.theme).toBe('navy');
    await userEvent.keyboard('{ArrowRight}');
    expect(getTheme()).toBe('police');
    await userEvent.keyboard('{ArrowRight}');
    expect(getTheme()).toBe('light');
    await userEvent.keyboard('{End}');
    expect(document.documentElement.dataset.theme).toBe('police');
    await userEvent.keyboard('{Home}');
    expect(screen.getByRole('radio', { name: 'Light' })).toHaveFocus();
  });

  it('links to LinkedIn and GitHub in a new tab', () => {
    render(<ContactLinks />);
    expect(screen.getByRole('link', { name: /LinkedIn/ })).toHaveAttribute('href', LINKEDIN_URL);
    expect(screen.getByRole('link', { name: /GitHub/ })).toHaveAttribute('href', GITHUB_URL);
    expect(screen.getByRole('link', { name: /GitHub/ })).toHaveAttribute('rel', 'noopener noreferrer');
  });
});
