// Single deterministic remap layer: the original (category, subgroup) placement -> the 11 catalogue groups.
// Loaded by the static site (before app.js) and evaluated by scripts/export_catalog.mjs, so the static pages,
// the Django catalogue and the React app all show exactly the same groups and subgroups.
(function (root) {
  const G = {
    econ: 'Economy & Markets',
    fin: 'Public Finance & States',
    ind: 'Industry, Energy & Technology',
    infra: 'Infrastructure & Mobility',
    people: 'People, Health & Society',
    env: 'Environment, Agriculture & Food',
    sec: 'Security, Justice & Defence',
    elec: 'Elections & Democracy',
    cult: 'Culture, Heritage & Sport',
    faith: 'Epics, Faiths & Journeys',
    maps: 'India in Maps',
  };

  // artCat is the old category whose artwork the group reuses; color/icon feed the cards and charts.
  const GROUPS = [
    { name: G.econ, artCat: 'Economic', color: '#58a6ff', icon: '📈', title: '📈 Economy & Markets', badge1: 'Growth, trade & prices', badge2: 'Payments & banking',
      desc: 'GDP, income, inflation, trade, reserves and markets, plus how UPI, cards, credit, insurance and pensions are reshaping Indian finance.' },
    { name: G.fin, artCat: 'Union Budget', color: '#d29922', icon: '💰', title: '💰 Public Finance & States', badge1: 'Union Budget', badge2: 'State fiscal health',
      desc: 'What the Union Budget raises and spends, how India borrows and shares revenue, and how fifteen-plus state economies compare.' },
    { name: G.ind, artCat: 'Industry Trends & Performance', color: '#f0883e', icon: '🏭', title: '🏭 Industry, Energy & Technology', badge1: 'Factories & minerals', badge2: 'Innovation & IP',
      desc: 'Manufacturing, mining, coal and oil, patents, research and the digital economy: the productive base of a rising industrial power.' },
    { name: G.infra, artCat: 'Indian Railways', color: '#3fb950', icon: '🚆', title: '🚆 Infrastructure & Mobility', badge1: 'Rail, air & ports', badge2: 'Freight & logistics',
      desc: 'Railways, airports, ports, waterways and freight corridors: how people and goods move across India and how it compares with the world.' },
    { name: G.people, artCat: 'Social', color: '#bc8cff', icon: '👥', title: '👥 People, Health & Society', badge1: 'Demographics & health', badge2: 'Public opinion',
      desc: 'Population, jobs, education, gender, health systems and what Indians (and the world) say in Pew Research surveys.' },
    { name: G.env, artCat: 'Environment & Climate', color: '#56d364', icon: '🌾', title: '🌾 Environment, Agriculture & Food', badge1: 'Climate & air', badge2: 'Farms & food',
      desc: 'Weather, air, water and forests alongside farm yields, inputs, livestock and food trade.' },
    { name: G.sec, artCat: 'Defence & Strategic', color: '#f85149', icon: '⚖️', title: '⚖️ Security, Justice & Defence', badge1: 'Defence & crime', badge2: 'Courts & pendency',
      desc: 'Defence budgets and forces, terrorism and insurgency, rule of law, and the full pending-case picture of the Supreme Court, High Courts and lower courts.' },
    { name: G.elec, artCat: 'Elections', color: '#ff9933', icon: '🗳️', title: '🗳️ Elections & Democracy', badge1: 'Lok Sabha & states', badge2: 'U.S. elections',
      desc: 'Lok Sabha 2024, state assemblies, electoral rolls, candidate fields and victory margins, set beside U.S. campaign-finance data.' },
    { name: G.cult, artCat: 'Tourism & Heritage', color: '#ec6cb9', icon: '🏛️', title: '🏛️ Culture, Heritage & Sport', badge1: 'Tourism & heritage', badge2: 'Cricket, hockey & more',
      desc: 'Visitors, World Heritage, pilgrim geography, and India on the field: Olympics, cricket, hockey, football and beyond.' },
    { name: G.faith, artCat: 'Epics, Faiths & Journeys', color: '#c2703d', icon: '🪔', title: '🪔 Epics, Faiths & Journeys', badge1: 'Routes & pilgrimages', badge2: 'Verses from the texts',
      desc: 'Follow Rama, the Pandavas, the Buddha, Mahavira, the Sikh Gurus, the Vedas and the Panchatantra across the map, stop by stop, with a verse in the original language for each place.' },
    { name: G.maps, artCat: 'India in Maps', color: '#2ea6a6', icon: '🗺️', title: '🗺️ India in Maps', badge1: 'State & district maps', badge2: 'Linked charts',
      desc: 'Every state-level indicator drawn on the map. Pick a state to highlight it and see the related charts beside it.' },
  ];

  // Ordered subgroup definitions: [group, name, description, art source (an old subgroup name or old category)].
  const SUBS = [
    [G.econ, 'Growth, Income & Monetary Policy', 'GDP growth, per-capita income and the RBI policy stance that frame the macroeconomic story.', 'Macroeconomics'],
    [G.econ, 'Trade, Debt & Reserves', 'Merchandise and services trade, bilateral balances, external debt and the foreign-exchange cushion.', 'Trade & External'],
    [G.econ, 'Prices, Markets & Commodities', 'Inflation benchmarks, equity indices, commodity prices and production in one view.', 'Prices & Inflation Benchmarks'],
    [G.econ, 'Savings, Investment & Media', 'How households save and invest, plus coverage of the economy in the press.', 'Savings & Investment'],
    [G.econ, 'UPI, Cards & Digital Payments', 'UPI volumes, card spends and the Digital Payments Index.', 'UPI & Digital Payments'],
    [G.econ, 'State Banking & Credit', 'Bank deposits, credit and branches by state.', 'State Banking & Credit'],
    [G.econ, 'Rural Banking & Financial Inclusion', 'Regional Rural Banks, account access and credit depth beyond the metros.', 'Financial Inclusion & Credit Depth'],
    [G.econ, 'Insurance, Pensions & Capital Markets', 'Insurance penetration, pensions and social security, and the capital-market boom.', 'Insurance & Capital Markets'],

    [G.fin, 'Union Budget: Receipts, Spending & Deficits', 'Where Union revenue comes from, how it is spent, and what the deficit and capex say.', 'Receipts'],
    [G.fin, 'How India Borrows & Shares Revenue', 'Government borrowing, market loans, debt service and transfers to states.', 'Borrowing'],
    [G.fin, 'State Finances & GSDP', 'State economic size, deficits and debt, state by state.', 'State Financial Health & GSDP'],
    [G.fin, 'State Fiscal Explorer & Welfare', 'State budgets, scheme coverage and socio-demographic milestones.', 'State Fiscal Explorer'],
    [G.fin, 'State Infrastructure & Industry Hubs', 'Roads, power, services and industrial clusters across states.', 'State Infrastructure & Services'],
    [G.fin, 'State Economies & Urbanisation', 'State economic structure, the urban-rural divide and the growth of cities.', 'State Economy & Industry'],

    [G.ind, 'Manufacturing & Industrial Output', 'Factory output, the Index of Industrial Production and manufacturing growth.', 'Manufacturing & Industrial Growth'],
    [G.ind, 'Consumer, Auto & Chemical Industries', 'Food processing, automobiles, chemicals, pharma and electronics.', 'Food Processing & Consumer Goods'],
    [G.ind, 'Heavy Industry, Infrastructure & Productivity', 'Steel and metals, infrastructure build-out and industrial productivity.', 'Heavy Industry & Metals'],
    [G.ind, 'Minerals & Ores', 'Metallic and non-metallic minerals: iron ore, bauxite, limestone and more.', 'Metallic Minerals & Ores'],
    [G.ind, 'Coal, Oil & Gas', 'Energy minerals and fuels: production, reserves and consumption.', 'Energy Minerals & Fuel'],
    [G.ind, 'Mining Trade, Output & Prices', 'Mineral exports, mining output in the IIP and mineral price monitors.', 'Mineral Exports & Trade'],
    [G.ind, 'Energy Use & Resource Rents', 'Energy consumption and imports, and the value of natural capital.', 'Energy Use & Imports'],
    [G.ind, 'Patents & Industrial Designs', 'Patent and design filings, grants and who files them.', 'Patents & Intellectual Property'],
    [G.ind, 'R&D & Global Innovation', 'Research spending and India\u2019s standing in global innovation benchmarks.', 'Research & Development'],
    [G.ind, 'Research Talent & Startups', 'Scientific publications, researchers and the startup ecosystem.', 'Scientific Publications & Talent'],
    [G.ind, 'High-Tech Trade & IP Payments', 'High-technology exports and royalties paid and earned.', 'High-Tech Trade & Manufacturing'],
    [G.ind, 'Digital Technology Adoption', 'Internet, broadband, mobile and digital adoption.', 'Digital Technology Adoption'],

    [G.infra, 'Rail Network & Passenger Services', 'Route length, electrification and passenger traffic on Indian Railways.', 'Network & Electrification'],
    [G.infra, 'Rail Freight & Rolling Stock', 'Freight tonnage, wagons, locomotives and coaches.', 'Freight Operations'],
    [G.infra, 'Rail Safety & Finance', 'Accidents, safety spending and the operating ratio.', 'Railway Safety'],
    [G.infra, 'Domestic vs International Air Traffic', 'Passengers and flights on domestic and international routes.', 'Domestic vs International'],
    [G.infra, 'Air Passenger Growth', 'Year-on-year growth in air passengers and capacity.', 'Air Passenger Growth'],
    [G.infra, 'Airports & UDAN', 'Airport counts and traffic, and the UDAN regional connectivity scheme.', 'Airports & UDAN'],
    [G.infra, 'Air Cargo', 'Air freight tonnage and the cargo network.', 'Air Cargo'],
    [G.infra, 'Airports Authority Finance & Investment', 'AAI revenue, capital spending and investment.', 'AAI Finance & Investment'],
    [G.infra, 'Ports & Container Traffic', 'Major-port cargo and container performance.', 'Port Cargo Traffic'],
    [G.infra, 'Waterways & Passenger Shipping', 'Inland waterways, coastal shipping and water passenger traffic.', 'Inland Waterways'],
    [G.infra, 'Global Transport Comparisons', 'India beside other countries in rail, air and maritime benchmarks.', 'Global Rail Comparison'],
    [G.infra, 'Road & Rail Freight Logistics', 'Road and rail freight volumes, costs and logistics performance.', 'Road Freight'],
    [G.infra, 'Sea & Air Freight, Modal Split & Revenue', 'Sea and air freight, the modal split of cargo and logistics revenue.', 'Sea Freight'],

    [G.people, 'Health Spending & Disease Burden', 'Public health spending, infrastructure, nutrition and the burden of disease.', 'Health Infrastructure & Spending'],
    [G.people, 'Mortality & Communicable Diseases', 'Life expectancy, mortality milestones and communicable-disease trends.', 'Mortality & Lifespan Milestones'],
    [G.people, 'State Health Outcomes', 'Health outcomes compared across states.', 'State Health Outcomes'],
    [G.people, 'Health Workforce, Immunisation & Infrastructure', 'Doctors, nurses, hospital capacity and immunisation coverage.', 'Health Workforce & Immunisation'],
    [G.people, 'Demographics & Population', 'Population size, age structure, fertility and migration.', 'Demographics'],
    [G.people, 'Welfare & Social Protection', 'Welfare schemes, coverage and transfers.', 'Welfare'],
    [G.people, 'Jobs, Poverty & Youth', 'Employment, poverty and the prospects of children and young people.', 'Employment & Poverty'],
    [G.people, 'Education', 'Schooling, enrolment and higher education.', 'Education'],
    [G.people, 'Gender & Population', 'Gender equality in work, education and representation.', 'Gender Equality'],
    [G.people, 'Pew Research: Public Opinion on India', 'How Indians and the world view the country, its leaders and its economy.', 'Public opinion'],
    [G.people, 'Pew Research: Reports & Survey Snapshots', 'Pew publication activity, report themes and survey comparisons.', 'Report Themes'],

    [G.env, 'Climate, Water & Forests', 'Weather, disasters, the energy transition, water resources and forest cover.', 'Climate & Weather'],
    [G.env, 'Air Quality, Pollution & Waste', 'Air quality, emissions and waste.', 'Air Quality & Emissions'],
    [G.env, 'Farm Inputs, Yields & Livestock', 'Fertiliser, crops, yields, livestock and fisheries.', 'Farm Productivity & Yields'],
    [G.env, 'Food Trade & Land Use', 'Agricultural trade, food security and how land is used.', 'Food Trade & Land Use'],

    [G.sec, 'Defence Budget, Production & Exports', 'Defence spending, modernisation, indigenous production and arms exports.', 'Defence Budget & Modernization'],
    [G.sec, 'Armed Forces & Military Spending', 'Personnel, capabilities and military spending benchmarks.', 'Armed Forces & Personnel'],
    [G.sec, 'Insurgency & Militancy', 'North-East, Jammu & Kashmir, Punjab and Maoist violence over time.', 'Maoism / LWE'],
    [G.sec, 'Terrorism, Conflict & Displacement', 'Terror attacks and fatalities, conflict and displacement.', 'Terrorism'],
    [G.sec, 'Violence, Crime & Rule of Law', 'Crime statistics, violence and governance indicators.', 'Violence & Crime'],
    // '@' entries are families whose subgroups are created while placing (courts, elections, maps); they keep this position.
    [G.sec, '@sc', '', ''],
    [G.sec, '@hc-national', '', ''],
    [G.sec, '@hc-court', '', ''],
    [G.sec, '@hc-rank', '', ''],
    [G.sec, '@lc-national', '', ''],
    [G.sec, '@lc-region', '', ''],
    [G.sec, '@lc-rank', '', ''],

    [G.elec, 'Live Results, Rolls & Recent Elections', 'Live ECI constituency snapshots, electoral rolls (SSR and SIR) and the recent candidate field.', 'Indian Elections'],
    [G.elec, 'Historical Candidate Field & Competition', 'How many candidates contest and how competitive seats have become since 1951.', 'Historical Candidate Field & Competition'],
    [G.elec, 'Victory Margins & State Comparisons', 'Winning margins over time and comparisons of elections across states.', 'Historical Victory Margins'],
    [G.elec, 'Lok Sabha 2024: National & Northern States', 'The national result and Delhi, Haryana, Himachal, Jammu & Kashmir, Punjab, Rajasthan, Uttarakhand.', 'Lok Sabha 2024 \u2014 National'],
    [G.elec, 'Lok Sabha 2024: Heartland, East & North-East', 'Uttar Pradesh, Bihar, Madhya Pradesh, Chhattisgarh, Jharkhand, Odisha, West Bengal and Assam.', 'Lok Sabha 2024 \u2014 States'],
    [G.elec, 'Lok Sabha 2024: West & South', 'Gujarat, Maharashtra, Karnataka, Kerala, Tamil Nadu, Telangana and Andhra Pradesh.', 'Lok Sabha 2024 \u2014 States'],
    [G.elec, '@assembly', '', ''],
    [G.elec, 'U.S. Presidential Races & Fundraising', 'Presidential results and campaign finance, cycle by cycle.', 'U.S. Presidential Elections'],
    [G.elec, 'U.S. House Candidate Finance', 'House candidates\u2019 receipts, disbursements, cash and debts by cycle.', 'U.S. Congressional Campaign Finance'],
    [G.elec, 'U.S. Senate Candidate Finance', 'Senate candidates\u2019 receipts, disbursements, cash and debts by cycle.', 'U.S. Congressional Campaign Finance'],
    [G.elec, 'Cycle Trends & Presidential Funding Mix', 'Cycle-over-cycle finance trends and where presidential money comes from.', 'Cycle-over-Cycle Finance Trends'],
    [G.elec, 'U.S. House Funding by State', 'House campaign money ranked by state.', 'State Finance Rankings'],
    [G.elec, 'U.S. Senate Funding by State', 'Senate campaign money ranked by state.', 'State Finance Rankings'],
    [G.elec, 'U.S. House Funding Composition', 'Party, incumbency and funding-source mix of House money.', 'U.S. Campaign Funding Composition'],
    [G.elec, 'U.S. Senate Funding Composition', 'Party, incumbency and funding-source mix of Senate money.', 'U.S. Campaign Funding Composition'],

    [G.cult, 'Heritage & Visitor Trends', 'International visitors and World Heritage Sites.', 'International Visitor Trends'],
    [G.cult, 'Global Tourism & Travel Spending', 'India beside other destinations, and travel spending and balances.', 'Global Tourism Comparison'],
    [G.cult, 'Tourism Connectivity', 'Air and transport links that carry tourists.', 'Air & Transport Connectivity'],
    [G.cult, 'Olympics, Games & Athletics', 'Olympic and Paralympic medals, Asian and Commonwealth Games, and athletics.', 'Olympic & Paralympic Medals'],
    [G.cult, 'Racket, Shooting, Combat & Mind Sports', 'Badminton, tennis, shooting, archery, wrestling, boxing, chess and kabaddi.', 'Racket Sports'],
    [G.cult, 'Cricket: Teams, Rankings & Tournaments', 'Men\u2019s and women\u2019s teams, ICC rankings and tournament records.', 'ICC Rankings'],
    [G.cult, 'Cricket: Batting & Bowling, Past vs Present', 'Batting and bowling greats compared across eras.', 'Batting: Past vs Current'],
    [G.cult, 'Hockey', 'FIH rankings, Pro League, men\u2019s and women\u2019s teams and players.', 'Men\u2019s Hockey'],
    [G.cult, 'Football', 'FIFA rankings, men\u2019s and women\u2019s football and players.', 'Men\u2019s Football'],

    [G.faith, 'Epics: Mahabharata & Ramayana', 'The kingdoms of the two epics on a map, with the routes of Rama and the Pandavas traced stop by stop.', 'Epics: Mahabharata & Ramayana'],
    [G.faith, 'Vedic & Upanishadic Journeys', 'From the Sapta Sindhu to the Gangetic plain: where the Vedas and Upanishads took shape and travelled.', 'Vedic & Upanishadic Journeys'],
    [G.faith, 'Buddhist Journeys', 'The Buddha\u2019s life from Lumbini to Kushinagar, and how his teaching spread across Asia.', 'Buddhist Journeys'],
    [G.faith, 'Jain Journeys', 'Mahavira\u2019s path from Kundagrama to Pavapuri.', 'Jain Journeys'],
    [G.faith, 'Sikh Journeys', 'The ten Gurus and the places that mark their lives, including Guru Nanak\u2019s long journeys.', 'Sikh Journeys'],
    [G.faith, 'Folk & Story Traditions', 'The Panchatantra\u2019s road from India to Persia, the Arab world and Europe.', 'Folk & Story Traditions'],
    [G.maps, 'Payments & Banking Maps', 'UPI, cards, deposits and credit drawn state by state.', 'Payments & Digital Banking on the map'],
    [G.maps, 'State Economy & Fiscal Maps', 'GSDP, income, taxes and fiscal strength on the map.', 'State Performance & Regional Health on the map'],
    [G.maps, 'State Services & Welfare Maps', 'Power, water, housing and scheme coverage on the map.', 'State Performance & Regional Health on the map'],
    [G.maps, 'Health, Environment & Transport Maps', 'Health outcomes, climate, air, rail and water transport by state.', 'Public Health & Epidemiology on the map'],
    [G.maps, 'Society & Elections Maps', 'Demographics, education, gender and election results by state.', 'Social on the map'],
    [G.maps, 'Court Rankings by Jurisdiction', 'Which jurisdictions lead on filings, disposals, delays and women and senior-citizen litigants.', 'Judiciary & Pending Cases on the map'],
    [G.maps, '@lc-maps', '', ''],
  ];

  // Old category -> new group; old (category, subgroup) -> [group, subgroup]. Entries not listed fall back to CAT_DEFAULT.
  const CAT_DEFAULT = {
    Economic: G.econ, 'Payments & Digital Banking': G.econ,
    'Union Budget': G.fin, 'State Performance & Regional Health': G.fin,
    'Industry Trends & Performance': G.ind, 'Mining & Natural Resources': G.ind, 'Innovation & Technology': G.ind,
    'Indian Railways': G.infra, 'Air Travel & Civil Aviation': G.infra, 'Water Transport & Shipping': G.infra, 'Logistics & Freight': G.infra,
    'Public Health & Epidemiology': G.people, Social: G.people, 'Pew Research': G.people,
    'Environment & Climate': G.env, 'Agriculture & Food': G.env,
    'Defence & Strategic': G.sec, 'Crime & Security': G.sec, 'Judiciary & Pending Cases': G.sec,
    Elections: G.elec, 'U.S. Elections': G.elec,
    'Tourism & Heritage': G.cult, Sports: G.cult, Cricket: G.cult, Hockey: G.cult, Football: G.cult,
    'Epics, Faiths & Journeys': G.faith,
    'India in Maps': G.maps,
  };
  const TABLE = {};
  const add = (cat, subs, group, sub) => subs.forEach(old => { TABLE[`${cat}\u0001${old}`] = [group, sub]; });
  const E = 'Economic';
  add(E, ['Macroeconomics', 'Per Capita Income & Wealth', 'Monetary Policy'], G.econ, 'Growth, Income & Monetary Policy');
  add(E, ['Trade & External', 'External Debt & Reserves'], G.econ, 'Trade, Debt & Reserves');
  add(E, ['Prices & Inflation Benchmarks', 'Production & Commodities', 'Markets'], G.econ, 'Prices, Markets & Commodities');
  add(E, ['Savings & Investment', 'Media & Publications'], G.econ, 'Savings, Investment & Media');
  add(E, ['Manufacturing & Industrial Growth'], G.ind, 'Manufacturing & Industrial Output');
  add(E, ['Fiscal & Union Budget'], G.fin, 'How India Borrows & Shares Revenue');
  const P = 'Payments & Digital Banking';
  add(P, ['UPI & Digital Payments', 'Card Spends & Ecosystem', 'Digital Financial Index'], G.econ, 'UPI, Cards & Digital Payments');
  add(P, ['State Banking & Credit'], G.econ, 'State Banking & Credit');
  add(P, ['Regional Rural Banks', 'Financial Inclusion & Credit Depth'], G.econ, 'Rural Banking & Financial Inclusion');
  add(P, ['Pensions & Social Security', 'Insurance & Capital Markets'], G.econ, 'Insurance, Pensions & Capital Markets');
  const U = 'Union Budget';
  add(U, ['Budget Anatomy', 'The Rupee', 'Receipts', 'Expenditure', 'Deficits & Capex'], G.fin, 'Union Budget: Receipts, Spending & Deficits');
  add(U, ['Borrowing', 'Transfers to States'], G.fin, 'How India Borrows & Shares Revenue');
  const S = 'State Performance & Regional Health';
  add(S, ['State Financial Health & GSDP'], G.fin, 'State Finances & GSDP');
  add(S, ['State Fiscal Explorer', 'State Welfare & Scheme Coverage', 'State Socio-Demographic Milestones'], G.fin, 'State Fiscal Explorer & Welfare');
  add(S, ['State Infrastructure & Services', 'State Industrial & Manufacturing Hubs'], G.fin, 'State Infrastructure & Industry Hubs');
  add(S, ['State Economy & Industry', 'Urban vs Rural Divide', 'Urbanisation & Cities'], G.fin, 'State Economies & Urbanisation');
  const I = 'Industry Trends & Performance';
  add(I, ['Production & Commodities', 'Manufacturing & Industrial Growth', 'Industrial Output Monitor (IIP)'], G.ind, 'Manufacturing & Industrial Output');
  add(I, ['Food Processing & Consumer Goods', 'Automobiles & Transport Equipment', 'Chemicals, Pharma & Electronics'], G.ind, 'Consumer, Auto & Chemical Industries');
  add(I, ['Heavy Industry & Metals', 'Infrastructure Development', 'Industrial Structure & Productivity'], G.ind, 'Heavy Industry, Infrastructure & Productivity');
  add(I, ['Logistics & Freight'], G.infra, 'Road & Rail Freight Logistics');
  const M = 'Mining & Natural Resources';
  add(M, ['Metallic Minerals & Ores', 'Non-Metallic & Industrial Minerals'], G.ind, 'Minerals & Ores');
  add(M, ['Energy Minerals & Fuel'], G.ind, 'Coal, Oil & Gas');
  add(M, ['Mineral Exports & Trade', 'Mining Output Monitor (IIP)', 'Mineral Price Monitor (WPI)'], G.ind, 'Mining Trade, Output & Prices');
  add(M, ['Energy Use & Imports', 'Resource Rents & Natural Capital'], G.ind, 'Energy Use & Resource Rents');
  const T = 'Innovation & Technology';
  add(T, ['Patents & Intellectual Property', 'Industrial Designs & IP Filings'], G.ind, 'Patents & Industrial Designs');
  add(T, ['Global Innovation Benchmarks', 'Research & Development'], G.ind, 'R&D & Global Innovation');
  add(T, ['Scientific Publications & Talent', 'Startups & New Business'], G.ind, 'Research Talent & Startups');
  add(T, ['High-Tech Trade & Manufacturing', 'IP Royalties & Technology Payments'], G.ind, 'High-Tech Trade & IP Payments');
  add(T, ['Digital Technology Adoption'], G.ind, 'Digital Technology Adoption');
  const R = 'Indian Railways';
  add(R, ['Network & Electrification', 'Passenger Services'], G.infra, 'Rail Network & Passenger Services');
  add(R, ['Freight Operations', 'Rolling Stock & Operations'], G.infra, 'Rail Freight & Rolling Stock');
  add(R, ['Railway Safety', 'Finance & Efficiency'], G.infra, 'Rail Safety & Finance');
  add(R, ['Global Rail Comparison'], G.infra, 'Global Transport Comparisons');
  const A = 'Air Travel & Civil Aviation';
  add(A, ['Domestic vs International'], G.infra, 'Domestic vs International Air Traffic');
  add(A, ['Air Passenger Growth'], G.infra, 'Air Passenger Growth');
  add(A, ['Airports & UDAN'], G.infra, 'Airports & UDAN');
  add(A, ['Air Cargo'], G.infra, 'Air Cargo');
  add(A, ['AAI Finance & Investment'], G.infra, 'Airports Authority Finance & Investment');
  add(A, ['Global Aviation Comparison'], G.infra, 'Global Transport Comparisons');
  const W = 'Water Transport & Shipping';
  add(W, ['Port Cargo Traffic', 'Container & Port Performance'], G.infra, 'Ports & Container Traffic');
  add(W, ['Inland Waterways', 'Coastal Shipping', 'Water Passenger Traffic'], G.infra, 'Waterways & Passenger Shipping');
  add(W, ['Global Maritime Comparison'], G.infra, 'Global Transport Comparisons');
  const L = 'Logistics & Freight';
  add(L, ['Road Freight', 'Rail Freight'], G.infra, 'Road & Rail Freight Logistics');
  add(L, ['Sea Freight', 'Air Freight', 'Modal Split & Comparison', 'Logistics Revenue'], G.infra, 'Sea & Air Freight, Modal Split & Revenue');
  const H = 'Public Health & Epidemiology';
  add(H, ['Health Infrastructure & Spending', 'Nutrition & Food Security', 'Disease Burden & Epidemiology'], G.people, 'Health Spending & Disease Burden');
  add(H, ['Mortality & Lifespan Milestones', 'Communicable Diseases'], G.people, 'Mortality & Communicable Diseases');
  add(H, ['State Health Outcomes'], G.people, 'State Health Outcomes');
  add(H, ['State Health Infrastructure', 'Health Workforce & Immunisation'], G.people, 'Health Workforce, Immunisation & Infrastructure');
  const So = 'Social';
  add(So, ['Demographics'], G.people, 'Demographics & Population');
  add(So, ['Welfare'], G.people, 'Welfare & Social Protection');
  add(So, ['Employment & Poverty', 'Children & Youth'], G.people, 'Jobs, Poverty & Youth');
  add(So, ['Higher Education', 'Education'], G.people, 'Education');
  add(So, ['Gender Equality', 'Gender & Population'], G.people, 'Gender & Population');
  add('Pew Research', ['Public opinion'], G.people, 'Pew Research: Public Opinion on India');
  add('Pew Research', ['Publication Activity', 'Report Themes', 'Survey Snapshot Comparisons'], G.people, 'Pew Research: Reports & Survey Snapshots');
  const En = 'Environment & Climate';
  add(En, ['Climate & Weather', 'Disasters & Extremes', 'Energy Transition', 'Water Resources', 'Forests & Land'], G.env, 'Climate, Water & Forests');
  add(En, ['Air Quality & Emissions', 'Pollution & Waste'], G.env, 'Air Quality, Pollution & Waste');
  const Ag = 'Agriculture & Food';
  add(Ag, ['Farm Inputs', 'Crop Production', 'Livestock & Fisheries', 'Farm Productivity & Yields'], G.env, 'Farm Inputs, Yields & Livestock');
  add(Ag, ['Food Trade & Land Use'], G.env, 'Food Trade & Land Use');
  const D = 'Defence & Strategic';
  add(D, ['Defence Budget & Modernization', 'Defence Exports & Production', 'Strategic Stockpiles & Capabilities'], G.sec, 'Defence Budget, Production & Exports');
  add(D, ['Armed Forces & Personnel', 'Military Spending Benchmarks'], G.sec, 'Armed Forces & Military Spending');
  const C = 'Crime & Security';
  add(C, ['North East Insurgency', 'Jammu & Kashmir Insurgency', 'Punjab Militancy & Security', 'Maoism / LWE'], G.sec, 'Insurgency & Militancy');
  add(C, ['Terrorism', 'Conflict & Displacement'], G.sec, 'Terrorism, Conflict & Displacement');
  add(C, ['Violence & Crime', 'Rule of Law & Governance'], G.sec, 'Violence, Crime & Rule of Law');
  const El = 'Elections';
  add(El, ['Indian Elections', 'Recent Effective Candidate Field', 'Maps'], G.elec, 'Live Results, Rolls & Recent Elections');
  add(El, ['Historical Candidate Field & Competition'], G.elec, 'Historical Candidate Field & Competition');
  add(El, ['Historical Victory Margins', 'Election Comparisons Across States'], G.elec, 'Victory Margins & State Comparisons');
  add(El, ['Lok Sabha 2024 \u2014 National'], G.elec, 'Lok Sabha 2024: National & Northern States');
  add('India in Maps', ['Electoral Rolls'], G.elec, 'Live Results, Rolls & Recent Elections');
  add('U.S. Elections', ['U.S. Presidential Elections', 'U.S. Presidential Campaign Finance'], G.elec, 'U.S. Presidential Races & Fundraising');
  add('U.S. Elections', ['Cycle-over-Cycle Finance Trends'], G.elec, 'Cycle Trends & Presidential Funding Mix');
  const Tr = 'Tourism & Heritage';
  add(Tr, ['International Visitor Trends', 'World Heritage Sites'], G.cult, 'Heritage & Visitor Trends');
  add(Tr, ['Epic geography'], G.faith, 'Epics: Mahabharata & Ramayana');
  add(Tr, ['Global Tourism Comparison', 'Travel Spending & Balance'], G.cult, 'Global Tourism & Travel Spending');
  add(Tr, ['Air & Transport Connectivity'], G.cult, 'Tourism Connectivity');
  add('Sports', ['Olympic & Paralympic Medals', 'Asian & Commonwealth Games', 'Athletics'], G.cult, 'Olympics, Games & Athletics');
  add('Sports', ['Racket Sports', 'Shooting & Archery', 'Combat & Strength', 'Chess & Kabaddi'], G.cult, 'Racket, Shooting, Combat & Mind Sports');
  add('Cricket', ['Men\u2019s Cricket', 'Women\u2019s Cricket', "Men's Cricket", "Women's Cricket", 'ICC Rankings', 'ICC Tournaments'], G.cult, 'Cricket: Teams, Rankings & Tournaments');
  add('Cricket', ['Batting: Past vs Current', 'Bowling: Past vs Current'], G.cult, 'Cricket: Batting & Bowling, Past vs Present');
  ['FIH Rankings & Pro League', "Men's Hockey", "Women's Hockey", 'Hockey Players: Past vs Current'].forEach(old => { TABLE[`Hockey\u0001${old}`] = [G.cult, 'Hockey']; });
  ['FIFA Rankings', "Men's Football", "Women's Football", 'Footballers: Past vs Current'].forEach(old => { TABLE[`Football\u0001${old}`] = [G.cult, 'Football']; });
  const OnMap = (old, sub) => { TABLE[`India in Maps\u0001${old} on the map`] = [G.maps, sub]; };
  OnMap('Payments & Digital Banking', 'Payments & Banking Maps');
  ['Public Health & Epidemiology', 'Environment & Climate', 'Air Travel & Civil Aviation', 'Indian Railways', 'Water Transport & Shipping'].forEach(old => OnMap(old, 'Health, Environment & Transport Maps'));
  ['Social', 'Elections'].forEach(old => OnMap(old, 'Society & Elections Maps'));
  OnMap('Judiciary & Pending Cases', 'Court Rankings by Jurisdiction');

  const CLASS = { ci1: 'Total cases', ci2: 'Civil', ci3: 'Criminal' };
  const METRIC = { ins: 'Filings', disp: 'Disposals', inscurr: 'Filings this year', dispcurr: 'Disposals this year', citizen: 'Senior citizens', women: 'Women', delay: 'Delays' };
  const METRIC_ORDER = Object.keys(METRIC);
  const ROMAN = ['', ' II', ' III', ' IV', ' V', ' VI'];
  const LC_REGIONS = [
    ['Delhi, Haryana, Punjab & Chandigarh', ['delhi', 'nct_of', 'haryana', 'punjab', 'chandigarh']],
    ['Himalayan States & Ladakh', ['himachal', 'jammu', 'ladakh', 'uttarakhand']],
    ['Uttar Pradesh, Rajasthan & Central India', ['uttar_pradesh', 'rajasthan', 'madhya_pradesh', 'chhattisgarh']],
    ['Bihar, Jharkhand, Odisha & West Bengal', ['bihar', 'jharkhand', 'odisha', 'west_bengal']],
    ['Assam, Arunachal, Manipur & Meghalaya', ['assam', 'arunachal', 'manipur', 'meghalaya']],
    ['Mizoram, Nagaland, Tripura & Sikkim', ['mizoram', 'nagaland', 'tripura', 'sikkim']],
    ['Maharashtra, Gujarat & Goa', ['maharashtra', 'gujarat', 'goa', 'the_dadra', 'dadra', 'daman']],
    ['Karnataka, Kerala, Tamil Nadu & Telangana', ['karnataka', 'kerala', 'tamil_nadu', 'telangana', 'andhra_pradesh']],
    ['Islands & Puducherry', ['andaman', 'lakshadweep', 'puducherry']],
  ];
  const LS_REGIONS = [
    ['Lok Sabha 2024: National & Northern States', ['nct_of', 'haryana', 'himachal', 'jammu', 'punjab', 'rajasthan', 'uttarakhand']],
    ['Lok Sabha 2024: Heartland, East & North-East', ['uttar_pradesh', 'bihar', 'madhya_pradesh', 'chhattisgarh', 'jharkhand', 'odisha', 'west_bengal', 'assam']],
    ['Lok Sabha 2024: West & South', ['gujarat', 'maharashtra', 'karnataka', 'kerala', 'tamil_nadu', 'telangana', 'andhra_pradesh']],
  ];

  const parts = (count, target = 30) => Math.max(1, Math.ceil(count / target));
  const slice = (list, n) => {
    const out = [];
    const base = Math.floor(list.length / n);
    let extra = list.length % n;
    let at = 0;
    for (let index = 0; index < n; index += 1) {
      const size = base + (extra > 0 ? 1 : 0);
      extra -= 1;
      out.push(list.slice(at, at + size));
      at += size;
    }
    return out.filter(part => part.length);
  };
  const yearSpan = years => (years.length ? (years[0] === years[years.length - 1] ? String(years[0]) : `${years[0]}\u2013${String(years[years.length - 1]).slice(2)}`) : '');
  const parseJud = key => {
    const rest = key.replace(/^jud_(supreme_court|high_courts|lower_courts)_/, '');
    const rank = rest.match(/^(rank|share)_([a-z]+)_ci(\d)/);
    if (rank) return { kind: 'rank', metric: rank[2], cls: Number(rank[3]), mode: 'rank' };
    const national = rest.match(/^national_ci(\d)_(pending|disposed_(\d{4}))/);
    if (national) return { kind: 'national', cls: Number(national[1]), mode: national[2].startsWith('pending') ? 'pending' : 'disposed', year: Number(national[3] || 0) };
    const monthly = rest.match(/^monthly_institution_vs_disposal_ci(\d)/);
    if (monthly) return { kind: 'national', cls: Number(monthly[1]), mode: 'monthly', year: 0 };
    const jurisdiction = rest.match(/^(.*?)_ci\d_/);
    if (jurisdiction) return { kind: 'court', slug: jurisdiction[1], cls: 0, mode: 'x', year: 0 };
    return { kind: 'national', cls: 0, mode: 'mix', year: 0 };
  };
  const modeOrder = { mix: 0, monthly: 1, pending: 2, disposed: 3 };
  const describeChunk = chunk => {
    const classes = [...new Set(chunk.map(entry => entry.p.cls).filter(Boolean))];
    const label = classes.length === 1 ? CLASS[`ci${classes[0]}`] : classes.length ? 'Civil & criminal' : 'All cases';
    const pending = chunk.some(entry => entry.p.mode === 'pending');
    const years = [...new Set(chunk.map(entry => entry.p.year).filter(Boolean))].sort();
    const span = [pending ? 'Pending' : '', years.length ? yearSpan(years) : ''].filter(Boolean).join(' & ') || (chunk.some(entry => entry.p.mode === 'monthly') ? 'Monthly flows' : 'Overview');
    return `${label} \u00b7 ${span}`;
  };
  const courtShort = title => {
    const name = String(title).split(':')[0].replace(/^High Court (of|for)( the)?( State of)?\s+/i, '').replace(/\s+High Court$/i, '').trim();
    return name || 'Other';
  };
  const metricLabel = chunk => {
    const used = METRIC_ORDER.filter(metric => chunk.some(entry => entry.p.metric === metric)).map(metric => METRIC[metric]);
    return used.length > 3 ? `${used[0]} to ${used[used.length - 1]}` : used.length > 2 ? `${used.slice(0, -1).join(', ')} & ${used[used.length - 1]}` : used.join(' & ');
  };
  const topicOf = key => {
    const found = key.match(/case-type|case-category|by-age|stage|filing-year|disposal-time|disposal-nature|institutions/);
    return { 'case-type': 'Case types', 'case-category': 'Case categories', 'by-age': 'Case age', stage: 'Case stage', 'filing-year': 'Filing year', 'disposal-time': 'Disposal time', 'disposal-nature': 'Disposal outcome', institutions: 'Institutions & disposals' }[found?.[0]] || 'Cases';
  };

  // Each handler receives the items of one old (category, subgroup) and returns placement records.
  const makeHandlers = () => {
    const handlers = {};
    const rec = (item, group, sub, family, desc, art, extra = {}) => ({ item, group, sub, family, desc, art, ...extra });
    const courtHandler = (court, label, fam) => items => {
      const out = [];
      const parsed = items.map(item => ({ item, p: parseJud(item.key) }));
      const national = parsed.filter(entry => entry.p.kind === 'national').sort((a, b) => a.p.cls - b.p.cls || modeOrder[a.p.mode] - modeOrder[b.p.mode] || a.p.year - b.p.year);
      const courts = parsed.filter(entry => entry.p.kind === 'court');
      const ranks = parsed.filter(entry => entry.p.kind === 'rank').sort((a, b) => METRIC_ORDER.indexOf(a.p.metric) - METRIC_ORDER.indexOf(b.p.metric) || a.p.cls - b.p.cls);
      const used = new Set();
      const name = base => { let n = 0; let candidate = base; while (used.has(candidate)) { n += 1; candidate = base + ROMAN[n]; } used.add(candidate); return candidate; };
      const nationalFamily = court === 'sc' ? '@sc' : `@${fam}-national`;
      const classLists = [1, 2, 3].map(cls => national.filter(entry => entry.p.cls === cls));
      const loose = national.filter(entry => ![1, 2, 3].includes(entry.p.cls));
      const nationalChunks = [];
      let pool = [];
      classLists.forEach(list => {
        if (list.length >= 20) slice(list, parts(list.length)).forEach(chunk => nationalChunks.push(chunk));
        else pool = pool.concat(list);
      });
      if (pool.length) nationalChunks.push(pool);
      if (loose.length) (nationalChunks[0] || (nationalChunks[0] = [])).push(...loose);
      nationalChunks.forEach(chunk => {
        const sub = name(`${label} \u00b7 ${describeChunk(chunk)}`);
        chunk.forEach(entry => out.push(rec(entry.item, G.sec, sub, nationalFamily, `${label}: ${describeChunk(chunk).replace(' \u00b7 ', ', ')} \u2014 case mix, age, stage, filing year and disposal.`, 'Supreme Court')));
      });
      if (courts.length) {
        const bySlug = new Map();
        courts.forEach(entry => { if (!bySlug.has(entry.p.slug)) bySlug.set(entry.p.slug, { short: courtShort(entry.item.title), entries: [] }); bySlug.get(entry.p.slug).entries.push(entry); });
        const slugs = [...bySlug.values()].sort((a, b) => a.short.localeCompare(b.short));
        if (court === 'hc') {
          slice(slugs, parts(slugs.length, 5)).forEach(chunk => {
            const sub = name(`${label} \u00b7 ${chunk[0].short} to ${chunk[chunk.length - 1].short}`);
            chunk.forEach(courtEntry => courtEntry.entries.forEach(entry => out.push(rec(entry.item, G.sec, sub, '@hc-court', `Pending cases, age, stage and institutions versus disposals for ${chunk.map(c => c.short).join(', ')} High Courts.`, 'High Courts'))));
          });
        } else {
          const placed = new Set();
          LC_REGIONS.forEach(([regionName, prefixes]) => {
            const members = slugs.filter(entry => prefixes.some(prefix => entry.entries[0].p.slug.startsWith(prefix)));
            const sub = name(`${label} \u00b7 ${regionName}`);
            members.forEach(courtEntry => { placed.add(courtEntry); courtEntry.entries.forEach(entry => out.push(rec(entry.item, G.sec, sub, '@lc-region', `District and subordinate courts of ${regionName}: pending cases by type, age, stage and filing year.`, 'Lower Courts'))); });
          });
          slugs.filter(entry => !placed.has(entry)).forEach(courtEntry => courtEntry.entries.forEach(entry => out.push(rec(entry.item, G.sec, name(`${label} \u00b7 ${LC_REGIONS[LC_REGIONS.length - 1][0]}`), '@lc-region', 'Subordinate courts of the remaining jurisdictions.', 'Lower Courts'))));
        }
      }
      if (ranks.length) {
        slice(ranks, parts(ranks.length)).forEach(chunk => {
          const sub = name(`${label} \u00b7 Leading jurisdictions: ${metricLabel(chunk)}`);
          chunk.forEach(entry => out.push(rec(entry.item, G.sec, sub, `@${fam}-rank`, `Which jurisdictions lead ${label.toLowerCase()} filings and disposals (${metricLabel(chunk).toLowerCase()}), with their share of the national total.`, court === 'sc' ? 'Supreme Court' : court === 'hc' ? 'High Courts' : 'Lower Courts')));
        });
      }
      return out;
    };
    handlers[`Judiciary & Pending Cases\u0001Supreme Court`] = courtHandler('sc', 'Supreme Court', 'sc');
    handlers[`Judiciary & Pending Cases\u0001High Courts`] = courtHandler('hc', 'High Courts', 'hc');
    handlers[`Judiciary & Pending Cases\u0001Lower Courts`] = courtHandler('lc', 'Lower Courts', 'lc');

    handlers['Elections\u0001Lok Sabha 2024 \u2014 States'] = items => items.map(item => {
      const slug = item.key.replace(/^india_ls2024_/, '');
      const region = LS_REGIONS.find(([, prefixes]) => prefixes.some(prefix => slug.startsWith(prefix))) || LS_REGIONS[LS_REGIONS.length - 1];
      return rec(item, G.elec, region[0], null, '', 'Lok Sabha 2024 \u2014 States');
    });
    handlers['Elections\u0001State Assembly Results 2022\u20132026'] = items => items.map(item => {
      const year = (item.key.match(/^india_assembly_(\d{4})_/) || [])[1];
      const sub = year ? `State Assembly Results ${year}` : 'State Assembly Results';
      return rec(item, G.elec, sub, '@assembly', `Seats, votes, margins and candidate fields for the ${year || ''} state assembly elections.`.replace('the  ', 'the '), 'State Assembly Results 2022\u20132026', { sortYear: Number(year || 0) });
    });
    const usSplit = (usGroupTitle, art, table) => items => items.map(item => {
      const chamber = (item.key.match(/_(h|s|p)_/) || [])[1];
      const sub = table[chamber] || table.h;
      return rec(item, G.elec, sub, null, '', art);
    });
    handlers['U.S. Elections\u0001U.S. Congressional Campaign Finance'] = usSplit('', 'U.S. Congressional Campaign Finance', { h: 'U.S. House Candidate Finance', s: 'U.S. Senate Candidate Finance', p: 'U.S. House Candidate Finance' });
    handlers['U.S. Elections\u0001State Finance Rankings'] = usSplit('', 'State Finance Rankings', { h: 'U.S. House Funding by State', s: 'U.S. Senate Funding by State', p: 'U.S. House Funding by State' });
    handlers['U.S. Elections\u0001U.S. Campaign Funding Composition'] = usSplit('', 'U.S. Campaign Funding Composition', { h: 'U.S. House Funding Composition', s: 'U.S. Senate Funding Composition', p: 'Cycle Trends & Presidential Funding Mix' });

    handlers['India in Maps\u0001State Performance & Regional Health on the map'] = items => slice(items, 2).flatMap((chunk, index) => chunk.map(item => rec(item, G.maps, ['State Economy & Fiscal Maps', 'State Services & Welfare Maps'][index], null, '', 'State Performance & Regional Health on the map')));
    handlers['India in Maps\u0001Lower Courts on the map'] = items => {
      const chunks = slice(items, parts(items.length, 26));
      const used = new Set();
      return chunks.flatMap(chunk => {
        const topics = [...new Set(chunk.map(item => topicOf(item.key)))];
        let sub = `Court Maps \u00b7 ${topics.slice(0, 2).join(' & ')}`;
        let n = 0;
        const base = sub;
        while (used.has(sub)) { n += 1; sub = base + ROMAN[n]; }
        used.add(sub);
        return chunk.map(item => rec(item, G.maps, sub, '@lc-maps', `Lower-court pendency by ${topics.slice(0, 2).join(' and ').toLowerCase()}, drawn state by state.`, 'Lower Courts on the map'));
      });
    };
    return handlers;
  };

  const place = items => {
    const records = new Map();
    const dynamic = [];
    const buckets = new Map();
    items.forEach(item => {
      const bucketKey = `${item.category}\u0001${item.subgroup}`;
      const direct = TABLE[bucketKey];
      if (direct) { records.set(item.key, { item, group: direct[0], sub: direct[1] }); return; }
      if (!buckets.has(bucketKey)) buckets.set(bucketKey, []);
      buckets.get(bucketKey).push(item);
    });
    const handlers = makeHandlers();
    buckets.forEach((list, bucketKey) => {
      if (handlers[bucketKey]) {
        handlers[bucketKey](list).forEach(entry => { records.set(entry.item.key, entry); if (entry.family || entry.desc) dynamic.push(entry); });
        return;
      }
      const [category, subgroup] = bucketKey.split('\u0001');
      const group = CAT_DEFAULT[category] || G.maps;
      list.forEach(item => { records.set(item.key, { item, group, sub: subgroup, family: '@other' }); });
      dynamic.push({ group, sub: subgroup, family: '@other', desc: '', art: subgroup });
    });
    return { records, dynamic };
  };

  const state = { subs: new Map(), aliases: { groups: {}, subgroups: {} }, rank: new Map() };

  const finish = (records, dynamic, oldOf) => {
    const subs = new Map();
    const familyOrder = {};
    const order = {};
    SUBS.forEach(([group, name, desc, art], index) => {
      if (name.startsWith('@')) { familyOrder[name] = index; return; }
      subs.set(name, { group, name, desc, artSub: art, rank: index, seq: 0 });
    });
    const seq = {};
    const dynEntries = [...dynamic].sort((a, b) => (a.sortYear || 0) - (b.sortYear || 0));
    dynEntries.forEach(entry => {
      if (subs.has(entry.sub)) return;
      const family = entry.family;
      const rank = familyOrder[family] ?? SUBS.length + 1;
      seq[family] = (seq[family] || 0) + 1;
      subs.set(entry.sub, { group: entry.group, name: entry.sub, desc: entry.desc || '', artSub: entry.art || entry.sub, rank, seq: seq[family] });
    });
    // Static subgroups defined above keep their own description even if a handler also names them.
    records.forEach(entry => {
      if (!subs.has(entry.sub)) subs.set(entry.sub, { group: entry.group, name: entry.sub, desc: '', artSub: entry.sub, rank: SUBS.length + 2, seq: 0 });
    });
    const groupIndex = Object.fromEntries(GROUPS.map((group, index) => [group.name, index]));
    const perGroup = {};
    const usedNames = new Set([...records.values()].map(entry => entry.sub));
    [...subs.values()].filter(sub => usedNames.has(sub.name)).sort((a, b) => a.rank - b.rank || a.seq - b.seq).forEach(sub => {
      perGroup[sub.group] = (perGroup[sub.group] || 0) + 1;
      sub.order = perGroup[sub.group] - 1;
    });
    state.subs = new Map([...subs].filter(([, sub]) => sub.order !== undefined));
    state.rank = new Map();
    records.forEach((entry, key) => {
      const sub = state.subs.get(entry.sub);
      state.rank.set(key, groupIndex[entry.group] * 1000 + sub.order);
    });
    // Legacy URLs: old group (and old group + subgroup) -> new group and the subgroup holding most of its items.
    const count = {};
    const countSub = {};
    records.forEach(entry => {
      const old = oldOf(entry.item);
      count[old.category] = count[old.category] || {};
      const key = `${entry.group}\u0001${entry.sub}`;
      count[old.category][key] = (count[old.category][key] || 0) + 1;
      const subKey = `${old.category}\u0001${old.subgroup}`;
      countSub[subKey] = countSub[subKey] || {};
      countSub[subKey][key] = (countSub[subKey][key] || 0) + 1;
    });
    const best = table => Object.entries(table).sort((a, b) => b[1] - a[1] || (state.subs.get(a[0].split('\u0001')[1]).rank - state.subs.get(b[0].split('\u0001')[1]).rank) || 0)[0][0].split('\u0001');
    state.aliases = { groups: {}, subgroups: {} };
    Object.entries(count).forEach(([oldCategory, table]) => {
      const [group, subgroup] = best(table);
      // Focus a subgroup only when the old group landed in a few of them; otherwise show the whole new group.
      state.aliases.groups[oldCategory] = { group, subgroup: Object.keys(table).length <= 3 ? subgroup : '' };
    });
    Object.entries(countSub).forEach(([key, table]) => {
      const [oldCategory, oldSubgroup] = key.split('\u0001');
      const [group, subgroup] = best(table);
      state.aliases.subgroups[`${oldCategory}|${oldSubgroup}`] = { group, subgroup };
    });
    return state;
  };

  const IndiaRegroup = {
    GROUPS, GROUP_NAMES: GROUPS.map(group => group.name), SUBS,
    // Applies the remap: items carry the original placement. Returns placement per key and mutates the caller's order map.
    applyPlacement({ definitions, categoryFor, subgroupFor, extraChartPlacement, categoryOrder }) {
      const items = definitions.map(([key, title]) => ({ key, title, category: categoryFor(key), subgroup: subgroupFor(key) }));
      const { records, dynamic } = place(items);
      finish(records, dynamic, item => ({ category: item.category, subgroup: item.subgroup }));
      records.forEach((entry, key) => { extraChartPlacement[key] = { category: entry.group, subgroup: entry.sub, rank: state.rank.get(key) }; });
      Object.keys(categoryOrder).forEach(name => delete categoryOrder[name]);
      GROUPS.forEach((group, index) => { categoryOrder[group.name] = index; });
      return state;
    },
    // Rewrites the category/subgroup art and hero maps (captured from the old ones) for the new groups.
    applyMeta({ categoryBgMap, groupHeroData, subgroupArtMap, subgroupHeroData }) {
      const oldCat = { ...categoryBgMap };
      const oldSub = { ...subgroupArtMap };
      [categoryBgMap, groupHeroData, subgroupArtMap, subgroupHeroData].forEach(map => Object.keys(map).forEach(name => delete map[name]));
      GROUPS.forEach(group => {
        categoryBgMap[group.name] = oldCat[group.artCat] || oldCat.Economic;
        groupHeroData[group.name] = { title: group.title, desc: group.desc, badge1: group.badge1, badge2: group.badge2 };
      });
      state.subs.forEach(sub => {
        const art = oldSub[sub.artSub] || oldCat[sub.artSub] || categoryBgMap[sub.group];
        subgroupArtMap[sub.name] = art;
        subgroupHeroData[sub.name] = { title: sub.name, desc: sub.desc || `${sub.name} within ${sub.group}.`, badge1: sub.group, badge2: '' };
      });
    },
    state: () => state,
    subgroupRank: key => state.rank.get(key) ?? 99999,
    // Resolves ?group=<old or new>&subgroup=<old or new> to the current group and subgroup.
    resolveLegacy(group, subgroup, known) {
      const names = new Set(known || GROUPS.map(entry => entry.name));
      if (group && names.has(group)) return { group, subgroup: subgroup || '' };
      const bySub = group && subgroup ? state.aliases.subgroups[`${group}|${subgroup}`] : null;
      if (bySub) return { group: bySub.group, subgroup: bySub.subgroup };
      const byGroup = group ? state.aliases.groups[group] : null;
      if (byGroup) return { group: byGroup.group, subgroup: byGroup.subgroup || (subgroup && state.subs.has(subgroup) ? subgroup : '') };
      return { group: group || '', subgroup: subgroup || '' };
    },
    place,
    finish,
  };
  root.IndiaRegroup = IndiaRegroup;
  if (typeof module !== 'undefined' && module.exports) module.exports = IndiaRegroup;
})(typeof window !== 'undefined' ? window : globalThis);
