import { API_DOCS_URL, BACKUP_URL } from '../config.js';
import { useDocumentTitle } from '../hooks.js';
import ThemeSelect from '../components/ThemeSelect.jsx';

const ENDPOINTS = [
  ['/api/health/', 'Health', 'Check the API service and catalogue status.'],
  ['/api/stats/', 'Statistics', 'Read indicator, group and data-point totals.'],
  ['/api/categories/', 'Groups', 'Browse the data groups and subgroups.'],
  ['/api/indicators/', 'Indicators', 'Search, filter and paginate the chart catalogue.'],
  ['/api/compare/?keys=gdp_growth,inflation', 'Compare', 'Align up to four indicator series.'],
  ['/api/articles/', 'Articles', 'Browse public articles and reports.'],
];

const staticApiUrl = new URL('api.html', BACKUP_URL).href;

export default function Api() {
  useDocumentTitle('API');

  return (
    <main className="api-page">
      <ThemeSelect className="theme-select-floating" />
      <section className="api-intro">
        <p className="eyebrow">Public data access</p>
        <h1>API &amp; endpoint explorer</h1>
        <p className="lead">Explore the read-only Django REST API, its schema and the static JSON resources published with the dashboard.</p>
        <div className="action-row">
          <a className="btn btn-primary" href={API_DOCS_URL}>Open Swagger UI</a>
          <a className="btn btn-ghost" href="/api/redoc/">ReDoc</a>
          <a className="btn btn-ghost" href="/api/schema/?format=json">OpenAPI schema</a>
          <a className="btn btn-ghost" href="/api/">API index</a>
        </div>
      </section>

      <section className="section" aria-labelledby="public-endpoints-title">
        <h2 id="public-endpoints-title">Public endpoints</h2>
        <div className="card-grid">
          {ENDPOINTS.map(([href, title, description]) => (
            <a className="card api-endpoint" href={href} key={href}>
              <span className="eyebrow">GET</span>
              <h3>{title}</h3>
              <code>{href}</code>
              <p className="muted">{description}</p>
            </a>
          ))}
        </div>
      </section>

      <section className="section">
        <h2>Static JSON API</h2>
        <p className="muted">The Netlify and GitHub Pages deployments publish read-only JSON data files with their own endpoint checks and Swagger explorer.</p>
        <a className="btn btn-ghost" href={staticApiUrl}>Open static JSON API explorer</a>
      </section>
    </main>
  );
}
