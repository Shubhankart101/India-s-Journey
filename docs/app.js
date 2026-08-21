const definitions = [
  ['cpi', 'India CPI Inflation', 'Annual consumer-price inflation', '#63b3ed', '%', 'https://data.worldbank.org/indicator/FP.CPI.TOTL.ZG?locations=IN'],
  ['NY.GDP.MKTP.KD.ZG', 'India GDP Growth', 'Annual real GDP growth', '#f6c344', '%', 'https://data.worldbank.org/indicator/NY.GDP.MKTP.KD.ZG?locations=IN'],
  ['NE.TRD.GNFS.ZS', 'India Trade Share of GDP', 'Exports plus imports as share of GDP', '#2ea44f', '%', 'https://data.worldbank.org/indicator/NE.TRD.GNFS.ZS?locations=IN'],
  ['FI.RES.TOTL.CD', 'India Foreign Exchange Reserves', 'Total reserves including gold; US dollars', '#a371f7', '', 'https://data.worldbank.org/indicator/FI.RES.TOTL.CD?locations=IN'],
  ['FS.AST.PRVT.GD.ZS', 'India Domestic Credit', 'Domestic credit to private sector as share of GDP', '#f56c6c', '%', 'https://data.worldbank.org/indicator/FS.AST.PRVT.GD.ZS?locations=IN'],
  ['NV.IND.TOTL.KD.ZG', 'India Industrial Growth', 'Annual industrial value-added growth', '#ff8f66', '%', 'https://data.worldbank.org/indicator/NV.IND.TOTL.KD.ZG?locations=IN'],
  ['substack', 'Publication Cadence', 'Polity and Policy public RSS feed; rolling 12-week count', '#63b3ed', '', 'https://politypolicy.substack.com/feed'],
];

const chartOptions = (suffix) => ({
  responsive: true,
  maintainAspectRatio: false,
  interaction: { mode: 'index', intersect: false },
  plugins: {
    legend: { display: false },
    tooltip: { backgroundColor: '#0d1117', titleColor: '#e8edf2', bodyColor: '#e8edf2', borderColor: '#2b3645', borderWidth: 1 },
    zoom: { pan: { enabled: true, mode: 'x' }, zoom: { wheel: { enabled: true }, pinch: { enabled: true }, mode: 'x' } },
  },
  scales: {
    x: { grid: { color: '#263241' }, ticks: { color: '#9aa8b6' } },
    y: { grid: { color: '#263241' }, ticks: { color: '#9aa8b6', callback: value => `${value}${suffix}` } },
  },
});

async function main() {
  const data = await fetch('data/chart-latest.json').then(response => response.json());
  document.querySelector('#generated').textContent = new Date(data.generated_at_utc).toLocaleString();
  const grid = document.querySelector('#charts');
  definitions.forEach(([key, title, subtitle, color, suffix, source], index) => {
    const series = key === 'cpi' ? data.cpi : key === 'substack' ? data.substack : data.world_bank[key];
    if (!series || series.error) return;
    const labels = series.years || series.weeks;
    const values = series.values || series.article_counts;
    const card = document.createElement('article');
    card.className = 'chart-card';
    card.innerHTML = `<header><div><h2>${title}</h2><p>${subtitle}</p></div><button class="reset" type="button">Reset</button></header><canvas id="chart-${index}"></canvas><a class="source-link" href="${source}" target="_blank" rel="noreferrer">Open source data</a>`;
    grid.append(card);
    const chart = new Chart(card.querySelector('canvas'), {
      type: 'line',
      data: { labels, datasets: [{ data: values, borderColor: color, backgroundColor: `${color}25`, fill: true, borderWidth: 2.5, pointRadius: 3, pointHoverRadius: 5, tension: 0.28 }] },
      options: chartOptions(suffix),
    });
    card.querySelector('.reset').addEventListener('click', () => chart.resetZoom());
  });
}

main().catch(error => {
  document.querySelector('#charts').innerHTML = `<p>Dashboard data could not be loaded: ${error.message}</p>`;
});
