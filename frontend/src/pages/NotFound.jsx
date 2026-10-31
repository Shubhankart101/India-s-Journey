import { Link } from 'react-router-dom';
import { useDocumentTitle } from '../hooks.js';
import { BackupLinks } from '../components/Resilience.jsx';

export default function NotFound() {
  useDocumentTitle('Page not found');
  return (
    <section className="page-hero center">
      <p className="eyebrow">404</p>
      <h1>This page wandered off.</h1>
      <p className="lead">The link may be old, or the indicator was renamed.</p>
      <div className="hero-actions">
        <Link className="btn btn-primary" to="/">Go home</Link>
        <Link className="btn btn-ghost" to="/explore">Explore indicators</Link>
      </div>
      <BackupLinks />
    </section>
  );
}
