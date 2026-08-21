const definitions = [
  ['cpi', 'CPI inflation', 'Consumer prices', 'Annual', '#63b3ed', '%', 'https://data.worldbank.org/indicator/FP.CPI.TOTL.ZG?locations=IN', 'Consumer price inflation tracks the annual change in the cost of a representative basket of goods and services. It is a broad measure of household purchasing-power pressure.\n\nThe series is useful alongside growth, exchange-rate, and trade indicators because imported costs and domestic demand can move inflation in different directions. Values are annual and come through the World Bank open API.'],
  ['gst', 'GST collections', 'Gross monthly GST revenue', 'Monthly', '#f6c344', 'INR bn', 'https://www.gst.gov.in/', 'GST collections are a high-frequency signal of recorded consumption and production moving through India\'s indirect-tax system. Strong receipts can reflect higher activity, improved compliance, price effects, or a combination of these factors.\n\nThe monthly series is collated from the Economic Survey Statistical Appendix table 9.1. It should not be confused with a forecast or an estimate.'],
  ['fiscal_deficit', 'Fiscal deficit', 'Union fiscal deficit as share of GDP', 'Annual', '#f56c6c', '% GDP', 'https://www.indiabudget.gov.in/economicsurvey/doc/stat/tab2.4.xlsx', 'The fiscal deficit is the gap between government expenditure and receipts excluding borrowings. It indicates how much the public sector needs to finance during a fiscal year.\n\nThe annual series is collated from official Economic Survey table 2.4 Excel files across previous editions and reported as a share of GDP.'],
  ['iip', 'IIP growth', 'Industrial production', 'Monthly', '#ff8f66', '%', 'https://www.mospi.gov.in/', 'Industrial production measures activity across mining, manufacturing, and electricity. It is a useful complement to GDP because it responds more directly to changes in factory output and infrastructure-linked production.\n\nThe monthly General IIP index is collated from Economic Survey Statistical Appendix table 9.2; MOSPI remains the authoritative Indian source.'],
  ['rupee', 'Rupee exchange rate', 'INR per US dollar', 'Monthly', '#2ea44f', 'INR', 'https://data.rbi.org.in/DBIE/#/dbie/home', 'This series expresses the Indian rupee required to purchase one US dollar. A rising value means rupee depreciation against the dollar, all else equal.\n\nMonthly exchange-rate observations are collated from Economic Survey Statistical Appendix table 9.4, with RBI DBIE linked as the official portal.'],
  ['trade', 'Trade share of GDP', 'Exports plus imports as share of GDP', 'Annual', '#63b3ed', '%', 'https://data.worldbank.org/indicator/NE.TRD.GNFS.ZS?locations=IN', 'Trade openness compares the combined value of exports and imports with GDP. It gives context for how strongly India\'s output is connected to external demand, imported inputs, and global price movements.\n\nThis is a ratio rather than a rupee total, so it can rise because trade grows or because GDP changes. The series is sourced through the World Bank open API.'],
  ['forex', 'Foreign exchange reserves', 'Total reserves including gold', 'Annual', '#a371f7', 'USD', 'https://data.worldbank.org/indicator/FI.RES.TOTL.CD?locations=IN', 'Foreign-exchange reserves are external assets held by the monetary authority, including gold in this indicator. They help provide resilience against external-payment stress and exchange-rate volatility.\n\nReserve adequacy should be read with imports, debt, and the current account rather than treated as a standalone score. The displayed series is annual and denominated in current US dollars.'],
  ['bank_credit', 'Bank credit', 'Domestic credit to private sector', 'Annual', '#f56c6c', '%', 'https://data.worldbank.org/indicator/FS.AST.PRVT.GD.ZS?locations=IN', 'Domestic credit to the private sector measures financial-sector lending relative to the size of the economy. It can signal whether businesses and households have expanding or tightening access to finance.\n\nCredit growth is not automatically positive: the composition, repayment quality, and cost of borrowing matter. This annual ratio is a structural indicator, not a substitute for RBI monthly banking statistics.'],
  ['wpi', 'WPI inflation', 'Wholesale price inflation', 'Monthly', '#f6c344', '%', 'https://eaindustry.nic.in/', 'Wholesale price inflation tracks price movement at the producer and bulk-trade level. It can reveal input-cost pressure before those changes fully appear in consumer prices.\n\nWPI is not included in the Economic Survey monthly HFI tables used by this pipeline. The Office of the Economic Adviser remains the official source, but its public portal does not currently expose a stable automated export for this dashboard.'],
  ['upi', 'UPI activity', 'UPI transaction volume', 'Monthly', '#ff8f66', 'Lakh', 'https://www.npci.org.in/what-we-do/upi/product-statistics', 'UPI transaction volume shows the scale of digital payments processed through India\'s real-time payments infrastructure. It is a useful activity and digitisation signal, especially when paired with transaction value.\n\nThe monthly volume series is collated from Economic Survey Statistical Appendix table 9.2; NPCI remains the authoritative product-statistics source.'],
  ['power_consumption', 'Power consumption', 'Electricity demand', 'Monthly', '#79c0ff', 'GWh', 'https://www.indiabudget.gov.in/economicsurvey/doc/stat/tab91.pdf', 'Power consumption is a high-frequency activity signal that reflects demand from households, services, and industry. It can move with weather, economic activity, and electrification.\n\nThe monthly series is collated from Economic Survey Statistical Appendix table 9.1. It measures electricity use, not generation capacity or reliability.'],
  ['eway_bills', 'E-way bills', 'Goods movement compliance volume', 'Monthly', '#56d364', 'million', 'https://www.indiabudget.gov.in/economicsurvey/doc/stat/tab91.pdf', 'E-way bills track electronically documented movement of goods. They provide a useful logistics and formal-commerce signal that complements GST collections.\n\nThe series is a transaction volume, not a rupee value or direct GDP estimate. It is collated from Economic Survey table 9.1.'],
  ['rail_freight', 'Rail freight traffic', 'Domestic rail freight', 'Monthly', '#f2cc60', 'thousand tonnes', 'https://www.indiabudget.gov.in/economicsurvey/doc/stat/tab91.pdf', 'Rail freight traffic reflects movement of bulk commodities and industrial inputs through the rail network. It provides a physical-economy signal alongside digital and tax indicators.\n\nThe series is reported in thousand tonnes and comes from Economic Survey table 9.1.'],
  ['port_cargo', 'Port cargo traffic', 'Cargo handled at ports', 'Monthly', '#d2a8ff', 'lakh tonnes', 'https://www.indiabudget.gov.in/economicsurvey/doc/stat/tab91.pdf', 'Port cargo traffic captures goods handled through India\'s ports and gives context for external trade and domestic supply chains.\n\nIt is a volume measure and should be read with merchandise exports, imports, and trade share rather than used as a price indicator.'],
  ['core_industries', 'Eight-core industries', 'Core industrial production index', 'Monthly', '#ff7b72', 'index', 'https://www.indiabudget.gov.in/economicsurvey/doc/stat/tab92.pdf', 'The eight-core industries index tracks major infrastructure-linked sectors including coal, crude oil, natural gas, refinery products, fertilisers, steel, cement, and electricity.\n\nIt is an important industrial activity companion to IIP and is collated from Economic Survey table 9.2.'],
  ['crude_oil', 'Indian crude oil basket', 'Average crude oil price', 'Monthly', '#ffa657', 'USD/barrel', 'https://www.indiabudget.gov.in/economicsurvey/doc/stat/tab93.pdf', 'The Indian crude oil basket price tracks an indicative average of crude prices relevant to India\'s import exposure. It helps explain fuel-cost pressure, inflation risk, and the external trade bill.\n\nThis is a crude price indicator, not a retail petrol or diesel price index. It is collated from Economic Survey table 9.3.'],
  ['fuel_consumption', 'Fuel consumption', 'Petroleum product consumption', 'Monthly', '#f778ba', 'million MT', 'https://www.indiabudget.gov.in/economicsurvey/doc/stat/tab94.pdf', 'Fuel consumption measures petroleum product demand and is a useful activity proxy for transport, industry, and household energy use.\n\nIt is not a fuel price index. The dashboard labels it explicitly as consumption and sources it from Economic Survey table 9.4.'],
  ['merchandise_exports', 'Merchandise exports', 'Goods exports', 'Monthly', '#3fb950', 'USD bn', 'https://www.indiabudget.gov.in/economicsurvey/doc/stat/tab94.pdf', 'Merchandise exports measure the value of goods sold abroad. They connect the dashboard to external demand, foreign exchange earnings, and manufacturing competitiveness.\n\nThe monthly values are collated from Economic Survey table 9.4 and should be interpreted with imports and the current account.'],
  ['merchandise_imports', 'Merchandise imports', 'Goods imports', 'Monthly', '#bc8cff', 'USD bn', 'https://www.indiabudget.gov.in/economicsurvey/doc/stat/tab94.pdf', 'Merchandise imports measure the value of goods purchased from abroad. They capture domestic demand, imported inputs, energy exposure, and pressure on the trade balance.\n\nThe monthly values are collated from Economic Survey table 9.4 and are not the same as total services-inclusive imports.'],
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
  ['homicide_rate', 'Intentional homicide rate', 'Intentional homicides per 100,000 people', 'Annual', '#ff7b72', ' per 100k', 'https://data.worldbank.org/indicator/VC.IHR.PSRC.P5?locations=IN', 'The intentional homicide rate is a broad violence indicator measuring deaths caused by another person per 100,000 population. It is useful as a long-run public-safety context signal, but it does not cover every violent incident.\n\nThe World Bank series provides modern historical coverage and should be interpreted alongside NCRB crime data, whose definitions and reporting systems vary by year.'],
  ['lwe_incidents', 'Maoist / LWE deaths', 'People killed in LWE violence, official aggregate', '2004-2025', '#f85149', ' deaths', 'https://www.mha.gov.in/en/divisionofmha/left-wing-extremism-division', 'The Ministry of Home Affairs identifies CPI (Maoist) as the major Left-Wing Extremist organization and reports national LWE context.\n\nThe live value is the official MHA aggregate of people killed between 2004 and 2025. It is intentionally shown as an aggregate period, not as invented annual incident counts.'],
  ['terror_attacks', 'Terrorist attacks', 'India attacks in GTD-derived open data', '1970-2020', '#d29922', ' attacks', 'https://www.start.umd.edu/gtd/', 'The Global Terrorism Database is a reputable open research dataset covering terrorist events internationally from 1970 onward. This dashboard uses the India rows published by Our World in Data, with GTD provenance.\n\nIt is not an official Government of India dataset, and its event definitions differ from MHA and NCRB reporting. The series is not presented as a complete 1947-present history.'],
    ['terror_fatalities', 'Terrorism fatalities', 'Deaths in India GTD-derived attacks', '1970-2020', '#f85149', ' deaths', 'https://ourworldindata.org/grapher/terrorism-deaths.csv', 'This graph counts fatalities associated with India rows in the GTD-derived public series. It complements the attack-count graph by showing human cost rather than event frequency.\n\nIt is not an official Government of India dataset and does not provide a complete 1947-present history.'],
  ['ncrb_crime', 'NCRB crime indicators', 'Crime in India official tables', 'Edition-based', '#f778ba', ' records', 'https://ncrb.gov.in/crime-in-india.html', 'The National Crime Records Bureau publishes Crime in India tables covering reported offences, crime rates, and related public-safety measures.\n\nNCRB tables are edition-based and definitions change across reporting periods, so this card remains a source-status entry until a comparable machine-readable series can be collated without mixing incompatible classifications.'],
    ['violent_incidents', 'Overall violent incidents', 'Comparable all-India incident series', 'Coverage pending', '#ff7b72', ' incidents', 'https://ncrb.gov.in/crime-in-india.html', 'No single official open series currently combines violent crime, Maoist violence, and terrorism consistently across India.\n\nThis card stays visible as a research target so the dashboard does not add incompatible NCRB, MHA, and GTD definitions into a misleading total.'],
    ['lwe_civilian_casualties', 'LWE civilian casualties', 'Civilian casualty category', '2004-present', '#ff7b72', ' deaths', 'https://www.mha.gov.in/en/divisionofmha/left-wing-extremism-division', 'MHA describes civilian and security-force casualties in LWE violence, but the current public page does not expose a stable annual category table.\n\nThe category is visible for future official extraction and is not populated with inferred shares of the aggregate.'],
    ['lwe_security_force_casualties', 'LWE security-force casualties', 'Security-force casualty category', '2004-present', '#f2cc60', ' deaths', 'https://www.mha.gov.in/en/divisionofmha/left-wing-extremism-division', 'MHA identifies security-force casualties as a distinct LWE impact category, but no stable annual machine-readable series is currently published on the public page.\n\nThis card remains pending until official category counts can be verified.'],
    ['lwe_perpetrator_casualties', 'LWE perpetrator casualties', 'Maoist/LWE perpetrator casualty category', '2004-present', '#d29922', ' deaths', 'https://www.mha.gov.in/en/divisionofmha/left-wing-extremism-division', 'The public MHA material does not provide a comparable annual perpetrator-casualty series.\n\nThis card is retained to make the requested dimension explicit without constructing values from unsupported assumptions.'],
  ['indian_matrix', 'Indian Matrix publication cadence', 'Articles published per week', 'Weekly', '#bc8cff', ' articles', 'https://substack.com/@indianmatrix', 'This graph tracks the public publication cadence of Indian Matrix articles. It adds the Substack source as a transparent, updateable public-data signal rather than treating article frequency as an economic or crime statistic.\n\nThe weekly RSS snapshot is collected by the pipeline and linked to Indian Matrix with appreciation for its visual public-data work.'],
  ['market_indices', 'Indian market indices', 'Sensex, Nifty, and Nifty VIX; rebased to 100', 'Monthly', '#58a6ff', ' index', 'https://www.indiabudget.gov.in/economicsurvey/doc/stat/tab9.3.pdf', 'This combined graph compares India\'s major equity-market indices and volatility using one normalized base-100 view. It makes direction and relative movement readable despite the different scales of the Sensex, Nifty, and VIX.\n\nThe monthly observations are collated from Economic Survey table 9.3. This is a market-context dashboard, not investment advice, and rebasing means the plotted values are relative rather than index levels.'],
];

