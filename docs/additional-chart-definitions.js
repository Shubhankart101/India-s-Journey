(() => {
  const worldBank = (key, title, subtitle, color, unit, indicator, details) => [
    key, title, subtitle, 'Annual', color, unit,
    `https://data.worldbank.org/indicator/${indicator}`, details,
  ];

  window.INDIA_EXTRA_CHART_DEFINITIONS = [
    worldBank('tourism_arrivals', 'International Tourist Arrivals', 'International tourism arrivals to India', '#ff9933', ' arrivals', 'ST.INT.ARVL', 'International tourist arrivals reported in the World Bank series. This annual count depends on national reporting and definitions; it is not a state-wise or monument-specific visitor count.'),
    worldBank('tourism_departures', 'International Tourist Departures', 'International tourism departures from India', '#58a6ff', ' departures', 'ST.INT.DPRT', 'International tourist departures reported in the World Bank series. This is a national outbound-travel count, not an inbound tourism measure.'),
    worldBank('tourism_receipts_usd', 'International Tourism Receipts', 'International tourism receipts in current US dollars', '#3fb950', ' USD', 'ST.INT.RCPT.CD', 'International tourism receipts in current US dollars. Values are nominal and exchange-rate sensitive; this series is not adjusted for inflation.'),
    ['unesco_india_sites_cumulative', 'India’s UNESCO World Heritage Sites', 'Cumulative properties by inscription year', 'Annual', '#e3b341', 'sites', 'https://whc.unesco.org/en/list/', 'The cumulative series is reconstructed from the current UNESCO property pages and their inscription dates. It is not a historical archived total and can change if the current list or site classification is revised.'],
    ['unesco_india_new_inscriptions', 'New UNESCO World Heritage Inscription Events', 'Properties inscribed in each year', 'Annual', '#bc8cff', 'sites', 'https://whc.unesco.org/en/list/', 'Annual additions are counted from inscription years on the current official list. The series can be revised if the official property record changes.'],
    ['unesco_india_current_categories', 'India’s Current UNESCO Site Categories', 'Current cultural, natural and mixed properties', 'Current list', '#79c0ff', 'sites', 'https://whc.unesco.org/en/list/', 'Current UNESCO property classifications; category counts are a snapshot and are not historical totals.'],
    worldBank('gdp_ppp', 'GDP at Purchasing Power Parity', 'Gross domestic product in current international dollars', '#58a6ff', ' USD', 'NY.GDP.MKTP.PP.CD', 'GDP converted using purchasing-power-parity rates for cross-country price differences. Sourced from World Bank Open Data.'),
    worldBank('gdp_deflator_growth', 'GDP Deflator Inflation', 'Annual GDP deflator inflation', '#ff9933', '%', 'NY.GDP.DEFL.KD.ZG', 'Annual change in the GDP deflator, covering prices across domestically produced output. Sourced from World Bank Open Data.'),
    worldBank('capital_formation_gdp', 'Gross Capital Formation', 'Gross capital formation as a share of GDP', '#3fb950', '% GDP', 'NE.GDI.FTOT.ZS', 'Investment in fixed assets and changes in inventories as a share of GDP. Sourced from World Bank Open Data.'),
    worldBank('household_consumption_gdp', 'Household Consumption Share', 'Household consumption expenditure as a share of GDP', '#f778ba', '% GDP', 'NE.CON.PRVT.ZS', 'Household and nonprofit institution final consumption expenditure as a share of GDP. Sourced from World Bank Open Data.'),
    worldBank('gross_savings_rate', 'Gross Savings Rate', 'Gross savings as a share of GDP', '#bc8cff', '% GDP', 'NY.GNS.ICTR.ZS', 'Gross national savings as a share of GDP. Sourced from World Bank Open Data.'),
    worldBank('exports_gdp', 'Exports of Goods and Services', 'Exports of goods and services as a share of GDP', '#3fb950', '% GDP', 'NE.EXP.GNFS.ZS', 'Exports of goods and services relative to GDP. Sourced from World Bank Open Data.'),
    worldBank('imports_gdp', 'Imports of Goods and Services', 'Imports of goods and services as a share of GDP', '#ff7b72', '% GDP', 'NE.IMP.GNFS.ZS', 'Imports of goods and services relative to GDP. Sourced from World Bank Open Data.'),
    worldBank('remittances_gdp', 'Personal Remittances', 'Personal remittances received as a share of GDP', '#79c0ff', '% GDP', 'BX.TRF.PWKR.DT.GD.ZS', 'Personal remittances received relative to GDP. Sourced from World Bank Open Data.'),
    worldBank('reserves_import_months', 'Foreign Reserves in Months of Imports', 'Total reserves measured in months of imports', '#a371f7', ' months', 'FI.RES.TOTL.MO', 'Reserve coverage expressed as the equivalent months of imports. Sourced from World Bank Open Data.'),
    worldBank('debt_service_exports', 'External Debt Service', 'Total external debt service as a share of exports', '#e3b341', '% exports', 'DT.TDS.DECT.GN.ZS', 'Total external debt service relative to exports of goods, services and primary income. Sourced from World Bank Open Data.'),
    worldBank('public_debt_gdp', 'Central Government Debt', 'Central government debt as a share of GDP', '#ff7b72', '% GDP', 'GC.DOD.TOTL.GD.ZS', 'Central government debt relative to GDP. Sourced from World Bank Open Data.'),
    worldBank('current_health_spending', 'Current Health Expenditure', 'Current health expenditure as a share of GDP', '#3fb950', '% GDP', 'SH.XPD.CHEX.GD.ZS', 'Current health expenditure relative to GDP. Sourced from World Bank Open Data.'),
    worldBank('physicians_density', 'Physicians per 1,000 People', 'Medical doctors per 1,000 people', '#58a6ff', ' per 1k people', 'SH.MED.PHYS.ZS', 'Practising physicians per 1,000 people. Sourced from World Bank Open Data.'),
    worldBank('under5_mortality', 'Under-Five Mortality Rate', 'Deaths before age five per 1,000 live births', '#ff7b72', ' per 1k births', 'SH.DYN.MORT', 'Probability of dying before age five, expressed per 1,000 live births. Sourced from World Bank Open Data.'),
    worldBank('basic_water_access', 'Basic Drinking Water Access', 'Population using at least basic drinking water services', '#79c0ff', '%', 'SH.H2O.BASW.ZS', 'Population using at least basic drinking-water services. Sourced from World Bank Open Data.'),
    worldBank('basic_sanitation_access', 'Basic Sanitation Access', 'Population using at least basic sanitation services', '#bc8cff', '%', 'SH.STA.SMSS.ZS', 'Population using at least basic sanitation services. Sourced from World Bank Open Data.'),
    worldBank('urban_population_share', 'Urban Population Share', 'Urban population as a share of total population', '#f778ba', '%', 'SP.URB.TOTL.IN.ZS', 'Population living in urban areas as a share of total population. Sourced from World Bank Open Data.'),
    worldBank('population_growth', 'Population Growth', 'Annual population growth rate', '#79c0ff', '%', 'SP.POP.GROW', 'Annual population growth rate. Sourced from World Bank Open Data.'),
    worldBank('fertility_rate', 'Total Fertility Rate', 'Births per woman', '#ff9933', ' births/woman', 'SP.DYN.TFRT.IN', 'Total fertility rate, the average number of births per woman. Sourced from World Bank Open Data.'),
    worldBank('primary_school_enrollment', 'Primary School Enrollment', 'Gross enrollment ratio in primary education', '#58a6ff', '%', 'SE.PRM.ENRR', 'Gross enrollment in primary education, which may exceed 100 percent due to age differences. Sourced from World Bank Open Data.'),
    worldBank('secondary_school_enrollment', 'Secondary School Enrollment', 'Gross enrollment ratio in secondary education', '#a371f7', '%', 'SE.SEC.ENRR', 'Gross enrollment in secondary education, which may exceed 100 percent due to age differences. Sourced from World Bank Open Data.'),
    worldBank('tertiary_school_enrollment', 'Tertiary School Enrollment', 'Gross enrollment ratio in tertiary education', '#f778ba', '%', 'SE.TER.ENRR', 'Gross enrollment in tertiary education. Sourced from World Bank Open Data.'),
    worldBank('education_spending_gdp', 'Government Education Spending', 'Government expenditure on education as a share of GDP', '#e3b341', '% GDP', 'SE.XPD.TOTL.GD.ZS', 'Government expenditure on education relative to GDP. Sourced from World Bank Open Data.'),
    worldBank('female_labor_participation', 'Female Labor Force Participation', 'Female labor force participation rate', '#f778ba', '%', 'SL.TLF.CACT.FE.ZS', 'Share of women ages 15 and older who are economically active. Sourced from World Bank Open Data.'),
    worldBank('labor_force_participation', 'Labor Force Participation', 'Labor force participation rate', '#79c0ff', '%', 'SL.TLF.CACT.ZS', 'Share of people ages 15 and older who are economically active. Sourced from World Bank Open Data.'),
    worldBank('employment_population_ratio', 'Employment-to-Population Ratio', 'Employment as a share of the working-age population', '#3fb950', '%', 'SL.EMP.TOTL.SP.ZS', 'Employed people as a share of the population ages 15 and older. Sourced from World Bank Open Data.'),
    worldBank('adult_literacy_rate', 'Adult Literacy Rate', 'Adult literacy rate, population ages 15 and older', '#bc8cff', '%', 'SE.ADT.LITR.ZS', 'Share of people ages 15 and older who can read and write with understanding. Sourced from World Bank Open Data.'),
    worldBank('agriculture_gdp_share', 'Agriculture Value Added', 'Agriculture, forestry and fishing value added as a share of GDP', '#3fb950', '% GDP', 'NV.AGR.TOTL.ZS', 'Agriculture, forestry and fishing value added relative to GDP. Sourced from World Bank Open Data.'),
    worldBank('industry_gdp_share', 'Industry Value Added', 'Industry value added as a share of GDP', '#ff9933', '% GDP', 'NV.IND.TOTL.ZS', 'Industry value added, including construction, relative to GDP. Sourced from World Bank Open Data.'),
    worldBank('services_gdp_share', 'Services Value Added', 'Services value added as a share of GDP', '#58a6ff', '% GDP', 'NV.SRV.TOTL.ZS', 'Services value added relative to GDP. Sourced from World Bank Open Data.'),
    worldBank('manufacturing_gdp_share', 'Manufacturing Value Added', 'Manufacturing value added as a share of GDP', '#e3b341', '% GDP', 'NV.IND.MANF.ZS', 'Manufacturing value added relative to GDP. Sourced from World Bank Open Data.'),
    worldBank('agricultural_land_share', 'Agricultural Land', 'Agricultural land as a share of total land area', '#3fb950', '%', 'AG.LND.AGRI.ZS', 'Land used for agriculture as a share of total land area. Sourced from World Bank Open Data.'),
    worldBank('cereal_yield', 'Cereal Yield', 'Cereal production per harvested hectare', '#e3b341', ' kg/hectare', 'AG.YLD.CREL.KG', 'Cereal production per hectare of harvested land. Sourced from World Bank Open Data.'),
    worldBank('energy_use_per_capita', 'Energy Use per Capita', 'Energy use per person', '#ff9933', ' kg oil equivalent/person', 'EG.USE.PCAP.KG.OE', 'Energy use per person, expressed in kilograms of oil equivalent. Sourced from World Bank Open Data.'),
    worldBank('electricity_use_per_capita', 'Electric Power Consumption per Capita', 'Electric power consumption per person', '#f6c344', ' kWh/person', 'EG.USE.ELEC.KH.PC', 'Electricity use per person in kilowatt-hours. Sourced from World Bank Open Data.'),
    worldBank('renewable_energy_consumption', 'Renewable Energy Consumption', 'Renewable energy as a share of total final energy consumption', '#3fb950', '%', 'EG.FEC.RNEW.ZS', 'Renewable sources as a share of final energy consumption. Sourced from World Bank Open Data.'),
    worldBank('renewable_electricity_output', 'Renewable Electricity Output', 'Renewable electricity as a share of total electricity output', '#79c0ff', '%', 'EG.ELC.RNEW.ZS', 'Electricity generated from renewable sources as a share of total output. Sourced from World Bank Open Data.'),
    worldBank('pm25_exposure', 'Fine Particulate Matter Exposure', 'Population-weighted annual mean PM2.5 exposure', '#ff7b72', ' µg/m3', 'EN.ATM.PM25.MC.M3', 'Population-weighted exposure to fine particulate matter. Sourced from World Bank Open Data.'),
    worldBank('forest_area_share', 'Forest Area', 'Forest area as a share of total land area', '#3fb950', '%', 'AG.LND.FRST.ZS', 'Forest area as a share of total land area. Sourced from World Bank Open Data.'),
    worldBank('mobile_subscriptions_per_100', 'Mobile Cellular Subscriptions', 'Mobile cellular subscriptions per 100 people', '#f778ba', ' per 100 people', 'IT.CEL.SETS.P2', 'Mobile cellular subscriptions per 100 people. Sourced from World Bank Open Data.'),
    worldBank('fixed_broadband_per_100', 'Fixed Broadband Subscriptions', 'Fixed broadband subscriptions per 100 people', '#58a6ff', ' per 100 people', 'IT.NET.BBND.P2', 'Fixed broadband subscriptions per 100 people. Sourced from World Bank Open Data.'),
    worldBank('military_expenditure_usd', 'Military Expenditure in Current US Dollars', 'Military expenditure converted to current US dollars', '#ff7b72', ' USD', 'MS.MIL.XPND.CD', 'Military expenditure in current US dollars. Sourced from World Bank Open Data.'),
    ['state_gsdp_share', 'State Share of Reported GSDP', 'State contribution to the sum of reported GSDP, FY2022-23', 'Annual snapshot (FY2022-23)', '#ff9933', '% of reported total', 'https://www.rbi.org.in/Scripts/PublicationsView.aspx?id=23470', 'RBI Table 21 GSDP observations for all 28 States expressed as shares of their reported total; Union Territories are excluded.'],
    ['state_per_capita_income_index', 'State Per-Capita Income Index', 'State per-capita NSDP indexed to the median = 100, FY2022-23', 'Annual snapshot (FY2022-23)', '#3fb950', ' index', 'https://www.rbi.org.in/Scripts/PublicationsView.aspx?id=23468', 'RBI Table 19 per-capita NSDP observations for all 28 States indexed to the state median; Union Territories are excluded. This is a relative comparison, not currency.'],
    ['state_power_availability_index', 'State Power Availability Index', 'State power availability indexed to the median = 100, FY2024-25', 'Annual snapshot (FY2024-25)', '#f6c344', ' index', 'https://www.rbi.org.in/Scripts/PublicationsView.aspx?id=23587', 'CEA per-capita power availability observations for all 28 States indexed to the state median; Union Territories are excluded.'],
    ['cyber_crime_rate', 'Cyber Crime Cases per 100,000 People', 'Registered cyber crime cases adjusted for population', 'Annual', '#ff7b72', ' cases per 100k', 'https://ncrb.gov.in/crime-in-india.html', 'NCRB registered cyber crime cases divided by World Bank population estimates.'],
    ['ndps_case_rate', 'NDPS Cases per 100,000 People', 'Registered NDPS cases adjusted for population', 'Annual', '#a371f7', ' cases per 100k', 'https://ncrb.gov.in/crime-in-india.html', 'NCRB registered NDPS cases divided by World Bank population estimates.'],
    ['road_fatality_rate', 'Road Fatalities per 100,000 People', 'Reported road fatalities adjusted for population', 'Annual', '#e3b341', ' deaths per 100k', 'https://morth.nic.in/road-accident-in-india', 'Reported road fatalities divided by World Bank population estimates.'],
    ['pew_india_religious_pluralism', 'Pew India: Religious Pluralism', 'Views on respecting religions and religious diversity', 'Survey snapshots', '#bc8cff', '% of respondents', 'https://www.pewresearch.org/religion/2021/06/29/religion-in-india-tolerance-and-segregation/', 'Thematic subset of separately labelled Pew survey responses; values are not combined or interpolated.'],
    ['pew_india_religious_practice', 'Pew India: Religious Identity and Practice', 'Survey responses on religious identity and practice', 'Survey snapshots', '#f778ba', '% of respondents', 'https://www.pewresearch.org/religion/2021/06/29/religion-in-india-tolerance-and-segregation/', 'Thematic subset of separately labelled Pew survey responses; values are not combined or interpolated.'],
    ['card_spend_total', 'Total Credit and Debit Card Spending', 'Reported credit and debit card point-of-sale spending combined', 'Annual', '#3fb950', ' INR lakh crore', 'https://www.rbi.org.in/Scripts/BS_ViewPaymentSystems.aspx', 'Sum of RBI-reported annual credit and debit card spending series.'],
    ['credit_card_spend_share', 'Credit Card Share of Card Spending', 'Credit card spending as a share of reported credit and debit card spending', 'Annual', '#58a6ff', '%', 'https://www.rbi.org.in/Scripts/BS_ViewPaymentSystems.aspx', 'Credit card spending divided by the combined reported credit and debit card spending.'],
    ['upi_value_growth', 'UPI Transaction Value Growth', 'Year-over-year change in annual UPI transaction value', 'Annual', '#f6c344', '%', 'https://www.npci.org.in/what-we-do/upi/product-statistics', 'Annual percentage change calculated from the reported UPI transaction-value series.'],
    ['military_expenditure_per_capita', 'Military Expenditure per Capita', 'Military expenditure in current US dollars per person', 'Annual', '#ff7b72', ' USD/person', 'https://data.worldbank.org/indicator/MS.MIL.XPND.CD', 'World Bank military expenditure divided by World Bank population estimates for matching years.'],
    ['upi_volume_index', 'UPI Transaction Volume Index', 'Monthly UPI transaction volume indexed to April 2020 = 100', 'Monthly', '#ff9933', ' index points', 'https://www.npci.org.in/what-we-do/upi/product-statistics', 'Calculated from the monthly UPI transaction-volume observations in the Government of India Economic Survey Statistical Appendix. April 2020 is the base month (100); this is a normalized index, not the RBI Digital Payments Index.'],
    ['pew_india_2026_global_views', 'Pew: Global views of India (2026)', 'Favorable, unfavorable and unsure views across 36 countries', 'Spring 2026 survey', '#3fb950', '%', 'https://www.pewresearch.org/short-reads/2026/08/13/public-opinion-of-india-is-mixed-across-36-countries/', 'Published Pew Spring 2026 Global Attitudes results for 36 countries. These responses measure views of India among people outside India; they are not a survey of Indian public opinion. Published percentages may not total 100 due to rounding.'],
    ['pew_india_2026_top_threats', 'Pew: Geopolitical threats named in India (2026)', 'Countries named as India’s greatest geopolitical threat', '2026 survey snapshot', '#ff7b72', '%', 'https://www.pewresearch.org/global/2026/08/13/india-and-pakistan-rivals-with-divergent-views-of-the-global-order/', 'Share of Indian adults naming Pakistan or China as India’s greatest geopolitical threat in Pew’s 2026 survey. Only figures published in the article summary are shown; the chart is not an exhaustive distribution.'],
    ['pew_india_2026_top_allies', 'Pew: Most important allies named in India (2026)', 'Countries named as India’s most important ally', '2026 survey snapshot', '#79c0ff', '%', 'https://www.pewresearch.org/global/2026/08/13/india-and-pakistan-rivals-with-divergent-views-of-the-global-order/', 'Share of Indian adults naming Russia or the United States as India’s most important ally in Pew’s 2026 survey. Only figures published in the article summary are shown; the chart is not an exhaustive distribution.'],
    ['pew_india_2021_diversity_views', 'Pew: Views on religious diversity in India', 'Whether religious diversity benefits or harms India', '2019–20 survey', '#bc8cff', '%', 'https://www.pewresearch.org/religion/2021/06/29/diversity-and-pluralism/', 'Pew’s Religion in India survey was conducted in 2019–2020 and published in 2021. The no-clear-position category includes “neither,” do not know, and no answer; rounded figures total 101%.'],
    ['pew_india_2021_religious_freedom', 'Pew: Religious freedom perceptions in India', 'Personal freedom to practice and perceived freedom for other faiths', '2019–20 survey', '#f778ba', '%', 'https://www.pewresearch.org/religion/2021/06/29/religious-freedom-discrimination-and-communal-relations/', 'Two distinct questions from Pew’s Religion in India survey (fieldwork in 2019–2020): respondents’ assessment of their own freedom and freedom for people of other religions.'],
    worldBank('agricultural_employment_share', 'Employment in Agriculture', 'Employment in agriculture as a share of total employment', '#3fb950', '%', 'SL.AGR.EMPL.ZS', 'Share of total employment in agriculture, based on the World Bank series that uses ILO modelled estimates.'),
    worldBank('urban_population_growth', 'Urban Population Growth', 'Annual growth rate of the urban population', '#f778ba', '%', 'SP.URB.GROW', 'Annual growth rate of the population living in urban areas. Sourced from World Bank Open Data.'),
    worldBank('net_energy_imports_share', 'Net Energy Imports', 'Net energy imports as a share of energy use', '#ff9933', '%', 'EG.IMP.CONS.ZS', 'Net energy imports relative to energy use; negative values indicate net exports. Sourced from World Bank Open Data.'),
    worldBank('lower_secondary_completion', 'Lower Secondary Completion Rate', 'Completion rate for lower secondary education', '#a371f7', '%', 'SE.SEC.CMPT.LO.ZS', 'Completion rate for lower secondary education. Sourced from World Bank Open Data.'),
    worldBank('government_health_spending_per_capita', 'Government Health Spending per Capita', 'Domestic general government health expenditure per person in current US dollars', '#3fb950', ' USD', 'SH.XPD.GHED.PC.CD', 'Domestic general government health expenditure per capita in current US dollars. Nominal values are not adjusted for inflation.'),
    worldBank('safely_managed_drinking_water', 'Safely Managed Drinking Water', 'Population using safely managed drinking-water services', '#79c0ff', '%', 'SH.H2O.SMDW.ZS', 'Share of the population using safely managed drinking-water services, as estimated in the World Bank series.'),
  ];

  window.INDIA_EXTRA_CHART_DEFINITIONS.push(
    ['gdp_sector_composition', 'GDP Sector Composition', 'Latest reported agriculture, industry and services shares of GDP', 'Latest common annual observation', '#ff9933', '% of GDP', 'https://data.worldbank.org/indicator/NV.AGR.TOTL.ZS?locations=IN', 'A doughnut view of the latest common World Bank sectoral value-added shares. Other GDP components are explicitly shown as the residual to 100%, not as a directly reported sector.'],
    ['state_gsdp_composition', 'State GSDP Share: Largest States', 'Eight largest State shares and the remaining 20 States', 'Annual snapshot (FY2022-23)', '#58a6ff', '% of reported State GSDP', 'https://www.rbi.org.in/Scripts/PublicationsView.aspx?id=23470', 'Distribution of reported GSDP across the 28 States. The eight largest shares are shown individually; the other 20 States are combined. Union Territories are excluded.'],
    ['urban_rural_population_composition', 'Urban and Rural Population Share', 'Latest urban and rural shares of India’s population', 'Latest annual estimate', '#f778ba', '% of population', 'https://data.worldbank.org/indicator/SP.URB.TOTL.IN.ZS?locations=IN', 'World Bank urban population share and its rural complement. The rural value is calculated as 100% minus the reported urban share.'],
    ['energy_supply_composition', 'Net Energy Import Dependence', 'Net energy imports and domestic supply as shares of energy use', 'Latest annual estimate', '#ff9933', '% of energy use', 'https://data.worldbank.org/indicator/EG.IMP.CONS.ZS?locations=IN', 'Doughnut summary of net energy imports and the calculated domestic-supply complement. This is net import dependence, not gross import volume.'],
    ['disease_burden_composition', 'Disease Burden Composition', 'NCD, communicable and residual causes in the latest reported year', 'Latest available estimate', '#ff7b72', '% of DALYs', 'https://www.icmr.gov.in/', 'Two categories from the existing disease-burden series plus the residual to 100%, labelled other causes. The residual is calculated, not a separately reported measurement.'],
    ['defence_budget_composition', 'Defence Share of Union Expenditure', 'Defence allocation compared with the remaining Union expenditure', 'Latest annual snapshot', '#f6c344', '% of Union expenditure', 'https://www.indiabudget.gov.in/', 'Defence expenditure share from the existing annual series and the calculated non-defence complement.'],
    ['card_spending_composition', 'Credit and Debit Card Spending Mix', 'Credit-card and debit-card POS/e-commerce spending in the latest common year', 'Latest common annual observation', '#58a6ff', 'INR lakh crore', 'https://www.rbi.org.in/Scripts/BS_ViewPaymentSystems.aspx', 'Latest common-year RBI credit-card and debit-card POS/e-commerce spending. Debit-card ATM withdrawals are excluded.'],
    ['india_live_party_seats_composition', 'Provisional Party Leads: Share of Published Seats', 'Party leads among currently published ECI constituencies', 'Live ECI snapshot', '#ff9933', 'constituencies', 'https://results.eci.gov.in/', 'Share of provisional party leads among only the constituencies currently published by ECI. This is not a statewide or all-election seat tally.']
  );

  const cycles = [2018, 2020, 2022, 2024];
  const offices = [
    { code: 'P', name: 'President', subgroup: 'U.S. Presidential Campaign Finance', scope: 'candidate party' },
    { code: 'S', name: 'Senate', subgroup: 'U.S. Congressional Campaign Finance', scope: 'candidate office state' },
    { code: 'H', name: 'House', subgroup: 'U.S. Congressional Campaign Finance', scope: 'candidate office state' },
  ];
  const measures = [
    { key: 'receipts', title: 'Total Receipts', color: '#3fb950' },
    { key: 'disbursements', title: 'Total Disbursements', color: '#ff9933' },
    { key: 'cash_on_hand', title: 'Cash on Hand', color: '#58a6ff' },
    { key: 'debts_owed', title: 'Debt Owed', color: '#ff7b72' },
  ];
  window.INDIA_EXTRA_CHART_DEFINITIONS.push(...cycles.flatMap(cycle =>
    offices.flatMap(office => measures.map(measure => {
      const key = `us_fec_${cycle}_${office.code.toLowerCase()}_${measure.key}`;
      const url = `https://www.fec.gov/files/bulk-downloads/${cycle}/weball${String(cycle).slice(-2)}.zip`;
      const details = `Federal Election Commission candidate-summary totals for the ${cycle} filing cycle. ${measure.title} are aggregated by ${office.scope}. ${office.code === 'P' ? 'Presidential candidate totals use party as the grouping because the FEC summary file does not report state presidential vote totals. The 2018 and 2022 filing cycles are midterm years, not Presidential election years.' : 'House and Senate candidate totals are grouped by candidate office state.'}\n\nThese are campaign-finance amounts, not votes, turnout, or public contributions alone. Candidate summaries include authorized committees and may be revised when amended reports are processed.`;
      return [
        key,
        `${cycle} ${office.code === 'P' ? 'Presidential' : office.name} Candidate ${measure.title}`,
        `${office.name} candidate campaign-finance totals by ${office.code === 'P' ? 'party' : 'state'}`,
        `FEC filing cycle ${cycle}`,
        measure.color,
        ' USD',
        url,
        details,
      ];
    }))
  ));
  window.INDIA_EXTRA_CHART_DEFINITIONS.push(...cycles.map(cycle => [
    `us_fec_${cycle}_p_receipt_composition`,
    `${cycle} Presidential Candidate Receipts by Party`,
    `Share of FEC-reported candidate receipts by party in filing cycle ${cycle}`,
    `FEC filing cycle ${cycle}`,
    '#3fb950',
    ' USD',
    `https://www.fec.gov/files/bulk-downloads/${cycle}/weball${String(cycle).slice(-2)}.zip`,
    `Federal Election Commission Presidential-office candidate receipts grouped by party for the ${cycle} filing cycle. ${cycle === 2018 || cycle === 2022 ? 'This is a midterm filing cycle, not a Presidential election year. ' : ''}Shares describe reported campaign-finance receipts, not votes or public contributions alone.`
  ]));
  const presidentialYears = [2000, 2004, 2008, 2012, 2016, 2020, 2024];
  window.INDIA_EXTRA_CHART_DEFINITIONS.push(...presidentialYears.map(year => [
    `us_presidential_electoral_composition_${year}`,
    `${year} Electoral College Vote Composition`,
    `Winner, main opponent and other or unassigned electors in ${year}`,
    `Presidential election ${year}`,
    '#58a6ff',
    ' electoral votes',
    `https://www.archives.gov/electoral-college/${year}`,
    `Distribution of all 538 Electoral College votes in ${year}. The remaining category includes votes for other candidates and any faithless or unassigned electors; these are not popular votes.`
  ]));

  const placements = {};
  const place = (keys, category, subgroup) => keys.forEach(key => { placements[key] = { category, subgroup }; });
  place(['gdp_ppp', 'gdp_deflator_growth', 'capital_formation_gdp', 'household_consumption_gdp', 'gross_savings_rate', 'public_debt_gdp'], 'Economic', 'Macroeconomics');
  place(['exports_gdp', 'imports_gdp', 'remittances_gdp', 'reserves_import_months', 'debt_service_exports'], 'Economic', 'Trade & External');
  place(['current_health_spending', 'physicians_density', 'basic_water_access', 'basic_sanitation_access'], 'Public Health & Epidemiology', 'Health Infrastructure & Spending');
  place(['under5_mortality'], 'Public Health & Epidemiology', 'Mortality & Lifespan Milestones');
  place(['urban_population_share', 'population_growth', 'fertility_rate', 'female_labor_participation', 'labor_force_participation', 'employment_population_ratio'], 'Social', 'Demographics');
  place(['crude_birth_rate', 'crude_death_rate'], 'Social', 'Demographics');
  place(['clean_fuel_access'], 'Social', 'Welfare');
  place(['primary_school_enrollment', 'secondary_school_enrollment', 'tertiary_school_enrollment', 'education_spending_gdp', 'adult_literacy_rate', 'mobile_subscriptions_per_100', 'fixed_broadband_per_100'], 'Social', 'Welfare');
  place(['agriculture_gdp_share', 'industry_gdp_share', 'services_gdp_share', 'manufacturing_gdp_share', 'cereal_yield'], 'Industry Trends & Performance', 'Manufacturing & Industrial Growth');
  place(['agricultural_land_share'], 'Industry Trends & Performance', 'Production & Commodities');
  place(['energy_use_per_capita', 'electricity_use_per_capita', 'renewable_energy_consumption', 'renewable_electricity_output', 'forest_area_share', 'pm25_exposure', 'net_energy_imports_share'], 'Mining & Natural Resources', 'Energy Minerals & Fuel');
  place(['agricultural_employment_share'], 'Industry Trends & Performance', 'Production & Commodities');
  place(['urban_population_growth'], 'Social', 'Demographics');
  place(['lower_secondary_completion'], 'Social', 'Welfare');
  place(['government_health_spending_per_capita', 'safely_managed_drinking_water'], 'Public Health & Epidemiology', 'Health Infrastructure & Spending');
  place(['state_gsdp_share'], 'State Performance & Regional Health', 'State Financial Health & GSDP');
  place(['state_per_capita_income_index'], 'State Performance & Regional Health', 'State Financial Health & GSDP');
  place(['state_power_availability_index'], 'State Performance & Regional Health', 'State Infrastructure & Services');
  place(['cyber_crime_rate', 'ndps_case_rate', 'road_fatality_rate'], 'Crime & Security', 'Violence & Crime');
  place(['pew_india_religious_pluralism', 'pew_india_religious_practice'], 'Pew Research', 'Public opinion');
  place(['card_spend_total', 'credit_card_spend_share'], 'Payments & Digital Banking', 'Card Spends & Ecosystem');
  place(['upi_value_growth'], 'Payments & Digital Banking', 'UPI & Digital Payments');
  place(['military_expenditure_usd', 'military_expenditure_per_capita'], 'Defence & Strategic', 'Defence Budget & Modernization');
  place(['upi_volume_index'], 'Payments & Digital Banking', 'UPI & Digital Payments');
  place(['tourism_arrivals', 'tourism_departures', 'tourism_receipts_usd'], 'Tourism & Heritage', 'International Visitor Trends');
  place(['unesco_india_sites_cumulative', 'unesco_india_new_inscriptions', 'unesco_india_current_categories'], 'Tourism & Heritage', 'World Heritage Sites');
  place(['pew_india_2026_global_views', 'pew_india_2026_top_threats', 'pew_india_2026_top_allies', 'pew_india_2021_diversity_views', 'pew_india_2021_religious_freedom'], 'Pew Research', 'Public opinion');
  place(['india_live_candidate_votes', 'india_live_candidate_vote_share', 'india_live_constituency_margin', 'india_live_winner_vote_share', 'india_live_party_seats'], 'Elections', 'Indian Elections');
  place(['india_live_party_seats_composition'], 'Elections', 'Indian Elections');
  place(['gdp_sector_composition'], 'Economic', 'Macroeconomics');
  place(['state_gsdp_composition'], 'State Performance & Regional Health', 'State Financial Health & GSDP');
  place(['urban_rural_population_composition'], 'Social', 'Demographics');
  place(['energy_supply_composition'], 'Mining & Natural Resources', 'Energy Minerals & Fuel');
  place(['disease_burden_composition'], 'Public Health & Epidemiology', 'Disease Burden & Epidemiology');
  place(['defence_budget_composition'], 'Defence & Strategic', 'Defence Budget & Modernization');
  place(['card_spending_composition'], 'Payments & Digital Banking', 'Card Spends & Ecosystem');
  place(['us_presidential_electoral_votes'], 'U.S. Elections', 'U.S. Presidential Elections');
  place(presidentialYears.map(year => `us_presidential_electoral_composition_${year}`), 'U.S. Elections', 'U.S. Presidential Elections');
  place(cycles.map(cycle => `us_fec_${cycle}_p_receipt_composition`), 'U.S. Elections', 'U.S. Presidential Campaign Finance');
  for (const cycle of cycles) {
    for (const office of offices) {
      place(
        measures.map(measure => `us_fec_${cycle}_${office.code.toLowerCase()}_${measure.key}`),
        'U.S. Elections',
        office.subgroup,
      );
    }
  }
  window.INDIA_EXTRA_CHART_PLACEMENT = placements;
})();
