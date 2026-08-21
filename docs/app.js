const definitions = [
  ['cpi', 'CPI inflation', 'Consumer prices', 'Annual', '#63b3ed', '%', 'https://data.worldbank.org/indicator/FP.CPI.TOTL.ZG?locations=IN', 'Consumer price inflation tracks the annual change in the cost of a representative basket of goods and services. It is a broad measure of household purchasing-power pressure.\n\nThe series is useful alongside growth, exchange-rate, and trade indicators because imported costs and domestic demand can move inflation in different directions. Values are annual and come through the World Bank open API.'],
  ['gst', 'GST collections', 'Gross monthly GST revenue', 'Monthly', '#f6c344', 'INR bn', 'https://www.gst.gov.in/', 'GST collections are a high-frequency signal of recorded consumption and production moving through India\'s indirect-tax system. Strong receipts can reflect higher activity, improved compliance, price effects, or a combination of these factors.\n\nThis card links to the official GST portal but remains pending until a stable public export can be consumed automatically. It should not be confused with a forecast or an estimate.'],
  ['fiscal_deficit', 'Fiscal deficit', 'Union fiscal deficit', 'Monthly', '#f56c6c', 'INR bn', 'https://cga.nic.in/', 'The fiscal deficit is the gap between government expenditure and receipts excluding borrowings. It indicates how much the public sector needs to finance during a fiscal year.\n\nThe Controller General of Accounts publishes the official Union accounts. This card remains pending until a stable machine-readable release is available, because monthly cumulative values require careful fiscal-year handling.'],
  ['iip', 'IIP growth', 'Industrial production', 'Annual', '#ff8f66', '%', 'https://www.mospi.gov.in/', 'Industrial production measures activity across mining, manufacturing, and electricity. It is a useful complement to GDP because it responds more directly to changes in factory output and infrastructure-linked production.\n\nThe current open series is an annual industrial value-added growth proxy. MOSPI is the authoritative Indian source for the higher-frequency IIP release.'],
  ['rupee', 'Rupee exchange rate proxy', 'Official exchange rate, INR per US dollar', 'Annual', '#2ea44f', 'INR', 'https://data.worldbank.org/indicator/PA.NUS.FCRF?locations=IN', 'This series expresses the Indian rupee required to purchase one US dollar. A rising value means rupee depreciation against the dollar, all else equal.\n\nThe dashboard uses the annual official exchange-rate series as a stable public proxy. Daily RBI market data is linked separately in the source list but is not represented as annual data.'],
  ['trade', 'Trade share of GDP', 'Exports plus imports as share of GDP', 'Annual', '#63b3ed', '%', 'https://data.worldbank.org/indicator/NE.TRD.GNFS.ZS?locations=IN', 'Trade openness compares the combined value of exports and imports with GDP. It gives context for how strongly India\'s output is connected to external demand, imported inputs, and global price movements.\n\nThis is a ratio rather than a rupee total, so it can rise because trade grows or because GDP changes. The series is sourced through the World Bank open API.'],
  ['forex', 'Foreign exchange reserves', 'Total reserves including gold', 'Annual', '#a371f7', 'USD', 'https://data.worldbank.org/indicator/FI.RES.TOTL.CD?locations=IN', 'Foreign-exchange reserves are external assets held by the monetary authority, including gold in this indicator. They help provide resilience against external-payment stress and exchange-rate volatility.\n\nReserve adequacy should be read with imports, debt, and the current account rather than treated as a standalone score. The displayed series is annual and denominated in current US dollars.'],
  ['bank_credit', 'Bank credit', 'Domestic credit to private sector', 'Annual', '#f56c6c', '%', 'https://data.worldbank.org/indicator/FS.AST.PRVT.GD.ZS?locations=IN', 'Domestic credit to the private sector measures financial-sector lending relative to the size of the economy. It can signal whether businesses and households have expanding or tightening access to finance.\n\nCredit growth is not automatically positive: the composition, repayment quality, and cost of borrowing matter. This annual ratio is a structural indicator, not a substitute for RBI monthly banking statistics.'],
  ['wpi', 'WPI inflation', 'Wholesale price inflation', 'Monthly', '#f6c344', '%', 'https://eaindustry.nic.in/', 'Wholesale price inflation tracks price movement at the producer and bulk-trade level. It can reveal input-cost pressure before those changes fully appear in consumer prices.\n\nThe Office of the Economic Adviser publishes the official Indian WPI release. This card remains pending until the portal exposes a stable automated export that can be checked without brittle page scraping.'],
  ['upi', 'UPI activity', 'UPI transaction value', 'Monthly', '#ff8f66', 'INR bn', 'https://www.npci.org.in/what-we-do/upi/product-statistics', 'UPI transaction value shows the scale of digital payments processed through India\'s real-time payments infrastructure. It is a useful activity and digitisation signal, especially when paired with transaction counts.\n\nNPCI publishes the authoritative product statistics. This card remains pending until its public statistics can be consumed reliably by the scheduled data pipeline.'],
  ['gdp_per_capita', 'GDP per capita', 'Current US dollars per person', 'Annual', '#d2a8ff', ' USD', 'https://data.worldbank.org/indicator/NY.GDP.PCAP.CD?locations=IN', 'GDP per capita divides the value of economic output by population. It is a broad scale indicator for comparing the economy over time, but it does not describe inequality, household income, or quality of life by itself.\n\nThe current-dollar series is sensitive to exchange rates and inflation. Read it alongside real growth and purchasing-power measures for a more complete picture.'],
  ['population', 'Population', 'Total population', 'Annual', '#79c0ff', '', 'https://data.worldbank.org/indicator/SP.POP.TOTL?locations=IN', 'Population provides the denominator and demographic context for many other indicators. A growing population can expand the workforce and consumer base while also increasing demand for jobs, housing, health, and infrastructure.\n\nThis is a count of people, not a welfare measure. Per-capita indicators and age structure are needed to understand how demographic change affects living standards.'],
  ['unemployment', 'Unemployment rate', 'Share of the labour force without work', 'Annual', '#ffa657', '%', 'https://data.worldbank.org/indicator/SL.UEM.TOTL.ZS?locations=IN', 'The unemployment rate measures the share of the labour force that is without work but available for and seeking employment. It does not capture underemployment or people who have stopped looking for work.\n\nLabour-market comparisons require care because survey design and informal employment affect measurement. This annual series is a useful macro context signal rather than a complete employment dashboard.'],
  ['current_account', 'Current account balance', 'Balance as share of GDP', 'Annual', '#56d364', '%', 'https://data.worldbank.org/indicator/BN.CAB.XOKA.GD.ZS?locations=IN', 'The current account records trade in goods and services, income flows, and transfers with the rest of the world. A deficit means the country is spending more foreign exchange on these flows than it receives during the period.\n\nThis indicator connects directly to reserves, the rupee, and external financing conditions. It is shown as a share of GDP to make changes in national scale easier to compare.'],
  ['broad_money', 'Broad money', 'Money supply as share of GDP', 'Annual', '#ff7b72', '%', 'https://data.worldbank.org/indicator/FM.LBL.BMNY.GD.ZS?locations=IN', 'Broad money captures currency and deposits available across the financial system. Relative to GDP, it provides a long-run view of liquidity and financial deepening.\n\nIt is not a direct measure of inflation or spending. Credit conditions, velocity, policy rates, and the distribution of deposits all influence how money supply affects the economy.'],
  ['tax_revenue', 'Tax revenue', 'Tax revenue as share of GDP', 'Annual', '#e3b341', '%', 'https://data.worldbank.org/indicator/GC.TAX.TOTL.GD.ZS?locations=IN', 'Tax revenue shows how much public revenue is collected through taxes relative to the size of the economy. It helps put fiscal capacity and public-service financing in a longer-run context.\n\nThe ratio can change because collections move, GDP moves, or both. It does not identify tax burden distribution or distinguish every type of levy.'],
  ['government_consumption', 'Government consumption', 'General government final consumption', 'Annual', '#58a6ff', '% GDP', 'https://data.worldbank.org/indicator/NE.CON.GOVT.ZS?locations=IN', 'Government final consumption measures public-sector spending on goods and services relative to GDP. It is a useful context signal for the size of direct government demand in the economy.\n\nThis is not the same as the fiscal deficit: transfers, capital spending, receipts, and borrowing are treated differently in national accounts.'],
  ['fdi', 'Foreign direct investment', 'Net FDI inflows as share of GDP', 'Annual', '#3fb950', '%', 'https://data.worldbank.org/indicator/BX.KLT.DINV.WD.GD.ZS?locations=IN', 'Foreign direct investment captures net cross-border investment intended to establish a lasting interest in an enterprise. Relative to GDP, it shows how important foreign investment flows are compared with national output.\n\nA single year can be volatile because of large transactions, restructurings, or exceptional deals. It should be read with the current account and reserves.'],
  ['domestic_savings', 'Domestic savings', 'Gross domestic savings as share of GDP', 'Annual', '#bc8cff', '%', 'https://data.worldbank.org/indicator/NY.GDS.TOTL.ZS?locations=IN', 'Gross domestic savings is the portion of national output not used for final consumption. It provides a macro view of the resources potentially available for domestic investment.\n\nThe indicator does not show which households, firms, or public institutions save, nor whether savings are invested productively. Its value is strongest when compared with investment and external financing.'],
  ['electricity_access', 'Electricity access', 'Population with access to electricity', 'Annual', '#79c0ff', '%', 'https://data.worldbank.org/indicator/EG.ELC.ACCS.ZS?locations=IN', 'Electricity access measures the share of the population with access to electricity. It is a core infrastructure and living-conditions indicator with direct relevance to households, schools, businesses, and digital services.\n\nCoverage does not fully describe reliability, affordability, or quality of supply. The series is annual and sourced through the open World Bank API.'],
  ['internet_users', 'Internet users', 'Individuals using the internet', 'Annual', '#f778ba', '%', 'https://data.worldbank.org/indicator/IT.NET.USER.ZS?locations=IN', 'Internet use measures the share of people using the internet. It provides a broad signal of digital access and the potential reach of online services, payments, education, and commerce.\n\nThe metric does not measure connection speed, affordability, quality, or intensity of use. Those dimensions require more detailed telecom and household datasets.'],
  ['life_expectancy', 'Life expectancy', 'Life expectancy at birth', 'Annual', '#ff7b72', ' years', 'https://data.worldbank.org/indicator/SP.DYN.LE00.IN?locations=IN', 'Life expectancy at birth estimates the average years a newborn would live under current mortality conditions. It is a high-level outcome indicator for population health and social development.\n\nIt is not an individual prediction and does not reveal regional, gender, or income differences. Trends should be interpreted alongside health-system and demographic data.'],
];

