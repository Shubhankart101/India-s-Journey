import { fireEvent, render, screen } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import Elections from '../pages/Elections.jsx';

const parties = { BJP: { name: 'Bharatiya Janata Party', colour: '#ff9933' }, INC: { name: 'Indian National Congress', colour: '#1e88e5' } };
const result = (lead, other, list) => ({ total: 2, lead, seats: { [lead]: 1, [other]: 1 }, turnout: 70, vote_share: { BJP: 42, INC: 38 }, list });
const index = {
  meta: { methodology: ['Party seat totals are reported election by election.'] },
  states: { Odisha: { slug: 'odisha', first: 2019, last: 2024, elections: 2, seats_now: 147, lead_latest: 'BJP', lead_latest_name: parties.BJP.name, latest_label: '2024', latest_seats: 1, latest_total: 2, latest_headline: 'Bharatiya Janata Party led with 1 of 2 seats in 2024' } },
  no_assembly: {},
};
const assembly = {
  state: 'Odisha', slug: 'odisha', house: 'AE', house_name: 'Odisha Vidhan Sabha', seats_now: 147, note: '',
  sources: [{ key: 'TCPD', name: 'TCPD Lok Dhaba', url: 'https://example.org/tcpd', licence: 'Cite TCPD' }], parties,
  years: [
    { id: '2019', year: 2019, label: '2019', total: 2, lead: 'INC', seats: { INC: 1, BJP: 1 }, turnout: 60, vote_share: { INC: 42, BJP: 38 }, source: 'TCPD' },
    { id: '2024', year: 2024, label: '2024', total: 2, lead: 'BJP', seats: { BJP: 1, INC: 1 }, turnout: 70, vote_share: { BJP: 42, INC: 38 }, source: 'TCPD' },
  ],
  elections: { 2019: { list: [['Puri', 'Candidate One', 'INC', 10], ['Cuttack', 'Candidate Two', 'BJP', 20]] }, 2024: { list: [['Puri', 'Candidate Three', 'BJP', 30], ['Cuttack', 'Candidate Four', 'INC', 40]] } },
};
const atlas = {
  meta: { sources: [{ name: 'Election Commission of India', url: 'https://example.org/eci' }], methodology: ['Lok Sabha note'] },
  years: [{ year: 1952, label: '1952' }, { year: 2024, label: '2024' }], parties,
  states: { Odisha: { 1952: result('INC', 'BJP', [['Puri', 'Candidate A', 'INC', 1], ['Cuttack', 'Candidate B', 'BJP', 2]]), 2024: result('BJP', 'INC', [['Puri', 'Candidate C', 'BJP', 3], ['Cuttack', 'Candidate D', 'INC', 4]]) } },
};
const response = json => ({ ok: true, json: async () => json });

beforeEach(() => {
  window.history.replaceState(null, '', '/');
  vi.spyOn(globalThis, 'fetch').mockImplementation(async input => {
    const url = String(input);
    if (url.includes('state-elections/index.json')) return response(index);
    if (url.includes('lok-sabha-atlas.json')) return response(atlas);
    if (url.includes('state-elections/odisha.json')) return response(assembly);
    throw new Error(`Unexpected request: ${url}`);
  });
});
afterEach(() => vi.restoreAllMocks());

describe('State election article page', () => {
  it('shows current results, assembly history, Lok Sabha coverage and sources', async () => {
    render(<MemoryRouter initialEntries={['/elections/odisha']}><Routes><Route path="/elections/:stateSlug" element={<Elections />} /></Routes></MemoryRouter>);
    expect(await screen.findByRole('heading', { name: 'How Odisha voted' })).toBeInTheDocument();
    const latestResult = screen.getAllByText(/Bharatiya Janata Party/).find(element => element.tagName === 'DD');
    expect(latestResult).toHaveTextContent(/1 of 2 seats/);
    expect(screen.getByText('Lok Sabha coverage').parentElement).toHaveTextContent(/1952.*2024/);
    expect(await screen.findByText('Candidate Three')).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: 'Vidhan Sabha (Assembly)' })).toHaveAttribute('aria-selected', 'true');
    expect(screen.getByRole('button', { name: /2024: BJP won the most seats/ })).toHaveAttribute('aria-pressed', 'true');
    expect(screen.getByRole('link', { name: 'TCPD Lok Dhaba ↗' })).toHaveAttribute('href', 'https://example.org/tcpd');
    fireEvent.click(screen.getByRole('button', { name: /2019: INC won the most seats/ }));
    expect(await screen.findByText('Candidate One')).toBeInTheDocument();
  });
});
