import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import EpicAtlas from '../components/EpicAtlas.jsx';
import LokSabhaAtlas from '../components/LokSabhaAtlas.jsx';
import { clearAtlasCache } from '../components/atlasData.js';
import { chartModes } from '../format.js';

const geometry = {
  viewBox: '0 0 100 100',
  states: { Kerala: 'M0,0L10,0L10,10Z', Goa: 'M20,0L30,0L30,10Z', Bihar: 'M60,0L70,0L70,10Z' },
};
const lok = {
  meta: { methodology: ['Old states are mapped to modern ones.'], years_available: [2019, 2024], missing_years: [] },
  years: [
    { year: 2019, label: '2019', seats_counted: 4, national: { BJP: 3, INC: 1 }, note: '' },
    { year: 2024, label: '2024', seats_counted: 4, national: { INC: 3, BJP: 1 }, note: '' },
  ],
  parties: { INC: { name: 'Indian National Congress', colour: '#1e88e5' }, BJP: { name: 'Bharatiya Janata Party', colour: '#ff9933' } },
  states: {
    Kerala: {
      2019: { total: 2, lead: 'INC', seats: { INC: 2 }, turnout: 77.1, vote_share: { INC: 40 }, list: [['Wayanad', 'A Winner', 'INC', 1000], ['Alappuzha', 'B Winner', 'INC', 500]] },
      2024: { total: 2, lead: 'BJP', seats: { BJP: 1, INC: 1 }, turnout: null, vote_share: null, list: [['Thrissur', 'C Winner', 'BJP', 7000], ['Wayanad', 'D Winner', 'INC', 9000]] },
    },
    Goa: { 2019: { total: 1, lead: 'BJP', seats: { BJP: 1 }, list: [['North Goa', 'E Winner', 'BJP', 100]] } },
  },
};
const epics = {
  meta: { methodology: ['Approximate locations.'] },
  epics: {
    mahabharata: {
      title: 'Kingdoms of the Mahabharata', toggle_label: 'Mahabharata', source_text: 'Mahabharata (Vyasa)', location_field: 'parva', edition_note: 'Note.', forces: { pandava: 7, kaurava: 11 },
      sides: { pandava: { label: 'Pandava side', colour: '#1e88e5' }, kaurava: { label: 'Kaurava side', colour: '#c62828' } },
      entries: [
        { id: 'hastinapura', name: 'Hastinapura', name_sa: 'हस्तिनापुर', side: 'kaurava', modern_location: 'Near Meerut', x: 10, y: 20, outside_india: false, ruler: 'Dhritarashtra', role: 'Kuru capital', parva: 'Adi Parva', description: 'Seat of the Kurus.', shloka: { sa: 'धर्मक्षेत्रे कुरुक्षेत्रे', translation: 'On the field of dharma', citation: 'Bhagavad Gita 1.1', verified_from: 'https://example.org/gita' } },
        { id: 'matsya', name: 'Matsya', name_sa: 'मत्स्य', side: 'pandava', modern_location: 'Rajasthan', x: 30, y: 40, outside_india: false, ruler: 'Virata', role: 'Refuge', parva: 'Virata Parva', description: 'Where the Pandavas hid.', shloka: { sa: 'विराटनगरे', translation: 'In the city of Virata', citation: 'Mahabharata 4.1', verified_from: 'https://example.org/virata', generic: true } },
      ],
      route: { title: 'The Pandavas', summary: 'S', stops: [
        { id: 'a', name: 'Hastinapura', x: 10, y: 20, note: 'Start', leg_km: 0, approximate: false, shloka: { sa: 'अ', translation: 'A', citation: 'MB 1', verified_from: 'https://example.org/a' } },
        { id: 'b', name: 'Virata', x: 30, y: 40, note: 'Hid', leg_km: 300, approximate: true, shloka: { sa: 'ब', translation: 'B', citation: 'MB 2', verified_from: 'https://example.org/b', generic: true } },
      ] },
    },
    ramayana: {
      title: 'Places of the Ramayana', toggle_label: 'Ramayana', source_text: 'Valmiki Ramayana', location_field: 'kanda', edition_note: '',
      sides: { lanka: { label: 'Lanka', colour: '#7b1fa2' } },
      entries: [{ id: 'lanka', name: 'Lanka', name_sa: 'लङ्का', side: 'lanka', modern_location: 'Sri Lanka', x: 50, y: 90, outside_india: true, ruler: 'Ravana', role: 'Ravana\'s city', kanda: 'Sundara Kanda', description: 'Island city.', shloka: null }],
    },
  },
};

beforeEach(() => {
  clearAtlasCache();
  vi.spyOn(globalThis, 'fetch').mockImplementation(async url => ({
    ok: true,
    json: async () => (String(url).includes('lok-sabha') ? lok : String(url).includes('epic-kingdoms') ? epics : geometry),
  }));
});
afterEach(() => vi.restoreAllMocks());