const categoryFor = key => ['homicide_rate', 'lwe_incidents', 'terror_attacks', 'ncrb_crime'].includes(key) ? 'Crime & Security' : ['population', 'unemployment', 'electricity_access', 'internet_users', 'life_expectancy'].includes(key) ? 'Social' : 'Economic';

const formatMagnitude = (value, suffix = '') => {
  const declaredUnit = /thousand|million|lakh|gwh|mt|tonnes|usd\/barrel|usd bn|inr bn|incidents|attacks|deaths/i.test(suffix);
  const formattedValue = Number(value).toLocaleString(undefined, { maximumFractionDigits: 2 });
  if (declaredUnit) return `${formattedValue}${suffix ? ` ${suffix}` : ''}`;
  const absolute = Math.abs(value);
  const units = [
    [1e12, 'trillion'],
    [1e9, 'billion'],
    [1e6, 'million'],
    [1e3, 'thousand'],
  ];
  const unit = units.find(([threshold]) => absolute >= threshold);
  if (!unit) return `${formattedValue}${suffix ? ` ${suffix}` : ''}`;
  const amount = value / unit[0];
  return `${amount.toLocaleString(undefined, { maximumFractionDigits: 2 })} ${unit[1]}${suffix ? ` ${suffix}` : ''}`;
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
    y: { grid: { color: '#263241' }, ticks: { color: '#9aa8b6', maxTicksLimit: 6, padding: 8, callback: value => formatMagnitude(value, suffix) } },
  },
});

