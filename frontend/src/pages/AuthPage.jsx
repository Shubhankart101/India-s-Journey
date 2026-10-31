import { useState } from 'react';
import { Link, Navigate, useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../auth.jsx';
import { useDocumentTitle } from '../hooks.js';

// Only allow same-site relative redirects after sign-in.
export const safeNext = value => (value && value.startsWith('/') && !value.startsWith('//') ? value : '/saved');

export default function AuthPage({ mode }) {
  const isRegister = mode === 'register';
  useDocumentTitle(isRegister ? 'Create account' : 'Sign in');
  const { user, login, register } = useAuth();
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const next = safeNext(params.get('next'));
  const [form, setForm] = useState({ username: '', email: '', password: '', confirm: '' });
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  if (user) return <Navigate to={next} replace />;

  const change = event => setForm(current => ({ ...current, [event.target.name]: event.target.value }));
  const submit = async event => {
    event.preventDefault();
    setError('');
    if (isRegister && form.password !== form.confirm) {
      setError('Passwords do not match.');
      return;
    }
    setBusy(true);
    try {
      if (isRegister) await register({ username: form.username, email: form.email, password: form.password });
      else await login({ username: form.username, password: form.password });
      navigate(next, { replace: true });
    } catch (failure) {
      setError(failure.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <section className="auth-wrap">
      <form className="card auth-card" onSubmit={submit} noValidate>
        <h1>{isRegister ? 'Create your account' : 'Welcome back'}</h1>
        <p className="muted">{isRegister ? 'Save charts and come back to them on any device.' : 'Sign in to see your saved charts.'}</p>
        <label>
          <span>Username</span>
          <input name="username" autoComplete="username" required value={form.username} onChange={change} />
        </label>
        {isRegister && (
          <label>
            <span>Email (optional)</span>
            <input name="email" type="email" autoComplete="email" value={form.email} onChange={change} />
          </label>
        )}
        <label>
          <span>Password</span>
          <input name="password" type="password" autoComplete={isRegister ? 'new-password' : 'current-password'} required value={form.password} onChange={change} />
        </label>
        {isRegister && (
          <label>
            <span>Confirm password</span>
            <input name="confirm" type="password" autoComplete="new-password" required value={form.confirm} onChange={change} />
          </label>
        )}
        {error && <p className="form-error" role="alert">{error}</p>}
        <button type="submit" className="btn btn-primary btn-block" disabled={busy || !form.username || !form.password}>
          {busy ? 'Please wait…' : isRegister ? 'Create account' : 'Sign in'}
        </button>
        <p className="muted small center">
          {isRegister
            ? <>Already have an account? <Link to={`/login?next=${encodeURIComponent(next)}`}>Sign in</Link></>
            : <>New here? <Link to={`/register?next=${encodeURIComponent(next)}`}>Create an account</Link></>}
        </p>
      </form>
    </section>
  );
}
