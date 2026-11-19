import { lazy, Suspense } from 'react';
import { Navigate, Route, Routes, useLocation } from 'react-router-dom';
import { AuthProvider, useAuth } from './auth.jsx';
import { CompareProvider } from './compare.jsx';
import Layout from './components/Layout.jsx';
import { Loading } from './components/States.jsx';
import Home from './pages/Home.jsx';
import AuthPage from './pages/AuthPage.jsx';

const Explore = lazy(() => import('./pages/Explore.jsx'));
const SubgroupRoute = lazy(() => import('./components/SubgroupPage.jsx').then(module => ({ default: module.SubgroupRoute })));
const Elections = lazy(() => import('./pages/Elections.jsx'));
const VoterRollPage = lazy(() => import('./pages/VoterRollPage.jsx'));
const Sources = lazy(() => import('./pages/Sources.jsx'));
const Indicator = lazy(() => import('./pages/Indicator.jsx'));
const Compare = lazy(() => import('./pages/Compare.jsx'));
const AiPage = lazy(() => import('./pages/AiPage.jsx'));
const About = lazy(() => import('./pages/About.jsx'));
const Articles = lazy(() => import('./pages/Articles.jsx'));
const PulsePage = lazy(() => import('./pages/PulsePage.jsx'));
const IndusScriptTranslator = lazy(() => import('./pages/IndusScriptTranslator.jsx'));
const Api = lazy(() => import('./pages/Api.jsx'));
const NotFound = lazy(() => import('./pages/NotFound.jsx'));

export function ProtectedRoute({ children }) {
  const { user, ready } = useAuth();
  const location = useLocation();

  if (!ready) {
    return <Loading label="Verifying access…" />;
  }

  if (!user) {
    const next = encodeURIComponent(`${location.pathname}${location.search}`);
    return <Navigate to={`/login?next=${next}`} replace />;
  }

  return children;
}

export function AppRoutes() {
  return (
    <Suspense fallback={<Loading />}>
      <Routes>
        <Route path="api" element={<Api />} />
        <Route path="embed/pulse/:slug" element={<PulsePage />} />
        <Route path="embed/pulse" element={<PulsePage />} />
        <Route element={<Layout />}>
          {/* Public authentication portal */}
          <Route path="login" element={<AuthPage />} />

          {/* Gated data and intelligence routes */}
          <Route index element={<ProtectedRoute><Home /></ProtectedRoute>} />
          <Route path="explore" element={<ProtectedRoute><Explore /></ProtectedRoute>} />
          <Route path="explore/:group" element={<ProtectedRoute><Explore /></ProtectedRoute>} />
          <Route path="explore/:group/:subgroup" element={<ProtectedRoute><SubgroupRoute /></ProtectedRoute>} />
          <Route path="explore/:group/:subgroup/:stateSlug" element={<ProtectedRoute><SubgroupRoute /></ProtectedRoute>} />
          <Route path="ai" element={<ProtectedRoute><AiPage /></ProtectedRoute>} />
          <Route path="ask-ai" element={<ProtectedRoute><AiPage /></ProtectedRoute>} />
          <Route path="metro" element={<ProtectedRoute><SubgroupRoute /></ProtectedRoute>} />
          <Route path="metro-in-maps" element={<ProtectedRoute><SubgroupRoute /></ProtectedRoute>} />
          <Route path="metro-atlas" element={<ProtectedRoute><SubgroupRoute /></ProtectedRoute>} />
          <Route path="delhi-metro" element={<ProtectedRoute><SubgroupRoute /></ProtectedRoute>} />
          <Route path="indian-metro-networks" element={<ProtectedRoute><SubgroupRoute /></ProtectedRoute>} />
          <Route path="maps" element={<ProtectedRoute><Explore /></ProtectedRoute>} />
          <Route path="maps/:subgroup" element={<ProtectedRoute><SubgroupRoute /></ProtectedRoute>} />
          <Route path="ivc-translator" element={<ProtectedRoute><IndusScriptTranslator /></ProtectedRoute>} />
          <Route path="elections" element={<ProtectedRoute><Elections /></ProtectedRoute>} />
          <Route path="elections/:stateSlug" element={<ProtectedRoute><Elections /></ProtectedRoute>} />
          <Route path="voter-list-sir-ssr" element={<ProtectedRoute><VoterRollPage /></ProtectedRoute>} />
          <Route path="pulse" element={<ProtectedRoute><PulsePage /></ProtectedRoute>} />
          <Route path="pulse/:slug" element={<ProtectedRoute><PulsePage /></ProtectedRoute>} />
          <Route path="sources" element={<ProtectedRoute><Sources /></ProtectedRoute>} />
          <Route path="indicator/:key" element={<ProtectedRoute><Indicator /></ProtectedRoute>} />
          <Route path="compare" element={<ProtectedRoute><Compare /></ProtectedRoute>} />
          <Route path="articles" element={<ProtectedRoute><Articles /></ProtectedRoute>} />
          <Route path="about" element={<ProtectedRoute><About /></ProtectedRoute>} />
          <Route path="*" element={<NotFound />} />
        </Route>
      </Routes>
    </Suspense>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <CompareProvider>
        <AppRoutes />
      </CompareProvider>
    </AuthProvider>
  );
}
