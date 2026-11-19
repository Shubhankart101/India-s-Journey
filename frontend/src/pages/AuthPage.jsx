import { useEffect, useState } from 'react';
import { Link, Navigate, useSearchParams } from 'react-router-dom';
import { api } from '../api.js';
import { useAuth } from '../auth.jsx';
import { BackupLinks } from '../components/Resilience.jsx';
import { Loading } from '../components/States.jsx';
import { useDocumentTitle } from '../hooks.js';

// Only allow same-site relative redirects after sign-in.
export const safeNext = value => (value && value.startsWith('/') && !value.startsWith('//') ? value : '/explore');

const ERRORS = {
  unavailable: 'That sign-in provider is not configured on this server yet.',
  cancelled: 'Sign-in was cancelled.',
  failed: "We couldn't sign you in. Please try again.",
};

function GoogleIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" aria-hidden="true" style={{ verticalAlign: 'middle' }}>
      <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
      <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
      <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z" />
      <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z" />
    </svg>
  );
}

function MicrosoftIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 21 21" aria-hidden="true" style={{ verticalAlign: 'middle' }}>
      <rect x="1" y="1" width="9" height="9" fill="#f25022" />
      <rect x="11" y="1" width="9" height="9" fill="#7fba00" />
      <rect x="1" y="11" width="9" height="9" fill="#00a4ef" />
      <rect x="11" y="11" width="9" height="9" fill="#ffb900" />
    </svg>
  );
}

function ProviderButton({ provider, next }) {
  const [token, setToken] = useState(api.csrfToken());

  return (
    <form
      method="post"
      action={provider.login_url}
      onSubmit={() => setToken(api.csrfToken())}
      style={{ width: '100%' }}
    >
      <input type="hidden" name="csrfmiddlewaretoken" value={token} readOnly />
      <input type="hidden" name="next" value={next} readOnly />
      <input type="hidden" name="process" value="login" readOnly />
      <button
        type="submit"
        className={`btn btn-block btn-provider btn-${provider.id}`}
        style={{
          width: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '12px',
          padding: '12px 18px',
          borderRadius: '10px',
          fontSize: '0.96rem',
          fontWeight: 600,
          cursor: 'pointer',
          marginBottom: '10px',
          textDecoration: 'none',
        }}
      >
        <span aria-hidden="true" className="provider-icon">
          {provider.id === 'google' && <GoogleIcon />}
          {provider.id === 'microsoft' && <MicrosoftIcon />}
          {provider.id !== 'google' && provider.id !== 'microsoft' && '→'}
        </span>
        Continue with {provider.name}
      </button>
    </form>
  );
}

export default function AuthPage() {
  useDocumentTitle('Sign in');
  const { user, logout, ready } = useAuth();
  const [params] = useSearchParams();
  const next = safeNext(params.get('next'));
  const [providers, setProviders] = useState(null);
  const [failure, setFailure] = useState(null);

  useEffect(() => {
    const controller = new AbortController();
    Promise.all([api.csrf().catch(() => null), api.providers(controller.signal)])
      .then(([, list]) => setProviders(list || []))
      .catch(error => {
        if (error.name !== 'AbortError') {
          // If providers endpoint is unavailable (e.g. static host or mock), provide default providers
          setProviders([
            { id: 'google', name: 'Google', login_url: '/accounts/google/login/' },
            { id: 'microsoft', name: 'Microsoft (Outlook)', login_url: '/accounts/microsoft/login/' },
          ]);
        }
      });
    return () => controller.abort();
  }, []);

  // When signed in: show profile info & logout
  if (user) {
    const displayName = user.first_name || user.username || user.email?.split('@')[0] || 'User';
    const email = user.email || '';
    const initial = (displayName[0] || 'U').toUpperCase();

    return (
      <section className="auth-wrap">
        <div className="card auth-card" style={{ textAlign: 'center', alignItems: 'center' }}>
          <div
            style={{
              width: '64px',
              height: '64px',
              borderRadius: '50%',
              background: 'var(--accent, #2997ff)',
              color: '#fff',
              display: 'grid',
              placeItems: 'center',
              fontSize: '1.8rem',
              fontWeight: 700,
              margin: '0 auto 12px',
            }}
          >
            {initial}
          </div>
          <h1>Signed in</h1>
          <p style={{ margin: '4px 0 2px', fontWeight: 600, fontSize: '1.15rem' }}>{displayName}</p>
          {email && <p className="muted" style={{ margin: '0 0 16px', fontSize: '0.9rem' }}>{email}</p>}
          <div style={{ display: 'flex', gap: '10px', marginTop: '12px', width: '100%', justifyContent: 'center' }}>
            <Link to="/explore" className="btn btn-primary" style={{ flex: 1 }}>
              Browse Data
            </Link>
            <button type="button" className="btn btn-ghost" onClick={logout} style={{ flex: 1 }}>
              Sign out
            </button>
          </div>
        </div>
      </section>
    );
  }

  const notice = ERRORS[params.get('error')];

  return (
    <section className="auth-wrap">
      <div className="card auth-card">
        <h1 style={{ marginBottom: '6px' }}>Sign in</h1>
        <p className="muted" style={{ fontSize: '0.93rem', lineHeight: '1.45', margin: '0 0 16px' }}>
          Sign in with your <strong>Google</strong> or <strong>Microsoft</strong> (Outlook, Hotmail, Live, Microsoft 365) account to bookmark indicators and save charts. We never see or store your password.
        </p>

        {notice && <p className="form-error" role="alert">{notice}</p>}
        {failure && <p className="form-error" role="alert">{failure.message}</p>}

        {!providers && !failure && <Loading label="Loading sign-in options…" />}

        {providers && providers.length > 0 && (
          <div className="provider-buttons" style={{ display: 'flex', flexDirection: 'column', gap: '8px', margin: '10px 0' }}>
            {providers.map(provider => (
              <ProviderButton key={provider.id} provider={provider} next={next} />
            ))}
          </div>
        )}

        {providers && providers.length === 0 && (
          <div style={{ background: 'rgba(255, 255, 255, 0.04)', padding: '16px', borderRadius: '10px', margin: '10px 0' }}>
            <p style={{ fontWeight: 600, marginBottom: '6px' }}>OAuth Configuration Note</p>
            <p className="muted small" style={{ margin: 0, lineHeight: '1.4' }}>
              Google and Microsoft authentication are enabled. To activate live authentication in your local environment, specify <code>GOOGLE_CLIENT_ID</code> and <code>MICROSOFT_CLIENT_ID</code> in your <code>.env</code> file.
            </p>
          </div>
        )}

        <div style={{ borderTop: '1px solid var(--line, rgba(255,255,255,0.1))', paddingTop: '14px', marginTop: '10px' }}>
          <p className="muted small" style={{ margin: 0, textAlign: 'center' }}>
            🔒 Privacy-first: No separate password or profile is required. Only your name and email are used for session verification.
          </p>
        </div>

        {failure && <BackupLinks compact />}
      </div>
    </section>
  );
}
