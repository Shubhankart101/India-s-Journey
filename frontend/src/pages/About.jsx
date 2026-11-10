import { Link } from 'react-router-dom';
import { marked } from 'marked';
import readme from '../../../README.md?raw';
import { api } from '../api.js';
import { formatDate } from '../format.js';
import { useAsync, useDocumentTitle } from '../hooks.js';
import ArtBackdrop from '../components/ArtBackdrop.jsx';
import { AMBIENT_ART } from '../art.js';

const README_HTML = marked.parse(readme)
  .replace(/\sid="([^"]+)"/g, ' id="readme-$1"')
  .replace(/href="#([^"]+)"/g, 'href="#readme-$1"')
  .replace(/href="(?!https?:|mailto:|#)([^"]+)"/g, 'href="https://github.com/Shubhankart101/India-s-Journey/blob/main/$1"');

function navigateReadmeAnchor(event) {
  const link = event.target.closest?.('a[href^="#readme-"]');
  const target = link && document.getElementById(link.hash.slice(1));
  if (!target || !event.currentTarget.contains(target)) return;
  event.preventDefault();
  target.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

export default function About() {
  useDocumentTitle('About');
  const stats = useAsync(signal => api.stats(signal), []);

  return (
    <>
      <section className="page-hero with-art">
        <ArtBackdrop art={AMBIENT_ART} />
        <p className="eyebrow">About the atlas</p>
        <h1>Understand the data, <span className="gradient-text">not just the line.</span></h1>
        {stats.data && (
          <p className="muted">
            {stats.data.indicators.toLocaleString('en-IN')} indicators · {stats.data.subgroups} subgroups · last refresh {formatDate(stats.data.last_refresh) || 'pending'}
          </p>
        )}
      </section>

      <section className="section two-col" id="about">
        <div>
          <span className="eyebrow">The idea behind the atlas</span>
          <h2>Big change is easier to see, one signal at a time.</h2>
          <p>India’s story isn’t a single headline or a single number. This independent, public-data project brings together long-run indicators and current snapshots so you can explore what changed, when it changed, and how the evidence is measured.</p>
          <p>Start with a theme, search for an indicator and narrow the period. Hover for exact values, zoom into a moment, or open any chart for the full series, notes and cited source. Every chart keeps its frequency and limitations visible; unavailable data is never filled with an estimate.</p>
        </div>
        <div>
          <span className="eyebrow">Reading the numbers</span>
          <h2>How numbers are shown</h2>
          <p>Values in U.S. dollars use the international system (thousand, million, billion). Everything else uses the Indian system (lakh, crore).</p>
          <p>Pie charts show the largest eleven slices and fold the rest into “Other”. Additive categorical charts can switch between pie and bar views.</p>
        </div>
      </section>

      <section className="section">
        <span className="eyebrow">Evidence before inference</span>
        <h2>Public data. Clear provenance.</h2>
        <p className="muted">Each graph links to its underlying source and explains its unit and cadence. Some indicators are annual, some are survey snapshots, and some are assembled from official tables. Read the chart note before comparing unlike measures.</p>
        <div className="about-steps">
          <div className="card about-step"><span className="eyebrow">1 · Choose</span><strong>Pick a group.</strong><span className="muted">Eleven groups cover the economy, industry, health, environment, agriculture, security, elections and more. Each has subgroups.</span></div>
          <div className="card about-step"><span className="eyebrow">2 · Inspect</span><strong>Hover, zoom, switch.</strong><span className="muted">Hover for exact values, zoom in, and switch between line, bar and pie views where the data allows.</span></div>
          <div className="card about-step"><span className="eyebrow">3 · Verify</span><strong>Open the source.</strong><span className="muted">Open any chart for the full series, the method and the cited publisher behind each indicator.</span></div>
        </div>
      </section>

      <section className="section two-col">
        <div>
          <h2>Using the data</h2>
          <p>Every indicator has its own page with a CSV and JSON download. The same data is available from the <a href="/api">API explorer</a>.</p>
          <p>Compare indicators side by side without an account.</p>
          <p>The complete project README is included below.</p>
          <p>Browse the complete article collection in its own window.</p>
          <Link className="btn btn-primary" to="/articles" target="_blank" rel="noopener noreferrer">Open articles <span aria-hidden="true">↗</span></Link>
        </div>
      </section>

      <section className="section about-readme" id="project-readme" onClick={navigateReadmeAnchor}>
        <h2>Project README</h2>
        <div dangerouslySetInnerHTML={{ __html: README_HTML }} />
      </section>

      <section className="section" id="pew-research">
        <span className="eyebrow">Pew Research indices</span>
        <h2>Browse the Pew collections</h2>
        <p className="muted">The Pew indicators are grouped under People, Health &amp; Society. Open either subgroup to see its indices and survey snapshots.</p>
        <p><Link to="/explore/people-health-society/pew-research-public-opinion-on-india">Public opinion on India</Link></p>
        <p><Link to="/explore/people-health-society/pew-research-reports-survey-snapshots">Reports and survey snapshots</Link></p>
      </section>

    </>
  );
}
