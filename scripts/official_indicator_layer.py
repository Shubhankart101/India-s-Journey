"""Self-describing World Bank (official national statistics) indicators and composition pies.

Every series carries ``meta`` so the dashboard registers it without a hand-written definition.
"""
from __future__ import annotations

from typing import Callable

WB_URL = "https://api.worldbank.org/v2/country/IND/indicator/{code}?format=json&per_page=100"

# key, World Bank code, title, subtitle, category, subgroup, color, suffix
LINE_INDICATORS = (
    ("wb_lending_rate", "FR.INR.LEND", "Bank Lending Interest Rate", "Average commercial-bank lending rate", "Economic", "Monetary Policy", "#58a6ff", "%"),
    ("wb_real_interest_rate", "FR.INR.RINR", "Real Interest Rate", "Lending rate adjusted for GDP-deflator inflation", "Economic", "Monetary Policy", "#bc8cff", "%"),
    ("wb_agriculture_growth", "NV.AGR.TOTL.KD.ZG", "Agriculture Value-Added Growth", "Real annual growth of agriculture, forestry and fishing", "Economic", "Production & Commodities", "#3fb950", "%"),
    ("wb_services_growth", "NV.SRV.TOTL.KD.ZG", "Services Value-Added Growth", "Real annual growth of services", "Economic", "Production & Commodities", "#58a6ff", "%"),
    ("wb_manufacturing_growth", "NV.IND.MANF.KD.ZG", "Manufacturing Value-Added Growth", "Real annual growth of manufacturing", "Industry Trends & Performance", "Manufacturing & Industrial Growth", "#ff9933", "%"),
    ("wb_high_tech_exports", "TX.VAL.TECH.MF.ZS", "High-Technology Exports", "High-tech share of manufactured exports", "Industry Trends & Performance", "Manufacturing & Industrial Growth", "#a371f7", "%"),
    ("wb_journal_articles", "IP.JRN.ARTC.SC", "Scientific & Technical Journal Articles", "Peer-reviewed articles published by India-based authors", "Economic", "Media & Publications", "#f778ba", " articles"),
    ("wb_resident_patents", "IP.PAT.RESD", "Resident Patent Applications", "Patent applications filed by Indian residents", "Economic", "Media & Publications", "#e3b341", " applications"),
    ("wb_secure_servers", "IT.NET.SECR.P6", "Secure Internet Servers", "Secure internet servers per million people", "Economic", "Media & Publications", "#79c0ff", " per million"),
    ("wb_atms_per_100k", "FB.ATM.TOTL.P5", "ATMs per 100,000 Adults", "Automated teller machine density", "Payments & Digital Banking", "Digital Financial Index", "#ff9933", " per 100k adults"),
    ("wb_bank_branches_per_100k", "FB.CBK.BRCH.P5", "Bank Branches per 100,000 Adults", "Commercial-bank branch density", "Payments & Digital Banking", "Digital Financial Index", "#3fb950", " per 100k adults"),
    ("wb_account_ownership", "FX.OWN.TOTL.ZS", "Account Ownership (Global Findex)", "Adults with an account at a financial institution or mobile-money provider", "Payments & Digital Banking", "Digital Financial Index", "#58a6ff", "%"),
    ("wb_rural_electricity_access", "EG.ELC.ACCS.RU.ZS", "Rural Electricity Access (All-India)", "Rural population with access to electricity", "State Performance & Regional Health", "State Infrastructure & Services", "#f6c344", "%"),
    ("wb_basic_sanitation", "SH.STA.BASS.ZS", "Basic Sanitation Coverage (All-India)", "Population using at least basic sanitation services", "State Performance & Regional Health", "State Infrastructure & Services", "#39c5bb", "%"),
    ("wb_rural_basic_water", "SH.H2O.BASW.RU.ZS", "Rural Basic Drinking Water (All-India)", "Rural population using at least basic drinking-water services", "State Performance & Regional Health", "State Infrastructure & Services", "#58a6ff", "%"),
    ("wb_infant_mortality", "SP.DYN.IMRT.IN", "Infant Mortality Rate", "Deaths before age one per 1,000 live births", "Public Health & Epidemiology", "Mortality & Lifespan Milestones", "#ff7b72", " per 1,000"),
    ("wb_neonatal_mortality", "SH.DYN.NMRT", "Neonatal Mortality Rate", "Deaths in the first 28 days per 1,000 live births", "Public Health & Epidemiology", "Mortality & Lifespan Milestones", "#f778ba", " per 1,000"),
    ("wb_maternal_mortality", "SH.STA.MMRT", "Maternal Mortality Ratio", "Modeled maternal deaths per 100,000 live births", "Public Health & Epidemiology", "Mortality & Lifespan Milestones", "#d2a8ff", " per 100k births"),
    ("wb_tb_incidence", "SH.TBS.INCD", "Tuberculosis Incidence", "New and relapse TB cases per 100,000 people", "Public Health & Epidemiology", "Disease Burden & Epidemiology", "#ffa657", " per 100k"),
    ("wb_hospital_beds", "SH.MED.BEDS.ZS", "Hospital Beds", "Hospital beds per 1,000 people", "Public Health & Epidemiology", "Health Infrastructure & Spending", "#79c0ff", " per 1,000"),
    ("wb_dpt_immunization", "SH.IMM.IDPT", "DPT Immunization", "Children aged 12-23 months immunized against DPT", "Public Health & Epidemiology", "Health Infrastructure & Spending", "#3fb950", "%"),
    ("wb_armed_forces_personnel", "MS.MIL.TOTL.P1", "Armed Forces Personnel", "Active-duty military personnel including paramilitary", "Defence & Strategic", "Strategic Stockpiles & Capabilities", "#ff7b72", " personnel"),
    ("wb_arms_imports_tiv", "MS.MIL.MPRT.KD", "Arms Imports (SIPRI TIV)", "Major conventional arms imports, SIPRI trend-indicator values", "Defence & Strategic", "Strategic Stockpiles & Capabilities", "#ffa657", " TIV"),
    ("wb_arms_exports_tiv", "MS.MIL.XPRT.KD", "Arms Exports (SIPRI TIV)", "Major conventional arms exports, SIPRI trend-indicator values", "Defence & Strategic", "Defence Exports & Production", "#3fb950", " TIV"),
    ("wb_tourism_expenditure", "ST.INT.XPND.CD", "Outbound Tourism Expenditure", "International tourism expenditure in current US dollars", "Tourism & Heritage", "International Visitor Trends", "#58a6ff", " USD"),
    ("wb_tourism_receipts_export_share", "ST.INT.RCPT.XP.ZS", "Tourism Receipts Share of Exports", "International tourism receipts as a share of total exports", "Tourism & Heritage", "International Visitor Trends", "#ff9933", "%"),
    ("wb_mineral_rents", "NY.GDP.MINR.RT.ZS", "Mineral Rents", "Mineral rents as a share of GDP", "Mining & Natural Resources", "Metallic Minerals & Ores", "#e3b341", "% GDP"),
    ("wb_fossil_fuel_share", "EG.USE.COMM.FO.ZS", "Fossil-Fuel Energy Consumption", "Fossil fuels as a share of total energy consumption", "Mining & Natural Resources", "Energy Minerals & Fuel", "#8b949e", "%"),
    ("wb_gini_index", "SI.POV.GINI", "Gini Index", "Consumption inequality (0 = perfect equality)", "Social", "Welfare", "#bc8cff", ""),
    ("wb_dependency_ratio", "SP.POP.DPND", "Age Dependency Ratio", "Dependants (under 15 and 65+) per 100 working-age people", "Social", "Demographics", "#79c0ff", ""),
    ("wb_poverty_extreme", "SI.POV.DDAY", "Extreme Poverty Headcount", "Population below the World Bank international extreme-poverty line (line value is revised by the Bank over time)", "Social", "Welfare", "#ff7b72", "%"),
    ("wb_poverty_lower_middle", "SI.POV.LMIC", "Lower-Middle-Income Poverty Headcount", "Population below the lower-middle-income-country poverty line", "Social", "Welfare", "#ffa657", "%"),
    ("wb_poverty_upper_middle", "SI.POV.UMIC", "Upper-Middle-Income Poverty Headcount", "Population below the upper-middle-income-country poverty line", "Social", "Welfare", "#e3b341", "%"),
    ("wb_female_labor_share", "SL.TLF.TOTL.FE.ZS", "Women's Share of the Labour Force", "Female labour force as a share of the total labour force", "Social", "Welfare", "#f778ba", "%"),
    ("wb_primary_completion", "SE.PRM.CMPT.ZS", "Primary Completion Rate", "Children completing the last year of primary school", "Social", "Welfare", "#3fb950", "%"),
    ("wb_net_migration", "SM.POP.NETM", "Net Migration", "Net migrants (immigrants minus emigrants) over five-year periods", "Social", "Demographics", "#79c0ff", " people"),
    ("wb_internet_users", "IT.NET.USER.ZS", "Internet Users", "Individuals using the internet as a share of the population", "Payments & Digital Banking", "Digital Financial Index", "#58a6ff", "%"),
    ("wb_ict_goods_exports", "TX.VAL.ICTG.ZS.UN", "ICT Goods Exports", "ICT goods as a share of total merchandise exports", "Industry Trends & Performance", "Manufacturing & Industrial Growth", "#bc8cff", "%"),
    ("wb_ict_goods_imports", "TM.VAL.ICTG.ZS.UN", "ICT Goods Imports", "ICT goods as a share of total merchandise imports", "Economic", "Trade & External", "#79c0ff", "%"),
    ("wb_military_gdp", "MS.MIL.XPND.GD.ZS", "Military Expenditure (% of GDP)", "Military spending as a share of GDP (SIPRI)", "Defence & Strategic", "Defence Budget & Modernization", "#ff7b72", "% GDP"),
    ("wb_military_govt", "MS.MIL.XPND.ZS", "Military Share of Government Expenditure", "Military spending as a share of general government expenditure (SIPRI)", "Defence & Strategic", "Defence Budget & Modernization", "#ffa657", "%"),
    ("wb_road_deaths", "SH.STA.TRAF.P5", "Road Traffic Death Rate", "Road-traffic deaths per 100,000 people (WHO)", "Crime & Security", "Violence & Crime", "#ff7b72", " per 100k"),
    ("wb_suicide_rate", "SH.STA.SUIC.P5", "Suicide Mortality Rate", "Suicide deaths per 100,000 people (WHO)", "Crime & Security", "Violence & Crime", "#d2a8ff", " per 100k"),
    ("wb_smoking", "SH.PRV.SMOK", "Smoking Prevalence", "Adults who smoke (WHO age-standardised)", "Public Health & Epidemiology", "Disease Burden & Epidemiology", "#8b949e", "%"),
    ("wb_malaria_incidence", "SH.MLR.INCD.P3", "Malaria Incidence", "Malaria cases per 1,000 people at risk", "Public Health & Epidemiology", "Disease Burden & Epidemiology", "#ffa657", " per 1,000"),
    ("wb_government_health_share", "SH.XPD.GHED.GE.ZS", "Health in Government Expenditure", "Domestic general government health expenditure as a share of total government spending", "Public Health & Epidemiology", "Health Infrastructure & Spending", "#3fb950", "%"),
    ("wb_renewable_final_energy", "EG.FEC.RNEW.ZS", "Renewables in Final Energy Consumption", "Renewable energy as a share of total final energy consumption", "Mining & Natural Resources", "Energy Minerals & Fuel", "#56d364", "%"),
    ("wb_protected_land", "ER.LND.PTLD.ZS", "Terrestrial Protected Areas", "Protected land as a share of total land area", "Mining & Natural Resources", "Non-Metallic & Industrial Minerals", "#3fb950", "%"),
    ("wb_total_resource_rents", "NY.GDP.TOTL.RT.ZS", "Total Natural Resource Rents", "Oil, gas, coal, mineral and forest rents as a share of GDP", "Mining & Natural Resources", "Metallic Minerals & Ores", "#ff9933", "% GDP"),
    ("wb_coal_rents", "NY.GDP.COAL.RT.ZS", "Coal Rents", "Coal rents (hard and soft coal) as a share of GDP", "Mining & Natural Resources", "Energy Minerals & Fuel", "#8b949e", "% GDP"),
    ("wb_oil_rents", "NY.GDP.PETR.RT.ZS", "Oil Rents", "Crude oil rents as a share of GDP", "Mining & Natural Resources", "Energy Minerals & Fuel", "#bc8cff", "% GDP"),
    ("wb_natural_gas_rents", "NY.GDP.NGAS.RT.ZS", "Natural Gas Rents", "Natural gas rents as a share of GDP", "Mining & Natural Resources", "Energy Minerals & Fuel", "#58a6ff", "% GDP"),
    ("wb_mineral_depletion", "NY.ADJ.DMIN.GN.ZS", "Mineral Depletion", "Value of mineral stocks extracted, as a share of GNI", "Mining & Natural Resources", "Metallic Minerals & Ores", "#d29922", "% GNI"),
    ("wb_energy_depletion", "NY.ADJ.DNGY.GN.ZS", "Energy Depletion", "Value of coal, oil and gas stocks extracted, as a share of GNI", "Mining & Natural Resources", "Energy Minerals & Fuel", "#ff7b72", "% GNI"),
    ("wb_ores_metals_exports", "TX.VAL.MMTL.ZS.UN", "Ores & Metals Exports", "Ores and metals as a share of merchandise exports", "Mining & Natural Resources", "Mineral Exports & Trade", "#e3b341", "%"),
    ("wb_ores_metals_imports", "TM.VAL.MMTL.ZS.UN", "Ores & Metals Imports", "Ores and metals as a share of merchandise imports", "Mining & Natural Resources", "Mineral Exports & Trade", "#ffa657", "%"),
    ("wb_fuel_exports", "TX.VAL.FUEL.ZS.UN", "Fuel Exports", "Fuels as a share of merchandise exports", "Mining & Natural Resources", "Mineral Exports & Trade", "#3fb950", "%"),
    ("wb_fuel_imports", "TM.VAL.FUEL.ZS.UN", "Fuel Imports", "Fuels as a share of merchandise imports", "Mining & Natural Resources", "Mineral Exports & Trade", "#ff7b72", "%"),
)

