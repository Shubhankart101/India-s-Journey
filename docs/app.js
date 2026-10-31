const definitions = [
  ['gdp_growth', 'Real GDP growth', 'Annual real GDP growth', 'Annual', '#ff9933', '%', 'https://data.worldbank.org/indicator/NY.GDP.MKTP.KD.ZG?locations=IN', 'Annual percentage growth in real gross domestic product. This is a historical national-accounts series, not a forecast.\n\nSourced from the World Bank indicator NY.GDP.MKTP.KD.ZG.'],
  ['cpi', 'CPI inflation', 'Consumer prices', 'Annual', '#63b3ed', '%', 'https://data.worldbank.org/indicator/FP.CPI.TOTL.ZG?locations=IN', 'Consumer price inflation tracks the annual change in the cost of a representative basket of goods and services. It is a broad measure of household purchasing-power pressure.\n\nThe series is useful alongside growth, exchange-rate, and trade indicators because imported costs and domestic demand can move inflation in different directions. Values are annual and come through the World Bank open API.'],
  ['per_capita_nni_inr', 'Per capita Net National Income', 'Per capita NNI at current prices in Indian Rupees', 'Annual', '#3fb950', ' INR', 'https://www.mospi.gov.in/', 'Per capita Net National Income (NNI) measures national income divided by population in current Indian Rupees. It expanded from ₹63,462 in FY2012 to ₹2.18 Lakh in FY2026.\n\nSourced from MOSPI National Accounts Statistics and official Economic Survey statements.'],
  ['per_capita_income_ppp', 'Per capita GNI in PPP dollars', 'GNI per capita in Purchasing Power Parity current international $', 'Annual', '#58a6ff', ' USD PPP', 'https://data.worldbank.org/indicator/NY.GNP.PCAP.PP.CD', 'GNI per capita converted to international dollars using purchasing power parity (PPP) rates, accounting for domestic price differences.\n\nSourced from World Bank Open Data indicator NY.GNP.PCAP.PP.CD.'],
  ['state_per_capita_income', 'Per-capita NSDP by state', 'Net State Domestic Product per person, FY2022-23', 'Annual snapshot (FY2022-23)', '#3fb950', ' INR lakh', 'https://www.rbi.org.in/Scripts/PublicationsView.aspx?id=23468', 'RBI Table 19 per-capita Net State Domestic Product at current prices. The comparable FY2022-23 snapshot covers all 28 States plus every Union Territory the RBI reports.'],
  ['state_power_per_capita', 'Per-capita power availability by state', 'Electricity availability per person, FY2024-25', 'Annual snapshot (FY2024-25)', '#f6c344', ' kWh/person', 'https://www.rbi.org.in/Scripts/PublicationsView.aspx?id=23587', 'RBI Table 138, sourced to the Central Electricity Authority. The FY2024-25 comparison covers all 28 States plus every Union Territory the RBI reports.'],
  ['state_gst_collections', 'Monthly State GST collections', 'Average monthly GST revenue by state', 'Static snapshot', '#f6c344', ' INR Cr', 'https://www.gst.gov.in/', 'Monthly State GST (SGST) collections comparing commercial consumption volume across states.\n\nSourced from GSTN Portal & Ministry of Finance.'],
  ['state_pmjdy_bank_accounts', 'PM Jan Dhan accounts by state', 'Cumulative PMJDY bank accounts opened in Crores', 'Annual / State', '#79c0ff', ' Crore accounts', 'https://pmjdy.gov.in/', 'State-wise distribution of PM Jan Dhan Yojana financial inclusion bank accounts (Uttar Pradesh 9.25 Cr, Bihar 5.82 Cr, West Bengal 4.95 Cr).\n\nSourced from Department of Financial Services, Ministry of Finance.'],
  ['state_pmjay_health_cards', 'Ayushman Bharat cards by state', 'Ayushman Bharat PM-JAY health cards issued in Crores', 'Static snapshot', '#f778ba', ' Crore cards', 'https://pmjay.gov.in/', 'State-wise distribution of Ayushman Bharat health protection cards issued to vulnerable households.\n\nSourced from National Health Authority (NHA) PM-JAY Open Dashboard.'],
  ['state_pmsvanidhi_street_vendors', 'PM SVANidhi vendor credit by state', 'Micro-credit working capital loans disbursed in Lakh vendors', 'Static snapshot', '#3fb950', ' Lakh vendors', 'https://pmsvanidhi.mohua.gov.in/', 'State-level street vendor micro-credit loan disbursements under PM SVANidhi scheme.\n\nSourced from Ministry of Housing and Urban Affairs (MoHUA).'],
  ['state_literacy_rates', 'Literacy rates across States & UTs', 'Literacy rate % across 28 States and 8 UTs', 'Static snapshot', '#bc8cff', '%', 'https://www.mospi.gov.in/', 'State-wise literacy rate comparison across India\'s federal landscape (Kerala 96.2%, Mizoram 91.3%, Goa 88.7%, Himachal 83.8%, Maharashtra 82.3%).\n\nSourced from MOSPI Periodic Labour Force Survey & Census Estimates.'],
  ['state_ev_adoption_charging', 'Electric Vehicle adoption by state', 'EV registrations & POS charging stations in Thousands', 'Static snapshot', '#3fb950', ' Thousand EVs', 'https://vahan.parivahan.gov.in/', 'State-wise electric mobility transition comparing EV vehicle registrations and charging station infrastructure.\n\nSourced from Ministry of Heavy Industries VAHAN Portal.'],
  ['state_export_preparedness_index', 'Export Preparedness Index by state', 'NITI Aayog EPI overall composite score out of 100', 'Static snapshot', '#58a6ff', ' Index', 'https://www.niti.gov.in/', 'State export competitiveness benchmark evaluating policy ecosystem, business environment, and export performance (Tamil Nadu 79.2, Maharashtra 78.6, Karnataka 76.4).\n\nSourced from NITI Aayog Export Preparedness Index.'],
  ['state_ease_of_doing_business', 'Ease of Doing Business by state', 'DPIIT BRAP Top Achievers Business Reform score %', 'Static snapshot', '#a371f7', '% score', 'https://dpiit.gov.in/', 'State business environment ranking evaluating Business Reform Action Plan (BRAP) implementation.\n\nSourced from DPIIT Ease of Doing Business State Rankings.'],
  ['northeast_insurgency_fatalities', 'North East insurgency fatalities', 'Annual fatalities in NE insurgent violence', 'Annual (2000-2025)', '#ff7b72', ' deaths', 'https://www.mha.gov.in/', 'Decadal fatality trajectory in insurgent violence across North Eastern states showing an 85%+ structural drop in security casualties.\n\nSourced from MHA North East Division & SATP North East Insurgency Database.'],
  ['northeast_insurgency_incidents', 'North East insurgent incidents', 'Annual registered insurgent incidents in North East', 'Annual (2014-2025)', '#ffa657', ' incidents', 'https://www.mha.gov.in/', 'Annual registered insurgent incidents across NE region showing pacification following major peace accords.\n\nSourced from Ministry of Home Affairs Annual Reports (North East Division).'],
  ['kashmir_insurgency_fatalities', 'Jammu & Kashmir insurgency deaths', 'Annual fatalities in J&K terrorism & insurgency', 'Annual (2000-2025)', '#f85149', ' deaths', 'https://www.mha.gov.in/', 'Annual total fatalities (civilians, security personnel, and terrorists) in J&K counter-terror operations dropping from 4,500+ in 2001 to under 100.\n\nSourced from MHA J&K Division & SATP Casualty Database.'],
  ['kashmir_terror_incidents', 'Jammu & Kashmir terror incidents', 'Annual registered terrorist incidents in J&K', 'Annual (2014-2025)', '#ff7b72', ' incidents', 'https://www.mha.gov.in/', 'Annual registered terrorist incidents in J&K showing a steep structural decline post-2019.\n\nSourced from Ministry of Home Affairs J&K Division Performance Reports.'],
  ['khalistan_insurgency_historical', 'Punjab militancy historical fatalities', 'Annual deaths during Punjab militancy period', 'Historical (1981-1995)', '#d29922', ' deaths', 'https://www.satp.org/', 'Historical annual fatality archive tracking the Punjab militancy period (1981-1995) prior to full restoration of peace.\n\nSourced from SATP Punjab Militancy Database & MHA Historical Security Reports.'],
  ['gst', 'GST collections', 'Gross monthly GST revenue', 'Monthly', '#f6c344', 'INR bn', 'https://www.gst.gov.in/', 'GST collections are a high-frequency signal of recorded consumption and production moving through India\'s indirect-tax system. Strong receipts can reflect higher activity, improved compliance, price effects, or a combination of these factors.\n\nThe monthly series is collated from the Economic Survey Statistical Appendix table 9.1. It should not be confused with a forecast or an estimate.'],
  ['fiscal_deficit', 'Fiscal deficit', 'Union fiscal deficit as share of GDP', 'Annual', '#f56c6c', '% GDP', 'https://www.indiabudget.gov.in/economicsurvey/doc/stat/tab2.4.xlsx', 'The fiscal deficit is the gap between government expenditure and receipts excluding borrowings. It indicates how much the public sector needs to finance during a fiscal year.\n\nThe annual series is collated from official Economic Survey table 2.4 Excel files across previous editions and reported as a share of GDP.'],
  ['iip', 'IIP growth', 'Industrial production', 'Monthly', '#ff8f66', '%', 'https://www.mospi.gov.in/', 'Industrial production measures activity across mining, manufacturing, and electricity. It is a useful complement to GDP because it responds more directly to changes in factory output and infrastructure-linked production.\n\nThe monthly General IIP index is collated from Economic Survey Statistical Appendix table 9.2; MOSPI remains the authoritative Indian source.'],
  ['rupee', 'Rupee exchange rate', 'INR per US dollar', 'Monthly', '#2ea44f', 'INR', 'https://data.rbi.org.in/DBIE/#/dbie/home', 'This series expresses the Indian rupee required to purchase one US dollar. A rising value means rupee depreciation against the dollar, all else equal.\n\nMonthly exchange-rate observations are collated from Economic Survey Statistical Appendix table 9.4, with RBI DBIE linked as the official portal.'],
  ['trade', 'Trade share of GDP', 'Exports plus imports as share of GDP', 'Annual', '#63b3ed', '%', 'https://data.worldbank.org/indicator/NE.TRD.GNFS.ZS?locations=IN', 'Trade openness compares the combined value of exports and imports with GDP. It gives context for how strongly India\'s output is connected to external demand, imported inputs, and global price movements.\n\nThis is a ratio rather than a rupee total, so it can rise because trade grows or because GDP changes. The series is sourced through the World Bank open API.'],
  ['forex', 'Foreign exchange reserves', 'Total reserves including gold', 'Annual', '#a371f7', 'USD', 'https://data.worldbank.org/indicator/FI.RES.TOTL.CD?locations=IN', 'Foreign-exchange reserves are external assets held by the monetary authority, including gold in this indicator. They help provide resilience against external-payment stress and exchange-rate volatility.\n\nReserve adequacy should be read with imports, debt, and the current account rather than treated as a standalone score. The displayed series is annual and denominated in current US dollars.'],
  ['bank_credit', 'Bank credit', 'Domestic credit to private sector', 'Annual', '#f56c6c', '%', 'https://data.worldbank.org/indicator/FS.AST.PRVT.GD.ZS?locations=IN', 'Domestic credit to the private sector measures financial-sector lending relative to the size of the economy. It can signal whether businesses and households have expanding or tightening access to finance.\n\nCredit growth is not automatically positive: the composition, repayment quality, and cost of borrowing matter. This annual ratio is a structural indicator, not a substitute for RBI monthly banking statistics.'],
  ['wpi', 'WPI inflation', 'Wholesale price inflation', 'Monthly', '#f6c344', '%', 'https://eaindustry.nic.in/', 'Wholesale price inflation tracks price movement at the producer and bulk-trade level. It can reveal input-cost pressure before those changes fully appear in consumer prices.\n\nWPI is not included in the Economic Survey monthly HFI tables used by this pipeline. The Office of the Economic Adviser remains the official source, but its public portal does not currently expose a stable automated export for this dashboard.'],
  ['upi', 'UPI activity', 'UPI transaction volume', 'Monthly', '#ff8f66', ' Crore', 'https://www.npci.org.in/what-we-do/upi/product-statistics', 'UPI transaction volume shows the scale of digital payments processed through India\'s real-time payments infrastructure. It is a useful activity and digitisation signal, especially when paired with transaction value.\n\nThe monthly volume series is collated from Economic Survey Statistical Appendix table 9.2; NPCI remains the authoritative product-statistics source.'],
  ['power_consumption', 'Power consumption', 'Electricity demand', 'Monthly', '#79c0ff', 'GWh', 'https://www.indiabudget.gov.in/economicsurvey/doc/stat/tab91.pdf', 'Power consumption is a high-frequency activity signal that reflects demand from households, services, and industry. It can move with weather, economic activity, and electrification.\n\nThe monthly series is collated from Economic Survey Statistical Appendix table 9.1. It measures electricity use, not generation capacity or reliability.'],
  ['eway_bills', 'E-way bills', 'Goods movement compliance volume', 'Monthly', '#56d364', 'million', 'https://www.indiabudget.gov.in/economicsurvey/doc/stat/tab91.pdf', 'E-way bills track electronically documented movement of goods. They provide a useful logistics and formal-commerce signal that complements GST collections.\n\nThe series is a transaction volume, not a rupee value or direct GDP estimate. It is collated from Economic Survey table 9.1.'],
  ['rail_freight', 'Rail freight traffic', 'Domestic rail freight', 'Monthly', '#f2cc60', 'thousand tonnes', 'https://www.indiabudget.gov.in/economicsurvey/doc/stat/tab91.pdf', 'Rail freight traffic reflects movement of bulk commodities and industrial inputs through the rail network. It provides a physical-economy signal alongside digital and tax indicators.\n\nThe series is reported in thousand tonnes and comes from Economic Survey table 9.1.'],
  ['port_cargo', 'Port cargo traffic', 'Cargo handled at ports', 'Monthly', '#d2a8ff', 'lakh tonnes', 'https://www.indiabudget.gov.in/economicsurvey/doc/stat/tab91.pdf', 'Port cargo traffic captures goods handled through India\'s ports and gives context for external trade and domestic supply chains.\n\nIt is a volume measure and should be read with merchandise exports, imports, and trade share rather than used as a price indicator.'],
  ['core_industries', 'Eight-core industries', 'Core industrial production index', 'Monthly', '#ff7b72', 'index', 'https://www.indiabudget.gov.in/economicsurvey/doc/stat/tab92.pdf', 'The eight-core industries index tracks major infrastructure-linked sectors including coal, crude oil, natural gas, refinery products, fertilisers, steel, cement, and electricity.\n\nIt is an important industrial activity companion to IIP and is collated from Economic Survey table 9.2.'],
  ['crude_oil', 'Indian crude oil basket', 'Average crude oil price', 'Monthly', '#ffa657', 'USD/barrel', 'https://www.indiabudget.gov.in/economicsurvey/doc/stat/tab93.pdf', 'The Indian crude oil basket price tracks an indicative average of crude prices relevant to India\'s import exposure. It helps explain fuel-cost pressure, inflation risk, and the external trade bill.\n\nThis is a crude price indicator, not a retail petrol or diesel price index. It is collated from Economic Survey table 9.3.'],
  ['fuel_consumption', 'Fuel consumption', 'Petroleum product consumption', 'Monthly', '#f778ba', 'million MT', 'https://www.indiabudget.gov.in/economicsurvey/doc/stat/tab94.pdf', 'Fuel consumption measures petroleum product demand and is a useful activity proxy for transport, industry, and household energy use.\n\nIt is not a fuel price index. The dashboard labels it explicitly as consumption and sources it from Economic Survey table 9.4.'],
  ['merchandise_exports', 'Merchandise exports', 'Goods exports', 'Monthly', '#3fb950', 'USD bn', 'https://www.indiabudget.gov.in/economicsurvey/doc/stat/tab94.pdf', 'Merchandise exports measure the value of goods sold abroad. They connect the dashboard to external demand, foreign exchange earnings, and manufacturing competitiveness.\n\nThe monthly values are collated from Economic Survey table 9.4 and should be interpreted with imports and the current account.'],
  ['merchandise_imports', 'Merchandise imports', 'Goods imports', 'Monthly', '#bc8cff', 'USD bn', 'https://www.indiabudget.gov.in/economicsurvey/doc/stat/tab94.pdf', 'Merchandise imports measure the value of goods purchased from abroad. They capture domestic demand, imported inputs, energy exposure, and pressure on the trade balance.\n\nThe monthly values are collated from Economic Survey table 9.4 and are not the same as total services-inclusive imports.'],
  ['merchandise_trade_balance', 'Merchandise trade balance', 'Goods exports minus goods imports', 'Monthly', '#f778ba', ' USD bn', 'https://www.indiabudget.gov.in/economicsurvey/doc/stat/tab94.pdf', 'The monthly merchandise trade balance is calculated as goods exports minus goods imports. Positive values indicate a surplus and negative values a deficit.\n\nThis national total excludes services and does not identify balances with individual countries or regions.'],
  ['bilateral_trade_balance', 'Merchandise balance by trading partner', 'Exports minus imports for leading partners', 'Annual', '#79c0ff', ' USD bn', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS', 'This chart compares India\'s reported merchandise exports and imports with its leading trading partners for the latest year with matching observations. Positive values indicate a surplus; negative values indicate a deficit.\n\nUN Comtrade reports exports on an FOB basis and imports on a CIF basis, so values are not perfectly symmetric. The chart covers goods only, not services, and is limited to the leading partners with verified code mappings.'],
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
  ['lwe_incidents', 'Maoist / LWE annual fatalities', 'Annual deaths in LWE violence', 'Annual (2004-2025)', '#f85149', ' deaths', 'https://www.mha.gov.in/en/divisionofmha/left-wing-extremism-division', 'Annual fatalities in Left-Wing Extremist violence across affected states, collated from official MHA annual reports and SATP compiled records.\n\nIt shows the structural decline in LWE violence over 22 years as security coverage and developmental interventions expanded across affected districts.'],
  ['terror_attacks', 'Terrorist attacks', 'India attacks in GTD-derived open data', '1970-2020', '#d29922', ' attacks', 'https://www.start.umd.edu/gtd/', 'The Global Terrorism Database is a reputable open research dataset covering terrorist events internationally from 1970 onward. This dashboard uses the India rows published by Our World in Data, with GTD provenance.\n\nIt is not an official Government of India dataset, and its event definitions differ from MHA and NCRB reporting. The series is not presented as a complete 1947-present history.'],
    ['terror_fatalities', 'Terrorism fatalities', 'Deaths in India GTD-derived attacks', '1970-2020', '#f85149', ' deaths', 'https://ourworldindata.org/grapher/terrorism-deaths.csv', 'This graph counts fatalities associated with India rows in the GTD-derived public series. It complements the attack-count graph by showing human cost rather than event frequency.\n\nIt is not an official Government of India dataset and does not provide a complete 1947-present history.'],
  ['terror_attacks_per_million', 'Terrorist attacks per million people', 'GTD-derived attacks normalized by population', '1970-2020', '#f6c344', ' per million', 'https://ourworldindata.org/grapher/terrorist-attacks.csv', 'Annual India attack counts divided by the World Bank population series and expressed per million residents. This supports population-scaled comparisons over time; it is a derived measure, not a separate official count.\n\nCoverage is limited to years shared by the GTD-derived attack series and World Bank population data.', ['https://ourworldindata.org/grapher/terrorist-attacks.csv', 'https://api.worldbank.org/v2/country/IND/indicator/SP.POP.TOTL?format=json&per_page=100']],
  ['terror_fatalities_per_million', 'Terrorism fatalities per million people', 'GTD-derived deaths normalized by population', '1970-2020', '#f85149', ' per million', 'https://ourworldindata.org/grapher/terrorism-deaths.csv', 'Annual fatalities associated with GTD-derived India attacks divided by the World Bank population series and expressed per million residents. This is a derived rate, not an official government terrorism count.\n\nCoverage is limited to years shared by the GTD-derived fatalities series and World Bank population data.', ['https://ourworldindata.org/grapher/terrorism-deaths.csv', 'https://api.worldbank.org/v2/country/IND/indicator/SP.POP.TOTL?format=json&per_page=100']],
  ['terror_fatalities_per_attack', 'Fatalities per terrorist attack', 'GTD-derived annual deaths divided by annual attacks', '1970-2020', '#ff7b72', ' deaths/attack', 'https://ourworldindata.org/grapher/terrorism-deaths.csv', 'Annual India terrorism fatalities divided by annual GTD-derived attack counts. It describes aggregate lethality by year and is not an estimate of the probability that an individual attack causes fatalities. Years with zero attacks are left blank.', ['https://ourworldindata.org/grapher/terrorism-deaths.csv', 'https://ourworldindata.org/grapher/terrorist-attacks.csv']],
  ['ncrb_crime', 'NCRB crime indicators', 'Crime in India 2023 rates by category', 'Single-year snapshot', '#f778ba', ' per 100k', 'https://en.wikipedia.org/wiki/Crime_in_India', 'The National Crime Records Bureau publishes Crime in India tables covering reported offences, crime rates, and related public-safety measures. Editions are not consistently comparable across years, so this card shows a single-year (2023) snapshot across crime categories rather than a fabricated multi-year trend.\n\nValues are official Crime in India 2023 rates per 100,000 population (per 100,000 children for crimes against children), compiled and cited on Wikipedia from NCRB Crime in India 2023 Volumes I-III.'],
  ['pew_india_global_power', 'Pew: India and global power', 'Indian views of global conflicts and neighbours', 'Survey snapshots', '#79c0ff', '%', 'https://www.pewresearch.org/global/2008/12/04/india/', 'Each point is a distinct survey statement from the cited Pew Global Attitudes Project report, not a continuous measurement. It shows the share of respondents agreeing with a specific statement in a specific year.\n\nStatements are not comparable to each other and should not be read as a trend line; the x-axis lists the statement and year, not an evenly spaced time series. Additional survey editions can be added as they are individually verified.'],
  ['pew_india_leadership', 'Pew: views of leadership', 'Indian public opinion and leadership', 'Survey editions', '#bc8cff', ' responses', 'https://www.pewresearch.org/global/', 'This subgroup tracks Pew Research Center India findings on public views of national leadership and political confidence when comparable India observations are available.\n\nSurvey editions are not the same as annual administrative statistics. Results must retain their field dates, question wording, sample design, and uncertainty notes before being plotted.'],
  ['pew_india_reports', 'Pew India report cadence', 'Pew India reports published by year', 'Report years', '#79c0ff', ' reports', 'https://www.pewresearch.org/search/india/', 'This graph catalogs dated Pew Research Center reports returned by the public India search corpus. It shows the volume of available India-related reporting by publication year, not a survey opinion estimate.\n\nEach report remains linked to its original Pew page, preserving the date, title, and study context. Individual survey percentages are not combined across incompatible questionnaires.'],
  ['pew_india_us_relations', 'Pew: US-India relations', 'Indian views of the United States, by survey statement', 'Survey snapshots', '#79c0ff', '%', 'https://www.pewresearch.org/global/2008/12/04/india/', 'Each point is a distinct survey statement from the cited Pew Global Attitudes Project report, not a continuous measurement. It shows the share of respondents agreeing with a specific statement in a specific year.\n\nStatements are not comparable to each other and should not be read as a trend line; the x-axis lists the statement and year, not an evenly spaced time series. Additional survey editions can be added as they are individually verified.'],
  ['pew_india_economy_confidence', 'Pew: Economic confidence in India', 'Indian public economic outlook, by survey statement', 'Survey snapshots', '#f6c344', '%', 'https://www.pewresearch.org/global/2008/12/04/india/', 'Each point is a distinct survey statement from the cited Pew Global Attitudes Project report, not a continuous measurement. It shows the share of respondents agreeing with a specific statement in a specific year.\n\nStatements are not comparable to each other and should not be read as a trend line; the x-axis lists the statement and year, not an evenly spaced time series. Additional survey editions can be added as they are individually verified.'],
  ['pew_india_technology', 'Pew: Technology adoption in India', 'Internet and mobile device use and attitudes', 'Survey editions', '#f778ba', ' responses', 'https://www.pewresearch.org/global/topic/india/', 'Pew surveys measure technology adoption rates, internet use frequency, and public attitudes toward digital platforms in India. This survey data contextualizes official telecom and internet-user statistics.\n\nSurvey-based adoption rates may differ from administrative telecom data because they reflect actual use patterns rather than connectivity or registration counts.'],
    ['violent_incidents', 'Overall violent incidents', 'Comparable all-India incident series', 'Coverage pending', '#ff7b72', ' incidents', 'https://ncrb.gov.in/crime-in-india.html', 'No single official open series currently combines violent crime, Maoist violence, and terrorism consistently across India.\n\nThis card stays visible as a research target so the dashboard does not add incompatible NCRB, MHA, and GTD definitions into a misleading total.'],
    ['lwe_civilian_casualties', 'LWE civilian casualties', 'Civilians killed in Maoist insurgency violence', '2000-2025', '#ff7b72', ' deaths', 'https://www.satp.org/datasheet-terrorist-attack/fatalities/india-maoistinsurgency', 'MHA describes civilian and security-force casualties in LWE violence, but the current public page does not expose a stable annual category table.\n\nThis series is sourced from the South Asia Terrorism Portal (SATP), a secondary, non-official source that compiles a year-wise civilian/security-force/perpetrator breakdown from news reports for its Maoist Insurgency tracker. It uses a different classification and count than MHA\'s own 2004-2025 aggregate of 8,956 deaths, so the two figures should not be summed or treated as the same series.'],
    ['lwe_security_force_casualties', 'LWE security-force casualties', 'Security forces killed in Maoist insurgency violence', '2000-2025', '#f2cc60', ' deaths', 'https://www.satp.org/datasheet-terrorist-attack/fatalities/india-maoistinsurgency', 'MHA identifies security-force casualties as a distinct LWE impact category, but no stable annual machine-readable series is currently published on the public page.\n\nThis series is sourced from the South Asia Terrorism Portal (SATP), a secondary, non-official source with its own Maoist Insurgency classification and news-based provisional counts. It is not the same series as MHA\'s own 2004-2025 aggregate of 8,956 deaths.'],
    ['lwe_perpetrator_casualties', 'LWE perpetrator casualties', 'Maoist/LWE cadre killed in insurgency violence', '2000-2025', '#d29922', ' deaths', 'https://www.satp.org/datasheet-terrorist-attack/fatalities/india-maoistinsurgency', 'The public MHA material does not provide a comparable annual perpetrator-casualty series.\n\nThis series is sourced from the South Asia Terrorism Portal (SATP), a secondary, non-official source reporting Maoist/CPI(Maoist) cadre killed under its own Maoist Insurgency classification, distinct from MHA\'s official aggregate.'],
  ['indian_matrix', 'Indian Matrix publication cadence', 'Articles published per week', 'Weekly', '#bc8cff', ' articles', 'https://substack.com/@indianmatrix', 'This graph tracks the public publication cadence of Indian Matrix articles. It adds the Substack source as a transparent, updateable public-data signal rather than treating article frequency as an economic or crime statistic.\n\nThe weekly RSS snapshot is collected by the pipeline and linked to Indian Matrix with appreciation for its visual public-data work.'],
  ['market_indices', 'Indian market indices', 'Sensex, Nifty, and Nifty VIX; rebased to 100', 'Monthly', '#58a6ff', ' index', 'https://www.indiabudget.gov.in/economicsurvey/doc/stat/tab9.3.pdf', 'This combined graph compares India\'s major equity-market indices and volatility using one normalized base-100 view. It makes direction and relative movement readable despite the different scales of the Sensex, Nifty, and VIX.\n\nThe monthly observations are collated from Economic Survey table 9.3. This is a market-context dashboard, not investment advice, and rebasing means the plotted values are relative rather than index levels.'],
  ['global_equity_indices', 'Global equity market comparison', 'BSE Sensex vs S&P 500, FTSE 100, Nikkei 225, and Shanghai Composite; rebased to 100', 'Annual / Monthly', '#ff9933', ' index', 'https://www.bseindia.com/', 'This graph compares India\'s primary equity benchmark (BSE Sensex) against leading global market indices (S&P 500, FTSE 100, Nikkei 225, Shanghai Composite) rebased to 100.\n\nIt illustrates the long-run compounding and relative performance of Indian capital markets alongside the world\'s major financial hubs.'],
  ['gdp_world_comparison', 'World top economies GDP comparison', 'GDP trajectories of India, US, China, Germany, Japan, and UK', 'Annual', '#ff9933', ' USD trillion', 'https://data.worldbank.org/indicator/NY.GDP.MKTP.CD', 'This chart plots the gross domestic product of India alongside the world\'s largest economies (United States, China, Germany, Japan, and United Kingdom) in current US dollars.\n\nIt contextualizes India\'s rise from an emerging developing economy following independence to one of the world\'s top 5 economic powerhouses.'],
  ['sectoral_market_indices', 'India sectoral market engines', 'Nifty IT, Nifty Bank, Nifty Auto, Nifty Energy, and Sensex; rebased to 100', 'Monthly / Annual', '#3fb950', ' index', 'https://www.nseindia.com/', 'This series tracks key sectoral engines of India\'s stock market expansion—Technology, Banking & Financials, Automotive, and Energy—rebased to 100 alongside the benchmark Sensex.\n\nIt reveals how different industry pillars have spearheaded growth across economic cycles.'],
  ['global_inflation_comparison', 'Global inflation benchmark comparison', 'Consumer price inflation in India, US, and Euro Area', 'Annual', '#ffa657', '%', 'https://data.worldbank.org/indicator/FP.CPI.TOTL.ZG', 'This indicator compares consumer price inflation rate trends across India, the United States, and the Euro Area.\n\nReading India\'s inflation alongside major global central bank economies highlights how global commodity shocks, monetary policy, and exchange rates impact domestic price stability.'],
  ['defence_expenditure', 'Defence expenditure', 'Military expenditure as share of GDP', 'Annual', '#ff7b72', '% GDP', 'https://data.worldbank.org/indicator/MS.MIL.XPND.GD.ZS?locations=IN', 'Military expenditure tracks defence spending relative to the size of the national economy. It measures military resource allocation across peacetime and security challenges.\n\nData comes through the World Bank open API and SIPRI military expenditure database.'],
  ['defence_exports', 'India defence exports', 'Annual defence exports from India', 'Annual', '#3fb950', 'INR Cr', 'https://www.ddpmod.gov.in/', 'India\'s defence exports have expanded significantly as part of indigenous manufacturing and Make in India defence initiatives.\n\nData is collated from official Ministry of Defence Department of Defence Production (DDP) statistics.'],
  ['defence_production', 'Value of defence production', 'Total value of indigenous defence production', 'Annual', '#58a6ff', 'INR Cr', 'https://www.ddpmod.gov.in/', 'Total value of defence production captures manufacturing output across Defence Public Sector Undertakings (DPSUs), ordnance factories, and private sector defence enterprises.\n\nOfficial data is published by the Department of Defence Production, Ministry of Defence.'],
  ['defence_stockpile', 'Defence stockpile index', 'SIPRI arms inventory & capability index', 'Historical', '#a371f7', ' SIPRI TIV', 'https://www.sipri.org/databases/armstransfers', 'SIPRI Trend Indicator Value (TIV) measures the volume of conventional military capability and major weapons stockpiles transferred and maintained.\n\nIt provides a long-run comparative measure of military equipment inventory.'],
  ['defence_production_exports', 'Defence production & exports engine', 'Defence production vs exports trajectory', 'Annual', '#58a6ff', 'INR Cr', 'https://www.ddpmod.gov.in/', 'This combined graph compares total indigenous defence production alongside defence export growth in INR Crores.\n\nIt illustrates the structural transition of India\'s defence industrial base toward export competitiveness.'],
  ['ncrb_ipc_crime_rate', 'NCRB IPC crime rate', 'Total cognizable IPC crime rate per 100k', 'Historical (1951-2023)', '#ff7b72', ' per 100k', 'https://ncrb.gov.in/crime-in-india.html', 'The IPC cognizable crime rate tracks total reported Indian Penal Code offences per 100,000 population across 7 decades of post-independence Crime in India reports.\n\nNote that changes in reporting, police registration, and population censuses affect long-term comparability.'],
  ['crimes_against_women', 'Crimes against women rate', 'Reported crimes per 100k female population', 'Annual (2005-2023)', '#f778ba', ' per 100k females', 'https://ncrb.gov.in/crime-in-india.html', 'This indicator tracks reported offences against women per 100,000 female population, including cruelty by husband/relatives, assault, kidnapping, and sexual offences.\n\nIncreased reporting can reflect greater public awareness and filing under revised legal definitions as well as baseline changes.'],
  ['cyber_crime', 'Cyber crime case volume', 'Registered cyber crime cases in India', 'Annual (2014-2023)', '#79c0ff', ' cases', 'https://ncrb.gov.in/crime-in-india.html', 'Cyber crime cases track registered offences under the Information Technology Act and cyber-enabled IPC crimes.\n\nThe rapid increase reflects nationwide digital adoption, online financial services, and expanded cyber police reporting.'],
  ['economic_offences', 'Economic offences rate', 'Cheating, fraud & forgery per 100k', 'Annual (2014-2023)', '#f6c344', ' per 100k', 'https://ncrb.gov.in/crime-in-india.html', 'Economic offences measure financial crimes including criminal breach of trust, forgery, cheating, and counterfeiting per 100,000 population.\n\nData is sourced from official NCRB Crime in India annual volumes.'],
  ['pew_india_religion_tolerance', 'Pew: Religion, diversity & tolerance', 'Pew survey on religious tolerance, pluralism and freedom', 'Survey snapshots', '#3fb950', '%', 'https://www.pewresearch.org/religion/2021/06/29/religion-in-india-tolerance-and-segregation/', 'Landmark Pew Research Center study (Religion in India: Tolerance and Segregation) based on face-to-face interviews with 29,999 Indian adults across 26 states and UTs.\n\nIt examines religious tolerance, freedom of practice, and public views on diversity among India\'s major religious communities.'],
  ['pew_india_demographics_family', 'Pew: Religion & family demographics', 'Pew survey on religious identity, practices and marriage views', 'Survey snapshots', '#a371f7', '%', 'https://www.pewresearch.org/religion/2021/06/29/religion-in-india-tolerance-and-segregation/', 'This indicator tracks core demographic findings from Pew Research Center\'s Religion in India study, covering religious practice frequency, karma belief, and social norms.\n\nEach point represents a specific survey statement from the 2019-2020 national Pew study.'],
  ['pew_india_gender_roles', 'Pew: Gender roles & equality', 'Pew survey on gender equality, leadership & family roles', 'Survey snapshots', '#f778ba', '%', 'https://www.pewresearch.org/religion/2022/03/02/how-indians-view-gender-roles-in-families-and-society/', 'Pew Research Center national study on gender roles in Indian society.\n\nIt examines attitudes toward equal rights, female political leadership, family decision-making, and employment priorities.'],
  ['pew_india_media_news', 'Pew: Media trust & news habits', 'Pew survey on news media trust, social media & fake news concerns', 'Survey snapshots', '#79c0ff', '%', 'https://www.pewresearch.org/global/topic/media-and-technology/', 'Pew Global Attitudes Project tracking news consumption habits, media trust, and digital platform impact in India.'],
  ['pew_india_climate_environment', 'Pew: Climate & environmental views', 'Pew survey on climate change, pollution & lifestyle willingness', 'Survey snapshots', '#3fb950', '%', 'https://www.pewresearch.org/global/topic/climate-change-energy/', 'Pew Research Center studies tracking public awareness and concern over climate change, air & water pollution, and willingness to adapt personal lifestyles in India.'],
  ['defence_budget_share', 'Defence allocation', 'Share of total Union budget expenditure', 'Annual', '#ffa657', '% Budget', 'https://www.indiabudget.gov.in/', 'Defence allocation tracks military budget spending as a percentage of overall Central Government Expenditure.\n\nData is collated from official Ministry of Finance Union Budget allocation documents.'],
  ['defence_rd_budget', 'Defence R&D expenditure', 'DRDO & defense research spending', 'Annual', '#79c0ff', 'INR Cr', 'https://www.drdo.gov.in/', 'Defence R&D expenditure measures capital and revenue allocation for indigenous weapons development, missile technology, and military research.\n\nData is sourced from DRDO and Ministry of Defence annual standing committee reports.'],
  ['defence_capital_acquisition', 'Defence modernization capital outlay', 'Capital acquisition spending for armed forces', 'Annual', '#58a6ff', 'INR Cr', 'https://www.ddpmod.gov.in/', 'Capital acquisition outlay reflects funds allocated for procuring weapons, aircraft, naval frigates, artillery, and modern military hardware.\n\nOfficial statistics are published by the Ministry of Defence.'],
  ['sipri_arms_imports', 'India arms imports trend', 'SIPRI arms import Trend Indicator Value (TIV)', 'Historical', '#ff7b72', ' SIPRI TIV', 'https://www.sipri.org/databases/armstransfers', 'SIPRI arms imports index tracks conventional weapon import volumes. The declining trend highlights India\'s structural shift from foreign import dependency toward indigenous manufacturing.'],
  ['union_budget_expenditure', 'Union Budget total expenditure', 'Union budget total spending trajectory', 'Annual', '#58a6ff', 'INR Lakh Cr', 'https://www.indiabudget.gov.in/', 'Total central government expenditure from post-independence budgets to modern Union Budgets in ₹ Lakh Crores.\n\nSourced from official Union Budget Expenditure statements.'],
  ['budget_yoy_growth', 'Union Budget YoY growth', 'Annual percentage increase in Union expenditure', 'Annual', '#3fb950', '% YoY', 'https://www.indiabudget.gov.in/', 'Year-on-year percentage increase in central budget allocation.\n\nReflects fiscal policy expansion across economic cycles.'],
  ['capital_expenditure_capex', 'Union capital expenditure (Capex)', 'Central budget capital expenditure for asset creation', 'Annual', '#ff9933', 'INR Lakh Cr', 'https://www.indiabudget.gov.in/', 'Capital Expenditure (Capex) allocation for roads, railways, ports, defense, and infrastructure creation.\n\nHighlights India\'s strategic pivot toward asset building and long-term capital formation.'],
  ['social_category_literacy', 'Literacy by social group', 'Literacy rates across SC, ST, OBC and General categories', 'Static snapshot', '#bc8cff', '%', 'https://www.mospi.gov.in/', 'Literacy rate breakdown across social categories (Scheduled Castes, Scheduled Tribes, Other Backward Classes, and General category).\n\nSourced from MOSPI Periodic Labour Force Survey and Census estimates.'],
  ['religious_demographics', 'Literacy by religious community', 'Literacy rates across major religious communities', 'Static snapshot', '#a371f7', '%', 'https://niti.gov.in/', 'Literacy rates across major religious groups in India (Hindu, Muslim, Christian, Sikh, Buddhist, Jain).\n\nSourced from Census of India and NFHS-5 socio-religious demographic studies.'],
  ['pm_mudra_social_breakdown', 'PM MUDRA loans by social group', 'MUDRA loan account distribution by social & gender category', 'Static snapshot', '#ff9933', '% share', 'https://www.mudra.org.in/', 'PMMY MUDRA loan account distribution showing financial inclusion across Women entrepreneurs (68%), OBCs (28%), SCs (18%), and STs (6%).\n\nSourced from PMMY Portal & Ministry of Finance.'],
  ['gross_tax_yoy_growth', 'Gross tax revenue YoY growth', 'Annual percentage growth in gross central tax collections', 'Annual', '#58a6ff', '% YoY', 'https://cga.nic.in/', 'Year-on-year growth rate of Gross Central Tax Collections.\n\nReflects tax compliance, economic activity, and fiscal revenue buoyancy. Sourced from Controller General of Accounts (CGA).'],
  ['iron_ore_production', 'Iron ore production', 'National iron ore mining output', 'Annual', '#58a6ff', ' Million Tonnes', 'https://mines.gov.in/', 'Iron ore is the primary raw material for steelmaking and industrial infrastructure. India is among the world\'s largest iron ore producers, led by Odisha, Chhattisgarh, and Karnataka.\n\nData is sourced from the Indian Bureau of Mines (IBM) and Ministry of Mines.'],
  ['bauxite_aluminium_output', 'Bauxite production', 'Bauxite ore mining output', 'Annual', '#f6c344', ' Million Tonnes', 'https://mines.gov.in/', 'Bauxite is the principal ore for aluminium smelting, vital for aerospace, power transmission, automotive, and packaging industries.\n\nSourced from IBM and Ministry of Mines annual mineral reports.'],
  ['copper_production', 'Refined copper production', 'Refined copper metal production', 'Annual', '#ff8f66', ' Thousand Tonnes', 'https://www.hindustancopper.com/', 'Refined copper is essential for electrical grids, electric vehicles, electronics, and urban infrastructure.\n\nData collated from Ministry of Mines and Hindustan Copper Limited (HCL).'],
  ['manganese_chromite_production', 'Manganese ore output', 'Manganese ore mining production', 'Annual', '#bc8cff', ' Lakh Tonnes', 'https://ibm.gov.in/', 'Manganese ore is a crucial alloy element in steel manufacturing and battery technologies.\n\nSourced from Indian Bureau of Mines (IBM) Annual Mineral Statistics.'],
  ['coal_production', 'Coal production trajectory', 'Domestic coal mining output', 'Annual', '#79c0ff', ' Million Tonnes', 'https://coal.nic.in/', 'Coal is India\'s primary baseload energy source, fueling thermal power stations, steel plants, and heavy manufacturing.\n\nSourced from Coal Controller\'s Organisation and Ministry of Coal.'],
  ['lignite_production', 'Lignite production', 'Lignite mining output', 'Annual', '#ffa657', ' Million Tonnes', 'https://www.nlcindia.in/', 'Lignite (brown coal) is mined predominantly in Tamil Nadu, Rajasthan, and Gujarat for regional thermal power generation.\n\nSourced from NLC India Limited and Ministry of Coal.'],
  ['crude_petroleum_domestic', 'Domestic crude oil production', 'Domestic crude petroleum output', 'Annual', '#f778ba', ' Million MT', 'https://mopng.gov.in/', 'Domestic crude oil production from onshore and offshore fields (Mumbai High, Assam, Rajasthan, KG Basin) supplies domestic refineries alongside energy imports.\n\nSourced from Ministry of Petroleum & Natural Gas (MoPNG) and PPAC.'],
  ['natural_gas_production', 'Natural gas production', 'Domestic natural gas production', 'Annual', '#56d364', ' BCM', 'https://dghindia.gov.in/', 'Natural gas is a clean energy transition fuel used in fertilizer production, city gas distribution (CGD), power plants, and industrial heating.\n\nSourced from Directorate General of Hydrocarbons (DGH) and MoPNG.'],
  ['limestone_production', 'Limestone production', 'Limestone mining for cement & steel', 'Annual', '#d2a8ff', ' Million Tonnes', 'https://ibm.gov.in/', 'Limestone is the foundational raw material for cement manufacturing and steel fluxing, reflecting real estate and infrastructure construction activity.\n\nSourced from Indian Bureau of Mines (IBM).'],
  ['rare_earths_critical_minerals', 'Critical minerals & REE index', 'Rare earth elements and critical minerals production index', 'Annual', '#3fb950', ' Index', 'https://www.irel.co.in/', 'Critical minerals (lithium, cobalt, neodymium, dysprosium, titanium) power clean energy transition, defence radars, and semiconductor supply chains.\n\nIndex compiled from IREL (India) Limited and Ministry of Mines Critical Minerals Mission.'],
  ['rock_phosphate_gypsum', 'Fertilizer mineral raw materials', 'Rock phosphate and gypsum output', 'Annual', '#e3b341', ' Lakh Tonnes', 'https://ibm.gov.in/', 'Rock phosphate and gypsum are core industrial minerals for chemical fertilizer production (DAP/SSP) and cement manufacturing.\n\nSourced from Indian Bureau of Mines.'],
  ['mineral_metal_exports', 'Mineral & metal exports value', 'Total mineral and metal exports', 'Annual', '#3fb950', ' USD bn', 'https://www.dgft.gov.in/', 'Value of mineral, ore, and metal exports contributing to foreign exchange earnings and global commodity trade.\n\nSourced from DGFT and Ministry of Commerce.'],
  ['iron_ore_exports', 'Iron ore exports volume', 'Iron ore export volume', 'Annual', '#58a6ff', ' Million Tonnes', 'https://www.mmtcltd.com/', 'Iron ore exports sent to international steelmakers, managed under export quotas and duty frameworks.\n\nSourced from DGFT, MMTC, and Ministry of Commerce.'],
  ['refined_petroleum_exports', 'Refined petroleum exports', 'Refined petroleum products exports', 'Annual', '#bc8cff', ' Million MT', 'https://www.ppac.gov.in/', 'India is a major regional refining hub, exporting diesel, petrol, aviation turbine fuel (ATF), and naphtha worldwide.\n\nSourced from Petroleum Planning & Analysis Cell (PPAC), MoPNG.'],
  ['critical_mineral_import_dependency', 'Critical minerals import reliance', 'Import dependency index for 24 critical minerals', 'Annual', '#ff7b72', '% import reliance', 'https://mines.gov.in/', 'Strategic import reliance index across 24 critical minerals. Lower values reflect growing domestic extraction, recycling, and overseas asset acquisition under National Critical Minerals Mission.'],
  ['upi_transaction_value', 'UPI transaction value', 'Annual UPI transaction value trajectory', 'Annual', '#3fb950', ' INR Lakh Cr', 'https://www.npci.org.in/', 'Annual transaction value processed via Unified Payments Interface (UPI). It highlights the massive scale of real-time digital payments in India\'s retail economy.\n\nSourced from National Payments Corporation of India (NPCI) and RBI.'],
  ['credit_card_spends', 'Credit card spends', 'Annual credit card POS & e-commerce spends', 'Annual', '#ff9933', ' INR Lakh Cr', 'https://www.rbi.org.in/', 'Total annual spending by consumers using credit cards at point-of-sale (POS) terminals and e-commerce portals.\n\nSourced from Reserve Bank of India Payment System Indicators.'],
  ['debit_card_spends', 'Debit card POS spends', 'Annual debit card POS transaction spends', 'Annual', '#58a6ff', ' INR Lakh Cr', 'https://www.rbi.org.in/', 'Annual consumer expenditure processed via debit cards at merchant POS terminals, excluding cash ATM withdrawals.\n\nSourced from Reserve Bank of India Payment System Statistics.'],
  ['credit_card_in_circulation', 'Active credit cards', 'Credit cards in circulation', 'Annual', '#a371f7', ' Crore cards', 'https://www.rbi.org.in/', 'Total active credit cards issued by banks in India, showing expanding formal consumer credit access.\n\nSourced from Reserve Bank of India.'],
  ['debit_card_in_circulation', 'Active debit cards', 'Debit cards in circulation', 'Annual', '#79c0ff', ' Crore cards', 'https://www.rbi.org.in/', 'Total active debit cards issued by financial institutions, driven by PM Jan Dhan Yojana bank account expansion.\n\nSourced from Reserve Bank of India.'],
  ['rbi_digital_payments_index', 'RBI Digital Payments Index', 'RBI DPI index trajectory', 'Annual', '#56d364', ' index', 'https://www.rbi.org.in/', 'Comprehensive index built by Reserve Bank of India to measure payment enablement, infrastructure, performance, and consumer centricity (Base 100 = March 2018).\n\nSourced from Reserve Bank of India.'],
  ['national_highways_built', 'National Highways construction', 'Kilometres of National Highways constructed', 'Annual', '#56d364', ' km/year', 'https://morth.nic.in/', 'Annual construction cadence of National Highways under Bharatmala Pariyojana and Ministry of Road Transport & Highways initiatives.\n\nSourced from MoRTH.'],
  ['railway_electrification', 'Railway electrification share', 'Electrified broad gauge rail network share', 'Annual', '#3fb950', '% network', 'https://indianrailways.gov.in/', 'Percentage of Indian Railways broad gauge network converted to 25 kV AC electric traction, moving toward 100% Net Zero Carbon Emitter target.\n\nSourced from Ministry of Railways.'],
  ['renewable_energy_capacity', 'Renewable energy capacity', 'Total installed renewable power capacity', 'Annual', '#f6c344', ' GW', 'https://mnre.gov.in/', 'Cumulative installed renewable energy capacity including Solar, Wind, Small Hydro, and Biomass power.\n\nSourced from Ministry of New and Renewable Energy (MNRE) and CEA.'],
  ['civil_aviation_passengers', 'Air passenger traffic', 'Domestic and international air passenger volume', 'Annual', '#79c0ff', ' Million passengers', 'https://www.dgca.gov.in/', 'Total annual passenger traffic handled by Indian airports, reflecting rising regional connectivity under UDAN scheme.\n\nSourced from Directorate General of Civil Aviation (DGCA).'],
  ['telecom_broadband_subscribers', 'High-speed broadband subscribers', 'Wireless & wireline broadband subscriber base', 'Annual', '#f778ba', ' Million subscribers', 'https://www.trai.gov.in/', 'Total high-speed broadband subscriber base across 4G/5G mobile networks and FTTH wireline connections.\n\nSourced from Telecom Regulatory Authority of India (TRAI).'],
  ['auto_production_volume', 'Automobile production', 'Total vehicles manufactured', 'Annual', '#ff9933', ' Million units', 'https://www.siam.in/', 'Total automobile manufacturing volume across passenger vehicles, commercial vehicles, three-wheelers, and two-wheelers.\n\nSourced from Society of Indian Automobile Manufacturers (SIAM).'],
  ['auto_domestic_sales', 'Automobile domestic sales', 'Annual sales by vehicle category, FY2008-09 to FY2013-14', 'Annual (2008-14)', '#ff9933', ' million vehicles', 'https://www.siam.in/statistics.aspx?mpgid=8&pgidtrail=14', 'Annual domestic sales of passenger vehicles, commercial vehicles, three-wheelers, and two-wheelers as reported by SIAM. The headline series is total domestic sales, with category trends shown as separate chart lines.\n\nSIAM\'s public table currently covers FY2008-09 through FY2013-14 only. This chart does not extrapolate the data or substitute production/registrations for sales.'],
  ['private_consumption_pc', 'Real household consumption per capita', 'Household final consumption per person, constant 2015 US dollars', 'Annual', '#3fb950', ' USD/person', 'https://data.worldbank.org/indicator/NE.CON.PRVT.PC.KD?locations=IN', 'Households and non-profit institutions serving households (NPISHs) final consumption expenditure per capita, expressed in constant 2015 US dollars. It provides a long-run, inflation-adjusted signal of material consumption per person.\n\nIt is an average, not a measure of distribution or each household\'s purchasing power, and it does not capture unpaid work or public services. Sourced from World Bank indicator NE.CON.PRVT.PC.KD.'],
  ['crude_steel_production', 'Crude steel production', 'Annual crude steel production output', 'Annual', '#58a6ff', ' Million Tonnes', 'https://steel.gov.in/', 'Total crude steel manufactured by integrated steel plants and secondary producers. India is the 2nd largest crude steel producer globally.\n\nSourced from Ministry of Steel and Joint Plant Committee (JPC).'],
  ['electronics_manufacturing', 'Electronics manufacturing output', 'Domestic electronics manufacturing value', 'Annual', '#bc8cff', ' INR Lakh Cr', 'https://www.meity.gov.in/', 'Total production value of mobile phones, consumer electronics, IT hardware, and industrial electronics boosted by PLI schemes.\n\nSourced from MeitY and ICEA.'],
  ['pharma_exports_trajectory', 'Pharmaceutical exports', 'Biotech & pharmaceutical export value', 'Annual', '#3fb950', ' USD bn', 'https://pharmexcil.com/', 'Export value of active pharmaceutical ingredients (APIs), formulations, vaccines, and biosimilars to over 200 countries.\n\nSourced from Pharmexcil and Ministry of Commerce.'],
  ['textiles_apparel_exports', 'Textiles & apparel exports', 'Textiles, garments & technical textiles exports', 'Annual', '#e3b341', ' USD bn', 'https://texmin.nic.in/', 'Export earnings from cotton yarn, ready-made garments, man-made fibres, and technical textiles.\n\nSourced from Ministry of Textiles and DGFT.'],
  ['state_gsdp_comparison', 'GSDP by state', 'Gross State Domestic Product at current prices, FY2022-23', 'Annual snapshot (FY2022-23)', '#58a6ff', ' INR Lakh Cr', 'https://www.rbi.org.in/Scripts/PublicationsView.aspx?id=23470', 'RBI Table 21, Gross State Domestic Product at current prices. The comparable FY2022-23 snapshot covers all 28 States plus every Union Territory the RBI reports. The chart is a one-year comparison, not a continuous growth trajectory.'],
  ['state_pmay_homes', 'PMAY housing completions by state', 'Cumulative pucca housing units completed', 'Static snapshot', '#56d364', ' Lakh houses', 'https://pmaymis.gov.in/', 'State-wise distribution of affordable housing units constructed under PM Awas Yojana (PMAY-G & PMAY-U).\n\nSourced from MoHUA and Ministry of Rural Development.'],
  ['state_jjm_water_coverage', 'Jal Jeevan tap water coverage by state', 'Rural households with tap water access %', 'Static snapshot', '#63b3ed', '% households', 'https://ejalshakti.gov.in/', 'Rural drinking water security comparing tap water connection coverage across states under Jal Jeevan Mission.\n\nSourced from Ministry of Jal Shakti Har Ghar Jal dashboard.'],
  ['state_mudra_loans', 'PM MUDRA loan disbursements by state', 'Cumulative loan amount disbursed', 'Static snapshot', '#a371f7', ' INR Cr', 'https://www.mudra.org.in/', 'Micro-enterprise credit expansion showing MUDRA loan disbursements across entrepreneurship hub states.\n\nSourced from PMMY Portal & Department of Financial Services.'],
  ['ndps_drug_cases', 'NDPS Act drug offences cases', 'Registered narcotics cases in India', 'Annual (2014-2023)', '#f778ba', ' cases', 'https://ncrb.gov.in/', 'Registered offences under the Narcotic Drugs and Psychotropic Substances (NDPS) Act.\n\nSourced from official NCRB Crime in India volumes.'],
  ['child_protection_pocso', 'Crimes against children & POCSO', 'Registered offences against children', 'Annual (2014-2023)', '#ff7b72', ' cases', 'https://ncrb.gov.in/', 'Crimes reported against children including offences registered under the Protection of Children from Sexual Offences (POCSO) Act.\n\nSourced from official NCRB Crime in India volumes.'],
  ['road_accidents_fatalities', 'Road traffic accident fatalities', 'Annual deaths from road traffic accidents', 'Annual (2010-2024)', '#ffa657', ' deaths', 'https://morth.nic.in/', 'Annual fatalities resulting from road traffic accidents across National Highways, State Highways, and urban roads.\n\nSourced from MoRTH and NCRB Accidental Deaths & Suicides in India (ADSI).'],
  ['police_per_population', 'Police personnel per 100k population', 'Sanctioned police strength per 100,000 people', 'Annual (2010-2024)', '#79c0ff', ' per 100k', 'https://bprd.nic.in/', 'Sanctioned civil and armed police personnel relative to population size, measuring law enforcement operational capacity.\n\nSourced from Bureau of Police Research and Development (BPR&D).'],
  ['india_live_candidate_votes', 'Indian live election results', 'Candidate vote totals in currently published Lok Sabha and State Assembly by-elections', 'Live (3-hour refresh)', '#ff9933', ' votes', 'https://results.eci.gov.in/', 'Top 30 candidates by currently reported vote totals from the Election Commission of India results portal. The chart is refreshed every three hours when the portal publishes data; the linked dataset preserves all parsed constituency and candidate rows. ECI displayed results are provisional until Form 20 is published. Historical Lok Sabha and Assembly result archives are not included because a stable, openly accessible official archive was not verified.'],
  ['india_live_candidate_vote_share', 'Indian candidate vote share', 'Reported candidate share of votes in currently published constituencies', 'Live (3-hour refresh)', '#f6c344', '%', 'https://results.eci.gov.in/', 'Top 30 candidates by vote share from currently published ECI constituency tables. ECI displayed results are provisional until Form 20 is published.'],
  ['india_live_constituency_margin', 'Indian constituency lead', 'Reported vote margin between the top two candidates', 'Live (3-hour refresh)', '#58a6ff', ' votes', 'https://results.eci.gov.in/', 'Calculated as the reported vote total of the leading candidate minus the runner-up in each currently published constituency. ECI displayed results are provisional until Form 20 is published.'],
  ['india_live_winner_vote_share', 'Indian leading-candidate vote share', 'Reported vote share of the leading candidate by constituency', 'Live (3-hour refresh)', '#3fb950', '%', 'https://results.eci.gov.in/', 'Reported vote share of the current leading candidate in each published constituency. This live lead is provisional until Form 20 is published.'],
  ['india_live_party_seats', 'Indian by-election party leads', 'Currently leading constituencies by party in the ECI snapshot', 'Live (3-hour refresh)', '#a371f7', ' constituencies', 'https://results.eci.gov.in/', 'Count of currently published constituencies in which each party candidate has the highest reported vote total. This is a provisional snapshot, not a historical or all-election seat tally.'],
  ['us_presidential_electoral_votes', 'U.S. Presidential Electoral College', 'Winner and main opponent electoral votes, 2000–2024', 'Every 4 years', '#58a6ff', ' electoral votes', 'https://www.archives.gov/electoral-college', 'Official Electoral College results for the U.S. presidential elections from 2000 through 2024, sourced from the National Archives. The series compares electoral votes, not popular votes. U.S. House candidate vote totals are not included: those returns are published by state and a consistent official national feed was not verified.'],
  ['crude_birth_rate', 'Crude Birth Rate', 'Annual births per 1,000 people in India', 'Annual', '#f778ba', ' births per 1,000 people', 'https://data.worldbank.org/indicator/SP.DYN.CBRT.IN?locations=IN', 'Annual national births per 1,000 people, from World Bank indicator SP.DYN.CBRT.IN. This is a national rate, not a state-level birth count.'],
  ['crude_death_rate', 'Crude Death Rate', 'Annual deaths per 1,000 people in India', 'Annual', '#79c0ff', ' deaths per 1,000 people', 'https://data.worldbank.org/indicator/SP.DYN.CDRT.IN?locations=IN', 'Annual national deaths per 1,000 people, from World Bank indicator SP.DYN.CDRT.IN. This is a national rate, not a state-level death count.'],
  ['clean_fuel_access', 'Access to Clean Fuels for Cooking', 'Population with access to clean fuels and technologies for cooking', 'Annual', '#e3b341', '%', 'https://data.worldbank.org/indicator/EG.CFT.ACCS.ZS?locations=IN', 'National share with access to clean cooking fuels and technologies, from World Bank indicator EG.CFT.ACCS.ZS. This is a clean-cooking access measure and must not be interpreted as household LPG connections or a state-wise gas network count.'],
];

