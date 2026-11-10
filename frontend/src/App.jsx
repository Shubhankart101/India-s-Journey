import { lazy, Suspense } from 'react';
import { Route, Routes } from 'react-router-dom';
import { CompareProvider } from './compare.jsx';
import Layout from './components/Layout.jsx';
import { Loading } from './components/States.jsx';
import Home from './pages/Home.jsx';

const Explore = lazy(() => import('./pages/Explore.jsx'));
const SubgroupRoute = lazy(() => import('./components/SubgroupPage.jsx').then(module => ({ default: module.SubgroupRoute })));
const Elections = lazy(() => import('./pages/Elections.jsx'));
const VoterRollPage = lazy(() => import('./pages/VoterRollPage.jsx'));
const Sources = lazy(() => import('./pages/Sources.jsx'));
const Indicator = lazy(() => import('./pages/Indicator.jsx'));
const Compare = lazy(() => import('./pages/Compare.jsx'));
const About = lazy(() => import('./pages/About.jsx'));
const Articles = lazy(() => import('./pages/Articles.jsx'));
const Api = lazy(() => import('./pages/Api.jsx'));
const NotFound = lazy(() => import('./pages/NotFound.jsx'));

export function AppRoutes() {
  return (
    <Suspense fallback={<Loading />}>
      <Routes>
        <Route path="api" element={<Api />} />
        <Route element={<Layout />}>
          <Route index element={<Home />} />
          <Route path="explore" element={<Explore />} />
          <Route path="explore/:group/:subgroup" element={<SubgroupRoute />} />
          <Route path="explore/:group/:subgroup/:stateSlug" element={<SubgroupRoute />} />
          <Route path="elections" element={<Elections />} />
          <Route path="elections/:stateSlug" element={<Elections />} />
          <Route path="voter-list-sir-ssr" element={<VoterRollPage />} />
          <Route path="sources" element={<Sources />} />
          <Route path="indicator/:key" element={<Indicator />} />
          <Route path="compare" element={<Compare />} />
          <Route path="articles" element={<Articles />} />
          <Route path="about" element={<About />} />
          <Route path="*" element={<NotFound />} />
        </Route>
      </Routes>
    </Suspense>
  );
}

export default function App() {
  return (
    <CompareProvider>
      <AppRoutes />
    </CompareProvider>
  );
}
