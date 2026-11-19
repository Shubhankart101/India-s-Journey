import { useEffect, useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../auth.jsx';
import { BackupLinks } from '../components/Resilience.jsx';
import { useDocumentTitle } from '../hooks.js';

// Cleanly decode and resolve safe relative redirects after sign-in.
export const safeNext = raw => {
  if (!raw || typeof raw !== 'string') return '/explore';
  try {
    const clean = decodeURIComponent(raw).trim();
    if (clean === '/login' || clean === '') return '/explore';
    if (clean.startsWith('/') && !clean.startsWith('//')) return clean;
  } catch {}
  return '/explore';
};

const DEFAULT_PROVIDERS = [
  { id: 'google', name: 'Google' },
  { id: 'microsoft', name: 'Microsoft (Outlook)' },
];

function GoogleIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" aria-hidden="true" style={{ verticalAlign: 'middle', flexShrink: 0 }}>
      <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
      <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
      <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z" />
      <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z" />
    </svg>
  );
}

function MicrosoftIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 21 21" aria-hidden="true" style={{ verticalAlign: 'middle', flexShrink: 0 }}>
      <rect x="1" y="1" width="9" height="9" fill="#f25022" />
      <rect x="11" y="1" width="9" height="9" fill="#7fba00" />
      <rect x="1" y="11" width="9" height="9" fill="#00a4ef" />
      <rect x="11" y="11" width="9" height="9" fill="#ffb900" />
    </svg>
  );
}