const formatMagnitude = (value, suffix = '') => {
  const absolute = Math.abs(value);
  const units = [
    [1e12, 'trillion'],
    [1e9, 'billion'],
    [1e6, 'million'],
    [1e3, 'thousand'],
  ];
  const unit = units.find(([threshold]) => absolute >= threshold);
  if (!unit) return `${Number(value).toLocaleString(undefined, { maximumFractionDigits: 2 })}${suffix}`;
  const amount = value / unit[0];
  return `${amount.toLocaleString(undefined, { maximumFractionDigits: 2 })} ${unit[1]}${suffix}`;
};

const chartOptions = (suffix) => ({
  responsive: true,
  maintainAspectRatio: false,
  interaction: { mode: 'index', intersect: false },
  plugins: {
    legend: { display: false },
    tooltip: { backgroundColor: '#0d1117', titleColor: '#e8edf2', bodyColor: '#e8edf2', borderColor: '#2b3645', borderWidth: 1, callbacks: { label: context => ` ${formatMagnitude(context.parsed.y, suffix)}` } },
    zoom: { pan: { enabled: true, mode: 'x' }, zoom: { wheel: { enabled: true }, pinch: { enabled: true }, mode: 'x' } },
  },
  scales: {
    x: { grid: { color: '#263241' }, ticks: { color: '#9aa8b6' } },
    y: { grid: { color: '#263241' }, ticks: { color: '#9aa8b6', callback: value => formatMagnitude(value, suffix) } },
  },
});

