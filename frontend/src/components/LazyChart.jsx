import { lazy, Suspense } from 'react';
import { useInView } from '../hooks.js';

const ChartView = lazy(() => import('./ChartView.jsx'));

// Defers loading chart.js and drawing the canvas until the chart scrolls near the viewport.
export default function LazyChart({ height = 180, eager = false, ...props }) {
  const [ref, inView] = useInView('300px');
  const show = eager || inView;
  return (
    <div ref={ref} className="lazy-chart" style={{ height }}>
      {show ? (
        <Suspense fallback={<div className="chart-skeleton" aria-hidden="true" />}>
          <ChartView {...props} />
        </Suspense>
      ) : <div className="chart-skeleton" aria-hidden="true" />}
    </div>
  );
}
