import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import VoterRollAtlas from '../components/VoterRollAtlas.jsx';

vi.mock('../components/IndiaMap.jsx', () => ({
  loadGeometry: vi.fn(() => Promise.resolve({ viewBox: '0 0 100 100', states: { Bihar: 'M0 0Z', Kerala: 'M10 10Z' } })),
}));

describe('VoterRollAtlas', () => {
  it('renders the five interactive figures', () => {
    render(<VoterRollAtlas />);
    expect(screen.getByRole('heading', { name: /The roll behind the ballot/i })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /SIR: a fresh enumeration/i })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /SSR: the annual update/i })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /Deletions and safeguards/i })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /Find the right form/i })).toBeInTheDocument();
  });

  it('opens state details from a map click', async () => {
    const { container } = render(<VoterRollAtlas />);
    await waitFor(() => expect(container.querySelector('[data-state="Bihar"]')).toBeInTheDocument());
    fireEvent.click(container.querySelector('[data-state="Bihar"]'));
    expect(screen.getByTestId('sir-state-detail')).toHaveTextContent('Before SIR');
    expect(screen.getByTestId('sir-state-detail')).toHaveTextContent('Draft roll');
    expect(screen.getByTestId('sir-state-detail')).toHaveTextContent('Final roll');
    fireEvent.click(container.querySelector('[data-state="Kerala"]'));
    expect(screen.getByTestId('sir-state-detail')).toHaveTextContent('Kerala');
    expect(screen.getByTestId('sir-state-detail')).toHaveTextContent('Comparable before');
  });

  it('steps through the selected voter scenario', async () => {
    const user = userEvent.setup();
    render(<VoterRollAtlas />);
    const scenario = screen.getByRole('combobox', { name: 'Choose a voter scenario' });
    await user.selectOptions(scenario, 'moved');
    expect(screen.getByRole('heading', { name: 'Form 8' })).toBeInTheDocument();
    await user.click(screen.getByRole('button', { name: 'Next step' }));
    expect(screen.getByText(/verifies the old entry and the new address/i)).toBeInTheDocument();
  });
});