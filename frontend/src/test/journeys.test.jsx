import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import JourneyMap from '../components/JourneyMap.jsx';
import { clearAtlasCache } from '../components/atlasData.js';

const quote = (text, generic = false) => ({ text, lang: 'sa', translation: `tr ${text}`, citation: `Cite ${text}`, work: 'Work', verified_from: 'https://example.org/x', generic, label: 'General verse' });
const journeys = {
  meta: { methodology: ['Own words.'] },
  journeys: [{
    id: 'demo', title: 'Demo', intro: 'A demo journey.', tradition: 'Buddhist',
    routes: [
      { id: 'one', label: 'Route one', colour: '#d33', stops: [
        { id: 's1', name: 'Lumbini', lat: 27.5, lon: 83.3, when: 'c. 563 BCE', description: 'Birth.', approximate: false, leg_km: 0, quote: quote('अ') },
        { id: 's2', name: 'Bodh Gaya', lat: 24.7, lon: 84.99, when: 'c. 528 BCE', description: 'Awakening.', approximate: false, leg_km: 400, quote: quote('ब', true) },
      ] },
      { id: 'two', label: 'Route two', colour: '#36c', stops: [
        { id: 't1', name: 'Sarnath', lat: 25.38, lon: 83.02, when: 'x', description: 'Sermon.', approximate: true, leg_km: 0, quote: quote('स') },
        { id: 't2', name: 'Kushinagar', lat: 26.74, lon: 83.89, when: 'y', description: 'End.', approximate: false, leg_km: 200, quote: quote('क') },
      ] },
    ],
  }, {
    id: 'rama-demo', title: 'Rama', intro: 'A route with adjacent stops.', tradition: 'Ramayana',
    routes: [{ id: 'rama', label: 'Rama route', colour: '#d33', stops: [
      { id: 'panchavati', name: 'Panchavati', lat: 20.01, lon: 73.79, when: 'x', description: 'Forest.', approximate: false, leg_km: 0, quote: quote('प') },
      { id: 'janasthana', name: 'Janasthana', lat: 20.01, lon: 73.79, when: 'y', description: 'Stronghold.', approximate: false, leg_km: 0, quote: quote('ज') },
    ] }],
  }],
};
const basemap = { k: 10, paths: [{ n: 'India', i: 'IND', d: 'M0,0L10,0L10,10Z' }] };

beforeEach(() => {
  clearAtlasCache();
  vi.spyOn(globalThis, 'fetch').mockImplementation(async url => ({ ok: true, json: async () => (String(url).includes('faith-journeys') ? journeys : basemap) }));
});
afterEach(() => vi.restoreAllMocks());

describe('Journey map', () => {
  it('shows the first stop with its verse and steps through the route', async () => {
    const { container } = render(<JourneyMap id="demo" />);
    expect(await screen.findByRole('heading', { name: /1\. Lumbini/ })).toBeInTheDocument();
    expect(container.querySelector('.jm-detail blockquote[lang="sa"]').textContent).toBe('अ');
    await userEvent.click(screen.getByRole('button', { name: 'Next stop →' }));
    expect(screen.getByRole('heading', { name: /2\. Bodh Gaya/ })).toBeInTheDocument();
    expect(container.querySelector('.jm-generic')).not.toBeNull();
    expect(container.querySelectorAll('.jm-stop')).toHaveLength(2);
    expect(container.querySelector('.jm-leg.is-done')).not.toBeNull();
    expect(container.querySelector('.jm-chart svg')).not.toBeNull();
  });

  it('switches routes and keeps the slider in range', async () => {
    const { container } = render(<JourneyMap id="demo" />);
    await userEvent.click(await screen.findByRole('button', { name: 'Route two' }));
    expect(screen.getByRole('heading', { name: /1\. Sarnath/ })).toBeInTheDocument();
    expect(container.querySelector('.jm-stop.is-approx')).not.toBeNull();
    expect(screen.getByRole('slider', { name: 'Stop' })).toHaveAttribute('max', '1');
  });

  it('offsets labels for Rama stops at the same map location', async () => {
    const { container } = render(<JourneyMap id="rama-demo" />);
    expect(await screen.findByRole('heading', { name: /1\. Panchavati/ })).toBeInTheDocument();
    const labels = [...container.querySelectorAll('.jm-label')];
    expect(labels).toHaveLength(2);
    expect(new Set(labels.map(label => label.getAttribute('text-anchor'))).size).toBe(2);
    expect(new Set(labels.map(label => label.getAttribute('x'))).size).toBe(2);
  });

  it('reports an unknown journey', async () => {
    render(<JourneyMap id="nope" />);
    expect(await screen.findByText(/Unknown journey/)).toBeInTheDocument();
  });
});
