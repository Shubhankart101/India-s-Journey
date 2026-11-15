import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { API_DOCS_URL, assetUrl, BACKUP_URL } from '../config.js';
import { useDocumentTitle } from '../hooks.js';
import './Api.css';

const ENDPOINTS = [
  { path: '/api/stats/', name: 'Statistics', desc: 'Read indicator, group and data-point totals.', method: 'GET' },
  { path: '/api/categories/', name: 'Groups & Subgroups', desc: 'Browse the 13 data groups and 138+ subgroups.', method: 'GET' },
  { path: '/api/indicators/', name: 'Indicators Catalogue', desc: 'Search, filter and paginate the indicator catalogue.', method: 'GET' },
  { path: '/api/compare/?keys=gdp_growth,inflation', name: 'Compare Series', desc: 'Align and compare multiple indicator time-series.', method: 'GET' },
  { path: '/api/articles/', name: 'Articles & Reports', desc: 'Browse public articles, essays and research writing.', method: 'GET' },
  { path: '/api/health/', name: 'System Health', desc: 'Check the API service and database connectivity.', method: 'GET' },
];

const staticApiUrl = new URL('api.html', BACKUP_URL).href;

export default function Api() {
  useDocumentTitle('API');
  const [activeTab, setActiveTab] = useState('swagger'); // 'swagger' | 'redoc' | 'schema' | 'index'
  const [schemaJson, setSchemaJson] = useState(null);
  const [schemaLoading, setSchemaLoading] = useState(true);
  const [schemaError, setSchemaError] = useState(null);
  const [copied, setCopied] = useState(false);
  const [filterText, setFilterText] = useState('');

  // Playground state
  const [selectedEndpoint, setSelectedEndpoint] = useState(ENDPOINTS[0]);
  const [playgroundLoading, setPlaygroundLoading] = useState(false);
  const [playgroundResponse, setPlaygroundResponse] = useState(null);
  const [playgroundLatency, setPlaygroundLatency] = useState(null);
  const [playgroundStatus, setPlaygroundStatus] = useState(null);

  const openApiUrl = assetUrl('api/openapi.json');

  useEffect(() => {
    let cancelled = false;
    async function loadOpenApi() {
      setSchemaLoading(true);
      try {
        let res = await fetch(openApiUrl).catch(() => null);
        if (!res || !res.ok) {
          res = await fetch('/api/schema/?format=json').catch(() => null);
        }
        if (!res || !res.ok) {
          res = await fetch(assetUrl('openapi.json')).catch(() => null);
        }
        if (res && res.ok) {
          const data = await res.json();
          if (!cancelled) {
            setSchemaJson(data);
            setSchemaLoading(false);
          }
          return;
        }
        throw new Error('Could not load OpenAPI schema');
      } catch (err) {
        if (!cancelled) {
          setSchemaError(err.message);
          setSchemaLoading(false);
        }
      }
    }
    loadOpenApi();
    return () => { cancelled = true; };
  }, [openApiUrl]);

  // Execute playground request
  const runPlayground = async (endpoint) => {
    setPlaygroundLoading(true);
    setPlaygroundResponse(null);
    const start = performance.now();
    try {
      let targetUrl = endpoint.path;
      let res = await fetch(targetUrl).catch(() => null);
      if (!res || !res.ok) {
        const clean = endpoint.path.replace(/^\/api\//, '').replace(/\/$/, '').split('?')[0];
        targetUrl = assetUrl(`api/${clean}.json`);
        res = await fetch(targetUrl).catch(() => null);
      }
      const duration = Math.round(performance.now() - start);
      setPlaygroundLatency(duration);
      if (res && res.ok) {
        const json = await res.json();
        setPlaygroundStatus(res.status);
        setPlaygroundResponse(json);
      } else {
        setPlaygroundStatus(res ? res.status : 503);
        setPlaygroundResponse({ error: 'Endpoint unreachable or returned error', status: res?.status });
      }
    } catch (e) {
      setPlaygroundStatus(500);
      setPlaygroundResponse({ error: e.message });
      setPlaygroundLatency(Math.round(performance.now() - start));
    } finally {
      setPlaygroundLoading(false);
    }
  };

  useEffect(() => {
    if (activeTab === 'index' && !playgroundResponse && !playgroundLoading) {
      runPlayground(selectedEndpoint);
    }
  }, [activeTab]);

  const handleCopy = () => {
    if (!schemaJson) return;
    navigator.clipboard.writeText(JSON.stringify(schemaJson, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const swaggerIframeSrcDoc = useMemo(() => {
    if (!schemaJson) return '';
    const safeSpec = JSON.stringify(schemaJson);
    return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>India's Journey Swagger UI</title>
  <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5.11.0/swagger-ui.css" />
  <style>
    body { margin: 0; background: #fafafa; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
    .swagger-ui .topbar { display: none; }
    .swagger-ui .info { margin: 25px 0; }
  </style>
</head>
<body>
  <div id="swagger-ui"></div>
  <script src="https://unpkg.com/swagger-ui-dist@5.11.0/swagger-ui-bundle.js"></script>
  <script src="https://unpkg.com/swagger-ui-dist@5.11.0/swagger-ui-standalone-preset.js"></script>
  <script>
    window.onload = function() {
      try {
        const spec = ${safeSpec};
        window.ui = SwaggerUIBundle({
          spec: spec,
          dom_id: '#swagger-ui',
          deepLinking: true,
          presets: [
            SwaggerUIBundle.presets.apis,
            SwaggerUIStandalonePreset
          ],
          layout: "BaseLayout"
        });
      } catch (e) {
        document.body.innerHTML = '<div style="padding: 24px; color: red;">Failed to render Swagger UI: ' + e.message + '</div>';
      }
    };
  </script>
</body>
</html>`;
  }, [schemaJson]);

  const redocIframeSrcDoc = useMemo(() => {
    if (!schemaJson) return '';
    const safeSpec = JSON.stringify(schemaJson);
    return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>India's Journey ReDoc</title>
  <style>
    body { margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
  </style>
</head>
<body>
  <div id="redoc-container"></div>
  <script src="https://cdn.redoc.ly/redoc/latest/bundles/redoc.standalone.js"></script>
  <script>
    try {
      const spec = ${safeSpec};
      Redoc.init(spec, {
        scrollYOffset: 20,
        hideDownloadButton: false,
        theme: {
          colors: { primary: { main: '#0284c7' } }
        }
      }, document.getElementById('redoc-container'));
    } catch (e) {
      document.body.innerHTML = '<div style="padding: 24px; color: red;">Failed to render ReDoc: ' + e.message + '</div>';
    }
  </script>
</body>
</html>`;
  }, [schemaJson]);

  const filteredSchemaString = useMemo(() => {
    if (!schemaJson) return '';
    if (!filterText) return JSON.stringify(schemaJson, null, 2);
    try {
      const filtered = {};
      const lowFilter = filterText.toLowerCase();
      if (schemaJson.info) filtered.info = schemaJson.info;
      if (schemaJson.paths) {
        filtered.paths = {};
        for (const [p, ops] of Object.entries(schemaJson.paths)) {
          if (p.toLowerCase().includes(lowFilter) || JSON.stringify(ops).toLowerCase().includes(lowFilter)) {
            filtered.paths[p] = ops;
          }
        }
      }
      return JSON.stringify(filtered, null, 2);
    } catch {
      return JSON.stringify(schemaJson, null, 2);
    }
  }, [schemaJson, filterText]);

  return (
    <main className="api-page">
      {/* Branded page header ensuring it feels like an authentic page */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '28px', paddingBottom: '16px', borderBottom: '1px solid var(--border-color)' }}>
        <Link to="/" className="brand" aria-label="India's Journey home" style={{ display: 'flex', alignItems: 'center', gap: '8px', textDecoration: 'none' }}>
          <span className="brand-emblem" aria-hidden="true">IJ</span>
          <span className="brand-stack">
            <span className="brand-text">India's Journey<span className="brand-dot" aria-hidden="true">.</span></span>
          </span>
        </Link>
        <div style={{ display: 'flex', gap: '10px' }}>
          <Link to="/" className="btn btn-ghost" style={{ fontSize: '0.85rem' }}>← Home</Link>
          <Link to="/explore" className="btn btn-primary" style={{ fontSize: '0.85rem' }}>Explore Data</Link>
        </div>
      </div>

      <section className="api-intro">
        <p className="eyebrow">Public data access</p>
        <h1>API &amp; endpoint explorer</h1>
        <p className="lead">
          Explore the read-only Django REST API, its schema and the static JSON resources published with the dashboard.
        </p>

        {/* 4 action buttons matching screenshot and testing expectations */}
        <div className="action-row api-tab-bar" role="tablist" aria-label="API Explorer Views">
          <a
            className={`btn ${activeTab === 'swagger' ? 'btn-primary' : 'btn-ghost'}`}
            href={API_DOCS_URL}
            onClick={e => { e.preventDefault(); setActiveTab('swagger'); }}
          >
            Open Swagger UI
          </a>
          <a
            className={`btn ${activeTab === 'redoc' ? 'btn-primary' : 'btn-ghost'}`}
            href="/api/redoc/"
            onClick={e => { e.preventDefault(); setActiveTab('redoc'); }}
          >
            ReDoc
          </a>
          <a
            className={`btn ${activeTab === 'schema' ? 'btn-primary' : 'btn-ghost'}`}
            href="/api/schema/?format=json"
            onClick={e => { e.preventDefault(); setActiveTab('schema'); }}
          >
            OpenAPI schema
          </a>
          <a
            className={`btn ${activeTab === 'index' ? 'btn-primary' : 'btn-ghost'}`}
            href="/api/"
            onClick={e => { e.preventDefault(); setActiveTab('index'); }}
          >
            API index
          </a>
        </div>
      </section>

      {/* Active Tab View */}
      <section className="api-viewer-card" aria-live="polite">
        {activeTab === 'swagger' && (
          <div>
            <div className="api-viewer-header">
              <div className="api-viewer-title">
                <span>⚡ Interactive Swagger UI</span>
                <span className="api-tab-badge">OpenAPI 3.0</span>
              </div>
              <div className="api-viewer-actions">
                <a className="btn btn-ghost" href={openApiUrl} target="_blank" rel="noopener noreferrer" download="openapi.json">
                  Download openapi.json
                </a>
              </div>
            </div>
            {schemaLoading ? (
              <div style={{ padding: '60px 24px', textAlign: 'center', color: 'var(--text-muted)' }}>
                Loading interactive OpenAPI specification…
              </div>
            ) : schemaError ? (
              <div style={{ padding: '40px 24px', color: '#f87171' }}>
                Error loading OpenAPI schema: {schemaError}. You can test endpoints in the API Index tab.
              </div>
            ) : (
              <iframe
                title="Swagger UI Explorer"
                className="api-frame"
                srcDoc={swaggerIframeSrcDoc}
                sandbox="allow-scripts allow-same-origin allow-popups"
              />
            )}
          </div>
        )}

        {activeTab === 'redoc' && (
          <div>
            <div className="api-viewer-header">
              <div className="api-viewer-title">
                <span>📖 ReDoc Comprehensive Reference</span>
                <span className="api-tab-badge">v3.0.3</span>
              </div>
              <div className="api-viewer-actions">
                <a className="btn btn-ghost" href={openApiUrl} target="_blank" rel="noopener noreferrer" download="openapi.json">
                  Download openapi.json
                </a>
              </div>
            </div>
            {schemaLoading ? (
              <div style={{ padding: '60px 24px', textAlign: 'center', color: 'var(--text-muted)' }}>
                Loading ReDoc documentation…
              </div>
            ) : (
              <iframe
                title="ReDoc API Documentation"
                className="api-frame"
                srcDoc={redocIframeSrcDoc}
                sandbox="allow-scripts allow-same-origin allow-popups"
              />
            )}
          </div>
        )}

        {activeTab === 'schema' && (
          <div>
            <div className="api-viewer-header">
              <div className="api-viewer-title">
                <span>📄 OpenAPI 3.0 Specification</span>
                <span className="api-tab-badge">JSON Format</span>
              </div>
              <div className="api-viewer-actions">
                <input
                  type="search"
                  placeholder="Filter paths..."
                  value={filterText}
                  onChange={e => setFilterText(e.target.value)}
                  style={{
                    padding: '6px 12px',
                    borderRadius: '8px',
                    border: '1px solid var(--border-color)',
                    background: 'var(--bg-card)',
                    color: 'inherit',
                    fontSize: '0.85rem',
                  }}
                />
                <button type="button" className="btn btn-ghost" onClick={handleCopy}>
                  {copied ? '✓ Copied' : 'Copy JSON'}
                </button>
                <a className="btn btn-primary" href={openApiUrl} target="_blank" rel="noopener noreferrer" download="openapi.json">
                  Download openapi.json
                </a>
              </div>
            </div>
            <div className="api-schema-container">
              {schemaLoading ? (
                <p style={{ color: 'var(--text-muted)' }}>Loading schema...</p>
              ) : (
                <pre className="api-schema-pre">{filteredSchemaString}</pre>
              )}
            </div>
          </div>
        )}

        {activeTab === 'index' && (
          <div>
            <div className="api-viewer-header">
              <div className="api-viewer-title">
                <span>🚀 Interactive API Playground &amp; Index</span>
                <span className="api-tab-badge">Live Endpoints</span>
              </div>
              <div className="api-viewer-actions">
                <span className="muted" style={{ fontSize: '0.85rem' }}>Select an endpoint to execute a real-time request</span>
              </div>
            </div>
            <div className="api-playground-grid">
              <div className="api-endpoints-sidebar">
                {ENDPOINTS.map(ep => (
                  <button
                    type="button"
                    key={ep.path}
                    className={`api-endpoint-item ${selectedEndpoint.path === ep.path ? 'selected' : ''}`}
                    onClick={() => {
                      setSelectedEndpoint(ep);
                      runPlayground(ep);
                    }}
                  >
                    <div className="api-endpoint-head">
                      <span className="api-method-badge">{ep.method}</span>
                      <span className="api-endpoint-path">{ep.path.split('?')[0]}</span>
                    </div>
                    <strong style={{ fontSize: '0.9rem', color: 'var(--text-color)' }}>{ep.name}</strong>
                    <p className="api-endpoint-desc">{ep.desc}</p>
                  </button>
                ))}
              </div>

              <div className="api-response-panel">
                <div className="api-response-header">
                  <div>
                    <span className="api-method-badge" style={{ marginRight: '8px' }}>{selectedEndpoint.method}</span>
                    <code style={{ fontSize: '0.95rem', fontWeight: 600 }}>{selectedEndpoint.path}</code>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    {playgroundStatus && (
                      <span className={`api-status-badge ${playgroundStatus >= 400 ? 'error' : ''}`}>
                        {playgroundStatus} {playgroundStatus === 200 ? 'OK' : 'Response'}
                      </span>
                    )}
                    {playgroundLatency !== null && (
                      <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{playgroundLatency} ms</span>
                    )}
                    <button
                      type="button"
                      className="btn btn-primary"
                      style={{ padding: '6px 14px', fontSize: '0.85rem' }}
                      disabled={playgroundLoading}
                      onClick={() => runPlayground(selectedEndpoint)}
                    >
                      {playgroundLoading ? 'Sending…' : 'Execute GET'}
                    </button>
                  </div>
                </div>

                <div className="api-response-body">
                  {playgroundLoading ? (
                    <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-muted)' }}>
                      Executing request to <code>{selectedEndpoint.path}</code>…
                    </div>
                  ) : playgroundResponse ? (
                    <pre className="api-response-pre">
                      {JSON.stringify(playgroundResponse, null, 2)}
                    </pre>
                  ) : (
                    <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-muted)' }}>
                      Click "Execute GET" to test this endpoint.
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}
      </section>

      {/* Static JSON API Section matching test assertions */}
      <section className="section">
        <h2>Static JSON API</h2>
        <p className="muted">
          The Netlify and GitHub Pages deployments publish read-only JSON data files with their own endpoint checks and Swagger explorer.
        </p>
        <a className="btn btn-ghost" href={staticApiUrl}>Open static JSON API explorer</a>
      </section>
    </main>
  );
}