async function main() {
  const articleLinks = document.querySelector('#article-links');
  const articlePromise = fetch(`data/substack-latest.json?ts=${Date.now()}`, { signal: AbortSignal.timeout(8000) })
    .then(response => response.ok ? response.json() : { articles: [] })
    .catch(() => ({ articles: [] }));
  const [data, articles, economicSurvey, indianMatrix] = await Promise.all([
    fetch(`data/chart-latest.json?ts=${Date.now()}`).then(response => response.json()),
    articlePromise,
    fetch(`data/economic-survey-monthly.json?ts=${Date.now()}`).then(response => response.ok ? response.json() : { series: {} }).catch(() => ({ series: {} })),
    fetch(`data/indian-matrix-latest.json?ts=${Date.now()}`).then(response => response.ok ? response.json() : { cadence: { labels: [], values: [] }, articles: [] }).catch(() => ({ cadence: { labels: [], values: [] }, articles: [] })),
  ]);
  data.series = { ...data.series, ...economicSurvey.series };
  data.series.indian_matrix = { labels: indianMatrix.cadence.labels, values: indianMatrix.cadence.values, source: 'Indian Matrix public RSS feed' };
  const marketKeys = ['sensex', 'nifty', 'nifty_vix'];
  const marketLabels = [...new Set(marketKeys.flatMap(key => data.series[key]?.labels || []))].sort();
  const marketDatasets = marketKeys.map(key => {
    const series = data.series[key] || {};
    const values = new Map((series.labels || []).map((label, index) => [label, series.values[index]]));
    const first = [...values.values()].find(value => value !== null && value !== undefined);
    return { label: key === 'sensex' ? 'Sensex' : key === 'nifty' ? 'Nifty' : 'Nifty VIX', data: marketLabels.map(label => values.has(label) ? values.get(label) / first * 100 : null), borderColor: key === 'sensex' ? '#58a6ff' : key === 'nifty' ? '#3fb950' : '#f2cc60', backgroundColor: 'transparent', borderWidth: 2.5, pointRadius: 2, tension: 0.25, spanGaps: true };
  });
  data.series.market_indices = { labels: marketLabels, datasets: marketDatasets };
  document.querySelector('#generated').textContent = new Date(data.generated_at_utc).toLocaleString();
  articleLinks.replaceChildren();
  const articleItems = (indianMatrix.articles || []).slice(0, 6);
  if (!articleItems.length) {
    articleLinks.innerHTML = '<p class="article-loading">No public article snapshot available yet.</p>';
  } else {
    articleItems.forEach(article => {
      const link = document.createElement('a');
      link.className = 'article-button';
      link.href = article.link;
      link.target = '_blank';
      link.rel = 'noreferrer';
      const title = document.createElement('strong');
      title.textContent = article.title || 'Untitled public article';
      const date = document.createElement('span');
      date.textContent = `${article.published || 'Public article'} ↗`;
      link.append(title, date);
      articleLinks.append(link);
    });
  }
  const grid = document.querySelector('#charts');
  const charts = [];
  let lastCategory = '';
  const categoryOrder = { Economic: 0, Social: 1, 'Crime & Security': 2 };
  const orderedDefinitions = [...definitions].sort((left, right) => categoryOrder[categoryFor(left[0])] - categoryOrder[categoryFor(right[0])]);
  orderedDefinitions.forEach(([key, title, subtitle, frequency, color, suffix, source, details], index) => {
    const category = categoryFor(key);
    if (category !== lastCategory) {
      const heading = document.createElement('h2');
      heading.className = 'category-heading';
      heading.dataset.category = category;
      heading.textContent = category;
      grid.append(heading);
      lastCategory = category;
    }
    const series = data.series[key];
    const live = series && !series.error && (series.values?.length || series.datasets?.length);
    const card = document.createElement('article');
    card.className = 'chart-card';
    const paragraphs = details.split('\\n\\n').map(paragraph => `<p>${paragraph}</p>`).join('');
    card.dataset.title = `${title} ${subtitle}`.toLowerCase();
    card.dataset.state = live ? 'live' : 'pending';
    card.dataset.category = category;
    const observationCount = series.values?.length || series.labels?.length || 0;
    const context = live ? `This ${frequency.toLowerCase()} series contains ${observationCount} available observations. Values are fetched from the cited public source and plotted without smoothing.` : 'This indicator is retained for source visibility, but no numeric values are shown until its official export can be checked automatically.';
    card.innerHTML = `<header><div><h2>${title}</h2><p>${subtitle} <span class="frequency">${frequency}</span></p></div><div><span class="status-pill ${live ? 'live' : ''}">${live ? 'Live' : 'Source adapter pending'}</span><button class="reset" type="button">Reset</button></div></header><div class="chart-wrap"><canvas id="chart-${index}"></canvas>${live ? '' : '<p class="empty-state">The official source is linked below. Values will appear when its public export adapter is available.</p>'}</div><details class="insight"><summary>Read the indicator note</summary><div>${paragraphs}<p><strong>Data context:</strong> ${context}</p></div></details><a class="source-link" href="${source}" target="_blank" rel="noreferrer">Open official source</a>`;
    grid.append(card);
    if (!live) return;
    const labels = series.labels;
    const values = series.values;
    const chart = new Chart(card.querySelector('canvas'), {
      type: 'line',
      data: { labels, datasets: series.datasets || [{ data: values, borderColor: color, backgroundColor: `${color}25`, fill: true, borderWidth: 2.5, pointRadius: 3, pointHoverRadius: 5, tension: 0.28 }] },
      options: chartOptions(suffix),
    });
    const reset = card.querySelector('.reset');
    if (reset) reset.addEventListener('click', () => chart.resetZoom());
    charts.push({ chart, labels, values: values || series.datasets[0].data, datasets: series.datasets?.map(dataset => ({ data: [...dataset.data] })) });
  });
  const cards = [...grid.querySelectorAll('.chart-card')];
  const headings = [...grid.querySelectorAll('.category-heading')];
  const filter = document.querySelector('#chart-filter');
  const groupFilter = document.querySelector('#group-filter');
  const search = document.querySelector('#chart-search');
  const rangeStart = document.querySelector('#range-start');
  const rangeEnd = document.querySelector('#range-end');
  const periods = [...new Set(charts.flatMap(({ labels }) => labels))].sort();
  const addPeriodOptions = (select, selected) => {
    select.replaceChildren(...periods.map(period => {
      const option = document.createElement('option');
      option.value = period;
      option.textContent = period;
      option.selected = period === selected;
      return option;
    }));
  };
  addPeriodOptions(rangeStart, periods[0]);
  addPeriodOptions(rangeEnd, periods[periods.length - 1]);
  const updateCards = () => {
    const query = search.value.trim().toLowerCase();
    const stateFilter = groupFilter.value !== 'all' ? 'all' : filter.value;
    cards.forEach(card => { const securityCard = card.dataset.category === 'Crime & Security'; card.hidden = (stateFilter !== 'all' && !securityCard && card.dataset.state !== stateFilter) || (groupFilter.value !== 'all' && card.dataset.category !== groupFilter.value) || (query && !card.dataset.title.includes(query)); });
    headings.forEach(heading => { heading.hidden = !cards.some(card => !card.hidden && card.dataset.category === heading.dataset.category); });
  };
  filter.addEventListener('change', updateCards);
  groupFilter.addEventListener('change', updateCards);
  search.addEventListener('input', updateCards);
  const updateRange = () => {
    const start = rangeStart.value;
    const end = rangeEnd.value;
    charts.forEach(({ chart, labels, values, datasets }) => {
      const visible = labels.reduce((result, label, index) => {
        if (label >= start && label <= end) result.push({ label, value: values[index] });
        return result;
      }, []);
      chart.data.labels = visible.map(point => point.label);
      if (chart.data.datasets.length === 1) chart.data.datasets[0].data = visible.map(point => point.value);
      else chart.data.datasets.forEach((dataset, datasetIndex) => { dataset.data = datasets[datasetIndex].data.map((value, index) => labels[index] >= start && labels[index] <= end ? value : null); });
      chart.resetZoom();
      chart.update();
    });
  };
  rangeStart.addEventListener('change', updateRange);
  rangeEnd.addEventListener('change', updateRange);
  updateCards();
}

main().catch(error => {
  const articleLinks = document.querySelector('#article-links');
  if (articleLinks) articleLinks.innerHTML = '<p class="article-loading">Articles are temporarily unavailable.</p>';
  document.querySelector('#charts').innerHTML = `<p>Dashboard data could not be loaded: ${error.message}</p>`;
});
