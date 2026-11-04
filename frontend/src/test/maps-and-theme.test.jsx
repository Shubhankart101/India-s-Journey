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
    const map = await screen.findByRole('img', { name: /Bank offices: 3 States\/UTs shaded\. Highest Goa/ });
    expect(map.querySelectorAll('path.has-value')).toHaveLength(3);
    expect(map.querySelector('path.no-value title').textContent).toBe('Jammu & Kashmir: not reported');
    expect(container.querySelector('.india-map-readout').textContent).toMatch(/^Highest: Goa/);
  });

  it('offers map and bar views for map indicators', () => {
    expect(chartModes({ chart_type: 'map', labels: ['Kerala'], datasets: [{ values: [1] }] })).toEqual({ modes: ['map', 'bar'], initial: 'map' });
  });
});

describe('Header controls', () => {
  it('switches theme with a segmented radio group', async () => {
    render(<ThemeSelect />);
    const group = screen.getByRole('radiogroup', { name: 'Display theme' });
    expect(within(group).getAllByRole('radio').map(button => button.textContent)).toEqual(['Light', 'Dark', 'Newspaper', 'Pamphlet']);
    await userEvent.click(within(group).getByRole('radio', { name: 'Newspaper' }));
    expect(within(group).getByRole('radio', { name: 'Newspaper' })).toHaveAttribute('aria-checked', 'true');
    expect(document.documentElement.dataset.theme).toBe('newspaper');
    await userEvent.keyboard('{ArrowRight}');
    expect(getTheme()).toBe('pamphlet');
  });

  it('links to LinkedIn and GitHub in a new tab', () => {
    render(<ContactLinks />);
    expect(screen.getByRole('link', { name: /LinkedIn/ })).toHaveAttribute('href', LINKEDIN_URL);
    expect(screen.getByRole('link', { name: /GitHub/ })).toHaveAttribute('href', GITHUB_URL);
    expect(screen.getByRole('link', { name: /GitHub/ })).toHaveAttribute('rel', 'noopener noreferrer');
  });
});
