"""Expansion layer: new subgroups of official World Bank API charts for twelve existing dashboard groups.

The World Bank API republishes IMF, ILO, WHO, UNESCO, SIPRI, ITU, FAO, UNHCR and UN Tourism statistics. Every value is
fetched at build time; nothing is hard-coded. Each series carries ``meta`` so the dashboard registers it without a
hand-written definition. Keys are prefixed ``xp_``.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

COUNTRIES = (
    ("IND", "India"), ("CHN", "China"), ("USA", "United States"), ("JPN", "Japan"), ("DEU", "Germany"),
    ("GBR", "United Kingdom"), ("FRA", "France"), ("BRA", "Brazil"), ("RUS", "Russia"), ("IDN", "Indonesia"),
    ("ZAF", "South Africa"), ("BGD", "Bangladesh"), ("PAK", "Pakistan"), ("LKA", "Sri Lanka"), ("NPL", "Nepal"),
)
NAMES = dict(COUNTRIES)
LINE_PEERS = ("IND", "CHN", "USA", "JPN", "DEU", "BRA", "BGD")
LINE_COLORS = ("#ff9933", "#58a6ff", "#3fb950", "#bc8cff", "#ff7b72", "#f6c344", "#39c5bb")
URL = ("https://api.worldbank.org/v2/country/" + ";".join(code for code, _ in COUNTRIES)
       + "/indicator/{code}?format=json&per_page=20000&date=1980:2026")
WGI_SOURCE = "&source=3"  # Worldwide Governance Indicators live in their own World Bank source


@dataclass
class Ind:
    code: str
    title: str
    suffix: str
    kinds: str  # T trend, P peers, R ranking, D decade averages, Q share doughnut
    what: str
    hint: str
    why: str
    scale: float = 1
    dec: int = 2
    pub: Optional[str] = None
    codes: tuple = ()
    fn: Optional[Callable] = None
    color: Optional[str] = None


@dataclass
class Pie:
    slug: str
    title: str
    comps: tuple  # (code, label)
    what: str
    hint: str
    why: str
    remainder: Optional[tuple] = None  # (total code, label of the residual slice)
    pub: Optional[str] = None


@dataclass
class Multi:
    slug: str
    title: str
    comps: tuple  # (code, label)
    suffix: str
    what: str
    hint: str
    why: str
    scale: float = 1
    pub: Optional[str] = None


@dataclass
class Group:
    category: str
    subgroup: str
    color: str
    pub: str
    items: tuple


SUBGROUPS_SPEC = (
    Group("Economic", "Savings & Investment", "#ff9933", "IMF / World Bank national accounts", (
        Ind("NE.GDI.TOTL.ZS", "Gross Capital Formation", "%", "TPR",
            "Gross capital formation is the share of GDP spent on new fixed assets and inventory build-up.",
            "A higher share means the economy is channelling more output into future capacity.",
            "Investment is the engine of medium-term growth; India's rate shows how much of its growth is capital-led."),
        Ind("NY.GNP.PCAP.PP.CD", "GNI per Capita (PPP)", " int. $", "TR",
            "Gross national income per person converted at purchasing-power-parity so prices are comparable across countries.",
            "Higher means more income per resident after adjusting for local price levels.",
            "PPP income shows real living standards better than market exchange rates do."),
        Ind("NY.GNS.ICTR.ZS", "Gross Savings Rate", "%", "P",
            "Gross savings is national income left after household and government consumption, as a share of GDP.",
            "Lines above India mean peers save more of their income.",
            "High domestic savings let a country fund investment without relying on foreign capital."),
        Ind("NE.RSB.GNFS.ZS", "External Balance on Goods & Services", "%", "TD",
            "The external balance is exports minus imports of goods and services as a share of GDP.",
            "Values below zero are trade deficits; above zero are surpluses.",
            "A persistent deficit must be financed by foreign inflows, so it signals external vulnerability."),
    )),
    Group("Economic", "Prices & Inflation Benchmarks", "#58a6ff", "IMF / World Bank price statistics", (
        Ind("FP.CPI.TOTL", "Consumer Price Index (2010 = 100)", " index", "TR",
            "The consumer price index tracks the cost of a typical household basket, rebased so 2010 equals 100.",
            "A steeper line means faster cumulative price rises since the 2010 base.",
            "The index level shows how much purchasing power has been eroded over the long run."),
        Ind("FP.CPI.TOTL.ZG", "Consumer Price Inflation", "%", "PRD",
            "Annual percentage change in consumer prices.",
            "Spikes show inflation episodes; a line near zero or below shows stable or falling prices.",
            "Inflation decides real incomes, interest rates and central-bank policy."),
        Ind("PA.NUS.PPP", "PPP Conversion Factor", " LCU per int. $", "T",
            "How many rupees are needed to buy what one international dollar buys in the United States.",
            "A rising line means the rupee's domestic purchasing power is falling relative to the dollar's.",
            "It is the basis for converting India's GDP into internationally comparable PPP terms."),
        Ind("price_level_ratio", "Comparative Price Level of Consumption", "x", "PR",
            "Private-consumption PPP divided by the market exchange rate; values below 1 mean prices are lower than in the US.",
            "Lower bars mean everyday goods and services are cheaper in dollar terms.",
            "A low price level helps household affordability but also depresses dollar-measured GDP.",
            codes=("PA.NUS.PRVT.PP", "PA.NUS.FCRF"), fn=lambda ppp, fx: ppp / fx),
        Ind("FM.LBL.BMNY.ZG", "Broad Money Growth", "%", "TD",
            "Annual growth in broad money (M3), the stock of currency, deposits and near-money.",
            "Faster growth than GDP often precedes higher inflation or credit booms.",
            "Money supply growth is a leading indicator for inflation and financial-sector expansion."),
    )),
    Group("Economic", "External Debt & Reserves", "#3fb950", "World Bank International Debt Statistics / IMF", (
        Ind("DT.DOD.DECT.GN.ZS", "External Debt Stocks", "% of GNI", "TPR",
            "Total external debt owed to non-residents as a share of gross national income.",
            "Lower means the country's foreign obligations are small relative to its income.",
            "A modest ratio protects against currency and rollover crises."),
        Ind("DT.DOD.DECT.CD", "External Debt Stock", " USD bn", "T",
            "Total outstanding external debt (public, publicly guaranteed and private) in US dollars.",
            "The line shows how fast India's dollar obligations have grown.",
            "The absolute stock matters because servicing it drains foreign-exchange reserves.", scale=1e9),
        Ind("DT.TDS.DECT.EX.ZS", "Debt Service", "% of exports", "TD",
            "Principal plus interest paid on external debt as a share of exports of goods, services and income.",
            "A rising line means a bigger slice of export earnings is spent on debt.",
            "Debt service relative to export earnings is a classic stress gauge for external solvency."),
        Ind("FI.RES.TOTL.CD", "Foreign-Exchange Reserves", " USD bn", "RQ",
            "Total reserves including gold held by the central bank, in US dollars.",
            "Bigger slices or bars mean a larger buffer for defending the currency and paying for imports.",
            "Reserves are the first line of defence against capital-flow shocks.", scale=1e9),
        Ind("BX.TRF.PWKR.CD.DT", "Remittances Received", " USD bn", "TRQ",
            "Personal transfers and compensation of employees sent home by workers abroad, in US dollars.",
            "A rising line means more foreign income flowing to households.",
            "India is the world's largest remittance recipient, a stable source of foreign currency.", scale=1e9),
    )),
    Group("Industry Trends & Performance", "Industrial Structure & Productivity", "#ff9933", "World Bank national accounts / ILO", (
        Pie("sector_value_added", "India: Sector Composition of Value Added",
            (("NV.AGR.TOTL.CD", "Agriculture"), ("NV.IND.TOTL.CD", "Industry"), ("NV.SRV.TOTL.CD", "Services")),
            "India's value added split across agriculture, industry (including construction and mining) and services.",
            "Larger slices dominate output; services typically lead as an economy matures.",
            "The split shows how far India's structural transformation has progressed."),
        Ind("SL.GDP.PCAP.EM.KD", "GDP per Person Employed", " PPP $ per worker", "TPR",
            "Output per worker in constant 2021 PPP dollars, a standard measure of labour productivity.",
            "A rising line means each worker produces more; the gap to peers shows the productivity deficit.",
            "Productivity growth is the only sustainable route to higher wages."),
        Ind("NV.IND.MANF.CD", "Manufacturing Value Added", " USD bn", "TRQ",
            "Value added by manufacturing in current US dollars, the output created by factories net of inputs.",
            "Bigger bars or slices mean larger factory output in dollar terms.",
            "Manufacturing scale shows India's weight in global industry.", scale=1e9),
        Ind("NV.IND.MANF.ZS", "Manufacturing Share of GDP", "%", "PR",
            "Manufacturing value added as a share of GDP.",
            "Bars further right indicate more industrialised economies.",
            "The share tests the 'Make in India' ambition against peer industrial economies."),
    )),
    Group("Industry Trends & Performance", "Logistics & Freight", "#58a6ff", "World Bank / WTO / UNCTAD trade statistics", (
        Ind("TX.VAL.MRCH.CD.WT", "Merchandise Exports", " USD bn", "TRQ",
            "Value of goods exported, in current US dollars.",
            "Higher bars show larger goods-trading nations; India's slice shows its share of the group's exports.",
            "Goods exports reflect industrial competitiveness and supply-chain integration.", scale=1e9),
        Ind("merchandise_trade_balance", "Merchandise Trade Balance", " USD bn", "TR",
            "Merchandise exports minus merchandise imports, in US dollars.",
            "Negative values are trade deficits; positive are surpluses.",
            "India's chronic goods deficit shapes the current account and the rupee.",
            codes=("TX.VAL.MRCH.CD.WT", "TM.VAL.MRCH.CD.WT"), fn=lambda x, m: x - m, scale=1e9),
        Ind("TX.QTY.MRCH.XD.WD", "Export Volume Index (2015 = 100)", " index", "TP",
            "Quantity of goods exported, stripped of price effects, with 2015 set to 100.",
            "A steeper rise means the physical volume of exports is growing faster.",
            "Volume shows real export capacity independent of commodity-price swings."),
        Ind("TT.PRI.MRCH.XD.WD", "Net Barter Terms of Trade (2015 = 100)", " index", "TP",
            "Export prices relative to import prices; higher means each unit of exports buys more imports.",
            "A falling line means imports are getting dearer relative to exports.",
            "Terms of trade drive real income gains and losses from trade."),
        Ind("TM.TAX.MRCH.WM.AR.ZS", "Applied Tariff Rate", "%", "TR",
            "Weighted mean tariff applied on all imported products.",
            "Lower values mean freer trade; bars show how protected each economy is.",
            "Tariff levels shape the cost of inputs and India's access to global value chains."),
        Ind("LP.LPI.OVRL.XQ", "Logistics Performance Index", " score", "TR",
            "World Bank survey score (1 to 5) covering customs, infrastructure, shipments, tracking and timeliness.",
            "A higher score means smoother and cheaper movement of goods.",
            "Logistics efficiency is a major hidden cost in Indian manufacturing."),
    )),
    Group("Mining & Natural Resources", "Energy Use & Imports", "#ff7b72", "IEA / World Bank energy statistics", (
        Ind("EG.USE.COMM.GD.PP.KD", "Energy Intensity of GDP", " kg oil eq per $1,000", "TPR",
            "Energy use per 1,000 dollars of GDP at PPP, a measure of how efficiently an economy uses energy.",
            "A falling line means India squeezes more output from each unit of energy.",
            "Lower energy intensity reduces import bills and emissions for every rupee of growth."),
        Ind("EG.ELC.FOSL.ZS", "Electricity from Fossil Fuels", "%", "TPR",
            "Share of electricity generated from coal, oil and gas.",
            "A line moving down shows decarbonising power; peers show how dependent others are.",
            "Fossil dependence determines both mining demand and climate exposure."),
        Ind("EG.USE.COMM.CL.ZS", "Alternative & Nuclear Energy Share", "%", "TP",
            "Clean energy (hydro, nuclear, geothermal, solar and wind) as a share of total energy use, excluding combustible renewables.",
            "Higher means less reliance on carbon-based fuels.",
            "It tracks the pace of the energy transition against peers."),
        Ind("EG.IMP.CONS.ZS", "Net Energy Imports", "% of energy use", "PR",
            "Energy use less domestic production, as a percentage of energy use; positive means net importer.",
            "Bars above zero mean a country imports part of its energy; below zero it is a net exporter.",
            "India's import dependence on oil, gas and coal is its main energy-security risk."),
    )),
    Group("Mining & Natural Resources", "Resource Rents & Natural Capital", "#bc8cff", "World Bank wealth accounts", (
        Pie("resource_rents_mix", "India: Composition of Natural Resource Rents",
            (("NY.GDP.PETR.RT.ZS", "Oil"), ("NY.GDP.COAL.RT.ZS", "Coal"), ("NY.GDP.NGAS.RT.ZS", "Natural gas"),
             ("NY.GDP.MINR.RT.ZS", "Minerals"), ("NY.GDP.FRST.RT.ZS", "Forests")),
            "Rents are the revenue from extracting a resource minus production costs; slices show each resource's share of India's total rents.",
            "A larger slice means the economy leans more on that resource.",
            "The mix shows which parts of the natural estate India actually monetises."),
        Ind("NY.GDP.PETR.RT.ZS", "Oil Rents", "% of GDP", "TPR",
            "Oil rents as a percentage of GDP.",
            "Higher bars mark oil-dependent economies; see the note for India's rank.",
            "Low oil rents confirm India's role as a consumer rather than producer of oil."),
        Ind("NY.GDP.COAL.RT.ZS", "Coal Rents", "% of GDP", "PR",
            "Coal rents as a percentage of GDP.",
            "A higher line shows coal contributes more to national income.",
            "Coal is India's main domestic energy resource, so its rent share matters for the transition."),
        Ind("NY.ADJ.DRES.GN.ZS", "Natural Resource Depletion", "% of GNI", "TPR",
            "Value of energy, mineral and forest stock used up in a year, as a share of gross national income.",
            "Higher means more of national income is really liquidation of natural capital.",
            "Depletion is subtracted from savings to reveal true long-run sustainability."),
        Ind("NY.ADJ.SVNG.GN.ZS", "Adjusted Net Savings", "% of GNI", "TPRD",
            "Savings after deducting capital depreciation and resource depletion and adding education spending.",
            "Positive and rising values indicate that wealth is growing rather than being consumed.",
            "It is the World Bank's headline test of whether development is sustainable."),
    )),
    Group("Payments & Digital Banking", "Financial Inclusion & Credit Depth", "#ff9933", "World Bank Global Findex / IMF", (
        Ind("FX.OWN.TOTL.FE.ZS", "Women with a Financial Account", "% of women 15+", "TR",
            "Share of adult women owning an account at a bank, other financial institution or mobile-money provider.",
            "Points rise survey by survey; the gap to the 100% mark is the unbanked women's share.",
            "Women's account ownership is the base on which digital credit and payments can scale."),
        Ind("FX.OWN.TOTL.40.ZS", "Poorest 40% with an Account", "%", "TR",
            "Account ownership among adults in the poorest 40% of households.",
            "Higher means formal finance is reaching low-income households.",
            "Inclusion among the poor measures whether schemes such as Jan Dhan translate into real access."),
        Ind("FX.OWN.TOTL.ZS", "Adult Account Ownership", "%", "P",
            "Share of adults with a financial account.",
            "Compare India's catch-up with peers that started from similar levels.",
            "Account ownership is the first step to digital payments, savings and credit."),
        Ind("FD.AST.PRVT.GD.ZS", "Domestic Credit to Private Sector by Banks", "% of GDP", "TPR",
            "Financial resources banks provide to the private sector (loans, securities, trade credit), as a share of GDP.",
            "Higher means deeper bank financing; India's gap shows room for credit expansion.",
            "Credit depth supports investment and household consumption."),
        Ind("FB.AST.NPER.ZS", "Bank Non-Performing Loans", "% of gross loans", "TPR",
            "Share of bank loans that are overdue by 90 days or more.",
            "Lower is healthier; spikes mark banking-sector stress.",
            "NPLs limit banks' ability to lend and show asset-quality repair."),
        Ind("FB.BNK.CAPA.ZS", "Bank Capital to Assets", "%", "TR",
            "Bank capital and reserves as a share of total assets.",
            "Higher means a thicker cushion against loan losses.",
            "Capital adequacy underpins confidence in the banking system."),
    )),
    Group("Payments & Digital Banking", "Insurance & Capital Markets", "#58a6ff", "World Bank Financial Development / IMF BoP", (
        Ind("CM.MKT.LCAP.GD.ZS", "Stock Market Capitalisation", "% of GDP", "TPR",
            "Market value of all listed domestic companies as a share of GDP.",
            "Higher shows a deeper equity market relative to the economy.",
            "Market depth indicates how easily firms can raise equity."),
        Ind("CM.MKT.TRAD.GD.ZS", "Stocks Traded", "% of GDP", "TR",
            "Total value of shares traded in a year relative to GDP.",
            "Higher means a more actively traded, liquid market.",
            "Liquidity lowers the cost of capital and attracts investors."),
        Ind("CM.MKT.LDOM.NO", "Listed Domestic Companies", " companies", "TRQ",
            "Number of domestic companies listed on the country's exchanges.",
            "A larger bar or slice means a wider choice of listed businesses.",
            "Listing count reflects how broad the corporate base is that can access public equity."),
        Ind("CM.MKT.INDX.ZG", "S&P Global Equity Index Change", "%", "TP",
            "Annual percentage change in the S&P Global equity index for each country.",
            "Bars above zero are rising years; large drops mark market crashes.",
            "Equity returns drive household wealth and the attractiveness of retail investing."),
        Ind("BX.PEF.TOTL.CD.WD", "Portfolio Equity Net Inflows", " USD bn", "TR",
            "Net foreign purchases of equity securities, in US dollars.",
            "Spikes are foreign buying sprees; negative values are net outflows.",
            "Portfolio flows are volatile and move the rupee and stock prices.", scale=1e9),
        Ind("BX.GSR.INSF.ZS", "Insurance & Financial Services Exports", "% of service exports", "PR",
            "Insurance and financial services as a share of commercial-service exports.",
            "Higher bars mark financial-services exporters; India is a smaller player.",
            "It shows how far finance and insurance are an export industry, not only a domestic one."),
    )),
    Group("State Performance & Regional Health", "Urban vs Rural Divide", "#ff9933", "WHO / UNICEF JMP / World Bank", (
        Multi("water_urban_rural", "Basic Drinking Water: Urban vs Rural India",
              (("SH.H2O.BASW.UR.ZS", "Urban"), ("SH.H2O.BASW.RU.ZS", "Rural")), "%",
              "Share of urban and rural populations using at least a basic drinking-water service.",
              "The distance between the lines is the rural deficit; converging lines mean the gap is closing.",
              "Rural water access is central to the health gains targeted by regional programmes."),
        Multi("sanitation_urban_rural", "Basic Sanitation: Urban vs Rural India",
              (("SH.STA.BASS.UR.ZS", "Urban"), ("SH.STA.BASS.RU.ZS", "Rural")), "%",
              "Share of urban and rural people using at least basic sanitation facilities.",
              "A steeper rural line means faster catch-up after the Swachh Bharat push.",
              "Sanitation gaps drive diarrhoeal disease and child stunting in rural regions."),
        Multi("electricity_urban_rural", "Electricity Access: Urban vs Rural India",
              (("EG.ELC.ACCS.UR.ZS", "Urban"), ("EG.ELC.ACCS.RU.ZS", "Rural")), "%",
              "Share of urban and rural populations with access to electricity.",
              "Both lines near 100% mean the divide has effectively closed.",
              "Electrification is the precondition for rural clinics, schools and enterprises."),
        Multi("open_defecation_urban_rural", "Open Defecation: Urban vs Rural India",
              (("SH.STA.ODFC.UR.ZS", "Urban"), ("SH.STA.ODFC.RU.ZS", "Rural")), "%",
              "Share of urban and rural people practising open defecation.",
              "Falling lines are progress; the rural line starts much higher.",
              "Open defecation is a direct driver of infection and malnutrition."),
        Multi("population_urban_rural", "Population: Urban vs Rural India",
              (("SP.URB.TOTL", "Urban"), ("SP.RUR.TOTL", "Rural")), " million",
              "Absolute urban and rural population living in India.",
              "Where the lines cross shows when urban numbers overtake rural ones; rural numbers are flattening.",
              "The balance of urban and rural people drives service demand across states.", scale=1e6),
        Ind("water_gap", "Urban-Rural Gap in Basic Water Access", " pp", "R",
            "Urban minus rural share of people with basic drinking water, in percentage points.",
            "Bigger bars are bigger rural disadvantages; near zero means equal access.",
            "The gap pinpoints where rural investment is still lagging.",
            codes=("SH.H2O.BASW.UR.ZS", "SH.H2O.BASW.RU.ZS"), fn=lambda ur, ru: ur - ru),
        Ind("sanitation_gap", "Urban-Rural Gap in Basic Sanitation", " pp", "R",
            "Urban minus rural share of people with basic sanitation, in percentage points.",
            "Larger positive bars show rural populations being left behind.",
            "Closing this gap is a prerequisite for equal health outcomes across regions.",
            codes=("SH.STA.BASS.UR.ZS", "SH.STA.BASS.RU.ZS"), fn=lambda ur, ru: ur - ru),
    )),
    Group("State Performance & Regional Health", "Urbanisation & Cities", "#58a6ff", "UN World Urbanization Prospects via World Bank", (
        Ind("EN.URB.LCTY.UR.ZS", "Population in Largest City", "% of urban population", "TR",
            "Share of the urban population living in the country's largest city.",
            "Low values mean urban growth is spread over many cities rather than concentrated.",
            "Dispersed urbanisation reduces pressure on a single megacity."),
        Ind("EN.URB.MCTY.TL.ZS", "Population in Million-Plus Cities", "% of population", "TPR",
            "Share of the total population living in cities of more than one million people.",
            "A rising line shows people migrating into large metros.",
            "Large-city share influences housing, transport and health demand."),
        Ind("SP.URB.GROW", "Urban Population Growth", "%", "PR",
            "Annual growth rate of the urban population.",
            "Higher bars mean faster-expanding cities.",
            "Rapid urban growth tests housing and service delivery in city regions."),
        Ind("SP.URB.TOTL.IN.ZS", "Urban Share of Population", "%", "PR",
            "Urban population as a share of total population.",
            "Lines further up show more urbanised countries; India is still mostly rural.",
            "Urban share is a core development benchmark."),
        Ind("SP.URB.TOTL", "Urban Population", " million", "TQ",
            "Absolute number of people living in urban areas.",
            "The slice shows India's share of urban people across the 15 countries.",
            "India adds some of the world's largest urban populations each year.", scale=1e6),
        Ind("SP.RUR.TOTL.ZG", "Rural Population Growth", "%", "T",
            "Annual growth rate of the rural population.",
            "A line crossing below zero means the rural population is shrinking.",
            "Rural decline reflects migration to towns and falling fertility."),
    )),
    Group("Public Health & Epidemiology", "Communicable Diseases", "#ff7b72", "WHO Global TB / Malaria Programmes via World Bank", (
        Ind("SH.TBS.MORT", "Tuberculosis Mortality", " per 100,000", "TPR",
            "Estimated tuberculosis deaths per 100,000 people (HIV-negative).",
            "Falling lines show progress toward TB elimination targets.",
            "India carries the world's largest TB burden, so mortality progress is globally significant."),
        Ind("SH.TBS.DTEC.ZS", "TB Case Detection Rate", "%", "TR",
            "Estimated share of new and relapse TB cases that were detected and reported.",
            "Higher means fewer hidden cases; 100% means all cases are notified.",
            "Detection is the gateway to treatment and to stopping transmission."),
        Ind("SH.TBS.CURE.ZS", "TB Treatment Success Rate", "%", "TP",
            "Share of TB cases successfully treated (cured or treatment completed).",
            "Higher is better; dips show drop-outs or drug resistance.",
            "Treatment success determines whether TB is actually eliminated."),
        Ind("SH.MLR.INCD.P3", "Malaria Incidence", " per 1,000 at risk", "PR",
            "New malaria cases per 1,000 people at risk.",
            "Higher bars mean a heavier malaria burden among the countries with data.",
            "Malaria incidence tracks the success of vector control and diagnosis."),
        Ind("SH.STA.MALR",         "Malaria Cases Reported", " cases", "TR",
                    "Number of malaria cases reported by the national health system.",
                    "A falling line means fewer reported cases, though better testing can lift counts.",
                    "Reported cases track whether malaria control is reaching endemic districts."),
        Ind("SH.STA.MMRT", "Maternal Mortality Ratio", " per 100,000 births", "PR",
            "Maternal deaths per 100,000 live births (modelled estimate).",
            "Lower bars are safer childbirth systems.",
            "Maternal mortality is the sharpest test of the health system's reach."),
    )),
    Group("Public Health & Epidemiology", "Health Workforce & Immunisation", "#3fb950", "WHO / UNICEF WUENIC via World Bank", (
        Ind("SH.MED.NUMW.P3", "Nurses & Midwives", " per 1,000 people", "TPR",
            "Nursing and midwifery personnel per 1,000 people.",
            "Higher means more frontline care capacity.",
            "Nurses deliver most primary care and are the binding constraint in many health systems."),
        Ind("SH.IMM.HEPB", "Hepatitis B Immunisation", "% of 12-23 month-olds", "TPR",
            "Share of children immunised against hepatitis B.",
            "Closer to 100% means near-universal coverage.",
            "Hepatitis B vaccination prevents chronic liver disease and cancer later in life."),
        Ind("SH.IMM.HIB3", "Hib Immunisation", "% of children", "TR",
            "Share of children receiving three doses of Haemophilus influenzae type b vaccine.",
            "Rapid rises show new vaccine introduction.",
            "Hib vaccine prevents pneumonia and meningitis in young children."),
        Ind("SH.IMM.IDPT", "DPT Immunisation", "% of children", "PR",
            "Share of children immunised against diphtheria, pertussis and tetanus.",
            "Dips mark lapses such as pandemic disruption.",
            "DPT coverage is the standard measure of routine immunisation performance."),
        Ind("SH.IMM.MEAS", "Measles Immunisation", "% of children", "P",
            "Share of children immunised against measles.",
            "Gaps below the 95% herd-immunity line signal outbreak risk.",
            "Measles outbreaks reveal weaknesses in routine vaccination."),
        Ind("SH.ANM.ALLW.ZS", "Anaemia in Women", "% of women 15-49", "TPR",
            "Prevalence of anaemia among women of reproductive age.",
            "Lower is better; India's high value signals a persistent nutrition problem.",
            "Maternal anaemia raises risks in pregnancy and for newborn health."),
    )),
    Group("Social", "Gender Equality", "#bc8cff", "UNESCO / ILO / World Bank", (
        Ind("SE.ENR.TERT.FM.ZS", "Gender Parity in Tertiary Enrolment", " F/M ratio", "TPR",
            "Female-to-male ratio of gross tertiary enrolment; 1 is parity.",
            "Above 1 means more women than men are in higher education.",
            "Parity in universities shows women's access to skilled careers."),
        Ind("SL.TLF.CACT.FM.ZS", "Female-to-Male Labour-Force Participation", "%", "TPR",
            "Ratio of female to male labour-force participation rates.",
            "100% would mean equal participation; lower lines show women excluded from work.",
            "Women's work is India's biggest untapped growth lever."),
        Ind("SL.EMP.SMGT.FE.ZS", "Women in Senior & Middle Management", "%", "TR",
            "Share of senior and middle management positions held by women.",
            "Higher is more women in decision-making roles.",
            "Management representation shows whether education converts into authority."),
        Ind("SG.GEN.PARL.ZS", "Women in National Parliament", "% of seats", "PR",
            "Share of parliamentary seats held by women.",
            "Higher bars show greater political representation.",
            "Political voice influences policy on health, education and safety."),
        Ind("SP.ADO.TFRT", "Adolescent Fertility", " births per 1,000 girls 15-19", "TPR",
            "Births per 1,000 women aged 15-19.",
            "Falling lines show girls staying in school and delaying marriage.",
            "Adolescent births affect girls' education, health and earnings."),
        Ind("life_expectancy_gap", "Female Life-Expectancy Advantage", " years", "TR",
            "Female life expectancy at birth minus male life expectancy.",
            "A positive value means women live longer; narrow gaps may point to disadvantaged women.",
            "The gap is a compact signal of gender differences in health care and survival.",
            codes=("SP.DYN.LE00.FE.IN", "SP.DYN.LE00.MA.IN"), fn=lambda f, m: f - m),
    )),
    Group("Social", "Children & Youth", "#f6c344", "UNESCO UIS / ILO / UNICEF via World Bank", (
        Ind("SE.PRM.UNER.ZS", "Out-of-School Children of Primary Age", "%", "TR",
            "Share of primary-school-age children who are not enrolled in school.",
            "Lower is better; spikes show enrolment shocks.",
            "Out-of-school children are the clearest measure of unfinished universal education."),
        Ind("SE.PRE.ENRR", "Pre-Primary Enrolment", "% gross", "TPR",
            "Gross enrolment in pre-primary education.",
            "Higher means more children start learning before primary school.",
            "Early education raises later learning outcomes and lets mothers work."),
        Ind("SE.PRM.ENRL.TC.ZS", "Pupils per Primary Teacher", " pupils", "TR",
            "Number of pupils per teacher in primary school.",
            "Lower ratios mean more teacher attention per child.",
            "Class size influences learning quality."),
        Ind("SL.UEM.NEET.ZS", "Youth Not in Education, Employment or Training", "%", "TR",
            "Share of youth who are neither studying nor employed nor in training.",
            "Higher means more idle youth.",
            "A large NEET share signals wasted demographic dividend."),
        Ind("SH.DYN.0509", "Mortality Rate, Age 5-9", " per 1,000", "TR",
            "Probability of dying between ages 5 and 9 per 1,000 children.",
            "Falling values show safer school-age childhood.",
            "Mortality beyond infancy reflects injuries, infections and nutrition."),
        Ind("SH.STA.WAST.ZS", "Child Wasting", "% of under-5s", "TR",
            "Share of children under five with low weight for height.",
            "Higher means more acute malnutrition.",
            "Wasting is the most visible signal of acute child hunger."),
        Ind("SP.POP.0014.TO", "Population Aged 0-14", " million", "TQ",
            "Absolute number of children aged 0 to 14.",
            "The slice is India's share of the child population in the 15-country group.",
            "Child numbers set the scale of future school, health and job needs.", scale=1e6),
    )),
    Group("Environment & Climate", "Air Quality & Emissions", "#ff7b72", "EDGAR / CAIT / World Bank climate data", (
        Ind("EN.GHG.CO2.MT.CE.AR5", "CO2 Emissions", " Mt CO2e", "TRQ",
            "Carbon dioxide emissions excluding land use, in million tonnes of CO2 equivalent.",
            "Bigger bars or slices are bigger absolute emitters.",
            "India's rank shows its weight in global climate outcomes.", dec=1),
        Ind("EN.GHG.CH4.MT.CE.AR5", "Methane Emissions", " Mt CO2e", "TR",
            "Methane emissions, mostly from agriculture, livestock and waste, in CO2 equivalent.",
            "Rising lines show growth in livestock and rice farming.",
            "Methane is a potent short-lived warming gas where quick cuts pay off."),
        Ind("EN.GHG.CO2.RT.GDP.KD", "Carbon Intensity of GDP", " kg CO2 per $ GDP", "TPR",
            "Kilograms of CO2 emitted per dollar of GDP in constant prices.",
            "A falling line means growth is decoupling from emissions.",
            "Intensity is the metric behind India's climate pledge."),
        Ind("EN.GHG.ALL.PC.CE.AR5", "Total GHG Emissions per Capita", " t CO2e", "TP",
            "All greenhouse gases per person in tonnes of CO2 equivalent.",
            "India sits far below the lines for the US and China.",
            "Per-capita emissions anchor the equity argument in climate diplomacy."),
        Pie("co2_sectors", "India: CO2 Emissions by Source Sector",
            (("EN.GHG.CO2.PI.MT.CE.AR5", "Power industry"), ("EN.GHG.CO2.IP.MT.CE.AR5", "Industrial processes"),
             ("EN.GHG.CO2.BU.MT.CE.AR5", "Buildings"), ("EN.GHG.CO2.TR.MT.CE.AR5", "Transport")),
            "Slices split India's CO2 emissions among power generation, industrial processes, buildings and transport.",
            "The biggest slice is where decarbonisation pays off most.",
            "Sector shares guide which policy levers matter."),
        Pie("ghg_gases", "India: Greenhouse Gas Mix",
            (("EN.GHG.CO2.MT.CE.AR5", "CO2"), ("EN.GHG.CH4.MT.CE.AR5", "Methane"), ("EN.GHG.N2O.MT.CE.AR5", "Nitrous oxide")),
            "Share of India's non-land-use greenhouse emissions by gas, in CO2 equivalent.",
            "A larger methane or N2O slice reflects agriculture-heavy emissions.",
            "The mix shows India's non-CO2 emissions problem."),
        Ind("EN.ATM.PM25.MC.ZS", "Population Exposed to Unsafe PM2.5", "% of population", "TR",
            "Share of people living where annual PM2.5 exceeds the WHO guideline.",
            "Near 100% means essentially all residents breathe unsafe air.",
            "Exposure share frames air pollution as a nationwide issue."),
    )),
    Group("Environment & Climate", "Water Resources", "#58a6ff", "FAO AQUASTAT via World Bank", (
        Ind("ER.H2O.FWTL.K3", "Freshwater Withdrawals", " bn cubic metres", "TRQ",
            "Total annual freshwater withdrawals for agriculture, industry and households.",
            "Bigger slices show countries pulling most water from rivers and aquifers.",
            "India is among the largest water users globally."),
        Ind("ER.H2O.FWTL.ZS", "Withdrawals as Share of Internal Resources", "%", "TR",
            "Freshwater withdrawals as a percentage of internal renewable resources.",
            "Above 40% signals high water stress.",
            "Water stress affects farm output and city supply."),
        Ind("ER.H2O.INTR.PC", "Renewable Water per Person", " m3 per capita", "PR",
            "Internal renewable freshwater resources per person.",
            "Below 1,700 m3 is water stress; below 1,000 is scarcity.",
            "India is edging toward scarcity levels as population grows."),
        Ind("ER.GDP.FWTL.M3.KD", "Water Productivity", " GDP $ per m3", "TP",
            "Constant GDP produced per cubic metre of freshwater withdrawn.",
            "A rising line means more output per drop of water.",
            "Water productivity measures efficiency gains in a water-scarce country."),
        Pie("water_use_sectors", "India: Freshwater Withdrawals by Sector",
            (("ER.H2O.FWAG.ZS", "Agriculture"), ("ER.H2O.FWIN.ZS", "Industry"), ("ER.H2O.FWDM.ZS", "Domestic")),
            "Shares of India's freshwater withdrawals that go to farms, factories and households.",
            "Agriculture dominates the slice, so irrigation efficiency matters most.",
            "Sector shares show where water-saving policy would have the biggest effect."),
        Ind("AG.LND.PRCP.MM", "Average Annual Precipitation", " mm", "TR",
            "Long-term average rainfall depth across the country.",
            "India's rainfall is mostly monsoon-borne.",
            "Rainfall underpins water supply and agricultural output."),
    )),
    Group("Agriculture & Food", "Farm Productivity & Yields", "#3fb950", "FAO / World Bank", (
        Ind("AG.PRD.CREL.MT", "Cereal Production", " million tonnes", "TRQ",
            "Total harvested production of wheat, rice, maize and other cereals.",
            "Bigger bars or slices are larger producers.",
            "Cereals are the backbone of India's food supply.", scale=1e6),
        Ind("AG.PRD.CROP.XD", "Crop Production Index (2014-16 = 100)", " index", "TP",
            "Index of crop output relative to a 2014-2016 base.",
            "A rising line means crop output is growing faster.",
            "The index tracks output growth beyond land expansion."),
        Ind("AG.YLD.CREL.KG", "Cereal Yield", " kg per hectare", "PR",
            "Cereal output per hectare of harvested land.",
            "Higher bars show more intensive farming.",
            "Yield gaps between India and the leaders show scope for productivity growth."),
        Ind("cereal_per_capita", "Cereal Production per Person", " kg per person", "TR",
            "Cereal production divided by population, derived from two official series.",
            "A rising line means harvests are outpacing population.",
            "Per-person output shows food self-reliance.",
            codes=("AG.PRD.CREL.MT", "SP.POP.TOTL"), fn=lambda p, pop: p * 1000 / pop),
        Ind("NV.AGR.TOTL.KD", "Agriculture Value Added", " USD bn (2015 prices)", "TR",
            "Real value added by agriculture, forestry and fishing.",
            "A rising line is real growth in farm sector output.",
            "It shows how much farm output is expanding in real terms.", scale=1e9),
        Ind("AG.LND.CREL.HA", "Land Under Cereal Production", " million hectares", "T",
            "Area harvested for cereals.",
            "A flat line while production rises means yield gains.",
            "Cereal area shows land constraints on food growth.", scale=1e6),
    )),
    Group("Agriculture & Food", "Food Trade & Land Use", "#f6c344", "FAO / WTO / World Bank", (
        Ind("TX.VAL.FOOD.ZS.UN", "Food Exports", "% of merchandise exports", "PR",
            "Food exports as a share of merchandise exports.",
            "Higher bars show food-export dependence.",
            "India's food export share indicates its role in feeding the world."),
        Ind("TM.VAL.FOOD.ZS.UN", "Food Imports", "% of merchandise imports", "PR",
            "Food imports as a share of merchandise imports.",
            "Higher bars show food-import dependence.",
            "Low food-import share signals self-sufficiency."),
        Ind("AG.LND.AGRI.ZS", "Agricultural Land", "% of land area", "PR",
            "Agricultural land as a share of total land area.",
            "India has one of the highest shares globally.",
            "High land use leaves little room for further farm expansion."),
        Ind("AG.LND.ARBL.ZS", "Arable Land", "% of land area", "TR",
            "Arable land as a share of total land area.",
            "A flat line means no new land is being ploughed.",
            "Arable land is the natural ceiling on production."),
        Ind("AG.LND.AGRI.K2", "Agricultural Land Area", " million sq km", "TQ",
            "Total area devoted to farming and pasture.",
            "The slice shows India's share of the group's farm area.",
            "Absolute farm area shows how much land supports the food system.", scale=1e6),
        Pie("land_use_mix", "India: Land Use Composition",
            (("AG.LND.AGRI.K2", "Agricultural land"), ("AG.LND.FRST.K2", "Forest")),
            "India's land area split among agricultural land, forest and other land.",
            "The larger agricultural slice shows how intensively the land is used.",
            "Competing uses for land set limits on food and forest policy.",
            remainder=("AG.LND.TOTL.K2", "Other land")),
    )),
    Group("Defence & Strategic", "Armed Forces & Personnel", "#ff7b72", "SIPRI / IISS / World Bank", (
        Ind("MS.MIL.TOTL.P1", "Armed Forces Personnel", " million", "RQ",
            "Active military and paramilitary personnel.",
            "Bigger bars and slices show larger forces.",
            "India has one of the world's largest standing militaries.", scale=1e6),
        Ind("MS.MIL.TOTL.TF.ZS", "Armed Forces Share of Labour Force", "%", "TPR",
            "Military and paramilitary personnel as a share of the labour force.",
            "Higher means more workers are in uniform.",
            "It shows how much of the workforce national security absorbs."),
        Ind("spend_per_soldier", "Military Spending per Soldier", " USD thousand", "TR",
            "Military spending divided by armed-forces personnel.",
            "A rising line means more money per soldier, often for equipment.",
            "It separates manpower-heavy forces from capital-heavy forces.",
            codes=("MS.MIL.XPND.CD", "MS.MIL.TOTL.P1"), fn=lambda s, p: s / p, scale=1e3),
        Ind("forces_per_1000", "Armed Forces per 1,000 People", " per 1,000", "TR",
            "Armed-forces personnel per 1,000 residents.",
            "Higher means a more militarised society.",
            "India's ratio is low because its population is huge.",
            codes=("MS.MIL.TOTL.P1", "SP.POP.TOTL"), fn=lambda p, pop: p / pop * 1000),
    )),
    Group("Defence & Strategic", "Military Spending Benchmarks", "#58a6ff", "SIPRI Military Expenditure Database via World Bank", (
        Ind("MS.MIL.XPND.GD.ZS", "Military Spending", "% of GDP", "PRD",
            "Military expenditure as a share of GDP (SIPRI).",
            "Higher means a heavier defence burden.",
            "It frames India's defence effort against rivals and peers."),
        Ind("MS.MIL.XPND.ZS", "Military Spending Share of Government Expenditure", "%", "PR",
            "Military expenditure as a share of general government expenditure.",
            "Higher means defence takes a larger slice of public budgets.",
            "It shows the trade-off with social spending."),
        Ind("MS.MIL.XPND.CD", "Military Expenditure", " USD bn", "RQ",
            "Military expenditure in current US dollars.",
            "Bigger slices belong to the largest spenders.",
            "India ranks among the world's top military spenders.", scale=1e9),
        Ind("MS.MIL.MPRT.KD", "Arms Imports", " SIPRI TIV (million)", "RQ",
            "Volume of major conventional arms imported, SIPRI trend-indicator values.",
            "Bigger bars show greater import dependence.",
            "India has long been one of the largest arms importers.", scale=1e6),
        Ind("MS.MIL.XPRT.KD", "Arms Exports", " SIPRI TIV (million)", "R",
            "Volume of major conventional arms exported, SIPRI trend-indicator values.",
            "Bigger bars show larger exporters.",
            "Arms exports show industrial and strategic reach.", scale=1e6),
        Ind("defence_vs_health", "Military Spending Relative to Health Spending", " x", "TR",
            "Military spending (% of GDP) divided by current health spending (% of GDP).",
            "Above 1 means defence outweighs health in the economy.",
            "The ratio reveals social-versus-security trade-offs.",
            codes=("MS.MIL.XPND.GD.ZS", "SH.XPD.CHEX.GD.ZS"), fn=lambda m, h: m / h),
    )),
    Group("Crime & Security", "Conflict & Displacement", "#ff7b72", "UCDP / UNHCR / IDMC via World Bank", (
        Ind("VC.BTL.DETH", "Battle-Related Deaths", " deaths", "TR",
            "Deaths in battle-related conflicts between warring parties, as recorded by UCDP.",
            "Peaks mark intense conflict years.",
            "It gives the scale of organised armed conflict."),
        Ind("VC.IDP.NWCV", "New Displacements from Conflict & Violence", " cases", "TR",
            "New internal displacements associated with conflict and violence.",
            "Higher values mean more people were newly forced from their homes that year.",
            "It captures human cost beyond casualty counts."),
        Ind("VC.IDP.NWDS", "New Displacements from Disasters", " cases", "TRQ",
            "New internal displacements caused by floods, storms and other disasters.",
            "Check India's slice and rank: monsoon floods and cyclones force mass evacuations each year.",
            "Disaster displacement is a leading security and humanitarian concern."),
        Ind("SM.POP.RHCR.EA", "Refugees Hosted", " people", "TRQ",
            "Refugees under UNHCR mandate residing in the country.",
            "Bigger slices host more UNHCR-registered refugees.",
                        "Hosting numbers show the humanitarian responsibility a country shoulders."),
        Ind("SM.POP.RHCR.EO", "Refugees Originating from the Country", " people", "TR",
            "Refugees under UNHCR mandate who originate from the country.",
            "A rising line means more people from India have sought protection abroad.",
                        "Counts of refugees by origin are a visible footprint of insecurity at home."),
        Ind("SM.POP.FDIP", "Forcibly Displaced People", " people", "TR",
            "People displaced by conflict, persecution or violence.",
            "Compare bar heights to see how large displacement is relative to the other countries.",
            "It is the headline UNHCR measure of people driven from their homes by conflict, persecution or violence."),
    )),
    Group("Crime & Security", "Rule of Law & Governance", "#58a6ff", "Worldwide Governance Indicators via World Bank", (
        Ind("GOV_WGI_RL.SC", "Rule of Law", " score 0-100", "TPR",
            "Perceptions of confidence in contract enforcement, property rights, police and courts (percentile score).",
            "Higher means stronger rule of law.",
            "Rule of law underpins crime control and investment."),
        Ind("GOV_WGI_CC.SC", "Control of Corruption", " score 0-100", "TPR",
            "Perceptions of the extent public power is exercised for private gain.",
            "Higher means cleaner government.",
            "Corruption weakens security forces and justice."),
        Ind("GOV_WGI_PV.SC", "Political Stability & Absence of Violence", " score 0-100", "TPR",
            "Perceived likelihood of political instability or politically motivated violence.",
            "Higher means a more stable environment.",
            "It captures political violence risk."),
        Ind("GOV_WGI_GE.SC", "Government Effectiveness", " score 0-100", "TR",
            "Perceived quality of public services and civil service.",
            "Higher means more capable administration.",
            "Effective government is a prerequisite for policing and justice."),
        Ind("GOV_WGI_RQ.SC", "Regulatory Quality", " score 0-100", "T",
            "Perceived ability to formulate and implement sound regulation.",
            "Higher means better regulation.",
            "Regulatory quality shapes the business environment."),
        Ind("GOV_WGI_VA.SC", "Voice & Accountability", " score 0-100", "TR",
            "Perceptions of citizens' ability to participate in elections, free expression and free media.",
            "Higher means stronger democratic accountability.",
            "Accountability is the check on abuses of security powers."),
        Multi("homicide_by_sex", "Intentional Homicide: Male vs Female Rate in India",
              (("VC.IHR.PSRC.MA.P5", "Male"), ("VC.IHR.PSRC.FE.P5", "Female")), " per 100,000",
              "Intentional homicides per 100,000 people of each sex in India.",
              "The gap between the two lines is the male-female difference in homicide risk.",
              "Sex-disaggregated homicide shows who bears violent crime risk."),
    )),
    Group("Tourism & Heritage", "Air & Transport Connectivity", "#39c5bb", "ICAO / UIC / UNCTAD via World Bank", (
        Ind("IS.AIR.PSGR", "Air Passengers Carried", " million", "TRQ",
            "Domestic and international passengers carried by registered carriers.",
            "Bigger slices mean larger aviation markets.",
            "Air capacity underpins tourism growth.", scale=1e6),
        Ind("IS.AIR.DPRT", "Air Departures", " thousand", "TR",
            "Domestic and international take-offs by registered carriers.",
            "Rising lines show more scheduled flights.",
            "More flights widen access to destinations.", scale=1e3),
        Ind("IS.AIR.GOOD.MT.K1", "Air Freight", " million ton-km", "TR",
            "Cargo carried by air in million tonne-kilometres.",
            "Bigger bars show greater air-cargo capacity.",
            "Air freight is key to fast supply chains for goods and perishable products."),
        Ind("IS.RRS.PASG.KM", "Rail Passenger-Kilometres", " bn", "TRQ",
            "Passenger travel by rail measured in passenger-km.",
            "The slice shows India's share of rail passenger travel among the countries reporting.",
            "Rail connects heritage and pilgrimage circuits.", scale=1e3),
        Ind("IS.RRS.TOTL.KM", "Rail Lines", " thousand km", "TR",
            "Total route length of rail network.",
            "Longer networks are bigger bars.",
            "Network length is the physical base of rail tourism.", scale=1e3),
        Ind("IS.SHP.GOOD.TU", "Container Port Traffic", " million TEU", "TRQ",
            "Container traffic through ports, in twenty-foot equivalent units.",
            "Bigger slices belong to busier port systems.",
            "Port volumes show trade connectivity and cruise-port capacity.", scale=1e6),
        Ind("air_passengers_per_100", "Air Passengers per 100 People", " per 100", "TR",
            "Annual air passengers divided by population.",
            "A rising line means flying is becoming mainstream.",
            "Compare India with the ranking to see how much room air travel still has to grow.",
            codes=("IS.AIR.PSGR", "SP.POP.TOTL"), fn=lambda p, pop: p / pop * 100),
    )),
    Group("Tourism & Heritage", "Travel Spending & Balance", "#f6c344", "IMF Balance of Payments / UN Tourism via World Bank", (
        Ind("ST.INT.TVLX.CD", "Travel Expenditures Abroad", " USD bn", "TR",
            "Spending by residents on travel abroad, balance-of-payments basis.",
            "Rising lines show growing outbound tourism.",
            "Outbound travel spending is a leakage of foreign exchange.", scale=1e9),
        Ind("travel_balance", "Travel Balance (Receipts minus Expenditures)", " USD bn", "TR",
            "International travel receipts minus travel expenditures abroad.",
            "Positive means net earner of tourism income.",
            "Where the line sits relative to zero shows whether India earns or spends more on travel than it receives.",
            codes=("ST.INT.TVLR.CD", "ST.INT.TVLX.CD"), fn=lambda r, x: r - x, scale=1e9),
        Ind("travel_cover", "Travel Receipts Cover of Expenditures", " x", "TR",
            "Receipts divided by expenditures; above 1 means receipts exceed spending.",
            "Higher is more favourable.",
            "Cover shows tourism's net contribution to the external account.",
            codes=("ST.INT.TVLR.CD", "ST.INT.TVLX.CD"), fn=lambda r, x: r / x),
        Ind("ST.INT.TRNX.CD", "Passenger Transport Payments", " USD bn", "TR",
            "Payments to foreign carriers for passenger transport.",
            "Rising lines show more travel on foreign airlines.",
            "Transport leakages offset tourism receipts.", scale=1e9),
        Ind("ST.INT.TRNR.CD", "Passenger Transport Receipts", " USD bn", "RQ",
            "Receipts from foreign passengers carried by national carriers.",
            "Bigger slices belong to carriers earning more.",
            "Receipts are the transport side of tourism income.", scale=1e9),
        Ind("ST.INT.XPND.MP.ZS", "Outbound Travel Spending", "% of imports", "TPR",
            "International tourism expenditures as a share of total imports.",
            "Higher means travel abroad is a bigger import item.",
            "It tracks how much of import spending goes to overseas trips."),
    )),
)

NEW_SUBGROUPS: dict[str, tuple[str, ...]] = {}
for _group in SUBGROUPS_SPEC:
    NEW_SUBGROUPS[_group.category] = NEW_SUBGROUPS.get(_group.category, ()) + (_group.subgroup,)

KIND_NAMES = {"T": "trend", "P": "peers", "R": "rank", "D": "decade", "Q": "share"}


def _slug(text: str) -> str:
    return "".join(ch if ch.isalnum() else "_" for ch in text.lower()).strip("_")


def _observations(get_json: Callable[[str], object], code: str) -> dict[str, dict[str, float]]:
    url = URL.format(code=code) + (WGI_SOURCE if code.startswith("GOV_") else "")
    payload = get_json(url)
    if not isinstance(payload, list) or len(payload) < 2 or not payload[1]:
        raise ValueError(f"World Bank returned no observations for {code}")
    observed: dict[str, dict[str, float]] = {}
    for row in payload[1]:
        if row.get("value") is not None and row.get("countryiso3code") in NAMES:
            observed.setdefault(row["countryiso3code"], {})[row["date"]] = float(row["value"])
    if "IND" not in observed:
        raise ValueError(f"No India observations for {code}")
    return observed


def _fmt(value: float, dec: int) -> str:
    return f"{value:,.{dec}f}".rstrip("0").rstrip(".") if dec else f"{value:,.0f}"


def _meta(group: Group, title: str, subtitle: str, suffix: str, color: str, what: str, read: str, why: str) -> dict:
    return {"title": title, "subtitle": subtitle, "frequency": "Annual", "color": color, "suffix": suffix,
            "category": group.category, "subgroup": group.subgroup,
            "explain": {"what": what, "read": read, "why": why}}


def _note(text: str, codes: str, latest: str, pub: str) -> str:
    return f"{text} Source: World Bank API {codes} ({pub}); latest year with data: {latest}."


def build_expansion_layer(get_json: Callable[[str], object], previous: dict[str, dict]) -> dict[str, dict]:
    cache: dict[str, object] = {}

    def fetch(code: str) -> dict[str, dict[str, float]]:
        if code not in cache:
            for attempt in range(3):
                try:
                    cache[code] = _observations(get_json, code)
                    break
                except ValueError as error:
                    cache[code] = error
                    break
                except Exception as error:
                    if attempt == 2:
                        cache[code] = error
        result = cache[code]
        if isinstance(result, Exception):
            raise result
        return result  # type: ignore[return-value]

    def observed_for(ind: Ind) -> dict[str, dict[str, float]]:
        if not ind.fn:
            return fetch(ind.code)
        sources = [fetch(code) for code in ind.codes]
        merged: dict[str, dict[str, float]] = {}
        for iso in sources[0]:
            if not all(iso in source for source in sources):
                continue
            years = set(sources[0][iso])
            for source in sources[1:]:
                years &= set(source[iso])
            for year in years:
                try:
                    merged.setdefault(iso, {})[year] = ind.fn(*(source[iso][year] for source in sources))
                except ZeroDivisionError:
                    continue
        if "IND" not in merged:
            raise ValueError(f"No derived India observations for {ind.code}")
        return merged

    def codes_of(ind: Ind) -> str:
        return ", ".join(ind.codes) if ind.fn else ind.code

    def scaled(rows: dict[str, float], ind: Ind) -> dict[str, float]:
        return {year: value / ind.scale for year, value in rows.items()}

    def trend(group, ind, observed):
        india = scaled(observed["IND"], ind)
        years = sorted(india, key=int)
        latest = years[-1]
        what, hint = ind.what, ind.hint
        return {
            "labels": years, "values": [round(india[y], ind.dec) for y in years],
            "source": f"World Bank API {codes_of(ind)}", "unit": ind.suffix.strip(),
            "note": _note(f"{ind.title}: India's annual series, {years[0]} to {latest}; the latest value is "
                          f"{_fmt(india[latest], ind.dec)}{ind.suffix}.", codes_of(ind), latest, ind.pub or group.pub),
            "meta": _meta(group, ind.title, f"India, {years[0]}-{latest}", ind.suffix, ind.color or group.color,
                          f"{what} This chart follows India's annual series.",
                          f"The line ends at {_fmt(india[latest], ind.dec)}{ind.suffix} in {latest}. {hint}", ind.why),
        }

    def peers(group, ind, observed):
        years = sorted({y for iso in LINE_PEERS for y in observed.get(iso, {})}, key=int)
        datasets = [{"label": NAMES[iso], "color": LINE_COLORS[i],
                     "values": [round(observed[iso][y] / ind.scale, ind.dec) if y in observed[iso] else None for y in years]}
                    for i, iso in enumerate(LINE_PEERS) if observed.get(iso)]
        if len(datasets) < 2 or datasets[0]["label"] != "India":
            raise ValueError(f"Too few countries for {ind.code}")
        latest = max(observed["IND"], key=int)
        return {
            "labels": years, "datasets": datasets, "source": f"World Bank API {codes_of(ind)}", "unit": ind.suffix.strip(),
            "note": _note(f"{ind.title}: India against {len(datasets) - 1} comparison countries; gaps are years without "
                          "a reported value.", codes_of(ind), latest, ind.pub or group.pub),
            "meta": _meta(group, f"{ind.title}: India vs Peers", "India against major economies and neighbours",
                          ind.suffix, ind.color or group.color,
                          f"{ind.what} This chart overlays India with {len(datasets) - 1} comparison countries.",
                          f"India is the orange line; the others are {', '.join(d['label'] for d in datasets[1:])}. {ind.hint}",
                          ind.why),
        }

    def ranking_year(observed) -> str:
        counts: dict[str, int] = {}
        for rows in observed.values():
            for year in rows:
                counts[year] = counts.get(year, 0) + 1
        usable = [y for y in observed["IND"] if counts[y] >= 3]
        if not usable:
            raise ValueError("Too few countries for ranking")
        best = max(counts[y] for y in usable)
        threshold = min(8, best)
        return max((y for y in usable if counts[y] >= threshold), key=int)

    def ranking(group, ind, observed, doughnut=False):
        year = ranking_year(observed)
        points = sorted(((NAMES[iso], round(rows[year] / ind.scale, ind.dec)) for iso, rows in observed.items() if year in rows),
                        key=lambda item: -item[1])
        labels = [label for label, _ in points]
        rank = labels.index("India") + 1
        if doughnut:
            points = [(label, value) for label, value in points if value > 0]
            total = sum(value for _, value in points)
            if "India" not in dict(points) or total <= 0:
                raise ValueError(f"No positive values for share chart {ind.code}")
            share = dict(points)["India"] / total * 100
            series = {"chartType": "doughnut", "scope": "category"}
            title, subtitle = f"{ind.title}: Share Among Peers ({year})", "Each country's share of the 15-country total"
            read = (f"Slices are shares of the group total in {year}; India holds {share:.1f}% and ranks {rank} of "
                    f"{len(labels)}. A bigger slice means a larger absolute amount, not a better outcome.")
            what = f"{ind.what} Slices show each country's share of the sampled countries' total."
            note = f"{ind.title}, {year}: India holds {share:.1f}% of the group total and ranks {rank} of {len(labels)}."
        else:
            series = {"chartType": "bar", "indexAxis": "y", "scope": "category"}
            title, subtitle = f"{ind.title}: Peer Ranking ({year})", f"Countries ranked highest to lowest, {year}"
            read = f"Bars run from highest to lowest in {year}; India ranks {rank} of {len(labels)} (1 = highest value). {ind.hint}"
            what = f"{ind.what} Fifteen countries are ranked on the latest year with broad coverage."
            note = f"{ind.title}, {year}: India ranks {rank} of {len(labels)} (1 = highest value)."
        series.update({
            "labels": [label for label, _ in points], "values": [value for _, value in points],
            "source": f"World Bank API {codes_of(ind)}", "unit": ind.suffix.strip(),
            "note": _note(note, codes_of(ind), year, ind.pub or group.pub),
            "meta": _meta(group, title, subtitle, ind.suffix, ind.color or group.color, what, read, ind.why),
        })
        return series

    def decade(group, ind, observed):
        india = scaled(observed["IND"], ind)
        buckets: dict[int, list[float]] = {}
        for year, value in india.items():
            buckets.setdefault(int(year) // 10 * 10, []).append(value)
        if len(buckets) < 2:
            raise ValueError(f"Too few decades for {ind.code}")
        keys = sorted(buckets)
        values = [round(sum(buckets[k]) / len(buckets[k]), ind.dec) for k in keys]
        latest = max(india, key=int)
        change = values[-1] - values[0]
        return {
            "labels": [f"{k}s" for k in keys], "values": values, "chartType": "bar",
            "source": f"World Bank API {codes_of(ind)}", "unit": ind.suffix.strip(),
            "note": _note(f"{ind.title}: decade averages for India; the {keys[-1]}s average is "
                          f"{_fmt(change, ind.dec)}{ind.suffix} {'above' if change >= 0 else 'below'} the {keys[0]}s.",
                          codes_of(ind), latest, ind.pub or group.pub),
            "meta": _meta(group, f"{ind.title}: Decade Averages", "India, average per decade", ind.suffix,
                          ind.color or group.color,
                          f"{ind.what} Annual values are averaged within each decade to smooth year-to-year noise.",
                          f"Compare bars left to right: the {keys[-1]}s average is {_fmt(values[-1], ind.dec)}{ind.suffix} "
                          f"against {_fmt(values[0], ind.dec)}{ind.suffix} in the {keys[0]}s. {ind.hint}", ind.why),
        }

    def pie(group, spec: Pie):
        data = [(label, fetch(code)["IND"]) for code, label in spec.comps]
        common = set.intersection(*(set(rows) for _, rows in data))
        if not common:
            raise ValueError(f"No common year for {spec.slug}")
        year = max(common, key=int)
        parts = [(label, rows[year]) for label, rows in data]
        if spec.remainder:
            total = fetch(spec.remainder[0])["IND"].get(year)
            if total is None:
                raise ValueError(f"No total for {spec.slug}")
            parts.append((spec.remainder[1], total - sum(v for _, v in parts)))
        parts = [(label, value) for label, value in parts if value > 0]
        total = sum(v for _, v in parts)
        if len(parts) < 2 or total <= 0:
            raise ValueError(f"Too few positive components for {spec.slug}")
        parts.sort(key=lambda item: -item[1])
        codes = ", ".join(code for code, _ in spec.comps) + (f", {spec.remainder[0]}" if spec.remainder else "")
        top = parts[0]
        return {
            "labels": [label for label, _ in parts], "values": [round(v / total * 100, 2) for _, v in parts],
            "chartType": "doughnut", "scope": "category", "source": f"World Bank API {codes}", "unit": "%",
            "note": _note(f"{spec.title}, {year}: {top[0]} is the largest slice at {top[1] / total * 100:.1f}%.",
                          codes, year, spec.pub or group.pub),
            "meta": _meta(group, f"{spec.title} ({year})", f"India, shares of total, {year}", "%", group.color,
                          spec.what, f"{spec.hint} In {year}, {top[0]} is the largest slice at {top[1] / total * 100:.1f}%.",
                          spec.why),
        }

    def multi(group, spec: Multi):
        data = [(label, {y: v / spec.scale for y, v in fetch(code)["IND"].items()}) for code, label in spec.comps]
        years = sorted({y for _, rows in data for y in rows}, key=int)
        datasets = [{"label": label, "color": LINE_COLORS[i], "values": [round(rows[y], 2) if y in rows else None for y in years]}
                    for i, (label, rows) in enumerate(data)]
        latest = years[-1]
        return {
            "labels": years, "datasets": datasets, "source": "World Bank API " + ", ".join(c for c, _ in spec.comps),
            "unit": spec.suffix.strip(),
            "note": _note(f"{spec.title}, {years[0]} to {latest}.", ", ".join(c for c, _ in spec.comps), latest,
                          spec.pub or group.pub),
            "meta": _meta(group, spec.title, f"India, {years[0]}-{latest}", spec.suffix, group.color,
                          spec.what, spec.hint, spec.why),
        }

    builders: dict[str, Callable[[], dict]] = {}
    for group in SUBGROUPS_SPEC:
        for item in group.items:
            if isinstance(item, Pie):
                builders[f"xp_{item.slug}_pie"] = (lambda g=group, s=item: pie(g, s))
            elif isinstance(item, Multi):
                builders[f"xp_{item.slug}_multi"] = (lambda g=group, s=item: multi(g, s))
            else:
                slug = _slug(item.code)
                for letter in item.kinds:
                    def make(g=group, i=item, k=letter):
                        observed = observed_for(i)
                        if k == "T":
                            return trend(g, i, observed)
                        if k == "P":
                            return peers(g, i, observed)
                        if k == "R":
                            return ranking(g, i, observed)
                        if k == "D":
                            return decade(g, i, observed)
                        return ranking(g, i, observed, doughnut=True)
                    builders[f"xp_{slug}_{KIND_NAMES[letter]}"] = make

    series: dict[str, dict] = {}
    for key, build in builders.items():
        try:
            series[key] = build()
        except Exception:  # keep the last good series when the API is unavailable
            if previous.get(key, {}).get("values") or previous.get(key, {}).get("datasets"):
                series[key] = previous[key]
    return series


def _summarise(series: dict[str, dict]) -> dict[str, dict[str, int]]:
    counts: dict[str, dict[str, int]] = {}
    for item in series.values():
        meta = item["meta"]
        counts.setdefault(meta["category"], {}).setdefault(meta["subgroup"], 0)
        counts[meta["category"]][meta["subgroup"]] += 1
    return counts


if __name__ == "__main__":
    import json
    import time
    import urllib.request

    def live_get(url: str) -> object:
        request = urllib.request.Request(url, headers={"User-Agent": "india-journey-expansion/1.0"})
        with urllib.request.urlopen(request, timeout=60) as response:
            return json.load(response)

    started = time.time()
    built = build_expansion_layer(live_get, {})
    counts = _summarise(built)
    for category, subgroups in counts.items():
        print(f"{category}: {sum(subgroups.values())}")
        for subgroup, count in subgroups.items():
            print(f"    {subgroup}: {count}")
    print(f"TOTAL: {len(built)} series in {time.time() - started:.1f}s")
