import { describe, it, expect } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import AncientEmpiresAtlas from '../components/AncientEmpiresAtlas.jsx';
import IndusValleyAtlas from '../components/IndusValleyAtlas.jsx';
import { buildIvcArticleSections } from '../components/SubgroupPage.jsx';
import sitesData from '../data/indus-civilisation.json';

describe('Ancient Empires Atlas: Detailed History & Primary Epigraphs', () => {
  it('renders detailed history chronicle and primary source documentation when history tab is selected', async () => {
    render(<AncientEmpiresAtlas initialEmpireId="maurya-empire" />);

    // Check empire title is present
    const headings = await screen.findAllByText(/Mauryan Empire & Pan-Indian Hegemony/i);
    expect(headings.length).toBeGreaterThanOrEqual(1);

    // Click on the History & Quotes tab
    const historyTab = screen.getByRole('tab', { name: /History & Quotes/i });
    expect(historyTab).toBeInTheDocument();
    fireEvent.click(historyTab);

    // Verify detailed history overview is present
    expect(screen.getByText(/Imperial Era & Historical Trajectory/i)).toBeInTheDocument();

    // Verify chronological era narrative is rendered
    expect(screen.getByText(/Chandragupta Maurya & Seleucid Treaty/i)).toBeInTheDocument();

    // Verify authentic quoted primary epigraphic sources are rendered
    expect(screen.getByText(/Ashoka Major Rock Edict XIII/i)).toBeInTheDocument();
    expect(screen.getByText(/Megasthenes, Indika/i)).toBeInTheDocument();

    // Verify the academic citation is present
    expect(screen.getByText(/Corpus Inscriptionum Indicarum/i)).toBeInTheDocument();
  });
});

describe('Indus Valley Atlas: Period Boundaries & ASI Memoirs', () => {
  it('renders period boundary selectors and toggles to Harappan Periods & ASI Memoirs tab', async () => {
    render(<IndusValleyAtlas />);

    // Verify the period horizon buttons are rendered
    expect(screen.getByRole('button', { name: /Early Harappan/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Mature Harappan/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Late Harappan/i })).toBeInTheDocument();

    // Switch to Harappan Periods & ASI Quotes tab
    const periodsTab = screen.getByRole('tab', { name: /Harappan Periods & ASI Quotes/i });
    expect(periodsTab).toBeInTheDocument();
    fireEvent.click(periodsTab);

    // Verify Archaeological Trajectory and Quoted ASI Memoirs are rendered
    expect(screen.getByText(/Archaeological Trajectory & Urban Morphology/i)).toBeInTheDocument();
    expect(screen.getByText(/Quoted Primary Excavation Memoirs/i)).toBeInTheDocument();

    // Verify chronological horizons are populated with era names (not empty colons)
    expect(screen.getByText(/Urban Revolution & Grid-Iron Planning/i)).toBeInTheDocument();

    // Verify quoted Director-General Sir John Marshall memoir or ASI memoir
    expect(screen.getByText(/Sir John Marshall/i)).toBeInTheDocument();
  });

  it('renders IVC article sections with populated stratigraphic phases and no empty colons', () => {
    const sections = buildIvcArticleSections(sitesData);
    expect(sections.length).toBe(5);

    const firstSectionContent = sections[0].content;
    render(firstSectionContent);

    // Verify badge and extent
    expect(screen.getByText(/REGIONAL POLITIES & RAVI\/KOT DIJI PHASES/i)).toBeInTheDocument();
    expect(screen.getByText(/~500,000 km²/i)).toBeInTheDocument();

    // Verify stratigraphic phase text is fully populated without empty colons
    expect(screen.getByText(/Hakra Ware & Early Pastoral-Agricultural Settlements/i)).toBeInTheDocument();
    expect(screen.queryByText(/^:$/)).not.toBeInTheDocument();
  });
});
