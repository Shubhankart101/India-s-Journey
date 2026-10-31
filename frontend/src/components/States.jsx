import { BackupLinks } from './Resilience.jsx';

export function Loading({ label = 'Loading…' }) {
  return (
    <div className="state state-loading" role="status" aria-live="polite">
      <span className="spinner" aria-hidden="true" />
      <span>{label}</span>
    </div>
  );
}

export function ErrorState({ error, onRetry }) {
  const serverDown = error && (error.status === 0 || error.status >= 500);
  return (
    <div className="state state-error" role="alert">
      <p>{error?.message || 'Something went wrong.'}</p>
      {onRetry && <button type="button" className="btn" onClick={onRetry}>Try again</button>}
      {serverDown && <BackupLinks compact />}
    </div>
  );
}

export function Empty({ children }) {
  return <div className="state state-empty">{children}</div>;
}
