import { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import ArtBackdrop from '../components/ArtBackdrop.jsx';
import { AMBIENT_ART } from '../art.js';
import Thanks from '../components/Thanks.jsx';
import { Empty, ErrorState, Loading } from '../components/States.jsx';
import { api } from '../api.js';
import { useAsync, useDebounced, useDocumentTitle } from '../hooks.js';

const PUBLISHERS = [
  ['https://datahelpdesk.worldbank.org/knowledgebase/articles/889392', 'World Bank Open Data & API documentation'],
  ['https://data.rbi.org.in/DBIE/', 'Reserve Bank of India Database on Indian Economy'],
  ['https://www.mospi.gov.in/', 'Ministry of Statistics and Programme Implementation'],
  ['https://www.indiabudget.gov.in/economicsurvey/', 'Economic Survey of India'],
  ['https://www.npci.org.in/what-we-do/upi/product-statistics', 'NPCI UPI product statistics'],
  ['https://morth.gov.in/road-accident-in-india', 'Ministry of Road Transport and Highways — road accident reports'],
  ['https://mnre.gov.in/en/physical-progress/', 'Ministry of New and Renewable Energy — physical progress'],
  ['https://hmis.mohfw.gov.in/#!/standardReports', 'Ministry of Health and Family Welfare — HMIS reports'],
  ['https://ncrb.gov.in/', 'National Crime Records Bureau'],
  ['https://www.pewresearch.org/global/', 'Pew Research Center — Global'],
  ['https://www.sipri.org/databases', 'SIPRI databases'],
  ['https://www.eci.gov.in/', 'Election Commission of India'],
  ['https://www.archives.gov/electoral-college', 'U.S. National Archives — Electoral College results'],
  ['https://www.fec.gov/campaign-finance-data/candidate-summary-file-description/', 'Federal Election Commission — candidate summary file definitions'],
  ['https://whc.unesco.org/en/list/', 'UNESCO World Heritage List'],
  ['https://databank.worldbank.org/source/world-development-indicators', 'World Bank — World Development Indicators'],
  ['https://www3.wipo.int/ipstats/', 'WIPO IP Statistics Data Center — patents, trademarks & designs'],
  ['https://uis.unesco.org/', 'UNESCO Institute for Statistics — R&D and education'],
  ['https://njdg.ecourts.gov.in/njdg_v3/', 'National Judicial Data Grid — District & Subordinate Courts'],
  ['https://njdg.ecourts.gov.in/hcnjdg_v2/', 'National Judicial Data Grid — High Courts'],
  ['https://scdg.sci.gov.in/scnjdg/', 'National Judicial Data Grid — Supreme Court of India'],
  ['https://datahub.itu.int/', 'ITU DataHub — telecom & internet indicators'],
  ['https://www.worldbank.org/en/programs/entrepreneurship', 'World Bank Entrepreneurship Database — new business density'],
];

const SPORTS_SOURCES = [
  ["https://www.olympics.com/en/olympic-games/olympic-results", "International Olympic Committee — Olympic results"],
  ["https://www.paralympic.org/india", "International Paralympic Committee — India results"],
  ["https://www.ocasia.org/games/", "Olympic Council of Asia — Asian Games results"],
  ["https://thecgf.com/results", "Commonwealth Games Federation — results"],
  ["https://pib.gov.in/PressReleasePage.aspx?PRID=2045963", "Press Information Bureau — Ministry of Youth Affairs & Sports releases"],
  ["https://www.icc-cricket.com/rankings", "International Cricket Council — team & player rankings, events"],
  ["https://stats.espncricinfo.com/ci/engine/stats/index.html", "ESPNcricinfo Statsguru — cricket match & player records"],
  ["https://www.fih.hockey/events", "International Hockey Federation (FIH) — events, rankings, Pro League & player profiles"],
  ["https://inside.fifa.com/fifa-world-ranking/men", "FIFA — world rankings, match results & line-ups"],
  ["https://bwfbadminton.com/rankings/", "Badminton World Federation — rankings & championships"],
  ["https://www.daviscup.com/", "ITF — Davis Cup & Billie Jean King Cup"],
  ["https://www.issf-sports.org/competitions", "International Shooting Sport Federation — competitions"],
  ["https://www.worldarchery.sport/events", "World Archery — events & results"],
  ["https://uww.org/events/senior-world-championships", "United World Wrestling — World Championships"],
  ["https://www.iba.sport/", "International Boxing Association / World Boxing — medallists"],
  ["https://iwf.sport/results/results-by-events/", "International Weightlifting Federation — results"],
  ["https://worldathletics.org/competitions", "World Athletics — championships medal tables"],
  ["https://ratings.fide.com/", "FIDE — rating lists & Chess Olympiad"],
  ["https://www.prokabaddi.com/standings", "Pro Kabaddi League — standings"],
];

const PROJECT_REFERENCES = [
  ['https://politypolicy.com/', 'PolityPolicy — public-data storytelling'],
  ['https://politypolicy.substack.com/', 'Polity and Policy — essays and analysis'],
  ['https://substack.com/@indianmatrix', 'Indian Matrix — public writing'],
];

const CHART_TOOLS = [
  ['https://react.dev/', 'React documentation'],
  ['https://www.chartjs.org/docs/latest/', 'Chart.js documentation'],
  ['https://www.django-rest-framework.org/', 'Django REST framework documentation'],
];

const ILLUSTRATIONS = [
  ['parliament.svg', 'Parliament-inspired civic building', 'https://sansad.in/ls/about/introduction', 'Lok Sabha — Parliament of India'],
  ['eci-building.svg', 'Election institution illustration', 'https://www.eci.gov.in/', 'Election Commission of India'],
  ['us-capitol.svg', 'U.S. Capitol-inspired civic illustration', 'https://www.aoc.gov/explore-capitol-campus/buildings-grounds/capitol-building', 'Architect of the Capitol'],
  ['hampi.svg', 'Hampi-inspired heritage illustration', 'https://whc.unesco.org/en/list/241/', 'UNESCO — Group of Monuments at Hampi'],
  ['taj-mahal.svg', 'Taj Mahal-inspired heritage illustration', 'https://whc.unesco.org/en/list/252/', 'UNESCO — Taj Mahal'],
  ['red-fort.svg', 'Red Fort-inspired Independence Day scene', 'https://whc.unesco.org/en/list/231/', 'UNESCO — Red Fort Complex'],
  ['konark-sun-temple.svg', 'Konark Sun Temple-inspired chariot scene', 'https://whc.unesco.org/en/list/246/', 'UNESCO — Sun Temple, Konârak'],
  ['himalaya.svg', 'Himalayan peaks scene', 'https://whc.unesco.org/en/list/335/', 'UNESCO — Nanda Devi and Valley of Flowers'],
  ['backwaters.svg', 'Kerala backwaters scene', 'https://www.keralatourism.org/backwaters/', 'Kerala Tourism — Backwaters'],
  ['isro-launch.svg', 'Rocket launch scene', 'https://www.isro.gov.in/', 'Indian Space Research Organisation'],
  ['varanasi-ghats.svg', 'Varanasi ghats evening scene', 'https://varanasi.nic.in/', 'District Varanasi'],
  ['sea-link.svg', 'Cable-stayed sea link city scene', 'https://www.msrdc.in/', 'Maharashtra State Road Development Corporation'],
  ['renewables.svg', 'Wind and solar energy scene', 'https://mnre.gov.in/', 'Ministry of New and Renewable Energy'],
  ['monsoon-fields.svg', 'Monsoon fields scene', 'https://mausam.imd.gov.in/', 'India Meteorological Department'],
  ['toy-train-hills.svg', 'Hill toy-train scene', 'https://whc.unesco.org/en/list/944/', 'UNESCO — Mountain Railways of India'],
  ['sports.svg', 'Floodlit stadium scene', 'https://yas.gov.in/sports', 'Ministry of Youth Affairs & Sports'],
  ['sports-medals.svg', 'Medal podium scene', 'https://olympics.com/en/olympic-games/olympic-results', 'International Olympic Committee — Olympic results'],
  ['multi-sport-games.svg', 'Multi-sport Games cauldron scene', 'https://www.ocasia.org/', 'Olympic Council of Asia'],
  ['cricket.svg', 'Floodlit cricket ground scene', 'https://www.bcci.tv/', 'Board of Control for Cricket in India'],
  ['hockey-football.svg', 'Hockey and football pitch scene', 'https://www.hockeyindia.org/', 'Hockey India'],
  ['cricket-women.svg', "Women's cricket ground scene", 'https://www.bcci.tv/', 'Board of Control for Cricket in India'],
  ['trophy.svg', 'Trophy celebration scene', 'https://www.icc-cricket.com/', 'International Cricket Council'],
  ['rankings.svg', 'Rankings ladder scene', 'https://www.icc-cricket.com/rankings', 'ICC team rankings'],
  ['hockey.svg', 'Floodlit hockey turf scene', 'https://www.fih.hockey/', 'International Hockey Federation'],
  ['hockey-women.svg', "Women's hockey turf scene", 'https://www.hockeyindia.org/', 'Hockey India'],
  ['football.svg', 'Floodlit football pitch scene', 'https://www.the-aiff.com/', 'All India Football Federation'],
  ['athletics.svg', 'Athletics track scene', 'https://indianathletics.in/', 'Athletics Federation of India'],
  ['shooting-archery.svg', 'Shooting and archery range scene', 'https://www.issf-sports.org/', 'International Shooting Sport Federation'],
  ['combat-strength.svg', 'Wrestling mat and weightlifting scene', 'https://uww.org/', 'United World Wrestling'],
  ['racket-sports.svg', 'Badminton and tennis court scene', 'https://bwfbadminton.com/', 'Badminton World Federation'],
  ['chess-kabaddi.svg', 'Chessboard and kabaddi court scene', 'https://www.fide.com/', 'FIDE — International Chess Federation'],
  ['cricket-batting.svg', 'Batters then and now scene', 'https://www.bcci.tv/', 'Board of Control for Cricket in India'],
  ['cricket-bowling.svg', 'Bowlers then and now scene', 'https://www.bcci.tv/', 'Board of Control for Cricket in India'],
  ['hockey-players.svg', 'Hockey players then and now scene', 'https://www.hockeyindia.org/', 'Hockey India'],
  ['football-players.svg', 'Footballers then and now scene', 'https://www.the-aiff.com/', 'All India Football Federation'],
  ['football-women.svg', "Women's football pitch scene", 'https://www.the-aiff.com/', 'All India Football Federation'],
  ['football-rankings.svg', 'Football rankings ladder scene', 'https://inside.fifa.com/fifa-world-ranking/men', 'FIFA world rankings'],
  ['innovation.svg', 'Circuit city and light-bulb scene', 'https://www3.wipo.int/ipstats/', 'WIPO IP statistics'],
  ['patents-ip.svg', 'Patent filings scene', 'https://www3.wipo.int/ipstats/', 'WIPO IP statistics'],
  ['research-lab.svg', 'Research laboratory scene', 'https://uis.unesco.org/', 'UNESCO Institute for Statistics'],
  ['startup-hub.svg', 'Startup skyline scene', 'https://www.worldbank.org/en/programs/entrepreneurship', 'World Bank Entrepreneurship Database'],
  ['judiciary.svg', 'Scales of justice and case-file scene', 'https://njdg.ecourts.gov.in/', 'National Judicial Data Grid'],
  ['high-court.svg', 'High Court arcade and clock scene', 'https://njdg.ecourts.gov.in/hcnjdg_v2/', 'High Courts NJDG'],
  ['district-court.svg', 'District courthouse and case-file scene', 'https://njdg.ecourts.gov.in/njdg_v3/', 'District Courts NJDG'],
];

async function loadSources(signal) {
  const indicators = [];
  let page = 1;
  let hasNextPage = true;
  while (hasNextPage) {
    const data = await api.indicators({ page_size: 100, page }, signal);
    indicators.push(...data.results);
    hasNextPage = Boolean(data.next);
    page += 1;
  }
  return indicators.filter(indicator => indicator.source_url || indicator.source);
}

function parseSourceUrl(value) {
  try {
    const url = new URL(value);
    return ['http:', 'https:'].includes(url.protocol) ? url : null;
  } catch (error) {
    if (error instanceof TypeError) return null;
    throw error;
  }
}

const External = ({ href, children }) => <a href={href} target="_blank" rel="noopener noreferrer">{children}</a>;

const LinkList = ({ items }) => (
  <ul>{items.map(([href, label]) => <li key={href}><External href={href}>{label}</External></li>)}</ul>
);

function CitationItem({ indicator }) {
  const sourceUrl = parseSourceUrl(indicator.source_url);
  const meta = [indicator.category, indicator.subgroup, indicator.frequency].filter(Boolean).join(' / ');
  return (
    <li className="citation-item">
      <strong>{indicator.title}</strong>
      {meta && <span>{meta}</span>}
      <Link className="citation-graph-link" to={`/indicator/${encodeURIComponent(indicator.key)}`}>View graph</Link>
      {sourceUrl ? (
        <a href={sourceUrl.href} target="_blank" rel="noopener noreferrer" title={indicator.source || sourceUrl.href}>
          {sourceUrl.hostname.replace(/^www\./, '')} · Open source ↗
        </a>
      ) : indicator.source_url && <span>{indicator.source_url}</span>}
      {indicator.source && indicator.source !== indicator.source_url && !sourceUrl && <span>{indicator.source}</span>}
    </li>
  );
}

export default function Sources() {
  useDocumentTitle('Sources');
  const sources = useAsync(loadSources, []);
  const [query, setQuery] = useState('');
  const search = useDebounced(query.trim().toLowerCase(), 200);
  const visible = useMemo(() => (sources.data || []).filter(item => (
    !search || `${item.title} ${item.subtitle} ${item.frequency} ${item.category} ${item.subgroup} ${item.source} ${item.source_url}`
      .toLowerCase().includes(search)
  )), [sources.data, search]);

  return (
    <>
      <section className="page-hero with-art sources-hero">
        <ArtBackdrop art={AMBIENT_ART} />
        <p className="eyebrow">Follow the evidence</p>
        <h1>Sources &amp; references</h1>
        <p className="lead">Browse the original sources behind the indicators. Search by title, topic, institution, or URL.</p>
      </section>

      <section className="section references" aria-label="Sources and references">
        <p className="references-intro">
          Every chart has a direct source link. For charts built from multiple inputs, open the graph’s note for the full provenance and method.
        </p>

        <details className="reference-panel" open>
          <summary>
            Chart citations{' '}
            {sources.data && <span className="reference-count">{sources.data.length.toLocaleString('en-IN')} graphs</span>}
          </summary>
          <label className="citation-search">
            Find an indicator, publisher or URL
            <input
              type="search"
              placeholder="Try World Bank, RBI, health, or a chart title"
              value={query}
              onChange={event => setQuery(event.target.value)}
            />
          </label>
          {sources.loading && <Loading label="Loading source directory…" />}
          {sources.error && <ErrorState error={sources.error} onRetry={sources.reload} />}
          {!sources.loading && !sources.error && (
            visible.length === 0
              ? <Empty>No sources match. Try a broader search.</Empty>
              : (
                <ul className="citation-list" aria-live="polite">
                  {visible.map(indicator => <CitationItem key={indicator.key} indicator={indicator} />)}
                </ul>
              )
          )}
        </details>

        <details className="reference-panel">
          <summary>Public data publishers, project references &amp; tools</summary>
          <div className="reference-columns">
            <div>
              <h3>Public data publishers</h3>
              <LinkList items={PUBLISHERS} />
            </div>
            <div>
              <h3>Project &amp; reading references</h3>
              <LinkList items={PROJECT_REFERENCES} />
              <h3>Interactive chart tools</h3>
              <LinkList items={CHART_TOOLS} />
            </div>
          </div>
        </details>

        <details className="reference-panel">
          <summary>Official sports data sources</summary>
          <p>Every Sports, Cricket, Hockey and Football chart, including the past-vs-current player records, is taken from the governing body, organiser or its official statistics partner below; no encyclopaedia or wiki pages are used. Snapshots are stored in <code>data/sports_sources/</code> and refreshed weekly by <code>scripts/refresh_sports_sources.py</code>.</p>
          <LinkList items={SPORTS_SOURCES} />
        </details>

        <details className="reference-panel">
          <summary>Original background illustrations</summary>
          <p className="muted">These are original vector illustrations created for this dashboard. Their subjects are visual interpretations, not official depictions.</p>
          <ul className="illustration-list">
            {ILLUSTRATIONS.map(([file, label, href, source]) => (
              <li key={file}>
                <a href={`${import.meta.env.BASE_URL}art/${file}`}>{label}</a> · <External href={href}>{source}</External>
              </li>
            ))}
          </ul>
        </details>
      </section>
      <Thanks />
    </>
  );
}