const eraData = {
  all: {
    id: "all",
    name: "India's Multi-Era Long View Atlas",
    years: "3300 BCE — 2026 CE",
    desc: "A long-run journey through India's civilizational roots, freedom movement, republic building, economic reforms, defence production, and digital powerhouse transformation.",
    image: "assets/parliament.svg",
    attribution: "Original India-inspired vector illustration; see image references"
  },
  ancient: {
    id: "ancient",
    name: "Ancient & Classical India",
    years: "3300 BCE — 1200 CE",
    desc: "Indus Valley civilization, Vedic foundations, Maurya Empire under Ashoka, Gupta Golden Age, and Chola maritime trade.",
    image: "assets/hampi.svg",
    attribution: "Original Hampi-inspired vector illustration; see image references"
  },
  medieval: {
    id: "medieval",
    name: "Medieval & Imperial Era",
    years: "1200 — 1757 CE",
    desc: "Vijayanagara Empire, Mughal architecture, Maratha Confederacy, and historical silk & spice trade networks.",
    image: "assets/hampi.svg",
    attribution: "Original Hampi-inspired vector illustration; see image references"
  },
  freedom: {
    id: "freedom",
    name: "Colonial & Freedom Movement",
    years: "1757 — 1947 CE",
    desc: "Colonial trade monopoly, 1857 Uprising, Swadeshi Movement, Mahatma Gandhi's Salt Satyagraha, and 1947 Independence.",
    image: "assets/parliament.svg",
    attribution: "Original civic-building vector illustration; see image references"
  },
  republic: {
    id: "republic",
    name: "Early Republic & Industrialization",
    years: "1947 — 1990 CE",
    desc: "Nation building post-independence, Five-Year Plans, Green & White Revolutions, Bhakra Nangal Dam, and ISRO foundations.",
    image: "assets/parliament.svg",
    attribution: "Original civic-building vector illustration; see image references"
  },
  liberalization: {
    id: "liberalization",
    name: "Economic Reform & IT Revolution",
    years: "1991 — 2013 CE",
    desc: "1991 Economic Liberalization, BSE & NSE stock market growth, IT sector expansion, highway infrastructure, and global trade.",
    image: "assets/parliament.svg",
    attribution: "Original civic-building vector illustration; see image references"
  },
  modern: {
    id: "modern",
    name: "Modern Digital & Strategic Era",
    years: "2014 — Present",
    desc: "Digital India, UPI real-time payments, indigenous defence production (Make in India), defence exports, Chandrayaan space missions, and global powerhouse rise.",
    image: "assets/rail-station.svg",
    attribution: "Original infrastructure vector illustration; see image references"
  }
};

