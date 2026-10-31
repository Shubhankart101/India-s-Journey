import { Navigate } from 'react-router-dom';
import { useState } from 'react';
import { api } from '../api.js';
import { useAuth } from '../auth.jsx';
import { useAsync, useDocumentTitle } from '../hooks.js';
import IndicatorCard from '../components/IndicatorCard.jsx';
import { Empty, ErrorState, Loading } from '../components/States.jsx';
import { Link } from 'react-router-dom';

export default function Saved() {
  useDocumentTitle('Saved');
  const { user, ready } = useAuth();
  if (!ready) return <Loading />;
  if (!user) return <Navigate to="/login?next=/saved" replace />;
  return <SavedList />;
}

function SavedList() {
  const { data, error, loading, reload } = useAsync(() => api.saved(), []);
  const [removed, setRemoved] = useState([]);
  const [removeError, setRemoveError] = useState(null);
  const items = (data || []).filter(item => !removed.includes(item.indicator.key));

  const remove = async key => {
    setRemoveError(null);
    try {
      await api.unsave(key);
      setRemoved(current => [...current, key]);
    } catch (failure) {
      setRemoveError(failure);
    }
  };

  return (
    <>
      <section className="page-hero">
        <p className="eyebrow">Your library</p>
        <h1>Saved charts.</h1>
        <p className="lead">Indicators you have starred, kept with your account.</p>
      </section>
      <section className="section">
        {loading && <Loading label="Loading saved charts…" />}
        {error && <ErrorState error={error} onRetry={reload} />}
        {removeError && <ErrorState error={removeError} />}
        {!loading && !error && items.length === 0 && (
          <Empty>No saved charts yet. Open any indicator in <Link to="/explore">Explore</Link> and tap ☆ Save.</Empty>
        )}
        <div className="card-grid">
          {items.map(item => (
            <div key={item.indicator.key} className="saved-item">
              <IndicatorCard indicator={item.indicator} />
              <button type="button" className="btn btn-ghost btn-small" onClick={() => remove(item.indicator.key)}>
                Remove {item.indicator.title}
              </button>
            </div>
          ))}
        </div>
      </section>
    </>
  );
}
