import { Component, useEffect, useState } from 'react';
import { BACKUP_STATUS_URL, BACKUP_URL } from '../config.js';

export function BackupLinks({ compact = false }) {
  return (
    <p className={`backup-links${compact ? ' small' : ''}`}>
      App having trouble? Use the <a href={BACKUP_URL} rel="noopener">backup dashboard on GitHub Pages</a>
      {' '}or check <a href={BACKUP_STATUS_URL} rel="noopener">app status</a>.
    </p>
  );
}

export class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { error: null };
  }

  static getDerivedStateFromError(error) {
    return { error };
  }

  componentDidCatch(error, info) {
    console.error('UI crashed', error, info?.componentStack);
  }

  render() {
    if (!this.state.error) return this.props.children;
    return (
      <section className="page-hero center" role="alert">
        <p className="eyebrow">Something broke</p>
        <h1>This page hit an unexpected error.</h1>
        <p className="lead">Reload to try again — your saved charts are safe.</p>
        <div className="hero-actions">
          <button type="button" className="btn btn-primary" onClick={() => window.location.reload()}>Reload</button>
          <a className="btn btn-ghost" href={BACKUP_URL} rel="noopener">Open backup site</a>
        </div>
        <BackupLinks compact />
      </section>
    );
  }
}

export function OfflineBanner() {
  const [offline, setOffline] = useState(typeof navigator !== 'undefined' && navigator.onLine === false);
  useEffect(() => {
    const down = () => setOffline(true);
    const up = () => setOffline(false);
    window.addEventListener('offline', down);
    window.addEventListener('online', up);
    window.addEventListener('api:unreachable', down);
    return () => {
      window.removeEventListener('offline', down);
      window.removeEventListener('online', up);
      window.removeEventListener('api:unreachable', down);
    };
  }, []);
  if (!offline) return null;
  return (
    <div className="offline-banner" role="status">
      <span>Can't reach the server.</span>
      <a href={BACKUP_URL} rel="noopener">Use the backup site</a>
      <button type="button" className="btn btn-ghost" onClick={() => setOffline(false)} aria-label="Dismiss">×</button>
    </div>
  );
}
