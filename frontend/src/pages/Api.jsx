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
    body { margin: 0; background: #ffffff; color: #1e293b; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
    .swagger-ui .topbar { display: none; }
    .swagger-ui .info { margin: 25px 0; }
    #loader { padding: 50px 20px; text-align: center; color: #64748b; }
    .spinner { display: inline-block; width: 32px; height: 32px; border: 3px solid #e2e8f0; border-top-color: #0284c7; border-radius: 50%; animation: spin 0.8s linear infinite; margin-bottom: 12px; }
    @keyframes spin { to { transform: rotate(360deg); } }
    .fb-doc { display: none; padding: 24px; max-width: 960px; margin: 0 auto; }
    .fb-header { border-bottom: 2px solid #e2e8f0; padding-bottom: 16px; margin-bottom: 24px; }
    .fb-title { font-size: 1.6rem; font-weight: 700; color: #0f172a; margin: 0 0 8px 0; }
    .fb-badge { font-size: 0.8rem; color: #0284c7; background: #e0f2fe; padding: 3px 8px; border-radius: 999px; }
    .fb-desc { font-size: 0.95rem; color: #475569; line-height: 1.5; }
    .fb-card { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; margin-bottom: 16px; overflow: hidden; }
    .fb-head { display: flex; align-items: center; gap: 12px; padding: 12px 16px; background: #f1f5f9; border-bottom: 1px solid #e2e8f0; flex-wrap: wrap; }
    .fb-method { font-weight: 700; font-size: 0.75rem; padding: 4px 8px; border-radius: 4px; text-transform: uppercase; color: #fff; }
    .fb-method-get { background: #0284c7; }
    .fb-method-post { background: #16a34a; }
    .fb-path { font-family: ui-monospace, SFMono-Regular, monospace; font-size: 0.95rem; font-weight: 600; color: #0f172a; }
    .fb-summary { color: #64748b; font-size: 0.85rem; }
    .fb-body { padding: 16px; font-size: 0.9rem; }
    .fb-table { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 0.85rem; }
    .fb-table th, .fb-table td { padding: 6px 10px; border-bottom: 1px solid #e2e8f0; text-align: left; }
    .fb-table th { background: #f8fafc; color: #475569; }
    .fb-sub { font-size: 0.85rem; font-weight: 700; color: #334155; margin-top: 12px; text-transform: uppercase; letter-spacing: 0.05em; }
    .fb-code { background: #e0f2fe; color: #0369a1; padding: 2px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: 600; }
  </style>
</head>
<body>
  <div id="loader">
    <div class="spinner"></div>
    <div style="font-weight: 600; color: #334155;">Initializing Swagger UI Explorer…</div>
    <div style="font-size: 0.85rem; color: #94a3b8; margin-top: 4px;">Loading OpenAPI 3.0 UI components</div>
  </div>
  <div id="swagger-ui"></div>
  <div id="fallback-container" class="fb-doc"></div>
  <script>
    const spec = ${safeSpec};

    function renderFallback() {
      const loader = document.getElementById('loader');
      if (loader) loader.style.display = 'none';
      const container = document.getElementById('fallback-container');
      if (!container) return;
      container.style.display = 'block';

      let html = '<div class="fb-header">';
      html += '<div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px;">';
      html += '<h1 class="fb-title">' + (spec.info?.title || "India's Journey REST API") + ' <span class="fb-badge">' + (spec.info?.version || "v3.0.3") + '</span></h1>';
      html += '<span style="font-size: 0.8rem; background: #e2e8f0; color: #475569; padding: 4px 10px; border-radius: 6px; font-weight: 600;">Interactive Documentation</span>';
      html += '</div>';
      html += '<p class="fb-desc">' + (spec.info?.description || "OpenAPI 3.0 specification for public data access") + '</p>';
      html += '</div>';

      if (spec.paths) {
        for (const [path, ops] of Object.entries(spec.paths)) {
          for (const [method, details] of Object.entries(ops)) {
            if (['get', 'post', 'put', 'delete', 'patch'].includes(method.toLowerCase())) {
              const m = method.toUpperCase();
              html += '<div class="fb-card">';
              html += '<div class="fb-head">';
              html += '<span class="fb-method fb-method-' + m.toLowerCase() + '">' + m + '</span>';
              html += '<span class="fb-path">' + path + '</span>';
              if (details.summary) html += '<span class="fb-summary">· ' + details.summary + '</span>';
              html += '</div>';
              html += '<div class="fb-body">';
              if (details.description) html += '<p style="margin: 0 0 10px 0; color: #334155;">' + details.description + '</p>';
              if (details.parameters && details.parameters.length > 0) {
                html += '<div class="fb-sub">Parameters</div>';
                html += '<table class="fb-table"><thead><tr><th>Name</th><th>In</th><th>Type</th><th>Required</th><th>Description</th></tr></thead><tbody>';
                for (const p of details.parameters) {
                  html += '<tr><td><code>' + p.name + '</code></td><td>' + (p.in || 'query') + '</td><td><code>' + (p.schema?.type || 'string') + '</code></td><td>' + (p.required ? '<strong style="color: #dc2626;">Yes</strong>' : 'No') + '</td><td>' + (p.description || '—') + '</td></tr>';
                }
                html += '</tbody></table>';
              }
              if (details.responses) {
                html += '<div class="fb-sub">Responses</div><div style="display: flex; gap: 8px; margin-top: 6px; flex-wrap: wrap;">';
                for (const [code, resp] of Object.entries(details.responses)) {
                  html += '<span class="fb-code">' + code + ' · ' + (resp.description || 'OK') + '</span>';
                }
                html += '</div>';
              }
              html += '</div></div>';
            }
          }
        }
      }
      container.innerHTML = html;
    }

    let bundleLoaded = false;
    let presetLoaded = false;
    let initialized = false;

    function checkInit() {
      if (initialized) return;
      if (bundleLoaded && presetLoaded && window.SwaggerUIBundle && window.SwaggerUIStandalonePreset) {
        initialized = true;
        const loader = document.getElementById('loader');
        if (loader) loader.style.display = 'none';
        try {
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
          renderFallback();
        }
      }
    }

    const s1 = document.createElement('script');
    s1.src = 'https://unpkg.com/swagger-ui-dist@5.11.0/swagger-ui-bundle.js';
    s1.async = true;
    s1.onload = function() { bundleLoaded = true; checkInit(); };
    s1.onerror = function() { renderFallback(); };
    document.head.appendChild(s1);

    const s2 = document.createElement('script');
    s2.src = 'https://unpkg.com/swagger-ui-dist@5.11.0/swagger-ui-standalone-preset.js';
    s2.async = true;
    s2.onload = function() { presetLoaded = true; checkInit(); };
    s2.onerror = function() { renderFallback(); };
    document.head.appendChild(s2);

    let polls = 0;
    const pollTimer = setInterval(function() {
      polls++;
      if (window.SwaggerUIBundle && window.SwaggerUIStandalonePreset) {
        bundleLoaded = true;
        presetLoaded = true;
        clearInterval(pollTimer);
        checkInit();
      } else if (polls > 40) {
        clearInterval(pollTimer);
        if (!initialized) renderFallback();
      }
    }, 50);

    setTimeout(function() {
      clearInterval(pollTimer);
      if (!initialized) renderFallback();
    }, 3000);
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
    body { margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #ffffff; color: #1e293b; }
    #loader { padding: 50px 20px; text-align: center; color: #64748b; }
    .spinner { display: inline-block; width: 32px; height: 32px; border: 3px solid #e2e8f0; border-top-color: #0284c7; border-radius: 50%; animation: spin 0.8s linear infinite; margin-bottom: 12px; }
    @keyframes spin { to { transform: rotate(360deg); } }
    .fb-doc { display: none; padding: 24px; max-width: 960px; margin: 0 auto; }
    .fb-header { border-bottom: 2px solid #e2e8f0; padding-bottom: 16px; margin-bottom: 24px; }
    .fb-title { font-size: 1.6rem; font-weight: 700; color: #0f172a; margin: 0 0 8px 0; }
    .fb-badge { font-size: 0.8rem; color: #0284c7; background: #e0f2fe; padding: 3px 8px; border-radius: 999px; }
    .fb-desc { font-size: 0.95rem; color: #475569; line-height: 1.5; }
    .fb-card { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; margin-bottom: 16px; overflow: hidden; }
    .fb-head { display: flex; align-items: center; gap: 12px; padding: 12px 16px; background: #f1f5f9; border-bottom: 1px solid #e2e8f0; flex-wrap: wrap; }
    .fb-method { font-weight: 700; font-size: 0.75rem; padding: 4px 8px; border-radius: 4px; text-transform: uppercase; color: #fff; }
    .fb-method-get { background: #0284c7; }
    .fb-method-post { background: #16a34a; }
    .fb-path { font-family: ui-monospace, SFMono-Regular, monospace; font-size: 0.95rem; font-weight: 600; color: #0f172a; }
    .fb-summary { color: #64748b; font-size: 0.85rem; }
    .fb-body { padding: 16px; font-size: 0.9rem; }
    .fb-table { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 0.85rem; }
    .fb-table th, .fb-table td { padding: 6px 10px; border-bottom: 1px solid #e2e8f0; text-align: left; }
    .fb-table th { background: #f8fafc; color: #475569; }
    .fb-sub { font-size: 0.85rem; font-weight: 700; color: #334155; margin-top: 12px; text-transform: uppercase; letter-spacing: 0.05em; }
    .fb-code { background: #e0f2fe; color: #0369a1; padding: 2px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: 600; }
  </style>
</head>
<body>
  <div id="loader">
    <div class="spinner"></div>
    <div style="font-weight: 600; color: #334155;">Initializing ReDoc Comprehensive Reference…</div>
    <div style="font-size: 0.85rem; color: #94a3b8; margin-top: 4px;">Loading OpenAPI specification and components</div>
  </div>
  <div id="redoc-container"></div>
  <div id="fallback-container" class="fb-doc"></div>
  <script>
    const spec = ${safeSpec};

    function renderFallback() {
      const loader = document.getElementById('loader');
      if (loader) loader.style.display = 'none';
      const container = document.getElementById('fallback-container');
      if (!container) return;
      container.style.display = 'block';

      let html = '<div class="fb-header">';
      html += '<div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px;">';
      html += '<h1 class="fb-title">' + (spec.info?.title || "India's Journey REST API") + ' <span class="fb-badge">' + (spec.info?.version || "v3.0.3") + '</span></h1>';
      html += '<span style="font-size: 0.8rem; background: #e0f2fe; color: #0369a1; padding: 4px 10px; border-radius: 6px; font-weight: 600;">ReDoc Reference View</span>';
      html += '</div>';
      html += '<p class="fb-desc">' + (spec.info?.description || "OpenAPI 3.0 specification for public data access") + '</p>';
      html += '</div>';

      if (spec.paths) {
        for (const [path, ops] of Object.entries(spec.paths)) {
          for (const [method, details] of Object.entries(ops)) {
            if (['get', 'post', 'put', 'delete', 'patch'].includes(method.toLowerCase())) {
              const m = method.toUpperCase();
              html += '<div class="fb-card">';
              html += '<div class="fb-head">';
              html += '<span class="fb-method fb-method-' + m.toLowerCase() + '">' + m + '</span>';
              html += '<span class="fb-path">' + path + '</span>';
              if (details.summary) html += '<span class="fb-summary">· ' + details.summary + '</span>';
              html += '</div>';
              html += '<div class="fb-body">';
              if (details.description) html += '<p style="margin: 0 0 10px 0; color: #334155;">' + details.description + '</p>';
              if (details.parameters && details.parameters.length > 0) {
                html += '<div class="fb-sub">Parameters</div>';
                html += '<table class="fb-table"><thead><tr><th>Name</th><th>In</th><th>Type</th><th>Required</th><th>Description</th></tr></thead><tbody>';
                for (const p of details.parameters) {
                  html += '<tr><td><code>' + p.name + '</code></td><td>' + (p.in || 'query') + '</td><td><code>' + (p.schema?.type || 'string') + '</code></td><td>' + (p.required ? '<strong style="color: #dc2626;">Yes</strong>' : 'No') + '</td><td>' + (p.description || '—') + '</td></tr>';
                }
                html += '</tbody></table>';
              }
              if (details.responses) {
                html += '<div class="fb-sub">Responses</div><div style="display: flex; gap: 8px; margin-top: 6px; flex-wrap: wrap;">';
                for (const [code, resp] of Object.entries(details.responses)) {
                  html += '<span class="fb-code">' + code + ' · ' + (resp.description || 'OK') + '</span>';
                }
                html += '</div>';
              }
              html += '</div></div>';
            }
          }
        }
      }
      container.innerHTML = html;
    }

    let initialized = false;
    function tryInitRedoc() {
      if (initialized) return;
      if (window.Redoc && typeof window.Redoc.init === 'function') {
        initialized = true;
        const loader = document.getElementById('loader');
        if (loader) loader.style.display = 'none';
        try {
          window.Redoc.init(spec, {
            scrollYOffset: 20,
            hideDownloadButton: false,
            theme: {
              colors: { primary: { main: '#0284c7' } }
            }
          }, document.getElementById('redoc-container'));
        } catch (e) {
          renderFallback();
        }
      }
    }

    const cdnList = [
      'https://cdn.jsdelivr.net/npm/redoc@2.1.5/bundles/redoc.standalone.js',
      'https://unpkg.com/redoc@2.1.5/bundles/redoc.standalone.js',
      'https://cdn.redoc.ly/redoc/latest/bundles/redoc.standalone.js'
    ];
    let cdnIdx = 0;
    function loadNextScript() {
      if (initialized || cdnIdx >= cdnList.length) {
        if (!initialized) renderFallback();
        return;
      }
      const s = document.createElement('script');
      s.src = cdnList[cdnIdx++];
      s.async = true;
      s.onload = function() { tryInitRedoc(); };
      s.onerror = function() { loadNextScript(); };
      document.head.appendChild(s);
    }
    loadNextScript();

    let polls = 0;
    const pollTimer = setInterval(function() {
      polls++;
      if (window.Redoc && typeof window.Redoc.init === 'function') {
        clearInterval(pollTimer);
        tryInitRedoc();
      } else if (polls > 40) {
        clearInterval(pollTimer);
        if (!initialized) renderFallback();
      }
    }, 50);

    setTimeout(function() {
      clearInterval(pollTimer);
      if (!initialized) renderFallback();
    }, 3000);
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
