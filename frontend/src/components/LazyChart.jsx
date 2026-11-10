import { lazy, Suspense } from 'react';
import { useVisible } from '../hooks.js';

const ChartView = lazy(() => import('./ChartView.jsx'));

const CANVAS_TYPES = new Set(['line', 'bar', 'pie', 'doughnut', 'radar', 'polarArea', 'scatter', 'area']);

// Loads chart.js and draws the chart only while the card is near the viewport; charts that scroll far away are destroyed.
// Canvas charts need a fixed height; maps, atlases and journey views size to their content so they never spill into what follows.
export default function LazyChart({ height = 180, eager = false, ...props }) {
  const [ref, visible] = useVisible('500px');
  const show = eager || visible;
  const flows = !CANVAS_TYPES.has(props.type) && !props.compact;
  return (
    <div ref={ref} className={`lazy-chart${flows ? ' lazy-chart-flow' : ''}`} style={flows ? { minHeight: height } : { height }}>
      {show ? (
        <Suspense fallback={<div className="chart-skeleton" aria-hidden="true" />}>
          <ChartView {...props} />
        </Suspense>
      ) : <div className="chart-skeleton" aria-hidden="true" />}
    </div>
  );
}
