import {
  ArcElement, BarController, BarElement, CategoryScale, Chart as ChartJS, DoughnutController, Filler, Legend, LinearScale,
  LineController, LineElement, PieController, PointElement, Tooltip,
} from 'chart.js';
import { Chart } from 'react-chartjs-2';
import { formatAxis, formatMagnitude, isRadial } from '../format.js';

ChartJS.register(
  ArcElement, BarController, BarElement, CategoryScale, DoughnutController, Filler, Legend, LinearScale,
  LineController, LineElement, PieController, PointElement, Tooltip,
);
ChartJS.defaults.color = '#a1a1a6';
ChartJS.defaults.font.family = '-apple-system, BlinkMacSystemFont, "SF Pro Text", "Helvetica Neue", Helvetica, Arial, sans-serif';

export const PALETTE = [
  '#ff9933', '#3fb950', '#58a6ff', '#bc8cff', '#ff7b72', '#f6c344', '#39c5bb', '#f778ba', '#a5d6ff', '#d2a8ff',
  '#ffa657', '#7ee787', '#e3b341', '#79c0ff', '#db61a2', '#56d364', '#ff6b6b', '#8b949e', '#d29922', '#a371f7',
];
const GRID = 'rgba(255, 255, 255, 0.08)';

// Pie slices: positive values only, largest first, with the long tail folded into "Other".
export function radialPoints(labels, values, maxSlices = 12) {
  const points = labels.map((label, index) => ({ label, raw: values[index], value: Number(values[index]) }))
    .filter(point => point.raw !== null && point.raw !== undefined && Number.isFinite(point.value) && point.value > 0)
    .map(({ label, value }) => ({ label, value }))
    .sort((left, right) => right.value - left.value);
  if (points.length <= maxSlices) return points;
  const rest = points.slice(maxSlices - 1);
  return [...points.slice(0, maxSlices - 1), { label: `Other (${rest.length})`, value: rest.reduce((sum, point) => sum + point.value, 0) }];
}

export function buildChartData({ labels, datasets, type, color }) {
  if (isRadial(type)) {
    const points = radialPoints(labels, datasets[0]?.values || []);
    return {
      labels: points.map(point => point.label),
      datasets: [{
        label: datasets[0]?.label || '',
        data: points.map(point => point.value),
        backgroundColor: points.map((_, index) => PALETTE[index % PALETTE.length]),
        borderColor: '#1c1c1e',
        borderWidth: 2,
        hoverOffset: 12,
      }],
    };
  }
  const many = labels.length > 60;
  return {
    labels,
    datasets: datasets.map((dataset, index) => {
      const lineColor = dataset.color || (index === 0 ? color : null) || PALETTE[(index + 2) % PALETTE.length];
      return {
        label: dataset.label,
        data: dataset.values,
        borderColor: lineColor,
        backgroundColor: type === 'bar' ? `${lineColor.slice(0, 7)}cc` : `${lineColor.slice(0, 7)}22`,
        fill: type === 'line' && datasets.length === 1,
        borderWidth: type === 'bar' ? 0 : 2.4,
        borderRadius: type === 'bar' ? 4 : 0,
        pointRadius: many || type === 'bar' ? 0 : 2,
        pointHoverRadius: 5,
        tension: 0.3,
        spanGaps: true,
      };
    }),
  };
}

export function buildOptions({ type, suffix, compact, horizontal, multi }) {
  const radial = isRadial(type);
  const tooltip = {
    enabled: !compact,
    backgroundColor: 'rgba(28, 28, 30, 0.96)',
    borderColor: 'rgba(255, 255, 255, 0.14)',
    borderWidth: 1,
    padding: 10,
    callbacks: {
      label: context => {
        const value = radial ? context.parsed : (horizontal ? context.parsed.x : context.parsed.y);
        if (radial) {
          const total = context.dataset.data.reduce((sum, item) => sum + item, 0);
          const share = total ? ` (${((value / total) * 100).toFixed(1)}%)` : '';
          return ` ${context.label}: ${formatMagnitude(value, suffix)}${share}`;
        }
        return ` ${context.dataset.label}: ${formatMagnitude(value, suffix)}`;
      },
    },
  };
  const options = {
    responsive: true,
    maintainAspectRatio: false,
    animation: compact ? false : { duration: 400 },
    interaction: radial ? undefined : { mode: 'index', intersect: false },
    plugins: {
      legend: {
        display: !compact && (radial || multi),
        position: radial ? 'right' : 'bottom',
        labels: { color: '#d2d2d7', boxWidth: 10, boxHeight: 10, usePointStyle: true, padding: 12 },
      },
      tooltip,
    },
  };
  if (radial) {
    options.cutout = type === 'doughnut' ? '58%' : 0;
    return options;
  }
  const valueAxis = {
    grid: { color: GRID },
    border: { display: false },
    ticks: { display: !compact, callback: value => formatAxis(value, suffix), maxTicksLimit: 6 },
  };
  const labelAxis = {
    grid: { display: false },
    border: { display: false },
    ticks: { display: !compact, maxRotation: 0, autoSkip: true, maxTicksLimit: horizontal ? 20 : 8 },
  };
  options.indexAxis = horizontal ? 'y' : 'x';
  options.scales = horizontal ? { x: valueAxis, y: labelAxis } : { x: labelAxis, y: valueAxis };
  if (compact) options.scales[horizontal ? 'x' : 'y'].grid.display = false;
  return options;
}

export default function ChartView({ labels = [], datasets = [], type = 'line', indexAxis = 'x', suffix = '', color = '#58a6ff', compact = false, title = 'Chart' }) {
  const horizontal = type === 'bar' && indexAxis === 'y';
  const data = buildChartData({ labels, datasets, type, color });
  const options = buildOptions({ type, suffix, compact, horizontal, multi: datasets.length > 1 });
  return (
    <div className={`chart-canvas${compact ? ' compact' : ''}`} role="img" aria-label={`${title} (${type} chart)`}>
      <Chart type={type === 'pie' ? 'pie' : type} data={data} options={options} />
    </div>
  );
}
