import{r as e}from"./rolldown-runtime-XKyaHtl9.js";import{_ as t,g as n}from"./charts-B6pdgxOd.js";import{r}from"./vendor-CMZuCPfa.js";import{o as i,r as a,t as o}from"./config-uet0De6j.js";import{L as s}from"./index-BCCulvsx.js";var c=e(t(),1),l=n(),u=[{path:`/api/stats/`,name:`Statistics`,desc:`Read indicator, group and data-point totals.`,method:`GET`},{path:`/api/categories/`,name:`Groups & Subgroups`,desc:`Browse the 13 data groups and 138+ subgroups.`,method:`GET`},{path:`/api/indicators/`,name:`Indicators Catalogue`,desc:`Search, filter and paginate the indicator catalogue.`,method:`GET`},{path:`/api/compare/?keys=gdp_growth,inflation`,name:`Compare Series`,desc:`Align and compare multiple indicator time-series.`,method:`GET`},{path:`/api/articles/`,name:`Articles & Reports`,desc:`Browse public articles, essays and research writing.`,method:`GET`},{path:`/api/health/`,name:`System Health`,desc:`Check the API service and database connectivity.`,method:`GET`}],d=new URL(`api.html`,a).href;function f(){s(`API`);let[e,t]=(0,c.useState)(`swagger`),[n,a]=(0,c.useState)(null),[f,p]=(0,c.useState)(!0),[m,h]=(0,c.useState)(null),[g,_]=(0,c.useState)(!1),[v,y]=(0,c.useState)(``),[b,x]=(0,c.useState)(u[0]),[S,C]=(0,c.useState)(!1),[w,T]=(0,c.useState)(null),[E,D]=(0,c.useState)(null),[O,k]=(0,c.useState)(null),A=i(`api/openapi.json`);(0,c.useEffect)(()=>{let e=!1;async function t(){p(!0);try{let t=await fetch(A).catch(()=>null);if(t&&t.ok||(t=await fetch(`/api/schema/?format=json`).catch(()=>null)),t&&t.ok||(t=await fetch(i(`openapi.json`)).catch(()=>null)),t&&t.ok){let n=await t.json();e||(a(n),p(!1));return}throw Error(`Could not load OpenAPI schema`)}catch(t){e||(h(t.message),p(!1))}}return t(),()=>{e=!0}},[A]);let j=async e=>{C(!0),T(null);let t=performance.now();try{let n=e.path,r=await fetch(n).catch(()=>null);if(!r||!r.ok){let t=e.path.replace(/^\/api\//,``).replace(/\/$/,``).split(`?`)[0];n=i(`api/${t}.json`),r=await fetch(n).catch(()=>null)}let a=Math.round(performance.now()-t);if(D(a),r&&r.ok){let e=await r.json();k(r.status),T(e)}else k(r?r.status:503),T({error:`Endpoint unreachable or returned error`,status:r?.status})}catch(e){k(500),T({error:e.message}),D(Math.round(performance.now()-t))}finally{C(!1)}};(0,c.useEffect)(()=>{e===`index`&&!w&&!S&&j(b)},[e]);let M=()=>{n&&(navigator.clipboard.writeText(JSON.stringify(n,null,2)),_(!0),setTimeout(()=>_(!1),2e3))},N=(0,c.useMemo)(()=>n?`<!DOCTYPE html>
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
  <script src="https://unpkg.com/swagger-ui-dist@5.11.0/swagger-ui-bundle.js"><\/script>
  <script src="https://unpkg.com/swagger-ui-dist@5.11.0/swagger-ui-standalone-preset.js"><\/script>
  <script>
    window.onload = function() {
      try {
        const spec = ${JSON.stringify(n)};
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
  <\/script>
</body>
</html>`:``,[n]),P=(0,c.useMemo)(()=>n?`<!DOCTYPE html>
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
  <script src="https://cdn.redoc.ly/redoc/latest/bundles/redoc.standalone.js"><\/script>
  <script>
    try {
      const spec = ${JSON.stringify(n)};
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
  <\/script>
</body>
</html>`:``,[n]),F=(0,c.useMemo)(()=>{if(!n)return``;if(!v)return JSON.stringify(n,null,2);try{let e={},t=v.toLowerCase();if(n.info&&(e.info=n.info),n.paths){e.paths={};for(let[r,i]of Object.entries(n.paths))(r.toLowerCase().includes(t)||JSON.stringify(i).toLowerCase().includes(t))&&(e.paths[r]=i)}return JSON.stringify(e,null,2)}catch{return JSON.stringify(n,null,2)}},[n,v]);return(0,l.jsxs)(`main`,{className:`api-page`,children:[(0,l.jsxs)(`div`,{style:{display:`flex`,alignItems:`center`,justifyContent:`space-between`,marginBottom:`28px`,paddingBottom:`16px`,borderBottom:`1px solid var(--border-color)`},children:[(0,l.jsxs)(r,{to:`/`,className:`brand`,"aria-label":`India's Journey home`,style:{display:`flex`,alignItems:`center`,gap:`8px`,textDecoration:`none`},children:[(0,l.jsx)(`span`,{className:`brand-emblem`,"aria-hidden":`true`,children:`IJ`}),(0,l.jsx)(`span`,{className:`brand-stack`,children:(0,l.jsxs)(`span`,{className:`brand-text`,children:[`India's Journey`,(0,l.jsx)(`span`,{className:`brand-dot`,"aria-hidden":`true`,children:`.`})]})})]}),(0,l.jsxs)(`div`,{style:{display:`flex`,gap:`10px`},children:[(0,l.jsx)(r,{to:`/`,className:`btn btn-ghost`,style:{fontSize:`0.85rem`},children:`← Home`}),(0,l.jsx)(r,{to:`/explore`,className:`btn btn-primary`,style:{fontSize:`0.85rem`},children:`Explore Data`})]})]}),(0,l.jsxs)(`section`,{className:`api-intro`,children:[(0,l.jsx)(`p`,{className:`eyebrow`,children:`Public data access`}),(0,l.jsx)(`h1`,{children:`API & endpoint explorer`}),(0,l.jsx)(`p`,{className:`lead`,children:`Explore the read-only Django REST API, its schema and the static JSON resources published with the dashboard.`}),(0,l.jsxs)(`div`,{className:`action-row api-tab-bar`,role:`tablist`,"aria-label":`API Explorer Views`,children:[(0,l.jsx)(`a`,{className:`btn ${e===`swagger`?`btn-primary`:`btn-ghost`}`,href:o,onClick:e=>{e.preventDefault(),t(`swagger`)},children:`Open Swagger UI`}),(0,l.jsx)(`a`,{className:`btn ${e===`redoc`?`btn-primary`:`btn-ghost`}`,href:`/api/redoc/`,onClick:e=>{e.preventDefault(),t(`redoc`)},children:`ReDoc`}),(0,l.jsx)(`a`,{className:`btn ${e===`schema`?`btn-primary`:`btn-ghost`}`,href:`/api/schema/?format=json`,onClick:e=>{e.preventDefault(),t(`schema`)},children:`OpenAPI schema`}),(0,l.jsx)(`a`,{className:`btn ${e===`index`?`btn-primary`:`btn-ghost`}`,href:`/api/`,onClick:e=>{e.preventDefault(),t(`index`)},children:`API index`})]})]}),(0,l.jsxs)(`section`,{className:`api-viewer-card`,"aria-live":`polite`,children:[e===`swagger`&&(0,l.jsxs)(`div`,{children:[(0,l.jsxs)(`div`,{className:`api-viewer-header`,children:[(0,l.jsxs)(`div`,{className:`api-viewer-title`,children:[(0,l.jsx)(`span`,{children:`⚡ Interactive Swagger UI`}),(0,l.jsx)(`span`,{className:`api-tab-badge`,children:`OpenAPI 3.0`})]}),(0,l.jsx)(`div`,{className:`api-viewer-actions`,children:(0,l.jsx)(`a`,{className:`btn btn-ghost`,href:A,target:`_blank`,rel:`noopener noreferrer`,download:`openapi.json`,children:`Download openapi.json`})})]}),f?(0,l.jsx)(`div`,{style:{padding:`60px 24px`,textAlign:`center`,color:`var(--text-muted)`},children:`Loading interactive OpenAPI specification…`}):m?(0,l.jsxs)(`div`,{style:{padding:`40px 24px`,color:`#f87171`},children:[`Error loading OpenAPI schema: `,m,`. You can test endpoints in the API Index tab.`]}):(0,l.jsx)(`iframe`,{title:`Swagger UI Explorer`,className:`api-frame`,srcDoc:N,sandbox:`allow-scripts allow-same-origin allow-popups`})]}),e===`redoc`&&(0,l.jsxs)(`div`,{children:[(0,l.jsxs)(`div`,{className:`api-viewer-header`,children:[(0,l.jsxs)(`div`,{className:`api-viewer-title`,children:[(0,l.jsx)(`span`,{children:`📖 ReDoc Comprehensive Reference`}),(0,l.jsx)(`span`,{className:`api-tab-badge`,children:`v3.0.3`})]}),(0,l.jsx)(`div`,{className:`api-viewer-actions`,children:(0,l.jsx)(`a`,{className:`btn btn-ghost`,href:A,target:`_blank`,rel:`noopener noreferrer`,download:`openapi.json`,children:`Download openapi.json`})})]}),f?(0,l.jsx)(`div`,{style:{padding:`60px 24px`,textAlign:`center`,color:`var(--text-muted)`},children:`Loading ReDoc documentation…`}):(0,l.jsx)(`iframe`,{title:`ReDoc API Documentation`,className:`api-frame`,srcDoc:P,sandbox:`allow-scripts allow-same-origin allow-popups`})]}),e===`schema`&&(0,l.jsxs)(`div`,{children:[(0,l.jsxs)(`div`,{className:`api-viewer-header`,children:[(0,l.jsxs)(`div`,{className:`api-viewer-title`,children:[(0,l.jsx)(`span`,{children:`📄 OpenAPI 3.0 Specification`}),(0,l.jsx)(`span`,{className:`api-tab-badge`,children:`JSON Format`})]}),(0,l.jsxs)(`div`,{className:`api-viewer-actions`,children:[(0,l.jsx)(`input`,{type:`search`,placeholder:`Filter paths...`,value:v,onChange:e=>y(e.target.value),style:{padding:`6px 12px`,borderRadius:`8px`,border:`1px solid var(--border-color)`,background:`var(--bg-card)`,color:`inherit`,fontSize:`0.85rem`}}),(0,l.jsx)(`button`,{type:`button`,className:`btn btn-ghost`,onClick:M,children:g?`✓ Copied`:`Copy JSON`}),(0,l.jsx)(`a`,{className:`btn btn-primary`,href:A,target:`_blank`,rel:`noopener noreferrer`,download:`openapi.json`,children:`Download openapi.json`})]})]}),(0,l.jsx)(`div`,{className:`api-schema-container`,children:f?(0,l.jsx)(`p`,{style:{color:`var(--text-muted)`},children:`Loading schema...`}):(0,l.jsx)(`pre`,{className:`api-schema-pre`,children:F})})]}),e===`index`&&(0,l.jsxs)(`div`,{children:[(0,l.jsxs)(`div`,{className:`api-viewer-header`,children:[(0,l.jsxs)(`div`,{className:`api-viewer-title`,children:[(0,l.jsx)(`span`,{children:`🚀 Interactive API Playground & Index`}),(0,l.jsx)(`span`,{className:`api-tab-badge`,children:`Live Endpoints`})]}),(0,l.jsx)(`div`,{className:`api-viewer-actions`,children:(0,l.jsx)(`span`,{className:`muted`,style:{fontSize:`0.85rem`},children:`Select an endpoint to execute a real-time request`})})]}),(0,l.jsxs)(`div`,{className:`api-playground-grid`,children:[(0,l.jsx)(`div`,{className:`api-endpoints-sidebar`,children:u.map(e=>(0,l.jsxs)(`button`,{type:`button`,className:`api-endpoint-item ${b.path===e.path?`selected`:``}`,onClick:()=>{x(e),j(e)},children:[(0,l.jsxs)(`div`,{className:`api-endpoint-head`,children:[(0,l.jsx)(`span`,{className:`api-method-badge`,children:e.method}),(0,l.jsx)(`span`,{className:`api-endpoint-path`,children:e.path.split(`?`)[0]})]}),(0,l.jsx)(`strong`,{style:{fontSize:`0.9rem`,color:`var(--text-color)`},children:e.name}),(0,l.jsx)(`p`,{className:`api-endpoint-desc`,children:e.desc})]},e.path))}),(0,l.jsxs)(`div`,{className:`api-response-panel`,children:[(0,l.jsxs)(`div`,{className:`api-response-header`,children:[(0,l.jsxs)(`div`,{children:[(0,l.jsx)(`span`,{className:`api-method-badge`,style:{marginRight:`8px`},children:b.method}),(0,l.jsx)(`code`,{style:{fontSize:`0.95rem`,fontWeight:600},children:b.path})]}),(0,l.jsxs)(`div`,{style:{display:`flex`,alignItems:`center`,gap:`10px`},children:[O&&(0,l.jsxs)(`span`,{className:`api-status-badge ${O>=400?`error`:``}`,children:[O,` `,O===200?`OK`:`Response`]}),E!==null&&(0,l.jsxs)(`span`,{style:{fontSize:`0.8rem`,color:`var(--text-muted)`},children:[E,` ms`]}),(0,l.jsx)(`button`,{type:`button`,className:`btn btn-primary`,style:{padding:`6px 14px`,fontSize:`0.85rem`},disabled:S,onClick:()=>j(b),children:S?`Sending…`:`Execute GET`})]})]}),(0,l.jsx)(`div`,{className:`api-response-body`,children:S?(0,l.jsxs)(`div`,{style:{padding:`40px`,textAlign:`center`,color:`var(--text-muted)`},children:[`Executing request to `,(0,l.jsx)(`code`,{children:b.path}),`…`]}):w?(0,l.jsx)(`pre`,{className:`api-response-pre`,children:JSON.stringify(w,null,2)}):(0,l.jsx)(`div`,{style:{padding:`40px`,textAlign:`center`,color:`var(--text-muted)`},children:`Click "Execute GET" to test this endpoint.`})})]})]})]})]}),(0,l.jsxs)(`section`,{className:`section`,children:[(0,l.jsx)(`h2`,{children:`Static JSON API`}),(0,l.jsx)(`p`,{className:`muted`,children:`The Netlify and GitHub Pages deployments publish read-only JSON data files with their own endpoint checks and Swagger explorer.`}),(0,l.jsx)(`a`,{className:`btn btn-ghost`,href:d,children:`Open static JSON API explorer`})]})]})}export{f as default};