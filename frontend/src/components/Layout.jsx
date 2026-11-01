import { Link, NavLink, Outlet, useLocation } from 'react-router-dom';
import { useEffect } from 'react';
import { MAX_COMPARE, useCompare } from '../compare.jsx';
import { PALETTE_COMPARE } from '../palette.js';
import { BACKUP_MIRROR_URL, BACKUP_URL } from '../config.js';
import { ErrorBoundary, OfflineBanner } from './Resilience.jsx';
import ArtBackdrop from './ArtBackdrop.jsx';
import { AMBIENT_ART } from '../art.js';
import { ScrollProgress, ScrollTopButton, useAutoReveal, usePointerSpotlight, useScrolled } from './Motion.jsx';

const NAV = [
  { to: '/', label: 'Home', icon: '⌂', end: true },
  { to: '/explore', label: 'Explore', icon: '◎' },
  { to: '/sources', label: 'Sources', icon: '❡' },
  { to: '/compare', label: 'Compare', icon: '⇄' },
  { to: '/about', label: 'About', icon: 'ℹ' },
  { to: '/api', label: 'API', icon: '{ }' },
];

export default function Layout() {
  const compare = useCompare();
  const location = useLocation();
  const scrolled = useScrolled();
  const hasPageArtwork = ['/', '/explore', '/about', '/sources'].includes(location.pathname)
    || location.pathname.startsWith('/indicator/');
  useAutoReveal();
  usePointerSpotlight();
  useEffect(() => {
    window.scrollTo?.(0, 0);
  }, [location.pathname]);
  const compareHref = `/compare?keys=${compare.items.map(item => item.key).join(',')}`;

  return (
    <div className="app">
      {!hasPageArtwork && <ArtBackdrop art={AMBIENT_ART} className="app-default-backdrop" />}
      <a className="skip-link" href="#main">Skip to content</a>
      <ScrollProgress />
      <header className={`site-header${scrolled ? ' scrolled' : ''}`}>
        <div className="header-inner">
          <Link to="/" className="brand">India's Journey<span className="brand-dot" aria-hidden="true">.</span></Link>
          <nav className="desktop-nav" aria-label="Primary">
            {NAV.map(item => (
              <NavLink key={item.to} to={item.to} end={item.end}>
                {item.label}
                {item.to === '/compare' && compare.items.length > 0 && <span className="badge">{compare.items.length}</span>}
              </NavLink>
            ))}
          </nav>
          <Link to="/explore" className="btn btn-primary header-cta">Explore data</Link>
        </div>
      </header>

      <OfflineBanner />
      <main id="main" className="main">
        <ErrorBoundary key={location.pathname}>
          <Outlet />
        </ErrorBoundary>
      </main>

      {compare.items.length > 0 && location.pathname !== '/compare' && (
        <aside className="compare-tray" aria-label="Compare tray" aria-live="polite">
          <span className="tray-count"><span aria-hidden="true">⇄ </span>{compare.items.length} selected<small> / {MAX_COMPARE}</small></span>
          <ul className="tray-chips" aria-label="Selected for comparison">
            {compare.items.map((item, index) => (
              <li key={item.key} className="tray-chip" style={{ '--slot': PALETTE_COMPARE[index % PALETTE_COMPARE.length] }}>
                <span className="tray-chip-title" title={item.title}>{item.title}</span>
                <button type="button" aria-label={`Remove ${item.title} from compare`} onClick={() => compare.toggle(item)}>×</button>
              </li>
            ))}
          </ul>
          <Link className="btn btn-primary" to={compareHref}>Compare<span aria-hidden="true"> →</span></Link>
          <button type="button" className="btn btn-ghost" onClick={compare.clear}>Clear</button>
        </aside>
      )}

      <ScrollTopButton />

      <footer className="site-footer">
        <p>Official public data from MOSPI, RBI, World Bank, ECI, FEC, NCRB and more. Every chart links to its source.</p>
        <p>
          <Link to="/api">API</Link> · <Link to="/sources">Sources</Link>
          {' · '}<a href={BACKUP_URL} rel="noopener">Backup site</a> · <a href={BACKUP_MIRROR_URL} rel="noopener">Mirror</a>
          {' · '}<a href="https://github.com/Shubhankart101/India-s-Journey">GitHub</a>
        </p>
      </footer>

      <nav className="tab-bar" aria-label="Mobile">
        {NAV.map(item => (
          <NavLink key={item.to} to={item.to} end={item.end}>
            <span aria-hidden="true">{item.icon}</span>
            <small>{item.label}</small>
          </NavLink>
        ))}
      </nav>
    </div>
  );
}
