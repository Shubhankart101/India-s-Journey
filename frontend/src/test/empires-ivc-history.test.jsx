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

  it('renders all decisive battles and historic locations tabs with rich metadata and layer toggles', () => {
    render(<AncientEmpiresAtlas initialEmpireId="maurya-empire" />);

    // Verify map layer switcher buttons exist
    const allLayerBtn = screen.getByRole('button', { name: /All \(/i });
    const battlesLayerBtn = screen.getByRole('button', { name: /Battles \(/i });
    const locationsLayerBtn = screen.getByRole('button', { name: /Locations \(/i });
    expect(allLayerBtn).toBeInTheDocument();
    expect(battlesLayerBtn).toBeInTheDocument();
    expect(locationsLayerBtn).toBeInTheDocument();

    // Switch to Battles tab in dossier
    const battlesTab = screen.getByRole('tab', { name: /Battles \(/i });
    expect(battlesTab).toBeInTheDocument();
    fireEvent.click(battlesTab);

    // Verify decisive Mauryan battles are rendered both on map canvas and in dossier list
    expect(screen.getAllByText(/The Kalinga War/i).length).toBeGreaterThanOrEqual(2);
    expect(screen.getAllByText(/Mauryan–Seleucid War/i).length).toBeGreaterThanOrEqual(2);
    expect(screen.getAllByText(/Overthrow of the Nanda Empire/i).length).toBeGreaterThanOrEqual(2);

    // Switch to Locations & Cities tab in dossier
    const locationsTab = screen.getByRole('tab', { name: /Locations & Cities \(/i });
    expect(locationsTab).toBeInTheDocument();
    fireEvent.click(locationsTab);

    // Verify historical locations and citadels are rendered both on map canvas and in dossier list
    expect(screen.getAllByText(/Taxila \(Uttarapatha\)/i).length).toBeGreaterThanOrEqual(2);
    expect(screen.getAllByText(/Sannati/i).length).toBeGreaterThanOrEqual(2);
    expect(screen.getAllByText(/Alexandropolis \/ Kandahar/i).length).toBeGreaterThanOrEqual(2);
    expect(screen.getAllByText(/Tamralipti/i).length).toBeGreaterThanOrEqual(2);

    // Switch to Milestones tab
    const milestonesTab = screen.getByRole('tab', { name: /Milestones \(/i });
    expect(milestonesTab).toBeInTheDocument();
    fireEvent.click(milestonesTab);

    // Verify dynastic milestones and descriptive narrative are present
    expect(screen.getByText(/Third Buddhist Council convened at Pataliputra/i)).toBeInTheDocument();
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