const eraFor = key => {
  if (['defence_expenditure', 'defence_exports', 'defence_production', 'defence_stockpile', 'defence_production_exports', 'defence_budget_share', 'defence_rd_budget', 'defence_capital_acquisition', 'sipri_arms_imports', 'upi', 'upi_transaction_value', 'credit_card_spends', 'debit_card_spends', 'credit_card_in_circulation', 'debit_card_in_circulation', 'rbi_digital_payments_index', 'national_highways_built', 'railway_electrification', 'renewable_energy_capacity', 'civil_aviation_passengers', 'telecom_broadband_subscribers', 'auto_production_volume', 'crude_steel_production', 'electronics_manufacturing', 'pharma_exports_trajectory', 'textiles_apparel_exports', 'iron_ore_production', 'bauxite_aluminium_output', 'copper_production', 'manganese_chromite_production', 'coal_production', 'lignite_production', 'crude_petroleum_domestic', 'natural_gas_production', 'limestone_production', 'rare_earths_critical_minerals', 'rock_phosphate_gypsum', 'mineral_metal_exports', 'iron_ore_exports', 'refined_petroleum_exports', 'critical_mineral_import_dependency', 'state_gsdp_comparison', 'state_per_capita_income', 'state_own_tax_revenue', 'state_gst_collections', 'state_operating_factories', 'state_manufacturing_gsdp_share', 'state_pmay_homes', 'state_jjm_water_coverage', 'state_mudra_loans', 'state_pmjdy_bank_accounts', 'state_pmjay_health_cards', 'state_pmsvanidhi_street_vendors', 'state_renewable_energy_capacity', 'state_national_highway_length', 'state_literacy_rates', 'state_infant_mortality_rate', 'state_life_expectancy', 'state_ev_adoption_charging', 'state_export_preparedness_index', 'state_ease_of_doing_business', 'ndps_drug_cases', 'child_protection_pocso', 'road_accidents_fatalities', 'police_per_population', 'internet_users', 'cyber_crime', 'sectoral_market_indices'].includes(key)) return 'modern';
  if (['market_indices', 'global_equity_indices', 'gdp_world_comparison', 'fdi', 'trade', 'eway_bills', 'gst', 'crimes_against_women', 'economic_offences'].includes(key)) return 'liberalization';
  if (['gdp_per_capita', 'population', 'electricity_access', 'iip', 'power_consumption', 'rail_freight', 'port_cargo', 'broad_money', 'bank_credit', 'tax_revenue', 'ncrb_ipc_crime_rate'].includes(key)) return 'republic';
  if (['rupee', 'cpi', 'wpi', 'homicide_rate', 'terror_attacks', 'terror_fatalities'].includes(key)) return 'freedom';
  if (['lwe_incidents', 'lwe_civilian_casualties', 'lwe_security_force_casualties', 'lwe_perpetrator_casualties', 'ncrb_crime', 'life_expectancy'].includes(key)) return 'republic';
  if (['pew_india_global_power', 'pew_india_leadership', 'pew_india_reports', 'pew_india_us_relations', 'pew_india_economy_confidence', 'pew_india_technology', 'pew_india_religion_tolerance', 'pew_india_demographics_family'].includes(key)) return 'modern';
  return 'republic';
};