# key, title, subtitle, category, subgroup, unit, parts[(label, code)], residual label or None
COMPOSITIONS = (
    ("wb_exports_composition", "Merchandise Exports by Product Group", "Share of merchandise exports", "Economic", "Trade & External", "%",
     (("Manufactures", "TX.VAL.MANF.ZS.UN"), ("Fuels", "TX.VAL.FUEL.ZS.UN"), ("Food", "TX.VAL.FOOD.ZS.UN"),
      ("Agricultural raw materials", "TX.VAL.AGRI.ZS.UN"), ("Ores & metals", "TX.VAL.MMTL.ZS.UN")), "Other / unclassified"),
    ("wb_imports_composition", "Merchandise Imports by Product Group", "Share of merchandise imports", "Economic", "Trade & External", "%",
     (("Manufactures", "TM.VAL.MANF.ZS.UN"), ("Fuels", "TM.VAL.FUEL.ZS.UN"), ("Food", "TM.VAL.FOOD.ZS.UN"),
      ("Agricultural raw materials", "TM.VAL.AGRI.ZS.UN"), ("Ores & metals", "TM.VAL.MMTL.ZS.UN")), "Other / unclassified"),
    ("wb_tax_revenue_mix", "Central Government Revenue Mix", "Share of central government revenue", "Economic", "Fiscal & Union Budget", "%",
     (("Taxes on income & profits", "GC.TAX.YPKG.RV.ZS"), ("Taxes on goods & services", "GC.TAX.GSRV.RV.ZS"),
      ("Taxes on international trade", "GC.TAX.INTT.RV.ZS"), ("Other taxes", "GC.TAX.OTHR.RV.ZS")), "Non-tax revenue & grants"),
    ("wb_employment_by_sector", "Employment by Sector", "Share of total employment", "Industry Trends & Performance", "Production & Commodities", "%",
     (("Agriculture", "SL.AGR.EMPL.ZS"), ("Industry", "SL.IND.EMPL.ZS"), ("Services", "SL.SRV.EMPL.ZS")), None),
    ("wb_population_age_structure", "Population by Age Group", "Share of total population", "Social", "Demographics", "%",
     (("Ages 0-14", "SP.POP.0014.TO.ZS"), ("Ages 15-64", "SP.POP.1564.TO.ZS"), ("Ages 65+", "SP.POP.65UP.TO.ZS")), None),
    ("wb_urban_rural_population", "Urban vs Rural Population", "Share of total population", "Social", "Demographics", "%",
     (("Urban", "SP.URB.TOTL.IN.ZS"), ("Rural", "SP.RUR.TOTL.ZS")), None),
    ("wb_employment_status", "Wage Workers vs Self-Employed", "Share of total employment", "Social", "Welfare", "%",
     (("Wage & salaried workers", "SL.EMP.WORK.ZS"), ("Self-employed", "SL.EMP.SELF.ZS")), None),
    ("wb_income_quintile_shares", "Consumption Share by Quintile", "Share of consumption held by each fifth of the population", "Social", "Welfare", "%",
     (("Poorest 20%", "SI.DST.FRST.20"), ("Second 20%", "SI.DST.02ND.20"), ("Middle 20%", "SI.DST.03RD.20"),
      ("Fourth 20%", "SI.DST.04TH.20"), ("Richest 20%", "SI.DST.05TH.20")), None),
    ("wb_health_financing_mix", "Who Pays for Health Care", "Share of current health expenditure", "Public Health & Epidemiology", "Health Infrastructure & Spending", "%",
     (("Government", "SH.XPD.GHED.CH.ZS"), ("Private (incl. out-of-pocket)", "SH.XPD.PVTD.CH.ZS"), ("External aid", "SH.XPD.EHEX.CH.ZS")), "Unallocated"),
    ("wb_electricity_generation_mix", "Electricity Generation by Source", "Share of electricity production", "Mining & Natural Resources", "Energy Minerals & Fuel", "%",
     (("Coal", "EG.ELC.COAL.ZS"), ("Hydro", "EG.ELC.HYRO.ZS"), ("Natural gas", "EG.ELC.NGAS.ZS"), ("Nuclear", "EG.ELC.NUCL.ZS"),
      ("Oil", "EG.ELC.PETR.ZS"), ("Renewables excl. hydro", "EG.ELC.RNWX.ZS")), "Other sources"),
    ("wb_natural_resource_rents_mix", "Natural Resource Rents by Type", "Composition of total natural-resource rents (each part in % of GDP)", "Mining & Natural Resources", "Metallic Minerals & Ores", "% GDP",
     (("Coal", "NY.GDP.COAL.RT.ZS"), ("Minerals", "NY.GDP.MINR.RT.ZS"), ("Natural gas", "NY.GDP.NGAS.RT.ZS"),
      ("Oil", "NY.GDP.PETR.RT.ZS"), ("Forests", "NY.GDP.FRST.RT.ZS")), None),
    ("wb_land_use_mix", "Land Use", "Share of land area", "Mining & Natural Resources", "Non-Metallic & Industrial Minerals", "%",
     (("Agricultural land", "AG.LND.AGRI.ZS"), ("Forest", "AG.LND.FRST.ZS")), "Other land"),
    ("wb_tourism_receipts_mix", "Tourism Receipts by Type", "International tourism receipts, current US dollars", "Tourism & Heritage", "International Visitor Trends", " USD",
     (("Travel items", "ST.INT.TVLR.CD"), ("Passenger transport", "ST.INT.TRNR.CD")), None),
    ("wb_female_employment_sector", "Women's Employment by Sector", "Share of female employment", "Industry Trends & Performance", "Production & Commodities", "%",
     (("Agriculture", "SL.AGR.EMPL.FE.ZS"), ("Industry", "SL.IND.EMPL.FE.ZS"), ("Services", "SL.SRV.EMPL.FE.ZS")), None),
    ("wb_male_employment_sector", "Men's Employment by Sector", "Share of male employment", "Industry Trends & Performance", "Production & Commodities", "%",
     (("Agriculture", "SL.AGR.EMPL.MA.ZS"), ("Industry", "SL.IND.EMPL.MA.ZS"), ("Services", "SL.SRV.EMPL.MA.ZS")), None),
    ("wb_gdp_expenditure_mix", "GDP by Expenditure", "Share of GDP", "Economic", "Macroeconomics", "%",
     (("Household consumption", "NE.CON.PRVT.ZS"), ("Government consumption", "NE.CON.GOVT.ZS"), ("Gross fixed capital formation", "NE.GDI.FTOT.ZS")), "Net exports & inventories"),
    ("wb_services_exports_mix", "Commercial Services Exports by Type", "Share of commercial service exports", "Economic", "Trade & External", "%",
     (("Travel", "BX.GSR.TRVL.ZS"), ("Transport", "BX.GSR.TRAN.ZS"), ("Insurance & financial", "BX.GSR.INSF.ZS"),
      ("Communications, computer & ICT", "BX.GSR.CMCP.ZS")), "Other business services"),
    ("wb_services_imports_mix", "Commercial Services Imports by Type", "Share of commercial service imports", "Economic", "Trade & External", "%",
     (("Travel", "BM.GSR.TRVL.ZS"), ("Insurance & financial", "BM.GSR.INSF.ZS"), ("Communications, computer & ICT", "BM.GSR.CMCP.ZS")), "Transport & other services"),
    ("wb_government_expense_mix", "Central Government Expense by Type", "Share of central government expense", "Economic", "Fiscal & Union Budget", "%",
     (("Compensation of employees", "GC.XPN.COMP.ZS"), ("Interest payments", "GC.XPN.INTP.ZS"), ("Goods & services", "GC.XPN.GSRV.ZS"),
      ("Subsidies, grants & social benefits", "GC.XPN.TRFT.ZS")), "Other expense"),
    ("wb_external_debt_mix", "External Debt by Maturity and Creditor", "Total external debt stocks, current US dollars", "Economic", "Trade & External", " USD",
     (("Long-term debt", "DT.DOD.DLXF.CD"), ("Short-term debt", "DT.DOD.DSTC.CD"), ("Use of IMF credit", "DT.DOD.DIMF.CD")), None),
    ("wb_gender_population", "Population by Sex", "Share of total population", "Social", "Demographics", "%",
     (("Female", "SP.POP.TOTL.FE.ZS"), ("Male", "SP.POP.TOTL.MA.ZS")), None),
    ("wb_labour_force_status", "Employed vs Unemployed", "Share of the labour force (modelled ILO estimate)", "Social", "Welfare", "%",
     (("Unemployed", "SL.UEM.TOTL.ZS"),), "Employed"),
    ("wb_water_service_level", "Drinking-Water Service Level", "Share of population (JMP)", "State Performance & Regional Health", "State Infrastructure & Services", "%",
     (("Safely managed", "SH.H2O.SMDW.ZS"),), "Basic, limited or unimproved"),
    ("wb_sanitation_service_level", "Sanitation Service Level", "Share of population (JMP)", "State Performance & Regional Health", "State Infrastructure & Services", "%",
     (("Safely managed", "SH.STA.SMSS.ZS"), ("Open defecation", "SH.STA.ODFC.ZS")), "Basic or limited"),
    ("wb_causes_of_death", "Causes of Death", "Share of total deaths (WHO)", "Public Health & Epidemiology", "Disease Burden & Epidemiology", "%",
     (("Communicable, maternal & nutritional", "SH.DTH.COMM.ZS"), ("Non-communicable", "SH.DTH.NCOM.ZS"), ("Injuries", "SH.DTH.INJR.ZS")), None),
    ("wb_health_spending_split", "Out-of-Pocket vs Government Health Spending", "Share of current health expenditure", "Public Health & Epidemiology", "Health Infrastructure & Spending", "%",
     (("Out-of-pocket", "SH.XPD.OOPC.CH.ZS"), ("Government", "SH.XPD.GHED.CH.ZS")), "Other prepaid private & external"),
    ("wb_freshwater_withdrawals", "Freshwater Withdrawals by Sector", "Share of total freshwater withdrawals (FAO AQUASTAT)", "Mining & Natural Resources", "Non-Metallic & Industrial Minerals", "%",
     (("Agriculture", "ER.H2O.FWAG.ZS"), ("Industry", "ER.H2O.FWIN.ZS")), "Domestic use"),
    ("wb_military_budget_share", "Military Share of Government Spending", "Share of general government expenditure (SIPRI)", "Defence & Strategic", "Defence Budget & Modernization", "%",
     (("Military", "MS.MIL.XPND.ZS"),), "All other government spending"),
    ("wb_manufacturing_value_added_mix", "Manufacturing Value Added by Industry", "Share of manufacturing value added (UNIDO)", "Industry Trends & Performance", "Food Processing & Consumer Goods", "%",
     (("Food, beverages & tobacco", "NV.MNF.FBTO.ZS.UN"), ("Machinery & transport equipment", "NV.MNF.MTRN.ZS.UN"),
      ("Chemicals", "NV.MNF.CHEM.ZS.UN"), ("Textiles & clothing", "NV.MNF.TXTL.ZS.UN")), "Other manufacturing (incl. metals)"),
    ("wb_manufacturing_tech_intensity", "Manufacturing by Technology Intensity", "Medium- and high-tech share of manufacturing value added (UNIDO)", "Industry Trends & Performance", "Heavy Industry & Metals", "%",
     (("Medium & high-tech industry", "NV.MNF.TECH.ZS.UN"),), "Low-tech & resource-based industry"),
)