describe('Lok Sabha atlas', () => {
  it('shades each State/UT by the party with the most seats', async () => {
    const { container } = render(<LokSabhaAtlas title="Lok Sabha" />);
    const goa = await screen.findByRole('button', { name: /^Goa, 2024: no seats/ });
    expect(goa).toBeInTheDocument();
    expect(container.querySelector('path[data-state="Kerala"]').style.fill).toBe('rgb(255, 153, 51)');
  });

  it('changes the shading when the year changes', async () => {
    const { container } = render(<LokSabhaAtlas title="Lok Sabha" />);
    const slider = await screen.findByRole('slider', { name: 'Election year' });
    fireSlider(slider, 0);
    expect(container.querySelector('path[data-state="Kerala"]').style.fill).toBe('rgb(30, 136, 229)');
    expect(container.querySelector('.atlas-year').textContent).toMatch(/^2019/);
    expect(container.querySelectorAll('path.no-value')).toHaveLength(1);
  });

  it('lists seat-by-seat winners when a State is clicked and clears with Escape', async () => {
    const { container } = render(<LokSabhaAtlas title="Lok Sabha" />);
    await userEvent.click(await screen.findByRole('button', { name: /^Kerala, 2024/ }));
    const detail = container.querySelector('.atlas-detail');
    expect(detail.textContent).toMatch(/Thrissur/);
    expect(detail.textContent).toMatch(/C Winner/);
    expect(detail.textContent).toMatch(/7,000/);
    await userEvent.keyboard('{Escape}');
    expect(container.querySelector('.atlas-detail').textContent).toMatch(/Select a State/);
  });

  it('highlights the States a party leads from the legend', async () => {
    const { container } = render(<LokSabhaAtlas title="Lok Sabha" />);
    await screen.findByRole('slider', { name: 'Election year' });
    await userEvent.click(screen.getByRole('button', { name: /^INC/ }));
    expect(container.querySelectorAll('path.is-dim').length).toBeGreaterThan(0);
  });
});

function fireSlider(slider, value) {
  // React tracks the input value setter, so use the native one before dispatching.
  const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
  setter.call(slider, String(value));
  slider.dispatchEvent(new Event('input', { bubbles: true }));
  slider.dispatchEvent(new Event('change', { bubbles: true }));
}

describe('Epic atlas', () => {
  it('opens a detail panel with the shloka, citation and Devanagari language tag', async () => {
    const { container } = render(<EpicAtlas title="Kingdoms of the Mahabharata" />);
    await userEvent.click(await screen.findByRole('button', { name: /^Hastinapura, Near Meerut/ }));
    const detail = container.querySelector('.atlas-detail');
    expect(detail.textContent).toMatch(/Dhritarashtra/);
    expect(detail.textContent).toMatch(/Bhagavad Gita 1\.1/);
    expect(detail.querySelector('blockquote[lang="sa"]').textContent).toMatch(/धर्मक्षेत्रे/);
  });


  it('switches to Allegiance and shows the war force totals and selectable side filters', async () => {
    const { container } = render(<EpicAtlas title="Kingdoms of the Mahabharata" />);
    await userEvent.click(await screen.findByRole('button', { name: /^Hastinapura, Near Meerut/ }));
    await userEvent.click(screen.getByRole('button', { name: 'Allegiance' }));
    expect(container.querySelector('.atlas-forces').textContent).toMatch(/Pandava/);
    expect(container.querySelector('.atlas-forces').textContent).toMatch(/Kaurava/);
    expect(container.querySelector('.atlas-detail').textContent).toMatch(/Force size/);
    const filters = container.querySelectorAll('.atlas-side-filter input[type="checkbox"]');
    expect(filters.length).toBeGreaterThan(1);
    await userEvent.click(filters[0]);
    expect(container.querySelectorAll('.atlas-pin.is-dim').length).toBeGreaterThan(0);
  });

  it('shows a verse for every place (never a placeholder), toggles epics and traces the route', async () => {
    const { container } = render(<EpicAtlas title="Kingdoms of the Mahabharata" />);
    await userEvent.click(await screen.findByRole('button', { name: /^Matsya, Rajasthan/ }));
    const detail = container.querySelector('.atlas-detail');
    expect(detail.textContent).not.toMatch(/Shloka to be added/);
    expect(detail.querySelector('blockquote[lang="sa"]')).not.toBeNull();
    await userEvent.click(screen.getByRole('button', { name: 'Trace the route' }));
    expect(container.querySelectorAll('.atlas-stop').length).toBeGreaterThan(1);
    expect(container.querySelector('.atlas-detail blockquote[lang="sa"]')).not.toBeNull();
    await userEvent.click(screen.getByRole('button', { name: 'Ramayana' }));
    expect(await screen.findByRole('button', { name: /^Lanka, Sri Lanka/ })).toBeInTheDocument();
    expect(container.querySelector('circle.outside')).toBeInTheDocument();
  });

  it('is keyboard operable and filters by side', async () => {
    const { container } = render(<EpicAtlas title="Kingdoms of the Mahabharata" />);
    const pin = await screen.findByRole('button', { name: /^Matsya, Rajasthan/ });
    pin.focus();
    await userEvent.keyboard('{Enter}');
    expect(pin).toHaveAttribute('aria-pressed', 'true');
    await userEvent.click(screen.getByRole('button', { name: /^Kaurava side/ }));
    expect(container.querySelectorAll('circle.is-dim')).toHaveLength(1);
  });
});

describe('atlas chart modes', () => {
  it('renders atlas indicators in their own view', () => {
    expect(chartModes({ chart_type: 'categorical-map' })).toEqual({ modes: ['categorical-map'], initial: 'categorical-map' });
    expect(chartModes({ chart_type: 'point-map' })).toEqual({ modes: ['point-map'], initial: 'point-map' });
  });
});
