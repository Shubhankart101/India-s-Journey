import { lazy, Suspense } from 'react';
import { Route, Routes } from 'react-router-dom';
import { AuthProvider } from './auth.jsx';
import { CompareProvider } from './compare.jsx';
import Layout from './components/Layout.jsx';
import { Loading } from './components/States.jsx';
import Home from './pages/Home.jsx';

const Explore = lazy(() => import('./pages/Explore.jsx'));
const Indicator = lazy(() => import('./pages/Indicator.jsx'));
const Compare = lazy(() => import('./pages/Compare.jsx'));
const Saved = lazy(() => import('./pages/Saved.jsx'));
const AuthPage = lazy(() => import('./pages/AuthPage.jsx'));
const About = lazy(() => import('./pages/About.jsx'));
const NotFound = lazy(() => import('./pages/NotFound.jsx'));

export function AppRoutes() {
  return (
    <Suspense fallback={<Loading />}>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<Home />} />
          <Route path="explore" element={<Explore />} />
          <Route path="indicator/:key" element={<Indicator />} />
          <Route path="compare" element={<Compare />} />
          <Route path="saved" element={<Saved />} />
          <Route path="login" element={<AuthPage mode="login" />} />
          <Route path="register" element={<AuthPage mode="register" />} />
          <Route path="about" element={<About />} />
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