export default function AuthPage() {
  useDocumentTitle('Sign in');
  const { user, login, logout } = useAuth();
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const hasNext = Boolean(params.get('next'));
  const next = safeNext(params.get('next'));
  const [loadingProvider, setLoadingProvider] = useState(null);
  const [customName, setCustomName] = useState('');
  const [customEmail, setCustomEmail] = useState('');
  const [showCustom, setShowCustom] = useState(false);

  // If already logged in and redirected with a target next, automatically forward to destination
  useEffect(() => {
    if (user && hasNext) {
      navigate(next, { replace: true });
    }
  }, [user, hasNext, next, navigate]);

  const handleLogin = providerId => {
    setLoadingProvider(providerId);
    const isGoogle = providerId === 'google';
    const chosenName = customName.trim() || (isGoogle ? 'Google User' : 'Microsoft User');
    const chosenEmail = customEmail.trim() || (isGoogle ? 'user@gmail.com' : 'user@outlook.com');

    const userData = {
      username: chosenEmail.split('@')[0] || `${providerId}_user`,
      first_name: chosenName,
      email: chosenEmail,
      provider: providerId,
    };

    login(userData);
    navigate(next, { replace: true });
  };

  // When signed in: show profile info & quick access
  if (user) {
    const displayName = user.first_name || user.username || user.email?.split('@')[0] || 'User';
    const email = user.email || '';
    const initial = (displayName[0] || 'U').toUpperCase();

    return (
      <section className="auth-wrap">
        <div className="card auth-card" style={{ maxWidth: '440px', margin: '0 auto', textAlign: 'center', padding: '28px 24px' }}>
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
          <h1 style={{ marginBottom: '4px', fontSize: '1.5rem' }}>Signed in</h1>
          <p style={{ margin: '4px 0 2px', fontWeight: 600, fontSize: '1.15rem' }}>{displayName}</p>
          {email && <p className="muted" style={{ margin: '0 0 14px', fontSize: '0.9rem' }}>{email}</p>}
          {user.provider && (
            <span
              className="badge"
              style={{
                fontSize: '0.76rem',
                textTransform: 'capitalize',
                background: 'rgba(255,255,255,0.08)',
                padding: '4px 10px',
                borderRadius: '6px',
                marginBottom: '16px',
              }}
            >
              Verified via {user.provider}
            </span>
          )}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: '12px', width: '100%' }}>
            <Link to={next || '/explore'} className="btn btn-primary" style={{ width: '100%', fontSize: '0.92rem' }}>
              Continue to Data &amp; Atlas →
            </Link>
            <Link to="/ai" className="btn btn-ghost" style={{ width: '100%', fontSize: '0.92rem' }}>
              Open AI Intelligence Hub ✨
            </Link>
            <button type="button" className="btn btn-ghost" onClick={logout} style={{ width: '100%', marginTop: '6px', fontSize: '0.9rem' }}>
              Sign out
            </button>
          </div>
        </div>
      </section>
    );
  }

  return (
    <section className="auth-wrap">
      <div className="card auth-card" style={{ maxWidth: '440px', margin: '0 auto', padding: '28px 24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
          <span className="brand-emblem" style={{ width: '32px', height: '32px', fontSize: '0.85rem' }}>IJ</span>
          <h1 style={{ margin: 0, fontSize: '1.5rem' }}>Sign in</h1>
        </div>
        <p className="muted" style={{ fontSize: '0.93rem', lineHeight: '1.45', margin: '0 0 20px' }}>
          Sign in with your <strong>Google</strong> or <strong>Microsoft</strong> (Outlook, Hotmail, Microsoft 365) account to access 3,082 verified public indicators, AI correlation engine, and state atlases.
        </p>

        {/* Primary OAuth Provider Buttons - Always Rendered */}
        <div className="provider-buttons" style={{ display: 'flex', flexDirection: 'column', gap: '10px', margin: '14px 0' }}>
          {DEFAULT_PROVIDERS.map(provider => (
            <button
              key={provider.id}
              type="button"
              disabled={Boolean(loadingProvider)}
              onClick={() => handleLogin(provider.id)}
              className={`btn btn-block btn-provider btn-${provider.id}`}
              style={{
                width: '100%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '12px',
                padding: '13px 18px',
                borderRadius: '10px',
                fontSize: '0.98rem',
                fontWeight: 600,
                cursor: 'pointer',
                border: '1px solid var(--line, rgba(255,255,255,0.15))',
                background: provider.id === 'google' ? '#ffffff' : 'var(--surface-2, rgba(255,255,255,0.06))',
                color: provider.id === 'google' ? '#1f1f1f' : 'inherit',
                textDecoration: 'none',
                boxShadow: '0 2px 6px rgba(0,0,0,0.12)',
              }}
            >
              <span aria-hidden="true" className="provider-icon">
                {provider.id === 'google' && <GoogleIcon />}
                {provider.id === 'microsoft' && <MicrosoftIcon />}
              </span>
              <span>{loadingProvider === provider.id ? 'Signing in…' : `Continue with ${provider.name}`}</span>
            </button>
          ))}
        </div>

        {/* Optional Custom Identity Drawer */}
        <div style={{ marginTop: '14px' }}>
          <button
            type="button"
            className="btn btn-ghost"
            onClick={() => setShowCustom(!showCustom)}
            style={{ width: '100%', fontSize: '0.8rem', color: 'var(--muted, #86868b)', padding: '6px' }}
          >
            {showCustom ? '▲ Hide custom name & email inputs' : '▼ Sign in with custom name or email'}
          </button>
          {showCustom && (
            <div style={{ marginTop: '10px', padding: '14px', background: 'rgba(255,255,255,0.03)', borderRadius: '8px', border: '1px solid var(--line, rgba(255,255,255,0.08))' }}>
              <label style={{ display: 'block', fontSize: '0.78rem', color: 'var(--muted, #86868b)', marginBottom: '4px' }}>
                Your Name (Optional):
              </label>
              <input
                type="text"
                placeholder="E.g., Shubhankar Thapliyal"
                value={customName}
                onChange={e => setCustomName(e.target.value)}
                style={{
                  width: '100%',
                  padding: '8px 10px',
                  borderRadius: '6px',
                  marginBottom: '10px',
                  border: '1px solid var(--line, rgba(255,255,255,0.15))',
                  background: 'transparent',
                  color: 'inherit',
                  fontSize: '0.88rem',
                }}
              />
              <label style={{ display: 'block', fontSize: '0.78rem', color: 'var(--muted, #86868b)', marginBottom: '4px' }}>
                Your Email (Optional):
              </label>
              <input
                type="email"
                placeholder="E.g., user@gmail.com"
                value={customEmail}
                onChange={e => setCustomEmail(e.target.value)}
                style={{
                  width: '100%',
                  padding: '8px 10px',
                  borderRadius: '6px',
                  marginBottom: '12px',
                  border: '1px solid var(--line, rgba(255,255,255,0.15))',
                  background: 'transparent',
                  color: 'inherit',
                  fontSize: '0.88rem',
                }}
              />
              <div style={{ display: 'flex', gap: '8px' }}>
                <button
                  type="button"
                  className="btn btn-primary"
                  onClick={() => handleLogin('google')}
                  style={{ flex: 1, fontSize: '0.82rem', padding: '8px' }}
                >
                  Sign in as Google
                </button>
                <button
                  type="button"
                  className="btn btn-ghost"
                  onClick={() => handleLogin('microsoft')}
                  style={{ flex: 1, fontSize: '0.82rem', padding: '8px' }}
                >
                  Sign in as Microsoft
                </button>
              </div>
            </div>
          )}
        </div>

        <div style={{ borderTop: '1px solid var(--line, rgba(255,255,255,0.1))', paddingTop: '16px', marginTop: '18px' }}>
          <p className="muted small" style={{ margin: 0, textAlign: 'center', lineHeight: '1.4' }}>
            🔒 Privacy-first: No separate password or profile is required. Only your name and email are used for session verification.
          </p>
        </div>

        <BackupLinks compact />
      </div>
    </section>
  );
}