const categoryFor = key => ['pew_india_global_power', 'pew_india_leadership', 'pew_india_reports', 'pew_india_us_relations', 'pew_india_economy_confidence', 'pew_india_technology', 'pew_india_religion_tolerance', 'pew_india_demographics_family', 'pew_india_gender_roles', 'pew_india_media_news', 'pew_india_climate_environment'].includes(key) ? 'Pew Research' : ['defence_expenditure', 'defence_exports', 'defence_production', 'defence_stockpile', 'defence_production_exports', 'defence_budget_share', 'defence_rd_budget', 'defence_capital_acquisition', 'sipri_arms_imports'].includes(key) ? 'Defence & Strategic' : ['iron_ore_production', 'bauxite_aluminium_output', 'copper_production', 'manganese_chromite_production', 'coal_production', 'lignite_production', 'crude_petroleum_domestic', 'natural_gas_production', 'limestone_production', 'rare_earths_critical_minerals', 'rock_phosphate_gypsum', 'mineral_metal_exports', 'iron_ore_exports', 'refined_petroleum_exports', 'critical_mineral_import_dependency'].includes(key) ? 'Mining & Natural Resources' : ['upi', 'upi_transaction_value', 'credit_card_spends', 'debit_card_spends', 'credit_card_in_circulation', 'debit_card_in_circulation', 'rbi_digital_payments_index'].includes(key) ? 'Payments & Digital Banking' : ['auto_production_volume', 'crude_steel_production', 'electronics_manufacturing', 'pharma_exports_trajectory', 'textiles_apparel_exports', 'iip', 'power_consumption', 'eway_bills', 'rail_freight', 'port_cargo', 'core_industries', 'national_highways_built', 'railway_electrification', 'renewable_energy_capacity', 'civil_aviation_passengers', 'telecom_broadband_subscribers', 'crude_oil', 'fuel_consumption', 'wpi'].includes(key) ? 'Industry Trends & Performance' : ['state_gsdp_comparison', 'state_per_capita_income', 'state_own_tax_revenue', 'state_gst_collections', 'state_operating_factories', 'state_manufacturing_gsdp_share', 'state_pmay_homes', 'state_jjm_water_coverage', 'state_mudra_loans', 'state_pmjdy_bank_accounts', 'state_pmjay_health_cards', 'state_pmsvanidhi_street_vendors', 'state_renewable_energy_capacity', 'state_national_highway_length', 'state_literacy_rates', 'state_infant_mortality_rate', 'state_life_expectancy', 'state_ev_adoption_charging', 'state_export_preparedness_index', 'state_ease_of_doing_business'].includes(key) ? 'State Performance & Regional Health' : ['homicide_rate', 'lwe_incidents', 'northeast_insurgency_fatalities', 'northeast_insurgency_incidents', 'kashmir_insurgency_fatalities', 'kashmir_terror_incidents', 'khalistan_insurgency_historical', 'terror_attacks', 'terror_fatalities', 'ncrb_crime', 'ncrb_ipc_crime_rate', 'crimes_against_women', 'cyber_crime', 'economic_offences', 'ndps_drug_cases', 'child_protection_pocso', 'road_accidents_fatalities', 'police_per_population', 'violent_incidents', 'lwe_civilian_casualties', 'lwe_security_force_casualties', 'lwe_perpetrator_casualties'].includes(key) ? 'Crime & Security' : ['population', 'unemployment', 'electricity_access', 'internet_users', 'life_expectancy', 'social_category_literacy', 'religious_demographics', 'pm_mudra_social_breakdown'].includes(key) ? 'Social' : 'Economic';

const subgroupFor = key => ['union_budget_expenditure', 'budget_yoy_growth', 'capital_expenditure_capex', 'gross_tax_yoy_growth'].includes(key) ? 'Fiscal & Union Budget' : ['per_capita_nni_inr', 'per_capita_income_ppp'].includes(key) ? 'Per Capita Income & Wealth' : ['social_category_literacy', 'religious_demographics', 'pm_mudra_social_breakdown', 'population', 'unemployment'].includes(key) ? 'Demographics' : ['electricity_access', 'internet_users', 'life_expectancy'].includes(key) ? 'Welfare' : ['defence_exports', 'defence_production', 'defence_production_exports'].includes(key) ? 'Defence Exports & Production' : ['defence_expenditure', 'defence_budget_share', 'defence_rd_budget', 'defence_capital_acquisition'].includes(key) ? 'Defence Budget & Modernization' : ['defence_stockpile', 'sipri_arms_imports'].includes(key) ? 'Strategic Stockpiles & Capabilities' : ['iron_ore_production', 'bauxite_aluminium_output', 'copper_production', 'manganese_chromite_production'].includes(key) ? 'Metallic Minerals & Ores' : ['coal_production', 'lignite_production', 'crude_petroleum_domestic', 'natural_gas_production'].includes(key) ? 'Energy Minerals & Fuel' : ['limestone_production', 'rare_earths_critical_minerals', 'rock_phosphate_gypsum'].includes(key) ? 'Non-Metallic & Industrial Minerals' : ['mineral_metal_exports', 'iron_ore_exports', 'refined_petroleum_exports', 'critical_mineral_import_dependency'].includes(key) ? 'Mineral Exports & Trade' : ['upi', 'upi_transaction_value'].includes(key) ? 'UPI & Digital Payments' : ['credit_card_spends', 'debit_card_spends', 'credit_card_in_circulation', 'debit_card_in_circulation'].includes(key) ? 'Card Spends & Ecosystem' : ['rbi_digital_payments_index'].includes(key) ? 'Digital Financial Index' : ['auto_production_volume', 'crude_steel_production', 'electronics_manufacturing', 'pharma_exports_trajectory', 'textiles_apparel_exports', 'iip', 'core_industries'].includes(key) ? 'Manufacturing & Industrial Growth' : ['power_consumption', 'eway_bills', 'rail_freight', 'port_cargo', 'national_highways_built', 'railway_electrification', 'renewable_energy_capacity', 'civil_aviation_passengers', 'telecom_broadband_subscribers'].includes(key) ? 'Infrastructure Development' : ['crude_oil', 'fuel_consumption', 'wpi'].includes(key) ? 'Production & Commodities' : ['state_gsdp_comparison', 'state_per_capita_income', 'state_own_tax_revenue', 'state_gst_collections'].includes(key) ? 'State Financial Health & GSDP' : ['state_operating_factories', 'state_manufacturing_gsdp_share', 'state_export_preparedness_index', 'state_ease_of_doing_business'].includes(key) ? 'State Industrial & Manufacturing Hubs' : ['state_pmay_homes', 'state_jjm_water_coverage', 'state_mudra_loans', 'state_pmjdy_bank_accounts', 'state_pmjay_health_cards', 'state_pmsvanidhi_street_vendors', 'state_renewable_energy_capacity', 'state_national_highway_length', 'state_ev_adoption_charging'].includes(key) ? 'State Welfare & Scheme Coverage' : ['state_literacy_rates', 'state_infant_mortality_rate', 'state_life_expectancy'].includes(key) ? 'State Socio-Demographic Milestones' : ['cpi', 'gst', 'fiscal_deficit', 'gdp_per_capita', 'current_account', 'tax_revenue', 'government_consumption', 'domestic_savings', 'fdi'].includes(key) ? 'Macroeconomics' : ['broad_money', 'bank_credit'].includes(key) ? 'Monetary Policy' : ['trade', 'forex', 'rupee', 'merchandise_exports', 'merchandise_imports'].includes(key) ? 'Trade & External' : ['market_indices', 'sensex', 'nifty', 'nifty_vix', 'global_equity_indices', 'gdp_world_comparison', 'sectoral_market_indices', 'global_inflation_comparison'].includes(key) ? 'Markets' : ['indian_matrix'].includes(key) ? 'Media & Publications' : ['pew_india_global_power', 'pew_india_leadership', 'pew_india_us_relations', 'pew_india_economy_confidence', 'pew_india_technology', 'pew_india_reports', 'pew_india_religion_tolerance', 'pew_india_demographics_family', 'pew_india_gender_roles', 'pew_india_media_news', 'pew_india_climate_environment'].includes(key) ? 'Public opinion' : ['lwe_incidents', 'lwe_civilian_casualties', 'lwe_security_force_casualties', 'lwe_perpetrator_casualties'].includes(key) ? 'Maoism / LWE' : ['kashmir_insurgency_fatalities', 'kashmir_terror_incidents'].includes(key) ? 'Jammu & Kashmir Insurgency' : ['northeast_insurgency_fatalities', 'northeast_insurgency_incidents'].includes(key) ? 'North East Insurgency' : ['khalistan_insurgency_historical'].includes(key) ? 'Punjab Militancy & Security' : ['homicide_rate', 'ncrb_crime', 'ncrb_ipc_crime_rate', 'crimes_against_women', 'cyber_crime', 'economic_offences', 'ndps_drug_cases', 'child_protection_pocso', 'road_accidents_fatalities', 'police_per_population', 'violent_incidents'].includes(key) ? 'Violence & Crime' : ['terror_attacks', 'terror_fatalities'].includes(key) ? 'Terrorism' : 'Macroeconomics';