def _observations(get_json: Callable[[str], object], code: str) -> dict[str, float]:
    payload = get_json(WB_URL.format(code=code))
    if not isinstance(payload, list) or len(payload) < 2 or not payload[1]:
        raise ValueError(f"World Bank returned no observations for {code}")
    return {row["date"]: float(row["value"]) for row in payload[1] if row.get("value") is not None}


def _meta(title: str, subtitle: str, category: str, subgroup: str, color: str, suffix: str) -> dict:
    return {"title": title, "subtitle": subtitle, "frequency": "Annual", "color": color,
            "suffix": suffix, "category": category, "subgroup": subgroup}


def build_official_layer(get_json: Callable[[str], object], previous: dict[str, dict]) -> dict[str, dict]:
    cache: dict[str, dict[str, float]] = {}

    def fetch(code: str) -> dict[str, float]:
        if code not in cache:
            for attempt in range(3):
                try:
                    cache[code] = _observations(get_json, code)
                    break
                except ValueError:
                    raise  # no data is a definitive answer, not a transient failure
                except Exception:
                    if attempt == 2:
                        raise
        return cache[code]

    series: dict[str, dict] = {}
    for key, code, title, subtitle, category, subgroup, color, suffix in LINE_INDICATORS:
        try:
            observed = fetch(code)
            if not observed:
                raise ValueError(f"No numeric observations for {code}")
            years = sorted(observed, key=int)
            series[key] = {
                "labels": years,
                "values": [observed[year] for year in years],
                "source": f"World Bank API {code}",
                "unit": suffix.strip(),
                "note": f"{subtitle}. Official national statistics compiled by the World Bank (indicator {code}); gaps reflect years without a reported value.",
                "meta": _meta(title, subtitle, category, subgroup, color, suffix),
            }
        except Exception:  # keep the last good series when the API is unavailable
            if previous.get(key, {}).get("values"):
                series[key] = previous[key]

    for key, title, subtitle, category, subgroup, unit, parts, residual in COMPOSITIONS:
        try:
            observed = [fetch(code) for _, code in parts]
            common = set.intersection(*(set(item) for item in observed))
            if not common:
                raise ValueError(f"No common year for {key}")
            year = max(common, key=int)
            labels = [label for label, _ in parts]
            values = [round(item[year], 2) for item in observed]
            if residual and unit == "%" and 100 - sum(values) > 0.5:
                labels.append(residual)
                values.append(round(100 - sum(values), 2))
            points = [(label, value) for label, value in zip(labels, values) if value > 0]
            if len(points) < 2:
                raise ValueError(f"Too few positive parts for {key}")
            codes = ", ".join(code for _, code in parts)
            series[key] = {
                "labels": [label for label, _ in points],
                "values": [value for _, value in points],
                "chartType": "doughnut",
                "scope": "category",
                "source": f"World Bank API {codes}",
                "unit": unit.strip(),
                "note": (
                    f"{subtitle}, latest year with every component reported ({year}). World Bank indicators {codes}."
                    + (f" '{residual}' is the residual to 100%, not a directly reported category." if residual and residual in labels else "")
                ),
                "meta": _meta(f"{title} ({year})", subtitle, category, subgroup, "#ff9933", unit if unit.startswith(" ") else f" {unit}" if unit != "%" else "%"),
            }
        except Exception:
            if previous.get(key, {}).get("values"):
                series[key] = previous[key]
    return series