async function main() {
  const data = await fetch(`data/chart-latest.json?ts=${Date.now()}`).then(response => response.json());
  document.querySelector('#generated').textContent = new Date(data.generated_at_utc).toLocaleString();
  const grid = document.querySelector('#charts');
  definitions.forEach(([key, title, subtitle, frequency, color, suffix, source, details], index) => {
    const series = data.series[key];
    const live = series && !series.error && series.values?.length;
    const card = document.createElement('article');
    card.className = 'chart-card';
    const paragraphs = details.split('\\n\\n').map(paragraph => `<p>${paragraph}</p>`).join('');
    card.dataset.title = `${title} ${subtitle}`.toLowerCase();
    card.dataset.state = live ? 'live' : 'pending';
    const context = live ? `This ${frequency.toLowerCase()} series contains ${series.values.length} available observations. Values are fetched from the cited public source and plotted without smoothing.` : 'This indicator is retained for source visibility, but no numeric values are shown until its official export can be checked automatically.';
    card.innerHTML = `<header><div><h2>${title}</h2><p>${subtitle} <span class="frequency">${frequency}</span></p></div><div><span class="status-pill ${live ? 'live' : ''}">${live ? 'Live' : 'Source adapter pending'}</span><button class="reset" type="button">Reset</button></div></header><div class="chart-wrap"><canvas id="chart-${index}"></canvas>${live ? '' : '<p class="empty-state">The official source is linked below. Values will appear when its public export adapter is available.</p>'}</div><details class="insight"><summary>Read the indicator note</summary><div>${paragraphs}<p><strong>Data context:</strong> ${context}</p></div></details><a class="source-link" href="${source}" target="_blank" rel="noreferrer">Open official source</a>`;
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
  const cards = [...grid.children];
  const filter = document.querySelector('#chart-filter');
  const search = document.querySelector('#chart-search');
  const updateCards = () => {
    const query = search.value.trim().toLowerCase();
    cards.forEach(card => { card.hidden = (filter.value !== 'all' && card.dataset.state !== filter.value) || (query && !card.dataset.title.includes(query)); });
  };
  filter.addEventListener('change', updateCards);
  search.addEventListener('input', updateCards);
  updateCards();
}

main().catch(error => {
  document.querySelector('#charts').innerHTML = `<p>Dashboard data could not be loaded: ${error.message}</p>`;
});
