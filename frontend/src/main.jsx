import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter, HashRouter } from 'react-router-dom';
import App from './App.jsx';
import { applyTheme } from './theme.js';
import './styles.css';
import './themes.css';
import './vintage.css';
import './groupcards.css';
import './scripture.css';

const STATIC_MODE = import.meta.env.VITE_STATIC === '1';

function configureStaticAssetPaths() {
  if (!STATIC_MODE || !location.hostname.endsWith('github.io')) return;
  const project = location.pathname.split('/').filter(Boolean)[0];
  if (!project) return;
  const prefix = `/${project}/`;
  const rewrite = value => typeof value === 'string' && /^\/(art|data|maps)\//.test(value)
    ? `${prefix}${value.slice(1)}` : value;
  const originalFetch = window.fetch.bind(window);
  window.fetch = (input, init) => {
    const source = typeof input === 'string' ? input : input?.url;
    const target = rewrite(source);
    if (target === source) return originalFetch(input, init);
    return originalFetch(input instanceof Request ? new Request(target, input) : target, init);
  };
  const src = Object.getOwnPropertyDescriptor(HTMLImageElement.prototype, 'src');
  if (src?.set) Object.defineProperty(HTMLImageElement.prototype, 'src', {
    ...src,
    set(value) { src.set.call(this, rewrite(value)); },
  });
  const setAttribute = Element.prototype.setAttribute;
  Element.prototype.setAttribute = function (name, value) {
    return setAttribute.call(this, name, name.toLowerCase() === 'src' ? rewrite(value) : value);
  };
}

configureStaticAssetPaths();
applyTheme();

const Router = STATIC_MODE ? HashRouter : BrowserRouter;

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <Router>
      <App />
    </Router>
  </StrictMode>,
);
