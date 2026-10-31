import '@testing-library/jest-dom/vitest';
import { cleanup, configure } from '@testing-library/react';
import { afterEach, vi } from 'vitest';
import { clearApiCache } from '../api.js';

// Lazy chart chunks can take over a second to import on a busy machine; the default 1s findBy wait is flaky there.
configure({ asyncUtilTimeout: 5000 });

// Canvas rendering is not available in jsdom; render the chart config as data attributes instead.
vi.mock('react-chartjs-2', () => ({
  Chart: ({ type, data, options }) => (
    <div
      data-testid="chart"
      data-type={type}
      data-labels={JSON.stringify(data.labels)}
      data-datasets={data.datasets.length}
      data-values={JSON.stringify(data.datasets.map(dataset => dataset.data))}
      data-index-axis={options.indexAxis || ''}
    />
  ),
}));

// Recent Chromium returns a Promise from scrollTo; mirror that so effects that leak it as a cleanup fail in tests.
window.scrollTo = () => Promise.resolve();

afterEach(() => {
  cleanup();
  clearApiCache();
  localStorage.clear();
  document.cookie = 'csrftoken=; expires=Thu, 01 Jan 1970 00:00:00 GMT';
  vi.restoreAllMocks();
});