const renderChartSourceIndex = () => {
  const list = document.querySelector('#chart-source-index-list');
  const search = document.querySelector('#chart-source-index-search');
  const count = document.querySelector('#chart-source-index-count');
  if (!list) return;
  definitions.forEach(definition => {
    const [key, title, subtitle, frequency, , , source] = definition;
    const urls = Array.isArray(definition[8]) ? definition[8] : [source];
    const item = document.createElement('li');
    item.className = 'chart-source-index-item';
    const heading = document.createElement('strong');
    heading.textContent = title;
    const meta = document.createElement('span');
    const category = extraChartPlacement[key]?.category || (['terror_attacks_per_million', 'terror_fatalities_per_million', 'terror_fatalities_per_attack'].includes(key) ? 'Crime & Security' : key === 'state_power_per_capita' ? 'State Performance & Regional Health' : categoryFor(key));
    const subgroup = extraChartPlacement[key]?.subgroup || (['terror_attacks_per_million', 'terror_fatalities_per_million', 'terror_fatalities_per_attack'].includes(key) ? 'Terrorism' : key === 'state_power_per_capita' ? 'State Infrastructure & Services' : subgroupFor(key));
    meta.textContent = `${category} / ${subgroup} / ${frequency}`;
    item.append(heading, meta);
    const chartLink = document.createElement('a');
    chartLink.className = 'source-chart-link';
    chartLink.href = `#indicator-${key}`;
    chartLink.textContent = 'View graph';
    chartLink.addEventListener('click', event => {
      event.preventDefault();
      const groupSelect = document.querySelector('#group-filter');
      const subgroupSelect = document.querySelector('#subgroup-filter');
      if (groupSelect && subgroupSelect) {
        groupSelect.value = category;
        groupSelect.dispatchEvent(new Event('change', { bubbles: true }));
        subgroupSelect.value = subgroup;
        subgroupSelect.dispatchEvent(new Event('change', { bubbles: true }));
      }
      window.location.hash = `indicator-${key}`;
      document.getElementById(`indicator-${key}`)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
    item.append(chartLink);
    for (const url of new Set(urls.filter(Boolean))) {
      const link = document.createElement('a');
      link.href = url;
      link.target = '_blank';
      link.rel = 'noreferrer';
      link.textContent = `${new URL(url).hostname.replace(/^www\./, '')} · Open source ↗`;
      link.title = url;
      item.append(link);
    }
    item.dataset.search = `${title} ${subtitle} ${frequency} ${definition[7] || ''} ${category} ${subgroup} ${urls.join(' ')}`.toLowerCase();
    list.append(item);
  });
  if (count) count.textContent = `${definitions.length} graphs`;
  search?.addEventListener('input', () => {
    const query = search.value.trim().toLowerCase();
    for (const item of list.children) item.hidden = !item.dataset.search.includes(query);
  });
};

const extraChartPlacement = window.INDIA_EXTRA_CHART_PLACEMENT || {};
definitions.push(...(window.INDIA_EXTRA_CHART_DEFINITIONS || []));
renderChartSourceIndex();

const formatMagnitude = (value, suffix = '') => {
  const unitSuffix = suffix.trim();
  const locale = /\bUSD\b|US dollars?|international \$/i.test(unitSuffix) ? 'en-US' : 'en-IN';
  const declaredUnit = /thousand|million|lakh|gwh|mt|tonnes|usd\/barrel|usd bn|inr bn|inr cr|sipri tiv|incidents|attacks|deaths|cases|females/i.test(unitSuffix);
  const formattedValue = Number(value).toLocaleString(locale, { maximumFractionDigits: 2 });
  if (declaredUnit) return `${formattedValue}${unitSuffix ? ` ${unitSuffix}` : ''}`;
  const absolute = Math.abs(value);
  const units = locale === 'en-US'
    ? [[1e12, 'trillion'], [1e9, 'billion'], [1e6, 'million'], [1e3, 'thousand']]
    : [[1e12, 'lakh crore'], [1e7, 'crore'], [1e5, 'lakh'], [1e3, 'thousand']];
  const unit = units.find(([threshold]) => absolute >= threshold);
  if (!unit) return `${formattedValue}${unitSuffix ? ` ${unitSuffix}` : ''}`;
  const amount = value / unit[0];
  return `${amount.toLocaleString(locale, { maximumFractionDigits: 2 })} ${unit[1]}${unitSuffix ? ` ${unitSuffix}` : ''}`;
};

const CHART_THEME = {
  ink: '#f5f5f7', muted: '#a1a1a6', grid: 'rgba(255, 255, 255, 0.08)', legend: '#d2d2d7',
  tooltipBg: 'rgba(28, 28, 30, 0.96)', tooltipTitle: '#f5f5f7', tooltipBody: '#d2d2d7',
  tooltipBorder: 'rgba(255, 255, 255, 0.14)', sliceBorder: '#1c1c1e',
  font: '-apple-system, BlinkMacSystemFont, "SF Pro Text", "Helvetica Neue", Helvetica, Arial, sans-serif'
};

const chartOptions = (suffix, hasMultipleDatasets = false, horizontalBars = false, chartType = 'line') => {
  const isRadialChart = chartType === 'pie' || chartType === 'doughnut';
  const pluginsConfig = {
    legend: {
      display: isRadialChart,
      position: 'bottom',
      labels: isRadialChart ? {
        generateLabels: chart => {
          const generator = Chart.overrides?.[chart.config.type]?.plugins?.legend?.labels?.generateLabels;
          const items = generator ? generator(chart) : chart.data.labels.map((text, index) => ({ text, index }));
          const values = chart.data.datasets[0]?.data || [];
          const total = values.reduce((sum, value, index) => sum + (chart.getDataVisibility(index) ? Math.max(0, Number(value) || 0) : 0), 0);
          return items.map(item => {
            const value = Number(values[item.index]) || 0;
            return {
              ...item,
              text: `${item.text} (${total ? (value / total * 100).toFixed(1) : '0.0'}%)`
            };
          });
        }
      } : undefined
    },
    tooltip: {
      backgroundColor: CHART_THEME.tooltipBg,
      titleColor: CHART_THEME.tooltipTitle,
      bodyColor: CHART_THEME.tooltipBody,
      borderColor: CHART_THEME.tooltipBorder,
      borderWidth: 1,
      padding: 12,
      boxPadding: 6,
      usePointStyle: true,
      callbacks: {
        label: context => {
          const value = isRadialChart ? context.raw : horizontalBars ? context.parsed.x : context.parsed.y;
          const label = isRadialChart ? context.label : context.dataset.label || 'Value';
          if (isRadialChart) {
            const chart = context.chart;
            const dataset = context.dataset.data || [];
            const total = dataset.reduce((sum, amount, index) => sum + (chart.getDataVisibility(index) ? Math.max(0, Number(amount) || 0) : 0), 0);
            const share = total ? ` (${(Number(value) / total * 100).toFixed(1)}%)` : '';
            return ` ${label}: ${formatMagnitude(value, suffix)}${share}`;
          }
          return ` ${label}: ${formatMagnitude(value, suffix)}`;
        }
      }
    }
  };
  if (!isRadialChart && typeof Chart !== 'undefined' && Chart.registry && Chart.registry.plugins && Chart.registry.plugins.get('zoom')) {
    pluginsConfig.zoom = {
      pan: { enabled: true, mode: 'x' },
      zoom: { wheel: { enabled: true }, pinch: { enabled: true }, mode: 'x' }
    };
  }
  const options = {
    responsive: true,
    maintainAspectRatio: false,
    indexAxis: horizontalBars ? 'y' : 'x',
    animation: { duration: 600, easing: 'easeOutQuart' },
    interaction: { mode: 'index', intersect: isRadialChart },
    plugins: pluginsConfig,
    onClick: isRadialChart ? (event, elements, chart) => {
      if (!elements.length) return;
      chart.toggleDataVisibility(elements[0].index);
      chart.update();
    } : undefined
  };
  if (!isRadialChart) {
    const axisTicks = { color: CHART_THEME.muted, font: { size: 11, family: CHART_THEME.font } };
    const axisGrid = { color: CHART_THEME.grid, drawBorder: false };
    options.scales = horizontalBars ? {
      x: {
        grid: axisGrid,
        ticks: { ...axisTicks, callback: value => formatMagnitude(value, suffix) }
      },
      y: {
        grid: { display: false },
        ticks: { ...axisTicks, autoSkip: false, padding: 8 }
      }
    } : {
      x: {
        grid: axisGrid,
        ticks: { ...axisTicks }
      },
      y: {
        grid: axisGrid,
        ticks: { ...axisTicks, maxTicksLimit: 6, padding: 10, callback: value => formatMagnitude(value, suffix) }
      }
    };
  }
  if (isRadialChart) {
    options.cutout = chartType === 'doughnut' ? '58%' : 0;
    options.radius = '92%';
    options.layout = { padding: { top: 30 } };
    options.animation = { animateRotate: true, animateScale: true, duration: 800, easing: 'easeOutQuart' };
    options.onHover = (event, elements) => { if (event.native?.target) event.native.target.style.cursor = elements.length ? 'pointer' : 'default'; };
    pluginsConfig.legend.labels.color = CHART_THEME.legend;
    pluginsConfig.legend.labels.usePointStyle = true;
    pluginsConfig.legend.labels.boxWidth = 10;
    pluginsConfig.centerReadout = { suffix };
  }
  return options;
};
if (typeof Chart !== 'undefined' && !Chart.registry?.plugins?.get?.('centerReadout')) {
  Chart.register({
    id: 'centerReadout',
    afterDraw(chart, _args, pluginOptions) {
      if (chart.config.type !== 'doughnut' || !pluginOptions || pluginOptions.suffix === undefined) return;
      const meta = chart.getDatasetMeta(0);
      const arc = meta?.data?.[0];
      if (!arc) return;
      const values = chart.data.datasets[0]?.data || [];
      const total = values.reduce((sum, value, index) => sum + (chart.getDataVisibility(index) ? Math.max(0, Number(value) || 0) : 0), 0);
      const active = chart.getActiveElements()[0];
      const value = active ? Number(values[active.index]) || 0 : total;
      const caption = active ? `${String(chart.data.labels[active.index]).slice(0, 22)} · ${total ? (value / total * 100).toFixed(1) : '0.0'}%` : 'Total shown';
      const { ctx } = chart;
      const fontSize = Math.max(11, Math.min(20, arc.innerRadius / 4));
      ctx.save();
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillStyle = CHART_THEME.ink;
      ctx.font = `700 ${fontSize}px ${CHART_THEME.font}`;
      ctx.fillText(formatMagnitude(value, pluginOptions.suffix), arc.x, arc.y - fontSize * 0.45);
      ctx.fillStyle = CHART_THEME.muted;
      ctx.font = `500 ${Math.max(9, fontSize * 0.55)}px ${CHART_THEME.font}`;
      ctx.fillText(caption, arc.x, arc.y + fontSize * 0.65);
      ctx.restore();
    }
  });
}

async function safeFetchJson(filename, defaultVal = {}) {
  const paths = [
    `data/${filename}?ts=${Date.now()}`,
    `data/${filename}`,
    `./data/${filename}`,
    `docs/data/${filename}`
  ];
  for (const path of paths) {
    try {
      const res = await fetch(path);
      if (res.ok) {
        const json = await res.json();
        if (json) return json;
      }
    } catch (e) {
      // try next path
    }
  }
  return defaultVal;
}

async function main() {
  let dataPayload = window.INDIA_DASHBOARD_DATA;
  let economicSurvey = { series: {} };
  let indianMatrix = { cadence: { labels: [], values: [] }, articles: [] };
  let pewReports = { cadence: { labels: [], values: [] }, reports: [] };
  let ncrbeAnalyses = { series: {} };
  let pewSnapshots = { series: {} };

  if (!dataPayload || !dataPayload.series || Object.keys(dataPayload.series).length === 0) {
    [dataPayload, economicSurvey, indianMatrix, pewReports, ncrbeAnalyses, pewSnapshots] = await Promise.all([
      safeFetchJson('chart-latest.json', { series: {} }),
      safeFetchJson('economic-survey-monthly.json', { series: {} }),
      safeFetchJson('indian-matrix-latest.json', { cadence: { labels: [], values: [] }, articles: [] }),
      safeFetchJson('pew-india-reports.json', { cadence: { labels: [], values: [] }, reports: [] }),
      safeFetchJson('ncrb-and-analyses.json', { series: {} }),
      safeFetchJson('pew-snapshots.json', { series: {} }),
    ]);
  }

  const [electionResults, usCampaignFinance, electionIndices] = await Promise.all([
    safeFetchJson('election-results.json', { series: {} }),
    safeFetchJson('us-campaign-finance.json', { series: {} }),
    safeFetchJson('election-indices.json', { series: {} }),
  ]);
  const liveConstituencies = electionResults?.india_constituencies || [];
  liveConstituencies.forEach((record, index) => {
    const key = `india_live_constituency_vote_composition_${index + 1}`;
    definitions.push([
      key,
      `${record.constituency} candidate vote composition`,
      `Reported candidate votes in ${record.constituency}, ${record.state_or_ut}`,
      'Live ECI snapshot',
      '#ff9933',
      ' votes',
      record.source || 'https://results.eci.gov.in/',
      'Reported candidate votes for this currently published constituency. The five highest-vote candidates are shown individually; remaining candidates, including NOTA where present, are combined as Other candidates. ECI results are provisional until Form 20.'
    ]);
    extraChartPlacement[key] = { category: 'Elections', subgroup: 'Indian Elections' };
  });
  const data = dataPayload || { series: {} };
  data.series = { ...(data.series || {}), ...(economicSurvey?.series || {}), ...(ncrbeAnalyses?.series || {}), ...(pewSnapshots?.series || {}), ...(electionResults?.series || {}), ...(usCampaignFinance?.series || {}), ...(electionIndices?.series || {}) };
  // Generated series can describe themselves via `meta`, so new indices need no hand-written definition.
  const definedKeys = new Set(definitions.map(definition => definition[0]));
  Object.entries(data.series).forEach(([key, series]) => {
    const meta = series?.meta;
    if (!meta || definedKeys.has(key)) return;
    definitions.push([key, meta.title, meta.subtitle || '', meta.frequency || 'Periodic', meta.color || '#58a6ff', meta.suffix || '', series.source || '', series.note || meta.subtitle || '']);
    definedKeys.add(key);
    if (meta.category) extraChartPlacement[key] = { category: meta.category, subgroup: meta.subgroup || meta.category };
  });
  const heroChartCount = document.querySelector('#hero-chart-count');
  if (heroChartCount) heroChartCount.textContent = String(definitions.length);
  const matrixCadence = (data.series.indian_matrix && data.series.indian_matrix.values && data.series.indian_matrix.values.length) ? data.series.indian_matrix : (indianMatrix?.cadence || { labels: [], values: [] });
  data.series.indian_matrix = { labels: matrixCadence.labels || [], values: matrixCadence.values || [], source: 'Indian Matrix public RSS feed' };
  const pewCadence = (data.series.pew_india_reports && data.series.pew_india_reports.values && data.series.pew_india_reports.values.length) ? data.series.pew_india_reports : (pewReports?.cadence || { labels: [], values: [] });
  data.series.pew_india_reports = { labels: pewCadence.labels || [], values: pewCadence.values || [], source: 'Pew Research Center India public report catalog' };
  const marketKeys = ['sensex', 'nifty', 'nifty_vix'];
  const marketLabels = [...new Set(marketKeys.flatMap(key => data.series[key]?.labels || []))].sort();
  const marketDatasets = marketKeys.map(key => {
    const series = data.series[key] || {};
    const values = new Map((series.labels || []).map((label, index) => [label, (series.values || [])[index]]));
    const first = [...values.values()].find(value => value !== null && value !== undefined);
    return { label: key === 'sensex' ? 'Sensex' : key === 'nifty' ? 'Nifty' : 'Nifty VIX', data: marketLabels.map(label => values.has(label) ? values.get(label) / first * 100 : null), borderColor: key === 'sensex' ? '#58a6ff' : key === 'nifty' ? '#3fb950' : '#f2cc60', backgroundColor: 'transparent', borderWidth: 2.5, pointRadius: 2, tension: 0.25, spanGaps: true };
  });
  data.series.market_indices = { labels: marketLabels, datasets: marketDatasets };
  const genEl = document.querySelector('#generated');
  if (genEl) genEl.textContent = data.generated_at_utc ? new Date(data.generated_at_utc).toLocaleString() : new Date().toLocaleString();
  const pewReportItems = (dataPayload && dataPayload.pew_reports) || pewReports?.reports || [];
  const renderPewReports = () => {
    const list = document.querySelector('#pew-report-list');
    const searchInput = document.querySelector('#pew-report-search');
    const count = document.querySelector('#pew-report-count');
    if (!list || !searchInput || !count) return;
    const query = searchInput.value.trim().toLowerCase();
    const terms = query.split(/\s+/).filter(Boolean);
    const reports = pewReportItems
      .filter(report => {
        const searchable = `${report.title || ''} ${report.date || ''} ${report.link || ''}`.toLowerCase();
        return /india/i.test(searchable) && terms.every(term => searchable.includes(term));
      })
      .sort((left, right) => String(right.date || '').localeCompare(String(left.date || '')));
    list.replaceChildren();
    reports.slice(0, 18).forEach(report => {
      const item = document.createElement('a');
      item.className = 'pew-report-item';
      item.href = report.link;
      item.target = '_blank';
      item.rel = 'noreferrer';
      const title = document.createElement('strong');
      title.textContent = report.title || 'Pew Research report';
      const date = document.createElement('span');
      date.textContent = `${report.date || 'Date not listed'} · Open original report ↗`;
      item.append(title, date);
      list.append(item);
    });
    count.textContent = `${reports.length.toLocaleString()} India-related reports indexed · showing ${Math.min(reports.length, 18)}${query ? ' matches' : ' recent reports'}`;
  };
  document.querySelector('#pew-report-search')?.addEventListener('input', renderPewReports);
  renderPewReports();
  const categoryBgMap = {
    "Economic": "assets/economy.svg",
    "Industry Trends & Performance": "assets/industry.svg",
    "Mining & Natural Resources": "assets/mining.svg",
    "Payments & Digital Banking": "assets/payments.svg",
    "State Performance & Regional Health": "assets/states.svg",
    "Public Health & Epidemiology": "assets/health.svg",
    "Social": "assets/social.svg",
    "Defence & Strategic": "assets/defence.svg",
    "Crime & Security": "assets/security.svg",
    "Pew Research": "assets/opinion.svg",
    "Elections": "assets/elections.svg",
    "U.S. Elections": "assets/us-elections.svg",
    "Tourism & Heritage": "assets/tourism.svg"
  };

  const setEraBackground = (imgUrl) => {
    const bgLayer = document.querySelector('#era-bg-layer');
    if (!bgLayer || !imgUrl) return;
    const next = `url("${imgUrl}")`;
    if (bgLayer.style.backgroundImage === next) return;
    if (!bgLayer.style.backgroundImage) {
      bgLayer.style.backgroundImage = next;
      bgLayer.style.opacity = '0.55';
      return;
    }
    bgLayer.classList.add('is-swapping');
    clearTimeout(bgLayer.swapTimer);
    bgLayer.swapTimer = setTimeout(() => {
      bgLayer.style.backgroundImage = next;
      bgLayer.classList.remove('is-swapping');
    }, 380);
  };
  setEraBackground(categoryBgMap.Economic);

  const grid = document.querySelector('#charts');
  const charts = [];
  const savedChartKeys = new Set();
  const focusOverlay = document.querySelector('#chart-focus-overlay');
  const focusContent = document.querySelector('#chart-focus-content');
  const focusClose = document.querySelector('#chart-focus-close');
  let expandedChart = null;
  let expandedPlaceholder = null;
  let expandOpener = null;
  const closeExpandedChart = () => {
    if (!expandedChart || !expandedPlaceholder) return;
    const closingChart = expandedChart;
    expandedPlaceholder.replaceWith(closingChart);
    expandedChart = null;
    expandedPlaceholder = null;
    if (focusOverlay) focusOverlay.hidden = true;
    const chartEntry = charts.find(item => item.card === closingChart);
    chartEntry?.chart?.resize();
    expandOpener?.focus();
    expandOpener = null;
  };
  focusClose?.addEventListener('click', closeExpandedChart);
  focusOverlay?.addEventListener('click', event => {
    if (event.target === focusOverlay) closeExpandedChart();
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape') closeExpandedChart();
  });
  let lastCategory = '';
  const categoryOrder = { Economic: 0, 'Industry Trends & Performance': 1, 'Mining & Natural Resources': 2, 'Payments & Digital Banking': 3, 'State Performance & Regional Health': 4, 'Public Health & Epidemiology': 5, Social: 6, 'Defence & Strategic': 7, 'Crime & Security': 8, 'Pew Research': 9, Elections: 10, 'U.S. Elections': 11, 'Tourism & Heritage': 12 };
  const dashboardCategoryFor = key => extraChartPlacement[key]?.category || (['gdp_growth', 'merchandise_trade_balance', 'auto_production_volume', 'auto_domestic_sales', 'private_consumption_pc', 'crude_oil', 'fuel_consumption', 'iip', 'core_industries'].includes(key) ? 'Economic' : ['state_gsdp_comparison', 'state_per_capita_income', 'state_power_per_capita'].includes(key) ? 'State Performance & Regional Health' : ['terror_attacks_per_million', 'terror_fatalities_per_million', 'terror_fatalities_per_attack'].includes(key) ? 'Crime & Security' : categoryFor(key));
  const dashboardSubgroupFor = key => extraChartPlacement[key]?.subgroup || (['merchandise_trade_balance', 'bilateral_trade_balance'].includes(key) ? 'Trade & External' : ['auto_domestic_sales', 'iip', 'core_industries'].includes(key) ? 'Manufacturing & Industrial Growth' : ['private_consumption_pc'].includes(key) ? 'Per Capita Income & Wealth' : ['crude_oil', 'fuel_consumption'].includes(key) ? 'Production & Commodities' : key === 'state_power_per_capita' ? 'State Infrastructure & Services' : ['terror_attacks_per_million', 'terror_fatalities_per_million', 'terror_fatalities_per_attack'].includes(key) ? 'Terrorism' : subgroupFor(key));
  const orderedDefinitions = [...definitions].sort((left, right) => (categoryOrder[dashboardCategoryFor(left[0])] ?? 99) - (categoryOrder[dashboardCategoryFor(right[0])] ?? 99));
  // Building 900+ Chart.js instances up front froze the page for minutes; each chart is now created
  // only when its card comes near the viewport (hidden, filtered-out cards never build).
  const lazyCharts = new WeakMap();
  const chartObserver = typeof IntersectionObserver === 'function' ? new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      chartObserver.unobserve(entry.target);
      lazyCharts.get(entry.target)?.();
    });
  }, { rootMargin: '600px 0px' }) : null;
  orderedDefinitions.forEach(([key, title, subtitle, frequency, color, suffix, source, details], index) => {
    const category = dashboardCategoryFor(key);
    if (grid && category !== lastCategory) {
      const heading = document.createElement('h2');
      heading.className = 'category-heading';
      heading.dataset.category = category;
      heading.textContent = category;
      grid.append(heading);
      lastCategory = category;
    }
    const series = data.series[key] || { error: 'No generated series is available yet' };
    const live = series && !series.error && (series.values?.length || series.datasets?.length);
    // Pages without a chart grid only need group counts, so skip building the card.
    if (!grid) {
      charts.push({ category, subgroup: dashboardSubgroupFor(key), live: Boolean(live) });
      return;
    }
    const card = document.createElement('article');
    card.className = 'chart-card';
    if (series.chartType === 'bar' && series.indexAxis === 'y') card.classList.add('state-rank-chart');
    const paragraphs = details.split('\n\n').map(paragraph => `<p>${paragraph}</p>`).join('');
    const summary = details.split('\n\n')[0] || subtitle;
    card.id = `indicator-${key}`;
    card.dataset.key = key;
    card.dataset.title = `${title} ${subtitle} ${details} ${category} ${dashboardSubgroupFor(key)}`.toLowerCase();
    card.dataset.state = live ? 'live' : 'pending';
    card.dataset.category = category;
    card.dataset.subgroup = dashboardSubgroupFor(key);
    const eraKey = eraFor(key);
    card.dataset.era = eraKey;
    const observationCount = series?.values?.length || series?.labels?.length || 0;
    const context = live ? (series.note || `This ${frequency.toLowerCase()} series contains ${observationCount} available observations. Values are fetched from the cited public source and plotted without smoothing.`) : 'This indicator is retained for source visibility, but no numeric values are shown until its official export can be checked automatically.';
    
    const labels = series?.labels || [];
    const values = series?.values || [];
    const years = [...new Set(labels.map(label => String(label).match(/^(\d{4})/)?.[1]).filter(Boolean))].sort((a, b) => Number(a) - Number(b));

    let latestValStr = 'N/A';
    let growth5YrStr = 'N/A';
    let peakValStr = 'N/A';

    if (live) {
      if (['state', 'category'].includes(series.scope) && values.length > 0) {
        const available = values
          .map((value, index) => ({ value, state: labels[index] }))
          .filter(point => point.value !== null && point.value !== undefined && !isNaN(point.value));
        latestValStr = `${available.length} / ${labels.length}`;
        growth5YrStr = 'Cross-section';
        if (available.length > 0) {
          const highest = available.reduce((best, point) => point.value > best.value ? point : best);
          peakValStr = `${highest.state} (${formatMagnitude(highest.value, suffix)})`;
        }
      } else if (values && values.length > 0) {
        const numValues = values.filter(v => v !== null && v !== undefined && !isNaN(v));
        if (numValues.length > 0) {
          const lastVal = numValues[numValues.length - 1];
          latestValStr = formatMagnitude(lastVal, suffix);

          const maxVal = Math.max(...numValues);
          const maxIdx = values.indexOf(maxVal);
          const maxYear = labels[maxIdx] || '';
          peakValStr = `${formatMagnitude(maxVal, suffix)}${maxYear ? ` (${maxYear})` : ''}`;

          if (numValues.length >= 6) {
            const fiveYrAgo = numValues[numValues.length - 6];
            if (fiveYrAgo && fiveYrAgo !== 0) {
              const pct = ((lastVal - fiveYrAgo) / Math.abs(fiveYrAgo)) * 100;
              growth5YrStr = `${pct >= 0 ? '+' : ''}${pct.toFixed(1)}% (5Y)`;
            }
          }
        }
      } else if (series?.datasets && series.datasets.length > 0) {
        latestValStr = `${series.datasets.length} series`;
        growth5YrStr = 'Multi-series';
        peakValStr = series.chartType === 'bar' ? 'See legend' : 'Indexed comparison';
      }
    }

    const valueCruncherHtml = `
      <div class="value-cruncher-bar">
        <div class="vc-stat"><span class="vc-label">${['state', 'category'].includes(series.scope) ? (series.scopeLabel || 'Categories covered') : 'Latest Value'}</span><strong class="vc-val">${latestValStr}</strong></div>
        <div class="vc-stat"><span class="vc-label">${['state', 'category'].includes(series.scope) ? 'Measure' : '5Y Trend'}</span><strong class="vc-val growth">${growth5YrStr}</strong></div>
        <div class="vc-stat"><span class="vc-label">${['state', 'category'].includes(series.scope) ? (series.highestLabel || 'Highest category') : 'Historical Peak'}</span><strong class="vc-val">${peakValStr}</strong></div>
        <div class="vc-stat"><span class="vc-label">Observations</span><strong class="vc-val">${observationCount} ${frequency.toLowerCase()}</strong></div>
      </div>
    `;

    card.innerHTML = `<header><div><h2>${title}</h2><p class="chart-meta">${subtitle} <span class="frequency">${frequency}</span><span class="subgroup">${dashboardSubgroupFor(key)}</span></p></div><div class="card-actions"><span class="status-pill ${live ? 'live' : ''}">${live ? 'Data available' : 'Source-linked'}</span><button class="save-chart-btn" type="button" aria-pressed="false" aria-label="Save ${title}">☆ Save</button><button class="expand-chart-btn" type="button" aria-label="Expand ${title}">⛶ Expand</button><button class="deep-dive-btn" type="button">Deep dive <span aria-hidden="true">↗</span></button><button class="reset" type="button" aria-label="Reset chart zoom">Reset</button></div></header><p class="chart-story"><span>THE STORY</span>${summary}</p>${live ? valueCruncherHtml : ''}<div class="chart-wrap"><canvas id="chart-${index}" aria-label="${title}: ${subtitle}" role="img"></canvas>${live ? '' : '<p class="empty-state">The cited source is available. Values will appear when a verifiable data export is added.</p>'}</div><details class="insight"><summary>Method, context &amp; limitations</summary><div>${paragraphs}<p><strong>Data context:</strong> ${context}</p></div></details><a class="source-link" href="${source}" target="_blank" rel="noreferrer">Explore the cited source <span aria-hidden="true">↗</span></a>`;
    grid.append(card);
    let chart = null;
    card.querySelector('.expand-chart-btn').addEventListener('click', () => {
      if (!focusOverlay || !focusContent) return;
      lazyCharts.get(card)?.();
      expandedChart = card;
      expandedPlaceholder = document.createElement('div');
      expandedPlaceholder.hidden = true;
      card.after(expandedPlaceholder);
      expandOpener = card.querySelector('.expand-chart-btn');
      focusContent.append(card);
      focusOverlay.hidden = false;
      chart?.resize();
      focusClose?.focus();
    });
    if (years.length > 1) {
      const range = document.createElement('div');
      range.className = 'chart-range-controls';
      range.innerHTML = `<span>PERIOD</span><label>From <select class="chart-range-start" aria-label="Start year for ${title}"></select></label><label>To <select class="chart-range-end" aria-label="End year for ${title}"></select></label>`;
      const startSelect = range.querySelector('.chart-range-start');
      const endSelect = range.querySelector('.chart-range-end');
      for (const year of years) {
        startSelect.add(new Option(year, year));
        endSelect.add(new Option(year, year));
      }
      startSelect.value = years[0];
      endSelect.value = years[years.length - 1];
      card.querySelector('.chart-wrap').before(range);
      card._range = { startSelect, endSelect };
    }
    const saveButton = card.querySelector('.save-chart-btn');
    saveButton.addEventListener('click', event => {
      event.stopPropagation();
      if (savedChartKeys.has(key)) {
        savedChartKeys.delete(key);
        saveButton.textContent = '☆ Save';
        saveButton.setAttribute('aria-pressed', 'false');
      } else {
        savedChartKeys.add(key);
        saveButton.textContent = '★ Saved';
        saveButton.setAttribute('aria-pressed', 'true');
      }
      updateCards();
    });
    const deepDiveBtn = card.querySelector('.deep-dive-btn');
    if (deepDiveBtn) {
      deepDiveBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        openIndicatorModal(key, title, subtitle, frequency, suffix, source, details, series, category, dashboardSubgroupFor(key));
      });
    }
    if (!live) return;
    const chartEntry = { chart: null, card, labels, values: values || series.datasets?.[0]?.data || series.datasets?.[0]?.values || [], datasets: series.datasets?.map(dataset => ({ data: [...(dataset.data || dataset.values)] })) || [], category, subgroup: dashboardSubgroupFor(key), era: eraKey };
    charts.push(chartEntry);
    let chartBuilt = false;
    const ensureChart = () => {
    if (chartBuilt) return;
    chartBuilt = true;
    const hasMultipleDatasets = series.datasets && series.datasets.length > 1;

    const canvas = card.querySelector('canvas');
    const ctx = canvas.getContext('2d');
    const createGradientFill = (colorHex) => {
      const g = ctx.createLinearGradient(0, 0, 0, 320);
      const c = colorHex && colorHex.startsWith('#') ? colorHex : '#58a6ff';
      g.addColorStop(0, c + '40');
      g.addColorStop(0.7, c + '08');
      g.addColorStop(1, c + '00');
      return g;
    };

    const nativeRadial = series.chartType === 'pie' || series.chartType === 'doughnut';
    const numericValues = values.map(Number).filter(value => Number.isFinite(value));
    const additiveCategorical = !series.datasets?.length && labels.length >= 2 && labels.length <= 80
      && !labels.some(label => /^\d{4}/.test(String(label)))
      && (['state', 'category'].includes(series.scope) || series.chartType === 'bar')
      && !/%|rate|index|ratio|per\b|per-|score|average|share|growth|yoy|change|years|°|days|density|expectancy/i.test(`${suffix} ${title}`)
      && numericValues.every(value => value >= 0) && numericValues.filter(value => value > 0).length >= 2;
    const canTogglePie = nativeRadial || additiveCategorical;
    const preferPie = additiveCategorical && ['Elections', 'U.S. Elections'].includes(category);
    const barType = nativeRadial ? 'bar' : (series.chartType || 'line');
    let activeType = nativeRadial ? series.chartType : preferPie ? 'doughnut' : barType;
    const radialColors = [
      '#ff9933', '#3fb950', '#58a6ff', '#bc8cff', '#ff7b72', '#f6c344',
      '#39c5bb', '#f778ba', '#a5d6ff', '#d2a8ff', '#ffa657', '#7ee787',
      '#e3b341', '#79c0ff', '#db61a2', '#56d364', '#ff6b6b', '#8b949e',
      '#d29922', '#a371f7'
    ];
    const radialPoints = () => {
      const points = labels.map((label, i) => ({ label, value: Number(values[i]) }))
        .filter(point => Number.isFinite(point.value) && point.value > 0)
        .sort((a, b) => b.value - a.value);
      if (points.length <= 12) return points;
      const rest = points.slice(11);
      return [...points.slice(0, 11), { label: `Other (${rest.length})`, value: rest.reduce((sum, point) => sum + point.value, 0) }];
    };
    const buildDatasets = isRadialChart => {
      if (series.datasets && series.datasets.length > 0) {
        return { labels, datasets: series.datasets.map((dataset, i) => {
          const dsColor = dataset.borderColor || dataset.color || ['#ff9933', '#58a6ff', '#3fb950', '#a371f7', '#ff7b72', '#f6c344'][i % 6];
          return {
            label: dataset.label,
            data: dataset.values || dataset.data,
            borderColor: dsColor,
            backgroundColor: createGradientFill(dsColor.slice(0, 7)),
            fill: true,
            borderWidth: labels.length > 60 ? 2 : 2.8,
            pointRadius: labels.length > 60 ? 0 : 2.5,
            pointHoverRadius: 6,
            pointHoverBackgroundColor: dsColor,
            tension: 0.32,
            spanGaps: true
          };
        }) };
      }
      const singleColor = color || '#58a6ff';
      const points = isRadialChart ? radialPoints() : null;
      const shownLabels = points ? points.map(point => point.label) : labels;
      const palette = shownLabels.map((_, index) => radialColors[index % radialColors.length]);
      return { labels: shownLabels, datasets: [{
        label: title,
        data: points ? points.map(point => point.value) : values,
        borderColor: isRadialChart ? CHART_THEME.sliceBorder : singleColor,
        backgroundColor: isRadialChart ? palette : createGradientFill(singleColor.slice(0, 7)),
        fill: !isRadialChart,
        borderWidth: isRadialChart ? 2 : 2.8,
        hoverOffset: isRadialChart ? 14 : 0,
        hoverBorderWidth: isRadialChart ? 3 : 0,
        pointRadius: isRadialChart || labels.length > 60 ? 0 : 3,
        pointHoverRadius: isRadialChart ? 0 : 6,
        pointHoverBackgroundColor: singleColor,
        tension: isRadialChart ? 0 : 0.32
      }] };
    };
    let chartDatasets = buildDatasets(nativeRadial || preferPie).datasets;

    const createChart = type => {
      const isRadialChart = type === 'pie' || type === 'doughnut';
      const built = buildDatasets(isRadialChart);
      chartDatasets = built.datasets;
      return new Chart(canvas, {
        type,
        data: built,
        options: chartOptions(suffix, hasMultipleDatasets, !isRadialChart && series.chartType === 'bar' && series.indexAxis === 'y', type),
      });
    };
    if (typeof Chart !== 'undefined') {
      chart = createChart(activeType);
      canvas.addEventListener('dblclick', () => card.querySelector('.expand-chart-btn')?.click());
    }
    if (chart && canTogglePie) {
      const toggle = document.createElement('div');
      toggle.className = 'chart-type-toggle';
      toggle.setAttribute('role', 'group');
      toggle.setAttribute('aria-label', `Chart type for ${title}`);
      toggle.innerHTML = `<button type="button" data-type="doughnut">◔ Pie</button><button type="button" data-type="${barType}">▥ ${barType === 'line' ? 'Line' : 'Bar'}</button>`;
      const syncToggle = () => toggle.querySelectorAll('button').forEach(button => {
        const active = (button.dataset.type === 'doughnut') === (activeType === 'pie' || activeType === 'doughnut');
        button.classList.toggle('active', active);
        button.setAttribute('aria-pressed', String(active));
      });
      toggle.addEventListener('click', event => {
        const button = event.target.closest('button');
        if (!button) return;
        event.stopPropagation();
        const nextType = button.dataset.type === 'doughnut' ? (nativeRadial ? series.chartType : 'doughnut') : barType;
        if (nextType === activeType) return;
        chart.destroy();
        activeType = nextType;
        chart = createChart(activeType);
        const entry = charts.find(item => item.card === card);
        if (entry) entry.chart = chart;
        syncToggle();
      });
      syncToggle();
      card.querySelector('.chart-wrap').prepend(toggle);
    }
    if (chart && card._range) {
      const baseDatasets = chart.data.datasets.map(dataset => [...dataset.data]);
      const applyChartRange = () => {
        let startYear = Number(card._range.startSelect.value);
        let endYear = Number(card._range.endSelect.value);
        if (startYear > endYear) {
          if (document.activeElement === card._range.startSelect) {
            endYear = startYear;
            card._range.endSelect.value = String(endYear);
          } else {
            startYear = endYear;
            card._range.startSelect.value = String(startYear);
          }
        }
        const selected = labels.map((label, i) => ({ label, i, year: Number(String(label).slice(0, 4)) }))
          .filter(point => point.year >= startYear && point.year <= endYear);
        chart.data.labels = selected.map(point => point.label);
        chart.data.datasets.forEach((dataset, datasetIndex) => {
          dataset.data = selected.map(point => baseDatasets[datasetIndex][point.i]);
        });
        chart.resetZoom();
        chart.update();
      };
      card._range.startSelect.addEventListener('change', applyChartRange);
      card._range.endSelect.addEventListener('change', applyChartRange);
      card.querySelector('.reset').addEventListener('click', () => {
        card._range.startSelect.value = years[0];
        card._range.endSelect.value = years[years.length - 1];
        applyChartRange();
      });
    }

    if (hasMultipleDatasets) {
      const chartWrap = card.querySelector('.chart-wrap');
      const legendBar = document.createElement('div');
      legendBar.className = 'custom-legend';
      chartDatasets.forEach((dataset, datasetIdx) => {
        const chip = document.createElement('button');
        chip.type = 'button';
        chip.className = 'legend-chip';
        chip.innerHTML = `<span class="legend-dot" style="background-color:${dataset.borderColor}"></span> ${dataset.label}`;
        
        chip.addEventListener('mouseenter', () => {
          if (!chart) return;
          chart.data.datasets.forEach((ds, idx) => {
            if (idx !== datasetIdx) {
              chart.getDatasetMeta(idx).hidden = true;
            }
          });
          chart.update('none');
        });
        chip.addEventListener('mouseleave', () => {
          if (!chart) return;
          chart.data.datasets.forEach((ds, idx) => {
            chip.classList.contains('muted') ? chart.getDatasetMeta(idx).hidden = true : chart.getDatasetMeta(idx).hidden = false;
          });
          chart.update('none');
        });
        chip.addEventListener('click', () => {
          if (!chart) return;
          const isVisible = chart.isDatasetVisible(datasetIdx);
          chart.setDatasetVisibility(datasetIdx, !isVisible);
          chip.classList.toggle('muted', isVisible);
          chart.update();
        });
        legendBar.appendChild(chip);
      });
      chartWrap.insertBefore(legendBar, canvas);
    }

    card.addEventListener('click', () => {
      document.querySelectorAll('.chart-card').forEach(c => c.classList.remove('selected-card'));
      card.classList.add('selected-card');
      if (categoryBgMap[category]) setEraBackground(categoryBgMap[category]);
    });
    card.addEventListener('mouseenter', () => {
      if (categoryBgMap[category]) setEraBackground(categoryBgMap[category]);
    });

    const reset = card.querySelector('.reset');
    if (reset) reset.addEventListener('click', () => { if (chart) chart.resetZoom(); });
    chartEntry.chart = chart;
    };
    lazyCharts.set(card, ensureChart);
    if (chartObserver) chartObserver.observe(card);
    else ensureChart();
  });
  const cards = grid ? [...grid.querySelectorAll('.chart-card')] : [];
  const headings = grid ? [...grid.querySelectorAll('.category-heading')] : [];
  const subHeadings = grid ? [...grid.querySelectorAll('.subgroup-heading')] : [];
  const filter = document.querySelector('#chart-filter');
  const groupFilter = document.querySelector('#group-filter');
  const subgroupFilter = document.querySelector('#subgroup-filter');
  const search = document.querySelector('#chart-search');
  const savedToggle = document.querySelector('#saved-toggle');
  const resultCount = document.querySelector('#chart-result-count');
  const liveCount = document.querySelector('#hero-live-count');
  if (liveCount) liveCount.textContent = String(grid ? cards.filter(card => card.dataset.state === 'live').length : charts.filter(item => item.live).length);
  const subgroupOwners = new Map();
  const groupToSubgroups = { all: [] };
  cards.forEach(card => {
    const group = card.dataset.category;
    const subgroup = card.dataset.subgroup;
    if (!groupToSubgroups[group]) groupToSubgroups[group] = [];
    if (!groupToSubgroups[group].includes(subgroup)) {
      groupToSubgroups[group].push(subgroup);
      groupToSubgroups.all.push(subgroup);
    }
    if (!subgroupOwners.has(subgroup)) subgroupOwners.set(subgroup, new Set());
    subgroupOwners.get(subgroup).add(group);
  });
  const subgroupGroups = Object.fromEntries(
    [...subgroupOwners]
      .filter(([, groups]) => groups.size === 1)
      .map(([subgroup, groups]) => [subgroup, groups.values().next().value])
  );

  const updateSubgroupFilter = () => {
    const selectedGroup = groupFilter.value;
    const currentValue = subgroupFilter.value;

    subgroupFilter.replaceChildren();

    const defaultOpt = document.createElement('option');
    defaultOpt.value = 'all';
    defaultOpt.textContent = selectedGroup === 'all' ? 'All subgroups' : `All ${selectedGroup} subgroups`;
    subgroupFilter.appendChild(defaultOpt);

    if (selectedGroup === 'all') {
      const groupLabels = {
        Economic: '📈 Economic',
        Social: '👥 Social',
        'Defence & Strategic': '🛡️ Defence & Strategic',
        'Crime & Security': '⚖️ Crime & Security',
        'Pew Research': '📊 Pew Research',
        Elections: '🗳️ Elections',
        'U.S. Elections': '🇺🇸 U.S. Elections'
      };
      const displayedSubgroups = new Set();
      Object.keys(groupToSubgroups).forEach(grpKey => {
        if (grpKey === 'all') return;
        const optgroup = document.createElement('optgroup');
        optgroup.label = groupLabels[grpKey] || grpKey;
        groupToSubgroups[grpKey].forEach(subgroup => {
          if (displayedSubgroups.has(subgroup)) return;
          displayedSubgroups.add(subgroup);
          const option = document.createElement('option');
          option.value = subgroup;
          option.textContent = subgroup;
          optgroup.appendChild(option);
        });
        subgroupFilter.appendChild(optgroup);
      });
    } else {
      const availableSubgroups = groupToSubgroups[selectedGroup] || [];
      availableSubgroups.forEach(subgroup => {
        const option = document.createElement('option');
        option.value = subgroup;
        option.textContent = subgroup;
        subgroupFilter.appendChild(option);
      });
    }

    const allAvailable = groupToSubgroups[selectedGroup] || groupToSubgroups.all;
    if (allAvailable.includes(currentValue)) {
      subgroupFilter.value = currentValue;
    } else {
      subgroupFilter.value = 'all';
    }
  };
  const groupHeroData = {
    Economic: {
      title: "📈 Economic, Per Capita Wealth & Capital Markets Atlas",
      desc: "Macroeconomic balance sheet, per capita Net National Income (₹2.18 Lakh), purchasing power parity (PPP), monetary policy, GDP growth trajectory, trade openness, Union Budget fiscal balance, and global equity market comparisons.",
      badge1: "1947 — 2026",
      badge2: "GDP, Wealth & Fiscal"
    },
    "Industry Trends & Performance": {
      title: "🏭 Industry Trends, Performance & Industrial Stability Atlas",
      desc: "Manufacturing expansion, PLI scheme impact, automobile production, crude steel, electronics, pharmaceuticals, textiles, 100% railway electrification, National Highways construction, clean energy capacity, and core industrial indices.",
      badge1: "PLI Manufacturing",
      badge2: "Steel, Auto & Infrastructure"
    },
    "Mining & Natural Resources": {
      title: "⛏️ Mined Resources, Minerals & Energy Commodities Atlas",
      desc: "India's mineral wealth and strategic resource security: metallic ores (iron ore, bauxite, copper, manganese), energy minerals (coal, lignite, domestic crude, natural gas), industrial minerals (limestone, rare earths), and mineral export trade.",
      badge1: "Indian Bureau of Mines",
      badge2: "Critical Minerals Mission"
    },
    "Payments & Digital Banking": {
      title: "💳 Payments & Digital Financial Infrastructure Atlas",
      desc: "The world's largest real-time retail payment transformation: UPI transaction volume and annual value (₹265 Lakh Cr), credit & debit card POS spends, active card circulation, and official RBI Digital Payments Index (DPI).",
      badge1: "NPCI & RBI Data",
      badge2: "UPI & Card Ecosystem"
    },
    "State Performance & Regional Health": {
      title: "🏛️ State Performance, GSDP & Regional Industrial Health",
      desc: "State-wise economic, financial, and welfare comparison across India's federal landscape: GSDP growth trajectories, operating factory counts, fiscal deficit and own-tax ratios to GSDP, PMAY housing completions, Jal Jeevan tap water coverage, and PM MUDRA loan disbursements.",
      badge1: "RBI State Finances",
      badge2: "MOSPI & NITI Aayog"
    },
    "Public Health & Epidemiology": {
      title: "🩺 Public Health, Lifespan Milestones & Epidemiology Atlas",
      desc: "National health indicators from World Bank/WHO and the RBI state handbook: infant, under-five and maternal mortality, tuberculosis and malaria incidence, causes of death, health spending and who pays for care, plus State/UT health outcomes.",
      badge1: "ICMR & MoHFW",
      badge2: "WHO & NHA Data"
    },
    Social: {
      title: "👥 Demographics, Welfare & Human Capital",
      desc: "Long-term social transformation across decades: 1.4B population dynamics, nationwide electrification, high-speed broadband access, flagship welfare schemes, and life expectancy milestones.",
      badge1: "1.4B Population",
      badge2: "Welfare & Infrastructure"
    },
    "Defence & Strategic": {
      title: "🛡️ Defence, Arms Production & Strategic Modernization Atlas",
      desc: "India's defense manufacturing evolution, historic Make in India defense export surge (₹23,497 Cr), indigenous production (₹1.45 Lakh Cr), SIPRI arms capability trends, DRDO R&D, and defense capital acquisition modernization.",
      badge1: "Make in India Defence",
      badge2: "Export Surge & Modernization"
    },
    "Pew Research": {
      title: "📊 Global Standing & Public Opinion",
      desc: "Pew Research Center global attitudes studies tracking international perception, economic confidence, bilateral ties, and leadership opinions.",
      badge1: "Pew Global Attitudes",
      badge2: "Survey Snapshots"
    },
    "Crime & Security": {
      title: "⚖️ Public Safety, Internal Security & Anti-Insurgency Atlas",
      desc: "Comprehensive national security atlas: Left-Wing Extremism (LWE / Maoism) 22-year fatality decline, Jammu & Kashmir terrorism reduction (2000-2025), North East insurgency pacification (2000-2025), historical Punjab militancy archive (1981-1995), NDPS drug offences, child protection/POCSO cases, road accident fatalities, and police strength.",
      badge1: "National Security",
      badge2: "MHA & SATP Databases"
    },
    Elections: {
      title: "🗳️ Election Results Atlas",
      desc: "Explore current ECI candidate results alongside a growing archive of downloadable ECI historical statistical reports. Historical rows are source-linked and selectable by election, state and constituency; available archived workbooks do not yet provide complete coverage of every election year or state.",
      badge1: "Election Commission of India",
      badge2: "Historical coverage is partial"
    },
    "U.S. Elections": {
      title: "🇺🇸 U.S. Elections & Campaign Finance",
      desc: "Explore U.S. presidential Electoral College outcomes from the National Archives alongside Federal Election Commission candidate-finance summaries for presidential, Senate and House cycles. Finance charts report aggregate receipts, disbursements, cash on hand and debts by party or candidate office state; they are not voting or turnout measures.",
      badge1: "U.S. National Archives & FEC",
      badge2: "Presidential + Congress"
    },
    "Tourism & Heritage": {
      title: "🏛️ Tourism & UNESCO World Heritage",
      desc: "Follow annual international visitor and receipts indicators, then explore India’s UNESCO World Heritage properties by inscription year. Visitor totals are national, while the heritage series is reconstructed from current official inscription records; neither is a state-wise monument attendance measure.",
      badge1: "World Bank annual indicators",
      badge2: "UNESCO property records"
    }
  };

  const subgroupArtMap = {
    "Macroeconomics": "assets/macro-skyline.svg",
    "Per Capita Income & Wealth": "assets/income-wealth.svg",
    "Manufacturing & Industrial Growth": "assets/factory-floor.svg",
    "Trade & External": "assets/port-trade.svg",
    "Monetary Policy": "assets/central-bank.svg",
    "Production & Commodities": "assets/commodities.svg",
    "Media & Publications": "assets/media-press.svg",
    "Markets": "assets/stock-market.svg",
    "Fiscal & Union Budget": "assets/union-budget.svg",
    "Infrastructure Development": "assets/infrastructure.svg",
    "Food Processing & Consumer Goods": "assets/food-processing.svg",
    "Heavy Industry & Metals": "assets/steel-plant.svg",
    "Automobiles & Transport Equipment": "assets/auto-highway.svg",
    "Chemicals, Pharma & Electronics": "assets/chem-pharma.svg",
    "Industrial Output Monitor (IIP)": "assets/iip-monitor.svg",
    "Metallic Minerals & Ores": "assets/metal-ores.svg",
    "Energy Minerals & Fuel": "assets/energy-fuel.svg",
    "Non-Metallic & Industrial Minerals": "assets/industrial-minerals.svg",
    "Mineral Exports & Trade": "assets/mineral-exports.svg",
    "Mining Output Monitor (IIP)": "assets/mining-output.svg",
    "Mineral Price Monitor (WPI)": "assets/mineral-prices.svg",
    "UPI & Digital Payments": "assets/upi-payments.svg",
    "Card Spends & Ecosystem": "assets/card-spends.svg",
    "Digital Financial Index": "assets/digital-index.svg",
    "State Banking & Credit": "assets/state-banking.svg",
    "Regional Rural Banks": "assets/rural-banks.svg",
    "Pensions & Social Security": "assets/pensions.svg",
    "State Financial Health & GSDP": "assets/state-gsdp.svg",
    "State Infrastructure & Services": "assets/state-infra.svg",
    "State Welfare & Scheme Coverage": "assets/state-welfare.svg",
    "State Socio-Demographic Milestones": "assets/state-demography.svg",
    "State Industrial & Manufacturing Hubs": "assets/state-industry.svg",
    "State Economy & Industry": "assets/state-economy.svg",
    "Mortality & Lifespan Milestones": "assets/lifespan.svg",
    "Disease Burden & Epidemiology": "assets/epidemiology.svg",
    "Health Infrastructure & Spending": "assets/health-infra.svg",
    "State Health Outcomes": "assets/state-health.svg",
    "State Health Infrastructure": "assets/state-hospitals.svg",
    "Demographics": "assets/demographics.svg",
    "Welfare": "assets/welfare.svg",
    "Employment & Poverty": "assets/employment.svg",
    "Education": "assets/education.svg",
    "Defence Budget & Modernization": "assets/defence-budget.svg",
    "Defence Exports & Production": "assets/defence-exports.svg",
    "Strategic Stockpiles & Capabilities": "assets/strategic-assets.svg",
    "North East Insurgency": "assets/northeast-hills.svg",
    "Jammu & Kashmir Insurgency": "assets/kashmir-valley.svg",
    "Punjab Militancy & Security": "assets/punjab-border.svg",
    "Violence & Crime": "assets/law-justice.svg",
    "Maoism / LWE": "assets/red-corridor.svg",
    "Terrorism": "assets/counter-terror.svg",
    "Public opinion": "assets/public-opinion.svg",
    "Indian Elections": "assets/ballot-box.svg",
    "Lok Sabha 2024 — National": "assets/lok-sabha.svg",
    "Lok Sabha 2024 — States": "assets/vote-map.svg",
    "Election Comparisons Across States": "assets/election-compare.svg",
    "State Assembly Results 2022–2026": "assets/assembly-results.svg",
    "U.S. Presidential Elections": "assets/white-house.svg",
    "U.S. Presidential Campaign Finance": "assets/campaign-finance.svg",
    "U.S. Congressional Campaign Finance": "assets/congress-finance.svg",
    "U.S. Campaign Funding Composition": "assets/funding-mix.svg",
    "International Visitor Trends": "assets/visitor-trends.svg",
    "World Heritage Sites": "assets/heritage-sites.svg",
    "Global Tourism Comparison": "assets/global-tourism.svg"
  };

  const subgroupHeroData = {
    "Heavy Industry & Metals": {
      title: "🏗️ Heavy Industry, Metals & Capital Goods",
      desc: "Basic metals (iron, steel, aluminium), fabricated metal products, machinery, electrical equipment, cement and other non-metallic minerals, and refined petroleum, tracked through MOSPI's Index of Industrial Production since 2011-12, plus UNIDO's technology-intensity split.",
      badge1: "MOSPI IIP",
      badge2: "Steel, Machinery & Cement"
    },
    "Automobiles & Transport Equipment": {
      title: "🚗 Cars, Two-Wheelers & Transport Equipment",
      desc: "Output of motor vehicles (cars, utility vehicles, trucks, trailers) and other transport equipment (dominated by two-wheelers), monthly and annual from MOSPI IIP, with SIAM's segment-wise production mix.",
      badge1: "MOSPI IIP & SIAM",
      badge2: "Cars & Two-Wheelers"
    },
    "Food Processing & Consumer Goods": {
      title: "🍚 Food Processing & Consumer Manufacturing",
      desc: "Food products, beverages, tobacco, textiles, apparel, leather, wood, paper, printing and furniture: the labour-intensive consumer industries, with UNIDO's composition of manufacturing value added.",
      badge1: "MOSPI IIP & UNIDO",
      badge2: "Food, Textiles & Consumer"
    },
    "Chemicals, Pharma & Electronics": {
      title: "💊 Chemicals, Pharmaceuticals & Electronics",
      desc: "Chemicals, pharmaceuticals, rubber and plastics, and computers, electronics and optical products: India's process and high-technology manufacturing base.",
      badge1: "MOSPI IIP",
      badge2: "Pharma & Electronics"
    },
    "Industrial Output Monitor (IIP)": {
      title: "📡 Industrial Output Monitor",
      desc: "Monthly IIP by use (capital, intermediate, infrastructure, consumer durables and non-durables), industry growth rankings, cumulative change since 2011-12, and how many industries are expanding versus contracting.",
      badge1: "Monthly MOSPI data",
      badge2: "Growth Rankings"
    },
    "Global Tourism Comparison": {
      title: "🌍 India vs the World's Top Destinations",
      desc: "International arrivals, tourism receipts, spending per visitor and the tourism balance for India against France, Spain, the United States, China, Italy, Türkiye, Mexico, Thailand, Germany, the UK, Japan and the UAE.",
      badge1: "World Bank / UN Tourism",
      badge2: "Global Benchmark"
    },
    "Macroeconomics": {
      title: "📊 Macroeconomics & Growth Trajectory",
      desc: "Core macroeconomic balance sheet: GDP per capita, CPI inflation, Union fiscal deficit, current account balance, tax-to-GDP ratio, and gross domestic savings.",
      badge1: "Macro Balances",
      badge2: "World Bank & RBI"
    },
    "Per Capita Income & Wealth": {
      title: "💰 Per Capita Income & National Wealth Trajectory",
      desc: "India's per capita Net National Income (NNI) growth in Indian Rupees (₹2.18 Lakh) alongside GNI per capita in Purchasing Power Parity (PPP current international $).",
      badge1: "MOSPI & World Bank",
      badge2: "Per Capita Wealth"
    },
    "Monetary Policy": {
      title: "🏛️ Monetary Policy & Banking Credit",
      desc: "Financial system liquidity, money supply (M3 broad money share of GDP), and private sector bank credit expansion.",
      badge1: "RBI Policy",
      badge2: "Financial Deepening"
    },
    "Trade & External": {
      title: "🌐 External Trade & Foreign Reserves",
      desc: "Trade openness ratio, foreign exchange reserves (forex), official rupee-dollar exchange rate, and monthly merchandise export/import bills.",
      badge1: "Foreign Trade",
      badge2: "Forex Reserves"
    },
    "Markets": {
      title: "📈 Capital Markets & Global Benchmarks",
      desc: "BSE Sensex, Nifty 50, and Nifty VIX rebased to 100 alongside benchmark comparisons with US S&P 500, UK FTSE 100, Japan Nikkei 225, China Shanghai Composite, and top global GDP economies.",
      badge1: "BSE & NSE Indices",
      badge2: "Global Comparisons"
    },
    "Manufacturing & Industrial Growth": {
      title: "🏭 Manufacturing Sectors & Industrial Performance",
      desc: "Industrial growth engines boosted by Production Linked Incentive (PLI) schemes: General IIP index, Eight Core Industries index, automobile production volume (SIAM), crude steel output (2nd largest globally), electronics & smartphone manufacturing value (MeitY), pharma exports (Pharmexcil), and textiles/apparel export trajectory.",
      badge1: "PLI Manufacturing",
      badge2: "Steel, Auto & Electronics"
    },
    "Infrastructure Development": {
      title: "🛣️ Infrastructure Development & Connectivity Networks",
      desc: "Physical and digital asset creation: National Highways construction cadence (km/yr), 100% Railway electrification share, renewable power capacity (GW), civil aviation passenger traffic, power consumption, e-way bills, rail freight, port cargo, and high-speed broadband expansion.",
      badge1: "MoRTH & Railways",
      badge2: "Clean Energy & Telecom"
    },
    "Production & Commodities": {
      title: "🛢️ Commodities, Energy & High-Frequency Signals",
      desc: "Indian crude oil basket pricing, petroleum fuel product consumption, WPI wholesale price inflation, and high-frequency production indicators.",
      badge1: "Energy Exposure",
      badge2: "Production Proxies"
    },
    "UPI & Digital Payments": {
      title: "⚡ UPI & Real-Time Digital Payments",
      desc: "The world's leading real-time payment system: monthly UPI transaction volume and annual transaction value (₹265 Lakh Crores).",
      badge1: "NPCI & RBI Data",
      badge2: "Real-Time Payments"
    },
    "Card Spends & Ecosystem": {
      title: "💳 Credit & Debit Card Ecosystem",
      desc: "Annual consumer spending on credit cards (₹25.8 Lakh Cr) vs debit card POS transactions (₹6.8 Lakh Cr) and active card circulation counts (12.8 Cr Credit, 101.5 Cr Debit).",
      badge1: "RBI Payment Indicators",
      badge2: "Credit & Debit Cards"
    },
    "Digital Financial Index": {
      title: "📊 RBI Digital Payments Index (RBI DPI)",
      desc: "Official Reserve Bank of India composite index measuring digital payment enablement, infrastructure, performance, and consumer centricity across India (Base 100 = March 2018).",
      badge1: "RBI DPI Index",
      badge2: "Digital Adoption"
    },
    "State Financial Health & GSDP": {
      title: "🏛️ State Financial Health & GSDP Growth",
      desc: "GSDP trajectories comparing India's largest state economies (Maharashtra, Tamil Nadu, Gujarat, Karnataka, UP, West Bengal) alongside RBI fiscal-deficit and own-tax-revenue ratios to GSDP.",
      badge1: "RBI State Finances",
      badge2: "GSDP & Fiscal Health"
    },
    "State Industrial & Manufacturing Hubs": {
      title: "🏭 State Manufacturing & Investment Hubs",
      desc: "State export-preparedness and ease-of-doing-business snapshots, alongside RBI factory-employment rankings.",
      badge1: "ASI Factory Census",
      badge2: "DPIIT FDI Data"
    },
    "State Welfare & Scheme Coverage": {
      title: "🏡 State Welfare Scheme Execution",
      desc: "State-level delivery of national welfare infrastructure: PMAY pucca housing units built, Jal Jeevan Mission Har Ghar Jal tap water access %, and PM MUDRA micro-credit loan disbursements.",
      badge1: "Welfare Schemes",
      badge2: "PMAY, JJM & MUDRA"
    },
    "Mortality & Lifespan Milestones": {
      title: "👶 Infant & Maternal Mortality Milestones",
      desc: "World Bank infant, neonatal and under-five mortality (per 1,000 live births) and the modelled maternal mortality ratio (per 100,000 live births).",
      badge1: "SRS & MoHFW",
      badge2: "Lifespan & Mortality"
    },
    "Disease Burden & Epidemiology": {
      title: "🔬 Disease Burden & Epidemiological Transition",
      desc: "Shifting epidemiology: WHO tuberculosis and malaria incidence, smoking prevalence, and the World Bank causes-of-death split between communicable, non-communicable and injury deaths.",
      badge1: "ICMR & WHO Nikshay",
      badge2: "Disease Burden"
    },
    "Health Infrastructure & Spending": {
      title: "🏥 Government Health Spending & Out-of-Pocket Expenditure",
      desc: "Health financing from WHO Global Health Expenditure data: current and government health spending, out-of-pocket share, hospital beds, physicians, immunisation and water and sanitation access.",
      badge1: "National Health Accounts",
      badge2: "Health Spending"
    },
    "Maoism / LWE": {
      title: "⛰️ Left-Wing Extremism (LWE) & Maoist Insurgency",
      desc: "Ministry of Home Affairs official LWE aggregate fatalities (8,956 killed 2004-2025) alongside annual LWE deaths trajectory (2004-2025) and South Asia Terrorism Portal (SATP 2000-2025) annual casualty breakdown across Civilians, Security Forces, and Perpetrators.",
      badge1: "MHA LWE Division",
      badge2: "SATP Casualty Breakdown"
    },
    "Jammu & Kashmir Insurgency": {
      title: "🏔️ Jammu & Kashmir Counter-Terrorism & Insurgency",
      desc: "Annual counter-terrorism fatalities and terrorist incident volume in J&K showing a steep structural decline in violence levels.",
      badge1: "MHA J&K Division",
      badge2: "SATP J&K Casualty Data"
    },
    "North East Insurgency": {
      title: "🌲 North East Insurgency Pacification",
      desc: "Decadal decline in insurgent fatalities and registered incidents across North Eastern states following peace accords and border security operations.",
      badge1: "MHA North East Division",
      badge2: "NE Peace Accords"
    },
    "Punjab Militancy & Security": {
      title: "🌾 Historical Punjab Militancy & Security Archive",
      desc: "Historical fatality archive tracking the Punjab militancy period (1981-1995) prior to the restoration of full peace and democratic stability.",
      badge1: "MHA Historical Archive",
      badge2: "SATP Punjab Database"
    },
    "Fiscal & Union Budget": {
      title: "📜 Union Budget & Fiscal Expansion",
      desc: "Post-independence Union Budget expenditure trajectory (₹48.2 Lakh Cr), annual expenditure YoY growth %, strategic Capex allocation for capital asset creation, and gross central tax revenue buoyancy.",
      badge1: "Ministry of Finance",
      badge2: "Union Budget & Capex"
    },
    "Media & Publications": {
      title: "📰 Media & Public Data Cadence",
      desc: "Transparent public-data publication signals and Substack writing cadence.",
      badge1: "Public Data",
      badge2: "Indian Matrix RSS"
    },
    "Demographics": {
      title: "👥 Demographics & Social Equity",
      desc: "Total 1.4B population trajectory, labour force unemployment rate, literacy rate breakdowns across SC/ST/OBC social categories, religious community literacy rates, and PM MUDRA loan social inclusion distribution.",
      badge1: "1.4B Population",
      badge2: "MOSPI & Census Data"
    },
    "Welfare": {
      title: "🏥 Social Welfare & Essential Access",
      desc: "Universal household electricity access (100%), internet penetration %, and life expectancy at birth milestones.",
      badge1: "Living Standards",
      badge2: "World Bank & MOSPI"
    },
    "Defence Exports & Production": {
      title: "🚀 Defence Manufacturing & Export Engine",
      desc: "Indigenous defence production surge (₹1.45 Lakh Cr) across DPSUs and private sector enterprises, alongside historic Make in India defence export growth (₹23,497 Cr to 85+ nations).",
      badge1: "DDP Ministry of Defence",
      badge2: "Export Surge ₹23.4k Cr"
    },
    "Defence Budget & Modernization": {
      title: "🎖️ Defence Allocation & R&D Capital Outlay",
      desc: "Defence expenditure share of Union Budget, DRDO R&D research allocation, and Capital Acquisition Outlay for modernizing weapons, aircraft, naval frigates, and artillery.",
      badge1: "DRDO & Armed Forces",
      badge2: "Capital Acquisition"
    },
    "Strategic Stockpiles & Capabilities": {
      title: "🛡️ Strategic Stockpiles & Arms Imports Trend",
      desc: "SIPRI arms inventory & conventional capability index, alongside declining foreign arms import reliance as indigenous defence manufacturing expands.",
      badge1: "SIPRI Database",
      badge2: "Stockpiles & Imports"
    },
    "Metallic Minerals & Ores": {
      title: "⛏️ Metallic Minerals & Ferrous/Non-Ferrous Ores",
      desc: "Foundational metallic mineral production powering heavy industry: Iron Ore output (315 MT), Bauxite for aluminium smelting (27.8 MT), Refined Copper output (615k Tonnes), and Manganese Ore (38.2 Lakh Tonnes).",
      badge1: "IBM & Ministry of Mines",
      badge2: "Iron, Bauxite & Copper"
    },
    "Energy Minerals & Fuel": {
      title: "🔥 Energy Minerals & Fossil Fuel Resources",
      desc: "Baseload power and domestic fuel production: total domestic Coal production (1.14 Billion Tonnes), Lignite brown coal mining (54.8 MT), domestic Crude Petroleum output (30.8 MMT), and offshore/onshore Natural Gas production (42 BCM).",
      badge1: "Ministry of Coal & MoPNG",
      badge2: "Coal, Crude & Gas"
    },
    "Non-Metallic & Industrial Minerals": {
      title: "🧱 Non-Metallic, Industrial & Critical Minerals",
      desc: "Raw materials for construction, fertilizers, and technology: Limestone production for cement (505 MT), IREL Critical Minerals & Rare Earth Elements (REE) Index, and Rock Phosphate/Gypsum for chemical fertilizers.",
      badge1: "IREL & IBM Data",
      badge2: "Limestone & Rare Earths"
    },
    "Mineral Exports & Trade": {
      title: "🚢 Mineral & Metal Exports & Strategic Trade Reliance",
      desc: "Global mineral trade trajectory: total Mineral & Metal export value ($38.5 Billion), Iron Ore export volume (49.5 MT), Refined Petroleum product export volume (71.5 MMT), and Critical Mineral Strategic Import Dependency Index (reduced from 100% to 68.5%).",
      badge1: "DGFT & PPAC Trade",
      badge2: "Petroleum & Ore Exports"
    },
    "Mineral Price Monitor (WPI)": {
      title: "💹 Mineral Price Monitor",
      desc: "Official monthly wholesale prices of iron ore, bauxite, copper, zinc, lead, manganese, chromite, limestone, rock phosphate, crude oil, natural gas, coal and lignite since 2012, with inflation rankings, price-change bands and rising-vs-falling pies.",
      badge1: "MOSPI / DPIIT WPI",
      badge2: "16 Commodities"
    },
    "Mining Output Monitor (IIP)": {
      title: "⛏️ Mining Output Monitor",
      desc: "Annual and monthly mining and quarrying output from MOSPI's Index of Industrial Production, compared with manufacturing and electricity, with growth trends and mining's official weight in the IIP.",
      badge1: "Monthly MOSPI data",
      badge2: "Mining & Quarrying"
    },
    "Violence & Crime": {
      title: "⚖️ Cognizable Crime & Public Safety",
      desc: "Historical IPC cognizable crime rates per 100k (1951-2023), NCRB 2023 crime category snapshot, crimes against women rate, cyber crime case volume, economic offences rate, NDPS drug offences, child protection/POCSO cases, road accident fatalities, and police strength.",
      badge1: "NCRB Crime in India",
      badge2: "Public Safety Records"
    },
    "Terrorism": {
      title: "💥 Counter-Terrorism & Event Trends",
      desc: "Global Terrorism Database (GTD) open series tracking terrorist attack counts and human fatalities in India (1970-2020).",
      badge1: "GTD & OWID Data",
      badge2: "Terrorism Statistics"
    },
    "Public opinion": {
      title: "📊 Pew Research Public Opinion & Global Attitudes",
      desc: "Landmark Pew Research Center survey snapshots: global power perceptions, US-India bilateral ties, domestic economic confidence, religious tolerance & pluralism (29,999 respondents), gender equality views, news media trust, and climate change awareness.",
      badge1: "Pew Global Survey",
      badge2: "Public Attitudes Data"
    },
    "Indian Elections": {
      title: "🗳️ Indian Lok Sabha & State Assembly Results",
      desc: "Compare currently published ECI constituency tables with candidate rows parsed from available ECI historical statistical-report workbooks. Select an available election, year, State/UT and constituency to inspect the original reported votes. The historical workbook archive is partial: missing periods or seats are unavailable, not zero, and live results remain provisional until Form 20.",
      badge1: "ECI results & report archive",
      badge2: "Historical archive is partial"
    },
    "U.S. Presidential Elections": {
      title: "🇺🇸 U.S. Presidential Elections",
      desc: "Compare completed U.S. Presidential Electoral College results from the National Archives. Electoral College totals are not popular votes or ballots cast; campaign finances are presented in separate subgroups.",
      badge1: "U.S. National Archives",
      badge2: "2000–2024 Electoral College"
    },
    "U.S. Presidential Campaign Finance": {
      title: "💵 U.S. Presidential Campaign Finance",
      desc: "Compare Federal Election Commission candidate receipts, disbursements, cash on hand and debts by party across presidential-office campaign-finance cycles. These filing-cycle snapshots are financial aggregates, not electoral results; some cycle years are midterms with no Presidential election.",
      badge1: "Federal Election Commission",
      badge2: "Candidate filings by cycle"
    },
    "U.S. Congressional Campaign Finance": {
      title: "🏛️ U.S. Congressional Campaign Finance",
      desc: "Compare FEC-reported House and Senate candidate receipts, disbursements, cash on hand and debts by candidate office state. These are campaign-finance totals—not votes, turnout, or winning seats.",
      badge1: "Federal Election Commission",
      badge2: "House & Senate cycles"
    },
    "International Visitor Trends": {
      title: "🧳 International Visitor Trends",
      desc: "Track World Bank annual counts of international arrivals and departures alongside international tourism receipts in current US dollars. These are national measures reported at different frequencies of availability; receipts are nominal, and the indicators do not measure domestic travel, visits to individual monuments or State-level tourism.",
      badge1: "World Bank indicators",
      badge2: "Annual national series"
    },
    "World Heritage Sites": {
      title: "🏛️ UNESCO World Heritage Inscription Record",
      desc: "Explore annual inscription events, a cumulative count reconstructed from current UNESCO property pages, and current cultural/natural/mixed classifications. The historical line is not an archived snapshot for each year: revisions to today's list can change the reconstructed past, and inscription counts are not visitor numbers.",
      badge1: "UNESCO World Heritage Centre",
      badge2: "Current-list reconstruction"
    }
  };

  const updateGroupHero = () => {
    const hero = document.querySelector('#group-hero');
    if (!hero) return;
    const grp = groupFilter.value;
    if (grp === 'all' || !groupHeroData[grp]) {
      hero.hidden = true;
      return;
    }
    const heroInfo = subgroupHeroData[subgroupFilter.value] || groupHeroData[grp];
    const heroTitle = document.querySelector('#group-hero-title');
    const heroDesc = document.querySelector('#group-hero-desc');
    const heroBadges = document.querySelector('#group-hero-badges');
    const heroImage = document.querySelector('#group-hero-image');
    const heroImageCaption = document.querySelector('#group-hero-image-caption');
    const artPath = subgroupArtMap[subgroupFilter.value] || categoryBgMap[grp];
    if (artPath) setEraBackground(artPath);
    if (heroTitle) heroTitle.textContent = heroInfo.title;
    if (heroDesc) heroDesc.textContent = heroInfo.desc;
    if (heroBadges) heroBadges.innerHTML = `<span class="hero-badge saffron">${heroInfo.badge1}</span><span class="hero-badge green">${heroInfo.badge2}</span>`;
    if (heroImage && artPath) {
      heroImage.src = artPath;
      heroImage.alt = `${subgroupFilter.value !== 'all' ? subgroupFilter.value : grp} themed original illustration`;
    }
    if (heroImageCaption) {
      heroImageCaption.textContent = subgroupFilter.value !== 'all'
        ? `Original illustration · ${subgroupFilter.value}`
        : 'Original India-inspired vector illustration';
    }
    hero.hidden = false;
  };

  const syncGroupPills = (grpVal) => {
    if (groupPills.length > 0) {
      groupPills.forEach(p => {
        const active = p.dataset.group === grpVal;
        p.classList.toggle('active', active);
        p.setAttribute('aria-pressed', String(active));
      });
    }
  };

  const groupEraMap = {
    Economic: 'liberalization',
    Social: 'republic',
    'Defence & Strategic': 'modern',
    'Crime & Security': 'republic',
    'Pew Research': 'modern'
  };

  const groupPills = document.querySelectorAll('.group-pill');
  if (groupPills.length > 0) {
    groupPills.forEach(pill => {
      pill.addEventListener('click', () => {
        syncGroupPills(pill.dataset.group);
        groupFilter.value = pill.dataset.group;
        subgroupFilter.value = 'all';
        if (categoryBgMap[pill.dataset.group]) setEraBackground(categoryBgMap[pill.dataset.group]);
        updateSubgroupFilter();
        updateGroupHero();
        updateCards();
      });
    });
  }

  const tileGallery = document.querySelector('#tile-gallery-track');
  if (tileGallery) {
    const groupCounts = charts.reduce((counts, item) => ({ ...counts, [item.category]: (counts[item.category] || 0) + 1 }), {});
    Object.keys(categoryOrder).forEach(group => {
      const info = groupHeroData[group];
      if (!info) return;
      const tile = document.createElement('button');
      tile.type = 'button';
      tile.className = 'product-tile';
      tile.style.setProperty('--tile-art', `url("${categoryBgMap[group] || 'assets/parliament.svg'}")`);
      const eyebrow = document.createElement('span');
      eyebrow.className = 'product-tile-eyebrow';
      eyebrow.textContent = `${groupCounts[group] || 0} indicators`;
      const heading = document.createElement('strong');
      heading.textContent = info.title.replace(/^[^\p{L}\p{N}]+/u, '');
      const blurb = document.createElement('span');
      blurb.className = 'product-tile-copy';
      blurb.textContent = `${info.badge1} · ${info.badge2}`;
      const plus = document.createElement('span');
      plus.className = 'product-tile-plus';
      plus.setAttribute('aria-hidden', 'true');
      plus.textContent = '+';
      tile.append(eyebrow, heading, blurb, plus);
      tile.setAttribute('aria-label', `Explore ${group}`);
      tile.addEventListener('click', () => {
        window.location.href = `explore.html?group=${encodeURIComponent(group)}`;
      });
      tileGallery.append(tile);
    });
    document.querySelectorAll('[data-gallery-scroll]').forEach(button => {
      button.addEventListener('click', () => {
        tileGallery.scrollBy({ left: Number(button.dataset.galleryScroll) * tileGallery.clientWidth * 0.8, behavior: 'smooth' });
      });
    });
  }

  if (!grid) return;

  const historicalExplorer = document.querySelector('#historical-election-explorer');
  let historicalPayloadPromise = null;
  let historicalChart = null;
  let historicalCompositionChart = null;
  let historicalExplorerInitialized = false;
  let historicalExplorerInitializing = false;
  const loadHistoricalExplorer = async () => {
    if (historicalExplorerInitialized || historicalExplorerInitializing) return;
    historicalExplorerInitializing = true;
    const status = document.querySelector('#history-status');
    const resultPanel = document.querySelector('#history-result');
    const typeSelect = document.querySelector('#history-type');
    const yearSelect = document.querySelector('#history-year');
    const stateSelect = document.querySelector('#history-state');
    const constituencySelect = document.querySelector('#history-constituency');
    if (!status || !resultPanel || !typeSelect || !yearSelect || !stateSelect || !constituencySelect) {
      historicalExplorerInitializing = false;
      return;
    }
    if (!historicalPayloadPromise) {
      historicalPayloadPromise = Promise.all([
        safeFetchJson('historical-elections.json', { observations: [] }),
        safeFetchJson('recent-indian-elections.json', { observations: [] })
      ]);
    }
    const [payload, recentPayload] = await historicalPayloadPromise;
    const archiveObservations = Array.isArray(payload?.observations) ? payload.observations : [];
    const recentObservations = Array.isArray(recentPayload?.observations)
      ? recentPayload.observations.map(row => ({
        ...row,
        source: recentPayload.source_files?.[row.source_file]?.url || '',
        vote_share_method: row.vote_share_percent === null ? null : recentPayload.vote_share_method,
        electors: null,
        result_status: row.result_status || 'reported'
      }))
      : [];
    const liveObservations = liveConstituencies.flatMap(record => {
      const year = record.year || Number(record.source.match(/(?:19|20)\d{2}/)?.[0]);
      if (!year) return [];
      return record.candidates.map(candidate => ({
        year,
        election_type: record.election_type,
        state_or_ut: record.state_or_ut,
        constituency_number: record.constituency_number || '',
        constituency: record.constituency,
        candidate: candidate.candidate,
        party: candidate.party,
        votes: candidate.votes,
        vote_share_percent: candidate.vote_share_percent,
        electors: null,
        source: record.source
      }));
    });
    const observationsByKey = new Map();
    [...recentObservations, ...archiveObservations, ...liveObservations].forEach(row => {
      const constituencyKey = row.election_type === 'Lok Sabha'
        ? row.constituency
        : row.constituency_number || row.constituency;
      const key = [
        row.year,
        row.election_type,
        row.state_or_ut.trim().toLowerCase(),
        String(constituencyKey).trim().toLowerCase(),
        row.candidate.trim().toLowerCase()
      ].join('|');
      observationsByKey.set(key, {
        ...observationsByKey.get(key),
        ...row,
        vote_share_method: row.vote_share_percent !== null && row.vote_share_percent !== undefined
          ? row.vote_share_method || null
          : observationsByKey.get(key)?.vote_share_method || null,
        vote_share_percent: row.vote_share_percent ?? observationsByKey.get(key)?.vote_share_percent ?? null,
        electors: row.electors ?? observationsByKey.get(key)?.electors ?? null
      });
    });
    const observations = [...observationsByKey.values()];
    if (!observations.length) {
      status.textContent = 'Historical ECI results could not be loaded. Try again later or open the official statistical-report archive.';
      resultPanel.hidden = true;
      historicalExplorerInitializing = false;
      return;
    }
    historicalExplorerInitialized = true;
    historicalExplorerInitializing = false;
    const years = [...new Set(observations.map(row => String(row.year)))].sort((a, b) => Number(b) - Number(a));
    const types = [...new Set(observations.map(row => row.election_type))].sort();
    const reportedYears = [...new Set(observations.map(row => row.year))].sort((a, b) => a - b);
    const reportedStates = new Set(observations.map(row => row.state_or_ut).filter(Boolean)).size;
    const liveLokSabhaSeats = liveConstituencies.filter(record => record.election_type === 'Lok Sabha by-election').length;
    const parliamentarySeats = new Set(recentObservations
      .filter(row => row.election_type === 'Lok Sabha')
      .map(row => `${row.state_or_ut}|${row.constituency}`)).size;
    const archiveCoverage = payload?.reports_with_candidate_results
      ? `${payload.reports_with_candidate_results} of ${payload.catalog_entries_scanned} ECI archive entries yielded parseable workbooks; ${payload.reports_without_supported_download} had no supported XLSX.`
      : 'Historical ECI workbook coverage remains partial.';
    status.textContent = `Election coverage: ${reportedYears[0]}–${reportedYears[reportedYears.length - 1]} · ${reportedStates} States/UTs · ${observations.length.toLocaleString('en-IN')} candidate results. The recent dataset includes ${parliamentarySeats} of 543 constituencies in the 2024 Lok Sabha election and State Assembly results from ${recentPayload?.assembly_election_years?.join(', ') || 'recent available years'}. ${liveLokSabhaSeats ? `The current ECI feed also includes ${liveLokSabhaSeats} Lok Sabha by-election constituency. ` : ''}Recent data source snapshot: ${recentPayload?.source_commit?.slice(0, 12) || 'unavailable'}. Vote shares calculated from listed candidate votes are marked with *; reported ECI shares are unmarked. ${archiveCoverage} Missing constituencies are not zero-vote results.`;

    const setOptions = (select, values, prompt) => {
      select.replaceChildren(new Option(prompt, ''));
      values.forEach(item => select.add(new Option(item.label, item.value)));
      select.disabled = values.length === 0;
    };
    const stateFor = () => {
      const type = typeSelect.value;
      const year = yearSelect.value;
      return [...new Set(observations
        .filter(row => row.election_type === type && String(row.year) === year && row.state_or_ut)
        .map(row => row.state_or_ut))].sort((a, b) => a.localeCompare(b));
    };
    const constituenciesFor = () => {
      const byId = new Map();
      observations
        .filter(row => row.election_type === typeSelect.value
          && String(row.year) === yearSelect.value
          && row.state_or_ut === stateSelect.value)
        .forEach(row => byId.set(`${row.constituency_number}|${row.constituency}`, row));
      return [...byId.entries()]
        .map(([value, row]) => ({ value, label: `${row.constituency_number ? `${row.constituency_number} · ` : ''}${row.constituency}` }))
        .sort((a, b) => a.label.localeCompare(b.label));
    };
    const renderResults = () => {
      const [number, constituency] = constituencySelect.value.split('|');
      const rows = observations
        .filter(row => row.election_type === typeSelect.value
          && String(row.year) === yearSelect.value
          && row.state_or_ut === stateSelect.value
          && row.constituency_number === number
          && row.constituency === constituency
          && row.candidate.trim().toLowerCase() !== 'total')
        .sort((a, b) => (b.votes || 0) - (a.votes || 0));
      if (!rows.length) {
        resultPanel.hidden = true;
        return;
      }
      resultPanel.hidden = false;
      const numberFormat = new Intl.NumberFormat('en-IN');
      const winner = rows[0];
      const runnerUp = rows[1];
      const electorate = rows.find(row => row.electors !== null)?.electors;
      const uncontested = rows.some(row => row.result_status === 'uncontested');
      const metrics = document.querySelector('#history-metrics');
      metrics.replaceChildren();
      [
        ['Candidates reported', numberFormat.format(rows.length)],
        ['Leading candidate votes', winner.votes === null ? 'Not reported (uncontested)' : numberFormat.format(winner.votes)],
        ['Lead over next candidate', uncontested ? 'Not applicable' : runnerUp && winner.votes !== null ? numberFormat.format(winner.votes - runnerUp.votes) : 'Not reported'],
        ['Electorate reported', electorate === undefined ? 'Not reported' : numberFormat.format(electorate)]
      ].forEach(([label, value]) => {
        const item = document.createElement('div');
        item.className = 'history-metric';
        const strong = document.createElement('strong');
        strong.textContent = value;
        const caption = document.createElement('span');
        caption.textContent = label;
        item.append(strong, caption);
        metrics.append(item);
      });
      const body = document.querySelector('#history-candidate-rows');
      body.replaceChildren();
      rows.forEach(row => {
        const tr = document.createElement('tr');
        [row.candidate, row.party || 'Not reported', row.votes === null ? 'Not reported (uncontested)' : numberFormat.format(row.votes),
          row.vote_share_percent === null ? 'Not reported' : `${row.vote_share_percent.toLocaleString('en-IN')}%${row.vote_share_method ? '*' : ''}`]
          .forEach(value => {
            const td = document.createElement('td');
            td.textContent = value;
            tr.append(td);
          });
        body.append(tr);
      });
      const sourceLink = document.querySelector('#history-source-link');
      sourceLink.href = winner.source;
      sourceLink.textContent = `Open source results for ${stateSelect.value} ↗`;
      historicalChart?.destroy();
      const canvas = document.querySelector('#history-vote-chart');
      historicalChart = new Chart(canvas, {
        type: 'bar',
        data: {
          labels: rows.slice(0, 12).map(row => row.candidate),
          datasets: [{
            label: 'Votes',
            data: rows.slice(0, 12).map(row => row.votes),
            backgroundColor: rows.slice(0, 12).map((_, index) => index === 0 ? '#ff9933' : '#58a6ff'),
            borderRadius: 5
          }]
        },
        options: {
          indexAxis: 'y',
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false }, title: { display: true, text: `${constituency} · ${stateSelect.value} · ${yearSelect.value}` } },
          scales: {
            x: { ticks: { callback: value => Number(value).toLocaleString('en-IN') } },
            y: { ticks: { autoSkip: false } }
          }
        }
      });
      historicalCompositionChart?.destroy();
      const leadingCandidates = rows.slice(0, 5);
      const otherVotes = rows.slice(5).reduce((total, row) => total + (row.votes || 0), 0);
      const compositionLabels = leadingCandidates.map(row => row.candidate);
      const compositionValues = leadingCandidates.map(row => row.votes || 0);
      if (otherVotes > 0) {
        compositionLabels.push('Other candidates');
        compositionValues.push(otherVotes);
      }
      const compositionOptions = chartOptions(' votes', false, false, 'doughnut');
      compositionOptions.plugins.title = {
        display: true,
        text: `${constituency} candidate vote composition · ${stateSelect.value} · ${yearSelect.value}`
      };
      const compositionCanvas = document.querySelector('#history-vote-composition-chart');
      compositionCanvas.closest('.history-chart-wrap').hidden = compositionValues.every(value => value === 0);
      if (!compositionCanvas.closest('.history-chart-wrap').hidden) {
        historicalCompositionChart = new Chart(compositionCanvas, {
          type: 'doughnut',
          data: {
            labels: compositionLabels,
            datasets: [{
              label: 'Votes',
              data: compositionValues,
              backgroundColor: ['#ff9933', '#3fb950', '#58a6ff', '#bc8cff', '#ff7b72', '#f6c344'],
              borderColor: CHART_THEME.sliceBorder,
              borderWidth: 2,
              hoverOffset: 8
            }]
          },
          options: compositionOptions
        });
      }
    };
    const refreshConstituencies = () => {
      setOptions(constituencySelect, constituenciesFor(), 'Select a constituency');
      resultPanel.hidden = true;
    };
    const refreshStates = () => {
      setOptions(stateSelect, stateFor().map(value => ({ value, label: value })), 'Select a State/UT');
      refreshConstituencies();
    };
    const refreshYears = () => {
      const matchingYears = years.filter(year => observations.some(row =>
        row.election_type === typeSelect.value && String(row.year) === year));
      setOptions(yearSelect, matchingYears.map(value => ({ value, label: value })), 'Select an election year');
      refreshStates();
    };
    setOptions(typeSelect, types.map(value => ({ value, label: value })), 'Select an election type');
    typeSelect.addEventListener('change', refreshYears);
    yearSelect.addEventListener('change', refreshStates);
    stateSelect.addEventListener('change', refreshConstituencies);
    constituencySelect.addEventListener('change', renderResults);
    if (types.includes('State Assembly')) typeSelect.value = 'State Assembly';
    else typeSelect.value = types[0];
    refreshYears();
    if (yearSelect.options.length > 1) yearSelect.selectedIndex = 1;
    refreshStates();
    if (stateSelect.options.length > 1) stateSelect.selectedIndex = 1;
    refreshConstituencies();
    if (constituencySelect.options.length > 1) {
      constituencySelect.selectedIndex = 1;
      renderResults();
    }
  };

  const updateCards = () => {
    const query = search.value.trim().toLowerCase();
    updateGroupHero();
    const stateFilter = filter ? filter.value : 'all';
    const hasSelectedScope = groupFilter.value !== 'all' || subgroupFilter.value !== 'all';
    if (historicalExplorer) {
      historicalExplorer.hidden = groupFilter.value !== 'Elections';
      if (!historicalExplorer.hidden) void loadHistoricalExplorer();
    }
    const pewLibrary = document.querySelector('#pew-report-library');
    if (pewLibrary) pewLibrary.hidden = groupFilter.value !== 'Pew Research';

    let visibleCount = 0;
    cards.forEach(card => {
      const cardCategory = card.dataset.category;
      const cardSubgroup = card.dataset.subgroup;
      const cardState = card.dataset.state;
      const cardTitle = card.dataset.title;
      const isSaved = savedChartKeys.has(card.dataset.key);

      const matchesGroup = (groupFilter.value === 'all' || cardCategory === groupFilter.value);
      const matchesSubgroup = (subgroupFilter.value === 'all' || cardSubgroup === subgroupFilter.value);
      const matchesState = (stateFilter === 'all' || cardState === stateFilter);
      const matchesSearch = (!query || cardTitle.includes(query));
      const matchesSaved = (!savedToggle?.getAttribute('aria-pressed') || savedToggle.getAttribute('aria-pressed') !== 'true' || isSaved);

      const isMatch = (hasSelectedScope && matchesGroup && matchesSubgroup && matchesState && matchesSearch && matchesSaved);
      card.hidden = !isMatch;
      if (isMatch) visibleCount++;
    });
    headings.forEach(heading => {
      heading.hidden = !cards.some(card => !card.hidden && card.dataset.category === heading.dataset.category);
    });
    subHeadings.forEach(subHeading => {
      subHeading.hidden = !cards.some(card => !card.hidden && card.dataset.subgroup === subHeading.dataset.subgroup);
    });

    let emptyMsg = grid.querySelector('.no-charts-message');
    if (visibleCount === 0) {
      if (!emptyMsg) {
        emptyMsg = document.createElement('div');
        emptyMsg.className = 'no-charts-message';
        grid.appendChild(emptyMsg);
      }
      emptyMsg.innerHTML = `<p style="color:var(--muted); text-align:center; padding:40px; font-size:1.05rem;">${hasSelectedScope ? 'No indicators match this selection. Try another group, subgroup, or search.' : 'Choose a group or subgroup above to explore its charts.'}</p>`;
      emptyMsg.hidden = false;
    } else if (emptyMsg) {
      emptyMsg.hidden = true;
    }
    if (resultCount) resultCount.textContent = hasSelectedScope ? `Showing ${visibleCount} of ${cards.length} indicators` : 'Select a group or subgroup to begin';
  };
  savedToggle?.addEventListener('click', () => {
    const pressed = savedToggle.getAttribute('aria-pressed') !== 'true';
    savedToggle.setAttribute('aria-pressed', String(pressed));
    savedToggle.classList.toggle('active', pressed);
    updateCards();
  });
  document.querySelector('#clear-filters')?.addEventListener('click', () => {
    groupFilter.value = 'all';
    subgroupFilter.value = 'all';
    if (filter) filter.value = 'all';
    search.value = '';
    savedToggle?.setAttribute('aria-pressed', 'false');
    savedToggle?.classList.remove('active');
    syncGroupPills('all');
    updateSubgroupFilter();
    updateCards();
  });
  if (filter) filter.addEventListener('change', updateCards);
  groupFilter.addEventListener('change', () => { 
    const grp = groupFilter.value;
    syncGroupPills(grp);
    if (categoryBgMap[grp]) setEraBackground(categoryBgMap[grp]);
    subgroupFilter.value = 'all';
    updateSubgroupFilter(); 
    updateGroupHero();
    updateCards(); 
  });
  subgroupFilter.addEventListener('change', () => { 
    if (subgroupGroups[subgroupFilter.value]) {
      groupFilter.value = subgroupGroups[subgroupFilter.value]; 
      syncGroupPills(groupFilter.value);
      if (categoryBgMap[groupFilter.value]) setEraBackground(categoryBgMap[groupFilter.value]);
    }
    updateSubgroupFilter(); 
    updateGroupHero(); 
    updateCards(); 
  });
  search.addEventListener('input', updateCards);
  // Force form controls to default state on startup so browser autocomplete desync is avoided
  if (groupFilter) groupFilter.value = 'all';
  if (subgroupFilter) subgroupFilter.value = 'all';
  if (search) search.value = '';
  if (filter) filter.value = 'all';
  syncGroupPills('all');
  updateSubgroupFilter();
  updateCards();

  // Deep links such as explore.html?group=Economic&subgroup=...&q=gdp, kept in sync as filters change.
  const hasOption = (select, value) => [...select.options].some(option => option.value === value);
  const params = new URLSearchParams(window.location.search);
  const startGroup = params.get('group');
  if (startGroup && hasOption(groupFilter, startGroup)) {
    groupFilter.value = startGroup;
    groupFilter.dispatchEvent(new Event('change'));
  }
  const startSubgroup = params.get('subgroup');
  if (startSubgroup && hasOption(subgroupFilter, startSubgroup)) {
    subgroupFilter.value = startSubgroup;
    subgroupFilter.dispatchEvent(new Event('change'));
  }
  if (params.get('q')) {
    search.value = params.get('q');
    search.dispatchEvent(new Event('input'));
  }
  const syncUrl = () => {
    const next = new URLSearchParams();
    if (groupFilter.value !== 'all') next.set('group', groupFilter.value);
    if (subgroupFilter.value !== 'all') next.set('subgroup', subgroupFilter.value);
    if (search.value.trim()) next.set('q', search.value.trim());
    const query = next.toString();
    history.replaceState(null, '', `${window.location.pathname}${query ? `?${query}` : ''}${window.location.hash}`);
  };
  [groupFilter, subgroupFilter].forEach(select => select.addEventListener('change', syncUrl));
  search.addEventListener('input', syncUrl);
}

