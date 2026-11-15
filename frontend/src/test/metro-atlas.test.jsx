import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import MetroAtlas from '../components/MetroAtlas.jsx';

describe('MetroAtlas: Transit Guide, Route Planner & Operational Directory', () => {
  it('renders top bar, live IST clock, and 17 city selector pills', () => {
    render(<MetroAtlas />);
    expect(screen.getByText(/LIVE IST SCHEMATIC TRANSIT/i)).toBeInTheDocument();
    expect(screen.getByText(/All 17 Indian Metro Cities/i)).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /^Delhi-NCR/i })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /^Mumbai$/i })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /^Bengaluru/i })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /^Kolkata/i })).toBeInTheDocument();
  });

  it('renders all workbench view mode tabs', () => {
    render(<MetroAtlas />);
    expect(screen.getByRole('button', { name: /Geographic/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Live Transit Schematic/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Route Planner & Fare Finder/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Curated Directory Matrix/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Commuter Guide & Rules/i })).toBeInTheDocument();
  });

  it('switches to Route Planner and calculates shortest route, duration, and fare slabs', () => {
    render(<MetroAtlas />);
    const plannerBtn = screen.getByRole('button', { name: /Route Planner & Fare Finder/i });
    fireEvent.click(plannerBtn);

    expect(screen.getByText(/Interactive Route Planner & Fare Slabs/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Origin Station/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Destination Station/i)).toBeInTheDocument();

    // Check fare metrics are calculated and displayed
    expect(screen.getByText(/Estimated Travel Time/i)).toBeInTheDocument();
    expect(screen.getByText(/Total Distance/i)).toBeInTheDocument();
    expect(screen.getByText(/Token Fare/i)).toBeInTheDocument();
    expect(screen.getAllByText(/Smart Card/i).length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText(/Step-by-Step Commuter Itinerary/i)).toBeInTheDocument();
  });

  it('swaps origin and destination stations when swap button is clicked', () => {
    render(<MetroAtlas />);
    fireEvent.click(screen.getByRole('button', { name: /Route Planner & Fare Finder/i }));

    const originSelect = screen.getByLabelText(/Origin Station/i);
    const destSelect = screen.getByLabelText(/Destination Station/i);

    const initialOrigin = originSelect.value;
    const initialDest = destSelect.value;

    const swapBtn = screen.getByTitle(/Swap Origin and Destination/i);
    fireEvent.click(swapBtn);

    expect(originSelect.value).toBe(initialDest);
    expect(destSelect.value).toBe(initialOrigin);
  });

  it('renders the curated directory table with 17 operational networks and gauge filtering', () => {
    render(<MetroAtlas />);
    fireEvent.click(screen.getByRole('button', { name: /Curated Directory Matrix/i }));

    expect(screen.getByText(/National Rapid Transit Directory/i)).toBeInTheDocument();
    expect(screen.getByText(/Curated Directory & System Comparison Matrix/i)).toBeInTheDocument();

    // Check table headers
    expect(screen.getByText(/City & Network Name/i)).toBeInTheDocument();
    expect(screen.getByText(/Operator \/ Authority/i)).toBeInTheDocument();
    expect(screen.getByText(/Daily Ridership/i)).toBeInTheDocument();
    expect(screen.getByText(/Gauge & Electrification/i)).toBeInTheDocument();

    // Filter by Standard Gauge
    const standardBtn = screen.getByRole('button', { name: /Standard Gauge/i });
    fireEvent.click(standardBtn);
    expect(standardBtn).toHaveClass('active');
  });

  it('renders passenger guide cards for NCMC, women-only coaches, and baggage rules', () => {
    render(<MetroAtlas />);
    fireEvent.click(screen.getByRole('button', { name: /Commuter Guide & Rules/i }));

    expect(screen.getByText(/Passenger Rules, Fare Policies & Transit Guidelines/i)).toBeInTheDocument();
    expect(screen.getByText(/Women-Only Reserved Coaches/i)).toBeInTheDocument();
    expect(screen.getByText(/National Common Mobility Card/i)).toBeInTheDocument();
    expect(screen.getByText(/Luggage & Baggage Regulations/i)).toBeInTheDocument();
    expect(screen.getByText(/Section 64/i)).toBeInTheDocument();
  });
});
