import{r as e}from"./rolldown-runtime-XKyaHtl9.js";import{_ as t,g as n}from"./charts-B6pdgxOd.js";import{r}from"./vendor-CMZuCPfa.js";import{o as i,r as a,t as o}from"./config-uet0De6j.js";import{L as s}from"./index-QCMR0hJo.js";var c=e(t(),1),l=n(),u=[{path:`/api/stats/`,name:`Statistics`,desc:`Read indicator, group and data-point totals.`,method:`GET`},{path:`/api/categories/`,name:`Groups & Subgroups`,desc:`Browse the 13 data groups and 138+ subgroups.`,method:`GET`},{path:`/api/indicators/`,name:`Indicators Catalogue`,desc:`Search, filter and paginate the indicator catalogue.`,method:`GET`},{path:`/api/compare/?keys=gdp_growth,inflation`,name:`Compare Series`,desc:`Align and compare multiple indicator time-series.`,method:`GET`},{path:`/api/articles/`,name:`Articles & Reports`,desc:`Browse public articles, essays and research writing.`,method:`GET`},{path:`/api/health/`,name:`System Health`,desc:`Check the API service and database connectivity.`,method:`GET`}],d=new URL(`api.html`,a).href;function f(){s(`API`);let[e,t]=(0,c.useState)(`swagger`),[n,a]=(0,c.useState)(null),[f,p]=(0,c.useState)(!0),[m,h]=(0,c.useState)(null),[g,_]=(0,c.useState)(!1),[v,y]=(0,c.useState)(``),[b,x]=(0,c.useState)(u[0]),[S,C]=(0,c.useState)(!1),[w,T]=(0,c.useState)(null),[E,D]=(0,c.useState)(null),[O,k]=(0,c.useState)(null),A=i(`api/openapi.json`);(0,c.useEffect)(()=>{let e=!1;async function t(){p(!0);try{let t=await fetch(A).catch(()=>null);if(t&&t.ok||(t=await fetch(`/api/schema/?format=json`).catch(()=>null)),t&&t.ok||(t=await fetch(i(`openapi.json`)).catch(()=>null)),t&&t.ok){let n=await t.json();e||(a(n),p(!1));return}throw Error(`Could not load OpenAPI schema`)}catch(t){e||(h(t.message),p(!1))}}return t(),()=>{e=!0}},[A]);let j=async e=>{C(!0),T(null);let t=performance.now();try{let n=e.path,r=await fetch(n).catch(()=>null);if(!r||!r.ok){let t=e.path.replace(/^\/api\//,``).replace(/\/$/,``).split(`?`)[0];n=i(`api/${t}.json`),r=await fetch(n).catch(()=>null)}let a=Math.round(performance.now()-t);if(D(a),r&&r.ok){let e=await r.json();k(r.status),T(e)}else k(r?r.status:503),T({error:`Endpoint unreachable or returned error`,status:r?.status})}catch(e){k(500),T({error:e.message}),D(Math.round(performance.now()-t))}finally{C(!1)}};(0,c.useEffect)(()=>{e===`index`&&!w&&!S&&j(b)},[e]);let M=()=>{n&&(navigator.clipboard.writeText(JSON.stringify(n,null,2)),_(!0),setTimeout(()=>_(!1),2e3))},N=(0,c.useMemo)(()=>n?`<!DOCTYPE html>
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
    const spec = ${JSON.stringify(n)};

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
  <\/script>
</body>
</html>`:``,[n]),P=(0,c.useMemo)(()=>n?`<!DOCTYPE html>
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
    const spec = ${JSON.stringify(n)};

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

    const script = document.createElement('script');
    script.src = 'https://cdn.redoc.ly/redoc/latest/bundles/redoc.standalone.js';
    script.async = true;
    script.onload = function() {
      tryInitRedoc();
    };
    script.onerror = function() {
      renderFallback();
    };
    document.head.appendChild(script);

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
  <\/script>
</body>
</html>`:``,[n]),F=(0,c.useMemo)(()=>{if(!n)return``;if(!v)return JSON.stringify(n,null,2);try{let e={},t=v.toLowerCase();if(n.info&&(e.info=n.info),n.paths){e.paths={};for(let[r,i]of Object.entries(n.paths))(r.toLowerCase().includes(t)||JSON.stringify(i).toLowerCase().includes(t))&&(e.paths[r]=i)}return JSON.stringify(e,null,2)}catch{return JSON.stringify(n,null,2)}},[n,v]);return(0,l.jsxs)(`main`,{className:`api-page`,children:[(0,l.jsxs)(`div`,{style:{display:`flex`,alignItems:`center`,justifyContent:`space-between`,marginBottom:`28px`,paddingBottom:`16px`,borderBottom:`1px solid var(--border-color)`},children:[(0,l.jsxs)(r,{to:`/`,className:`brand`,"aria-label":`India's Journey home`,style:{display:`flex`,alignItems:`center`,gap:`8px`,textDecoration:`none`},children:[(0,l.jsx)(`span`,{className:`brand-emblem`,"aria-hidden":`true`,children:`IJ`}),(0,l.jsx)(`span`,{className:`brand-stack`,children:(0,l.jsxs)(`span`,{className:`brand-text`,children:[`India's Journey`,(0,l.jsx)(`span`,{className:`brand-dot`,"aria-hidden":`true`,children:`.`})]})})]}),(0,l.jsxs)(`div`,{style:{display:`flex`,gap:`10px`},children:[(0,l.jsx)(r,{to:`/`,className:`btn btn-ghost`,style:{fontSize:`0.85rem`},children:`← Home`}),(0,l.jsx)(r,{to:`/explore`,className:`btn btn-primary`,style:{fontSize:`0.85rem`},children:`Explore Data`})]})]}),(0,l.jsxs)(`section`,{className:`api-intro`,children:[(0,l.jsx)(`p`,{className:`eyebrow`,children:`Public data access`}),(0,l.jsx)(`h1`,{children:`API & endpoint explorer`}),(0,l.jsx)(`p`,{className:`lead`,children:`Explore the read-only Django REST API, its schema and the static JSON resources published with the dashboard.`}),(0,l.jsxs)(`div`,{className:`action-row api-tab-bar`,role:`tablist`,"aria-label":`API Explorer Views`,children:[(0,l.jsx)(`a`,{className:`btn ${e===`swagger`?`btn-primary`:`btn-ghost`}`,href:o,onClick:e=>{e.preventDefault(),t(`swagger`)},children:`Open Swagger UI`}),(0,l.jsx)(`a`,{className:`btn ${e===`redoc`?`btn-primary`:`btn-ghost`}`,href:`/api/redoc/`,onClick:e=>{e.preventDefault(),t(`redoc`)},children:`ReDoc`}),(0,l.jsx)(`a`,{className:`btn ${e===`schema`?`btn-primary`:`btn-ghost`}`,href:`/api/schema/?format=json`,onClick:e=>{e.preventDefault(),t(`schema`)},children:`OpenAPI schema`}),(0,l.jsx)(`a`,{className:`btn ${e===`index`?`btn-primary`:`btn-ghost`}`,href:`/api/`,onClick:e=>{e.preventDefault(),t(`index`)},children:`API index`})]})]}),(0,l.jsxs)(`section`,{className:`api-viewer-card`,"aria-live":`polite`,children:[e===`swagger`&&(0,l.jsxs)(`div`,{children:[(0,l.jsxs)(`div`,{className:`api-viewer-header`,children:[(0,l.jsxs)(`div`,{className:`api-viewer-title`,children:[(0,l.jsx)(`span`,{children:`⚡ Interactive Swagger UI`}),(0,l.jsx)(`span`,{className:`api-tab-badge`,children:`OpenAPI 3.0`})]}),(0,l.jsx)(`div`,{className:`api-viewer-actions`,children:(0,l.jsx)(`a`,{className:`btn btn-ghost`,href:A,target:`_blank`,rel:`noopener noreferrer`,download:`openapi.json`,children:`Download openapi.json`})})]}),f?(0,l.jsx)(`div`,{style:{padding:`60px 24px`,textAlign:`center`,color:`var(--text-muted)`},children:`Loading interactive OpenAPI specification…`}):m?(0,l.jsxs)(`div`,{style:{padding:`40px 24px`,color:`#f87171`},children:[`Error loading OpenAPI schema: `,m,`. You can test endpoints in the API Index tab.`]}):(0,l.jsx)(`iframe`,{title:`Swagger UI Explorer`,className:`api-frame`,srcDoc:N,sandbox:`allow-scripts allow-same-origin allow-popups`})]}),e===`redoc`&&(0,l.jsxs)(`div`,{children:[(0,l.jsxs)(`div`,{className:`api-viewer-header`,children:[(0,l.jsxs)(`div`,{className:`api-viewer-title`,children:[(0,l.jsx)(`span`,{children:`📖 ReDoc Comprehensive Reference`}),(0,l.jsx)(`span`,{className:`api-tab-badge`,children:`v3.0.3`})]}),(0,l.jsx)(`div`,{className:`api-viewer-actions`,children:(0,l.jsx)(`a`,{className:`btn btn-ghost`,href:A,target:`_blank`,rel:`noopener noreferrer`,download:`openapi.json`,children:`Download openapi.json`})})]}),f?(0,l.jsx)(`div`,{style:{padding:`60px 24px`,textAlign:`center`,color:`var(--text-muted)`},children:`Loading ReDoc documentation…`}):(0,l.jsx)(`iframe`,{title:`ReDoc API Documentation`,className:`api-frame`,srcDoc:P,sandbox:`allow-scripts allow-same-origin allow-popups`})]}),e===`schema`&&(0,l.jsxs)(`div`,{children:[(0,l.jsxs)(`div`,{className:`api-viewer-header`,children:[(0,l.jsxs)(`div`,{className:`api-viewer-title`,children:[(0,l.jsx)(`span`,{children:`📄 OpenAPI 3.0 Specification`}),(0,l.jsx)(`span`,{className:`api-tab-badge`,children:`JSON Format`})]}),(0,l.jsxs)(`div`,{className:`api-viewer-actions`,children:[(0,l.jsx)(`input`,{type:`search`,placeholder:`Filter paths...`,value:v,onChange:e=>y(e.target.value),style:{padding:`6px 12px`,borderRadius:`8px`,border:`1px solid var(--border-color)`,background:`var(--bg-card)`,color:`inherit`,fontSize:`0.85rem`}}),(0,l.jsx)(`button`,{type:`button`,className:`btn btn-ghost`,onClick:M,children:g?`✓ Copied`:`Copy JSON`}),(0,l.jsx)(`a`,{className:`btn btn-primary`,href:A,target:`_blank`,rel:`noopener noreferrer`,download:`openapi.json`,children:`Download openapi.json`})]})]}),(0,l.jsx)(`div`,{className:`api-schema-container`,children:f?(0,l.jsx)(`p`,{style:{color:`var(--text-muted)`},children:`Loading schema...`}):(0,l.jsx)(`pre`,{className:`api-schema-pre`,children:F})})]}),e===`index`&&(0,l.jsxs)(`div`,{children:[(0,l.jsxs)(`div`,{className:`api-viewer-header`,children:[(0,l.jsxs)(`div`,{className:`api-viewer-title`,children:[(0,l.jsx)(`span`,{children:`🚀 Interactive API Playground & Index`}),(0,l.jsx)(`span`,{className:`api-tab-badge`,children:`Live Endpoints`})]}),(0,l.jsx)(`div`,{className:`api-viewer-actions`,children:(0,l.jsx)(`span`,{className:`muted`,style:{fontSize:`0.85rem`},children:`Select an endpoint to execute a real-time request`})})]}),(0,l.jsxs)(`div`,{className:`api-playground-grid`,children:[(0,l.jsx)(`div`,{className:`api-endpoints-sidebar`,children:u.map(e=>(0,l.jsxs)(`button`,{type:`button`,className:`api-endpoint-item ${b.path===e.path?`selected`:``}`,onClick:()=>{x(e),j(e)},children:[(0,l.jsxs)(`div`,{className:`api-endpoint-head`,children:[(0,l.jsx)(`span`,{className:`api-method-badge`,children:e.method}),(0,l.jsx)(`span`,{className:`api-endpoint-path`,children:e.path.split(`?`)[0]})]}),(0,l.jsx)(`strong`,{style:{fontSize:`0.9rem`,color:`var(--text-color)`},children:e.name}),(0,l.jsx)(`p`,{className:`api-endpoint-desc`,children:e.desc})]},e.path))}),(0,l.jsxs)(`div`,{className:`api-response-panel`,children:[(0,l.jsxs)(`div`,{className:`api-response-header`,children:[(0,l.jsxs)(`div`,{children:[(0,l.jsx)(`span`,{className:`api-method-badge`,style:{marginRight:`8px`},children:b.method}),(0,l.jsx)(`code`,{style:{fontSize:`0.95rem`,fontWeight:600},children:b.path})]}),(0,l.jsxs)(`div`,{style:{display:`flex`,alignItems:`center`,gap:`10px`},children:[O&&(0,l.jsxs)(`span`,{className:`api-status-badge ${O>=400?`error`:``}`,children:[O,` `,O===200?`OK`:`Response`]}),E!==null&&(0,l.jsxs)(`span`,{style:{fontSize:`0.8rem`,color:`var(--text-muted)`},children:[E,` ms`]}),(0,l.jsx)(`button`,{type:`button`,className:`btn btn-primary`,style:{padding:`6px 14px`,fontSize:`0.85rem`},disabled:S,onClick:()=>j(b),children:S?`Sending…`:`Execute GET`})]})]}),(0,l.jsx)(`div`,{className:`api-response-body`,children:S?(0,l.jsxs)(`div`,{style:{padding:`40px`,textAlign:`center`,color:`var(--text-muted)`},children:[`Executing request to `,(0,l.jsx)(`code`,{children:b.path}),`…`]}):w?(0,l.jsx)(`pre`,{className:`api-response-pre`,children:JSON.stringify(w,null,2)}):(0,l.jsx)(`div`,{style:{padding:`40px`,textAlign:`center`,color:`var(--text-muted)`},children:`Click "Execute GET" to test this endpoint.`})})]})]})]})]}),(0,l.jsxs)(`section`,{className:`section`,children:[(0,l.jsx)(`h2`,{children:`Static JSON API`}),(0,l.jsx)(`p`,{className:`muted`,children:`The Netlify and GitHub Pages deployments publish read-only JSON data files with their own endpoint checks and Swagger explorer.`}),(0,l.jsx)(`a`,{className:`btn btn-ghost`,href:d,children:`Open static JSON API explorer`})]})]})}export{f as default};