main().catch(error => {
  const chartGrid = document.querySelector('#charts');
  if (chartGrid) chartGrid.innerHTML = `<p>Dashboard data could not be loaded: ${error.message}</p>`;
});


function openIndicatorModal(key, title, subtitle, frequency, suffix, source, details, series, category, subgroup) {
  const modal = document.querySelector('#indicator-modal');
  const body = document.querySelector('#modal-body');
  if (!modal || !body) return;
  const closeButton = modal.querySelector('#modal-close');

  const labels = series?.labels || [];
  const values = series?.values || [];
  const datasets = series?.datasets || [];
  const paragraphs = details.split('\n\n').map(p => `<p style="margin-bottom:12px; line-height:1.6; color:var(--muted);">${p}</p>`).join('');

  let tableRows = '';
  let statsHtml = '';

  if (values && values.length > 0) {
    const numValues = values.filter(v => v !== null && v !== undefined && !isNaN(v));
    const maxVal = numValues.length ? Math.max(...numValues) : 0;
    const minVal = numValues.length ? Math.min(...numValues) : 0;
    const maxYear = numValues.length ? (labels[values.indexOf(maxVal)] || 'N/A') : 'N/A';
    const minYear = numValues.length ? (labels[values.indexOf(minVal)] || 'N/A') : 'N/A';
    const sum = numValues.reduce((a, b) => a + b, 0);
    const avg = numValues.length ? (sum / numValues.length).toFixed(2) : 'N/A';
    const latestVal = numValues.length ? numValues[numValues.length - 1] : 0;

    statsHtml = `
      <div class="modal-stat-grid">
        <div class="modal-stat-card"><label>Latest Value</label><strong>${formatMagnitude(latestVal, suffix)}</strong></div>
        <div class="modal-stat-card"><label>All-Time Peak</label><strong>${formatMagnitude(maxVal, suffix)} (${maxYear})</strong></div>
        <div class="modal-stat-card"><label>All-Time Lowest</label><strong>${formatMagnitude(minVal, suffix)} (${minYear})</strong></div>
        <div class="modal-stat-card"><label>Series Average</label><strong>${formatMagnitude(avg, suffix)}</strong></div>
        <div class="modal-stat-card"><label>Observations</label><strong>${numValues.length} ${frequency.toLowerCase()}</strong></div>
      </div>
    `;

    tableRows = labels.map((lbl, idx) => {
      const val = values[idx];
      const valStr = val !== null && val !== undefined ? formatMagnitude(val, suffix) : 'N/A';
      let yoyStr = 'N/A';
      if (idx > 0 && values[idx - 1] !== null && values[idx - 1] !== 0 && val !== null && val !== undefined) {
        const pct = ((val - values[idx - 1]) / Math.abs(values[idx - 1])) * 100;
        yoyStr = `${pct >= 0 ? '+' : ''}${pct.toFixed(1)}%`;
      }
      const isPeak = val === maxVal ? ' 🏆 (Peak)' : '';
      return `<tr><td><strong>${lbl}</strong></td><td>${valStr}${isPeak}</td><td>${yoyStr}</td></tr>`;
    }).reverse().join('');

  } else if (datasets && datasets.length > 0) {
    statsHtml = `
      <div class="modal-stat-grid">
        <div class="modal-stat-card"><label>Comparison Engines</label><strong>${datasets.length} Series</strong></div>
        <div class="modal-stat-card"><label>Data Index</label><strong>Normalized Base 100</strong></div>
        <div class="modal-stat-card"><label>Total Dateline</label><strong>${labels.length} Observations</strong></div>
      </div>
    `;

    tableRows = labels.map((lbl, idx) => {
      const rowVals = datasets.map(d => `<strong>${d.label}:</strong> ${d.values[idx] !== null && d.values[idx] !== undefined ? d.values[idx] : 'N/A'}`).join('<br>');
      return `<tr><td><strong>${lbl}</strong></td><td colspan="2">${rowVals}</td></tr>`;
    }).reverse().join('');
  }

  body.innerHTML = `
    <div class="modal-header">
      <h2 id="modal-title">${title}</h2>
      <p>${subtitle}</p>
      <div class="modal-badges">
        <span class="hero-badge saffron">${category}</span>
        <span class="hero-badge green">${subgroup}</span>
        <span class="hero-badge blue">${frequency}</span>
      </div>
    </div>
    ${statsHtml}
    <h3 class="modal-section-title">📖 Indicator Overview &amp; Detailed Analysis</h3>
    <div class="modal-text">${paragraphs}</div>
    <p style="margin-top: 16px;"><strong>Official Source Provenance:</strong> <a href="${source}" target="_blank" rel="noreferrer">${series?.source || source} ↗</a></p>
    <h3 class="modal-section-title">📊 Complete Historical Observations Table</h3>
    <div class="modal-table-wrap">
      <table class="modal-table">
        <thead>
          <tr><th>Period / Year</th><th>Observed Value</th><th>YoY Growth</th></tr>
        </thead>
        <tbody>
          ${tableRows}
        </tbody>
      </table>
    </div>
  `;

  modal.hidden = false;
  closeButton?.focus();
}

const modalCloseBtn = document.querySelector('#modal-close');
const modalOverlay = document.querySelector('#indicator-modal');
if (modalCloseBtn && modalOverlay) {
  modalCloseBtn.addEventListener('click', () => { modalOverlay.hidden = true; });
  modalOverlay.addEventListener('click', (e) => {
    if (e.target === modalOverlay) modalOverlay.hidden = true;
  });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && !modalOverlay.hidden) modalOverlay.hidden = true;
  });
}
