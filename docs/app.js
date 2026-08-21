const definitions = [
  ['cpi', 'CPI inflation', 'Consumer prices', 'Annual', '#63b3ed', '%', 'https://data.worldbank.org/indicator/FP.CPI.TOTL.ZG?locations=IN'],
  ['gst', 'GST collections', 'Gross monthly GST revenue', 'Monthly', '#f6c344', 'INR bn', 'https://www.gst.gov.in/'],
  ['fiscal_deficit', 'Fiscal deficit', 'Union fiscal deficit', 'Monthly', '#f56c6c', 'INR bn', 'https://cga.nic.in/'],
  ['iip', 'IIP growth', 'Industrial production', 'Annual', '#ff8f66', '%', 'https://www.mospi.gov.in/'],
  ['rupee', 'Rupee exchange rate', 'INR per US dollar', 'Daily', '#2ea44f', 'INR', 'https://data.rbi.org.in/DBIE/#/dbie/home'],
  ['trade', 'Trade share of GDP', 'Exports plus imports as share of GDP', 'Annual', '#63b3ed', '%', 'https://data.worldbank.org/indicator/NE.TRD.GNFS.ZS?locations=IN'],
  ['forex', 'Foreign exchange reserves', 'Total reserves including gold', 'Annual', '#a371f7', 'USD', 'https://data.worldbank.org/indicator/FI.RES.TOTL.CD?locations=IN'],
  ['bank_credit', 'Bank credit', 'Domestic credit to private sector', 'Annual', '#f56c6c', '%', 'https://data.worldbank.org/indicator/FS.AST.PRVT.GD.ZS?locations=IN'],
  ['wpi', 'WPI inflation', 'Wholesale price inflation', 'Monthly', '#f6c344', '%', 'https://eaindustry.nic.in/'],
  ['upi', 'UPI activity', 'UPI transaction value', 'Monthly', '#ff8f66', 'INR bn', 'https://www.npci.org.in/what-we-do/upi/product-statistics'],
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
  const data = await fetch(`data/chart-latest.json?ts=${Date.now()}`).then(response => response.json());
  document.querySelector('#generated').textContent = new Date(data.generated_at_utc).toLocaleString();
  const grid = document.querySelector('#charts');
  definitions.forEach(([key, title, subtitle, frequency, color, suffix, source], index) => {
    const series = data.series[key];
    const live = series && !series.error && series.values?.length;
    const card = document.createElement('article');
    card.className = 'chart-card';
    card.innerHTML = `<header><div><h2>${title}</h2><p>${subtitle} <span class="frequency">${frequency}</span></p></div><div><span class="status-pill ${live ? 'live' : ''}">${live ? 'Live' : 'Source adapter pending'}</span><button class="reset" type="button">Reset</button></div></header><div class="chart-wrap"><canvas id="chart-${index}"></canvas>${live ? '' : '<p class="empty-state">The official source is linked below. Values will appear when its public export adapter is available.</p>'}</div><a class="source-link" href="${source}" target="_blank" rel="noreferrer">Open official source</a>`;
    grid.append(card);
    if (!live) return;
    const labels = series.labels;
    const values = series.values;
    const chart = new Chart(card.querySelector('canvas'), {
      type: 'line',
      data: { labels, datasets: [{ data: values, borderColor: color, backgroundColor: `${color}25`, fill: true, borderWidth: 2.5, pointRadius: 3, pointHoverRadius: 5, tension: 0.28 }] },
      options: chartOptions(suffix),
    });
    const reset = card.querySelector('.reset');
    if (reset) reset.addEventListener('click', () => chart.resetZoom());
  });
}

main().catch(error => {
  document.querySelector('#charts').innerHTML = `<p>Dashboard data could not be loaded: ${error.message}</p>`;
});
