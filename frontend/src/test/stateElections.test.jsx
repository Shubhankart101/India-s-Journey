import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import LokSabhaAtlas from '../components/LokSabhaAtlas.jsx';
import { clearAtlasCache } from '../components/atlasData.js';

const geometry = { viewBox: '0 0 100 100', states: { Kerala: 'M0,0L10,0L10,10Z', Odisha: 'M20,0L30,0L30,10Z', Ladakh: 'M60,0L70,0L70,10Z' } };
const parties = { INC: { name: 'Indian National Congress', colour: '#1e88e5' }, BJP: { name: 'Bharatiya Janata Party', colour: '#ff9933' } };
const rec = (lead, other, list) => ({ total: 2, lead, seats: { [lead]: 1, [other]: 1 }, turnout: 70, vote_share: { INC: 40, BJP: 30 }, list });
const lok = {
  meta: { methodology: ['m'], years_available: [2019, 2024], missing_years: [], sources: [] },
  years: [{ year: 2019, label: '2019', seats_counted: 2, national: { BJP: 1, INC: 1 }, note: '' }, { year: 2024, label: '2024', seats_counted: 2, national: { BJP: 1, INC: 1 }, note: '' }],
  parties,
  states: {
    Odisha: { 2019: rec('BJP', 'INC', [['Puri', 'P One', 'BJP', 10], ['Cuttack', 'C One', 'INC', 20]]), 2024: rec('BJP', 'INC', [['Puri', 'P Two', 'BJP', 30], ['Cuttack', 'C Two', 'INC', 40]]) },
    Kerala: { 2024: rec('INC', 'BJP', [['Thrissur', 'T One', 'BJP', 5], ['Wayanad', 'W One', 'INC', 6]]) },
  },
};
const yr = (id, lead, other) => ({ id, year: Number(id), label: id, total: 2, lead, seats: { [lead]: 1, [other]: 1 }, turnout: 60, vote_share: { INC: 40, BJP: 35 }, source: 'TCPD' });
const odisha = {
  state: 'Odisha', slug: 'odisha', house: 'AE', house_name: 'Odisha Vidhan Sabha', seats_now: 147, note: '', source: 'TCPD', source_url: 'https://example.org',
  sources: [{ key: 'tcpd', name: 'TCPD Lok Dhaba', url: 'https://example.org', licence: 'Non-commercial' }], parties,
  years: [yr('2019', 'BJP', 'INC'), yr('2024', 'INC', 'BJP')],
  elections: { 2019: { list: [['Puri', 'AE One', 'BJP', 1], ['Cuttack', 'AE Two', 'INC', 2]] }, 2024: { list: [['Puri', 'AE Three', 'INC', 3], ['Cuttack', 'AE Four', 'BJP', 4]] } },
};
const index = { meta: { methodology: ['x'] }, states: { Odisha: { slug: 'odisha' }, Kerala: { slug: 'kerala' } }, no_assembly: { Ladakh: 'No legislative assembly.' } };

beforeEach(() => {
  clearAtlasCache();
  window.history.replaceState(null, '', '/');
  vi.spyOn(globalThis, 'fetch').mockImplementation(async url => {
    const u = String(url);
    if (u.includes('state-elections/odisha')) return { ok: true, json: async () => odisha };
    if (u.includes('state-elections/index')) return { ok: true, json: async () => index };
    return { ok: true, json: async () => (u.includes('lok-sabha') ? lok : geometry) };
  });
});
afterEach(() => vi.restoreAllMocks());

async function openOdisha(user) {
  await user.click(await screen.findByRole('button', { name: /^Odisha, 2024/ }));
  await user.click(await screen.findByRole('button', { name: /How Odisha voted/ }));
}

describe('State election view', () => {
  it('opens from the map with Lok Sabha and Assembly tabs and writes a permalink', async () => {
    const user = userEvent.setup();
    render(<LokSabhaAtlas title="Lok Sabha" />);
    await openOdisha(user);
    expect(screen.getByRole('heading', { name: 'How Odisha voted' })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: 'Lok Sabha' })).toHaveAttribute('aria-selected', 'true');
    expect(screen.getAllByText('P Two').length).toBeGreaterThan(0);
    await user.click(screen.getByRole('tab', { name: 'Vidhan Sabha (Assembly)' }));
    expect(await screen.findByText('AE Three')).toBeInTheDocument();
    expect(window.location.hash).toBe('#state=Odisha&house=AE&year=2024');
  });

  it('changes the constituency list when the year changes', async () => {
    const user = userEvent.setup();
    render(<LokSabhaAtlas title="Lok Sabha" />);
    await openOdisha(user);
    await user.click(screen.getByRole('tab', { name: 'Vidhan Sabha (Assembly)' }));
    await screen.findByText('AE Three');
    await user.click(screen.getAllByRole('button', { name: /^2019:/ })[0]);
    expect(screen.getByText('AE One')).toBeInTheDocument();
    expect(screen.queryByText('AE Three')).toBeNull();
    expect(window.location.hash).toContain('year=2019');
  });

  it('opens from a permalink and closes back to the map', async () => {
    window.history.replaceState(null, '', '/#state=Odisha&house=AE&year=2019');
    const user = userEvent.setup();
    render(<LokSabhaAtlas title="Lok Sabha" />);
    expect(await screen.findByText('AE One')).toBeInTheDocument();
    await user.click(screen.getByRole('button', { name: /All India map/ }));
    await waitFor(() => expect(screen.queryByRole('tablist')).toBeNull());
    expect(window.location.hash).toBe('');
  });

  it('explains when a State/UT has no assembly', async () => {
    window.history.replaceState(null, '', '/#state=Ladakh&house=AE');
    render(<LokSabhaAtlas title="Lok Sabha" />);
    expect(await screen.findByText(/No legislative assembly/)).toBeInTheDocument();
  });
});
