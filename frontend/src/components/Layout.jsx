import { Link, NavLink, Outlet, useLocation } from 'react-router-dom';
import { useEffect } from 'react';
import { useAuth } from '../auth.jsx';
import { useCompare } from '../compare.jsx';
import { API_DOCS_URL, BACKUP_STATUS_URL, BACKUP_URL } from '../config.js';
import { ErrorBoundary, OfflineBanner } from './Resilience.jsx';

const NAV = [
  { to: '/', label: 'Home', icon: '⌂', end: true },
  { to: '/explore', label: 'Explore', icon: '◎' },
  { to: '/compare', label: 'Compare', icon: '⇄' },
  { to: '/saved', label: 'Saved', icon: '★' },
  { to: '/about', label: 'About', icon: 'ℹ' },
];

export default function Layout() {
  const { user, logout } = useAuth();
  const compare = useCompare();
  const location = useLocation();
  useEffect(() => {
    window.scrollTo?.(0, 0);
  }, [location.pathname]);
  const compareHref = `/compare?keys=${compare.items.map(item => item.key).join(',')}`;

  return (
    <div className="app">
      <a className="skip-link" href="#main">Skip to content</a>
      <header className="site-header">
        <div className="header-inner">
          <Link to="/" className="brand">India's Journey</Link>
          <nav className="desktop-nav" aria-label="Primary">
            {NAV.map(item => (
              <NavLink key={item.to} to={item.to} end={item.end}>
                {item.label}
                {item.to === '/compare' && compare.items.length > 0 && <span className="badge">{compare.items.length}</span>}
              </NavLink>
            ))}
          </nav>
          <div className="account">
            {user ? (
              <>
                <span className="muted hide-sm" title={user.email || undefined}>
                  Hi, {user.name || user.username}
                  {user.providers?.length > 0 && <small className="provider-tag"> · {user.providers.join(', ')}</small>}
                </span>
                <button type="button" className="btn btn-ghost" onClick={logout}>Sign out</button>
              </>
            ) : <Link to="/login" className="btn btn-ghost">Sign in</Link>}
          </div>
        </div>
      </header>

      <OfflineBanner />
      <main id="main" className="main">
        <ErrorBoundary key={location.pathname}>
          <Outlet />
        </ErrorBoundary>
      </main>

      {compare.items.length > 0 && location.pathname !== '/compare' && (
        <aside className="compare-tray" aria-label="Compare tray">
          <span>{compare.items.length} selected</span>
          <Link className="btn btn-primary" to={compareHref}>Compare</Link>
          <button type="button" className="btn btn-ghost" onClick={compare.clear}>Clear</button>
        </aside>
      )}

      <footer className="site-footer">
        <p>Official public data from MOSPI, RBI, World Bank, ECI, FEC, NCRB and more. Every chart links to its source.</p>
        <p>
          <a href={API_DOCS_URL}>API docs</a> · <a href="/api/">API</a> · <a href="/admin/">Admin</a>
          {' · '}<a href={BACKUP_URL} rel="noopener">Backup site</a> · <a href={BACKUP_STATUS_URL} rel="noopener">Status</a>
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
