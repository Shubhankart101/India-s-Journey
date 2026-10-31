import { useEffect, useState } from 'react';
import { Navigate, useSearchParams } from 'react-router-dom';
import { api } from '../api.js';
import { useAuth } from '../auth.jsx';
import { BackupLinks } from '../components/Resilience.jsx';
import { Loading } from '../components/States.jsx';
import { useDocumentTitle } from '../hooks.js';

// Only allow same-site relative redirects after sign-in.
export const safeNext = value => (value && value.startsWith('/') && !value.startsWith('//') ? value : '/saved');

const ICONS = { google: 'G', microsoft: '⊞' };
const ERRORS = {
  unavailable: 'That sign-in provider is not configured on this server yet.',
  cancelled: 'Sign-in was cancelled.',
  failed: "We couldn't sign you in. Please try again.",
};

// allauth requires a POST (with CSRF) to start the OAuth redirect, which blocks login CSRF.
function ProviderButton({ provider, next }) {
  const [token, setToken] = useState(api.csrfToken());
  return (
    <form method="post" action={provider.login_url} onSubmit={() => setToken(api.csrfToken())}>
      <input type="hidden" name="csrfmiddlewaretoken" value={token} readOnly />
      <input type="hidden" name="next" value={next} readOnly />
      <input type="hidden" name="process" value="login" readOnly />
      <button type="submit" className={`btn btn-block btn-provider btn-${provider.id}`}>
        <span aria-hidden="true" className="provider-icon">{ICONS[provider.id] || '→'}</span>
        Continue with {provider.name}
      </button>
    </form>
  );
}

export default function AuthPage() {
  useDocumentTitle('Sign in');
  const { user } = useAuth();
  const [params] = useSearchParams();
  const next = safeNext(params.get('next'));
  const [providers, setProviders] = useState(null);
  const [failure, setFailure] = useState(null);

  useEffect(() => {
    const controller = new AbortController();
    Promise.all([api.csrf().catch(() => null), api.providers(controller.signal)])
      .then(([, list]) => setProviders(list))
      .catch(error => error.name !== 'AbortError' && setFailure(error));
    return () => controller.abort();
  }, []);

  if (user) return <Navigate to={next} replace />;
  const notice = ERRORS[params.get('error')];

  return (
    <section className="auth-wrap">
      <div className="card auth-card">
        <h1>Sign in</h1>
        <p className="muted">Use your Google or Microsoft (Outlook, Hotmail, Live, Microsoft 365) account to save charts. We never see your password.</p>
        {notice && <p className="form-error" role="alert">{notice}</p>}
        {failure && <p className="form-error" role="alert">{failure.message}</p>}
        {!providers && !failure && <Loading label="Loading sign-in options…" />}
        {providers && providers.length === 0 && (
          <p className="form-error" role="alert">Sign-in is temporarily unavailable. You can still browse every chart.</p>
        )}
        {providers && providers.map(provider => <ProviderButton key={provider.id} provider={provider} next={next} />)}
        <p className="muted small center">No separate password or account is created — only your name and email are stored.</p>
        {failure && <BackupLinks compact />}
      </div>
    </section>
  );
}
