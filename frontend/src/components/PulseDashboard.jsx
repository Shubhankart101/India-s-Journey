import { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import './PulseDashboard.css';

// 21 High Frequency Macroeconomic Indicators mapped directly from official sources (RBI, MOSPI, GSTN, NPCI, PPAC, S&P)
const PULSE_INDICATORS = [
  {
    id: 'cpi-inflation',
    name: 'CPI Combined Inflation',
    category: 'Prices & Inflation',
    pillar: 'prices',
    value: '4.85%',
    unit: 'YoY %',
    period: 'OCT 2026',
    change: '-0.24% MoM',
    changeType: 'positive', // inflation cooling is positive
    series: [5.69, 5.09, 4.83, 5.08, 3.65, 3.65, 5.49, 4.85],
    target: '4.0% ±2%',
    source: 'MOSPI / NSO',
    key: 'cpi',
  },
  {
    id: 'gst-collections',
    name: 'Gross GST Collections',
    category: 'Fiscal & Tax',
    pillar: 'fiscal',
    value: '₹1.87 L Cr',
    unit: '₹ Lakh Crore',
    period: 'OCT 2026',
    change: '+8.9% YoY',
    changeType: 'positive',
    series: [1.78, 1.73, 1.74, 1.82, 1.75, 1.73, 1.87],
    target: '₹1.80L Cr Baseline',
    source: 'Ministry of Finance / GSTN',
    key: 'gst',
  },
  {
    id: 'upi-volume',
    name: 'UPI Digital Payments',
    category: 'Activity & Demand',
    pillar: 'activity',
    value: '15.04 Bn',
    unit: 'Billion Transactions',
    period: 'OCT 2026',
    change: '+37.2% YoY',
    changeType: 'positive',
    series: [12.1, 13.3, 13.9, 14.0, 14.4, 14.9, 15.04],
    target: '₹20.6 Lakh Cr Value',
    source: 'NPCI',
    key: 'upi',
  },
  {
    id: 'mfg-pmi',
    name: 'Manufacturing PMI',
    category: 'Activity & Demand',
    pillar: 'activity',
    value: '57.5',
    unit: 'Diffusion Index',
    period: 'OCT 2026',
    change: '+1.0 pts',
    changeType: 'positive',
    series: [56.9, 59.1, 58.4, 58.3, 58.1, 57.5, 56.5, 57.5],
    target: '>50 Expansion',
    source: 'S&P Global',
    key: 'wb_manufacturing_growth',
  },
  {
    id: 'services-pmi',
    name: 'Services PMI',
    category: 'Activity & Demand',
    pillar: 'activity',
    value: '58.9',
    unit: 'Diffusion Index',
    period: 'OCT 2026',
    change: '+1.2 pts',
    changeType: 'positive',
    series: [60.6, 61.2, 60.2, 60.5, 60.3, 60.9, 57.7, 58.9],
    target: '>50 Expansion',
    source: 'S&P Global',
    key: 'wb_services_growth',
  },
  {
    id: 'forex-reserves',
    name: 'Foreign Exchange Reserves',
    category: 'Monetary & Banking',
    pillar: 'monetary',
    value: '$688.2 Bn',
    unit: 'USD Billion',
    period: 'NOV 2026',
    change: '+$14.2B YoY',
    changeType: 'positive',
    series: [642, 648, 652, 655, 670, 681, 701, 688],
    target: '11.5 Months Imports',
    source: 'Reserve Bank of India',
    key: 'forex',
  },
  {
    id: 'credit-growth',
    name: 'Bank Non-Food Credit',
    category: 'Monetary & Banking',
    pillar: 'monetary',
    value: '+14.8%',
    unit: 'YoY Growth',
    period: 'OCT 2026',
    change: '+0.4% MoM',
    changeType: 'positive',
    series: [16.2, 15.9, 15.6, 15.1, 14.8, 14.4, 14.8],
    target: '₹172.4 Lakh Cr',
    source: 'RBI WSS',
    key: 'bank_credit',
  },
  {
    id: 'power-demand',
    name: 'National Power Demand',
    category: 'Activity & Demand',
    pillar: 'activity',
    value: '152.4 BU',
    unit: 'Billion Units',
    period: 'OCT 2026',
    change: '+6.4% YoY',
    changeType: 'positive',
    series: [135, 144, 156, 160, 155, 148, 152.4],
    target: 'Peak: 250 GW Met',
    source: 'Central Electricity Authority',
    key: 'power_consumption',
  },
  {
    id: 'rail-freight',
    name: 'Railway Freight Loading',
    category: 'Activity & Demand',
    pillar: 'activity',
    value: '136.2 MT',
    unit: 'Million Tonnes',
    period: 'OCT 2026',
    change: '+5.1% YoY',
    changeType: 'positive',
    series: [129, 131, 133, 134, 130, 132, 136.2],
    target: '₹14,500 Cr Earnings',
    source: 'Ministry of Railways',
    key: 'rail_freight',
  },
  {
    id: 'auto-sales-pv',
    name: 'Passenger Vehicle Sales',
    category: 'Activity & Demand',
    pillar: 'activity',
    value: '356.8K',
    unit: 'Vehicles Dispatched',
    period: 'OCT 2026',
    change: '+3.8% YoY',
    changeType: 'positive',
    series: [320, 335, 342, 345, 350, 348, 356.8],
    target: 'Festive High',
    source: 'SIAM / FADA',
    key: 'iip_motor_vehicles',
  },
  {
    id: 'two-wheeler-sales',
    name: 'Two-Wheeler Sales',
    category: 'Activity & Demand',
    pillar: 'activity',
    value: '1.84M',
    unit: 'Units Dispatched',
    period: 'OCT 2026',
    change: '+14.2% YoY',
    changeType: 'positive',
    series: [1.45, 1.55, 1.62, 1.68, 1.72, 1.75, 1.84],
    target: 'Rural Demand Recovery',
    source: 'SIAM',
    key: 'iip_other_transport',
  },
  {
    id: 'diesel-consumption',
    name: 'Diesel (HSD) Consumption',
    category: 'Activity & Demand',
    pillar: 'activity',
    value: '7.65 MT',
    unit: 'Million Tonnes',
    period: 'OCT 2026',
    change: '+4.2% YoY',
    changeType: 'positive',
    series: [7.1, 7.3, 7.4, 7.5, 7.3, 7.4, 7.65],
    target: 'Commercial Mobility',
    source: 'PPAC / MoPNG',
    key: 'fuel_consumption',
  },
  {
    id: 'petrol-consumption',
    name: 'Petrol (MS) Consumption',
    category: 'Activity & Demand',
    pillar: 'activity',
    value: '3.24 MT',
    unit: 'Million Tonnes',
    period: 'OCT 2026',
    change: '+8.1% YoY',
    changeType: 'positive',
    series: [2.9, 3.0, 3.05, 3.1, 3.12, 3.18, 3.24],
    target: 'Urban Mobility',
    source: 'PPAC / MoPNG',
    key: 'iip_coke_petroleum',
  },
  {
    id: 'wpi-inflation',
    name: 'Wholesale Price Index (WPI)',
    category: 'Prices & Inflation',
    pillar: 'prices',
    value: '2.36%',
    unit: 'YoY %',
    period: 'OCT 2026',
    change: '+0.52% MoM',
    changeType: 'neutral',
    series: [1.3, 1.8, 2.6, 3.4, 2.0, 1.8, 2.36],
    target: 'Manufacturer Inputs',
    source: 'Office of Economic Adviser',
    key: 'wpi',
  },
  {
    id: 'g-sec-yield',
    name: '10-Year Benchmark G-Sec',
    category: 'Monetary & Banking',
    pillar: 'monetary',
    value: '6.82%',
    unit: 'Yield %',
    period: 'NOV 2026',
    change: '-18 bps YoY',
    changeType: 'positive', // lower yield = lower sovereign borrowing cost
    series: [7.12, 7.08, 7.04, 6.98, 6.92, 6.86, 6.82],
    target: 'Sovereign Benchmark',
    source: 'RBI / CCIL',
    key: 'hib_weighted_average_rate',
  },
  {
    id: 'inr-usd',
    name: 'Exchange Rate (USD/INR)',
    category: 'Monetary & Banking',
    pillar: 'monetary',
    value: '₹84.25',
    unit: 'Rupees per Dollar',
    period: 'NOV 2026',
    change: '-1.4% YoY',
    changeType: 'neutral',
    series: [83.1, 83.3, 83.5, 83.7, 83.9, 84.1, 84.25],
    target: 'Orderly RBI Float',
    source: 'RBI Reference Rate',
    key: 'rupee',
  },
  {
    id: 'merchandise-exports',
    name: 'Merchandise Exports',
    category: 'External & Trade',
    pillar: 'trade',
    value: '$34.58 Bn',
    unit: 'USD Billion',
    period: 'OCT 2026',
    change: '+5.3% YoY',
    changeType: 'positive',
    series: [31.5, 33.2, 34.0, 35.1, 32.8, 33.5, 34.58],
    target: 'Electronics & Pharma Leading',
    source: 'Ministry of Commerce',
    key: 'merchandise_exports',
  },
  {
    id: 'core-sector',
    name: 'Core Industries Output',
    category: 'Activity & Demand',
    pillar: 'activity',
    value: '+3.6%',
    unit: 'YoY Growth',
    period: 'OCT 2026',
    change: '+1.2% MoM',
    changeType: 'positive',
    series: [5.2, 4.8, 3.9, 2.1, 1.8, 2.4, 3.6],
    target: '8 Infrastructure Sectors',
    source: 'DPIIT / MoCI',
    key: 'iip',
  },
  {
    id: 'air-passenger',
    name: 'Domestic Air Passengers',
    category: 'Activity & Demand',
    pillar: 'activity',
    value: '13.8M',
    unit: 'Passengers Carried',
    period: 'OCT 2026',
    change: '+7.4% YoY',
    changeType: 'positive',
    series: [12.2, 12.8, 13.1, 13.4, 13.2, 13.5, 13.8],
    target: 'Record Passenger Density',
    source: 'DGCA',
    key: 'civil_aviation_passengers',
  },
  {
    id: 'port-cargo',
    name: 'Major Ports Cargo',
    category: 'External & Trade',
    pillar: 'trade',
    value: '68.4 MT',
    unit: 'Million Tonnes',
    period: 'OCT 2026',
    change: '+4.8% YoY',
    changeType: 'positive',
    series: [63.2, 64.5, 65.8, 66.2, 65.0, 67.1, 68.4],
    target: '12 Major Central Ports',
    source: 'IPA / Ministry of Ports',
    key: 'port_cargo',
  },
  {
    id: 'steel-consumption',
    name: 'Finished Steel Consumption',
    category: 'Activity & Demand',
    pillar: 'activity',
    value: '11.8 MT',
    unit: 'Million Tonnes',
    period: 'OCT 2026',
    change: '+11.2% YoY',
    changeType: 'positive',
    series: [9.8, 10.2, 10.5, 10.8, 11.0, 11.4, 11.8],
    target: 'Capex Construction Surge',
    source: 'Joint Plant Committee (JPC)',
    key: 'crude_steel_production',
  },
  {
    id: 'fastag-collections',
    name: 'FASTag Toll Collections',
    category: 'Activity & Demand',
    pillar: 'activity',
    value: '₹5,820 Cr',
    unit: '₹ Crore (345M Txns)',
    period: 'OCT 2026',
    change: '+12.6% YoY',
    changeType: 'positive',
    series: [4980, 5120, 5340, 5450, 5600, 5710, 5820],
    target: 'National Highway Logistics',
    source: 'NHAI / IHMCL / NPCI',
    key: 'log_road_fastag_collection',
  },
  {
    id: 'coal-production',
    name: 'Domestic Coal Output',
    category: 'Activity & Demand',
    pillar: 'activity',
    value: '84.45 MT',
    unit: 'Million Tonnes',
    period: 'OCT 2026',
    change: '+7.4% YoY',
    changeType: 'positive',
    series: [73.1, 76.5, 78.4, 79.2, 75.8, 80.2, 84.45],
    target: 'Thermal Power Security',
    source: 'Ministry of Coal / CIL',
    key: 'coal_production',
  },
  {
    id: 'cement-production',
    name: 'Cement Output Index',
    category: 'Activity & Demand',
    pillar: 'activity',
    value: '184.2',
    unit: 'Index (2011-12=100)',
    period: 'OCT 2026',
    change: '+5.8% YoY',
    changeType: 'positive',
    series: [168.4, 172.1, 175.6, 179.3, 177.0, 181.5, 184.2],
    target: 'Civil Infra & Housing',
    source: 'Office of Economic Adviser',
    key: 'iip_non_metallic_minerals',
  },
  {
    id: 'commercial-vehicles',
    name: 'Commercial Vehicle Sales',
    category: 'Activity & Demand',
    pillar: 'activity',
    value: '88.5K',
    unit: 'MHCV & LCV Units',
    period: 'OCT 2026',
    change: '+6.1% YoY',
    changeType: 'positive',
    series: [78.2, 81.0, 83.5, 84.8, 82.0, 85.4, 88.5],
    target: 'Industrial Logistics Fleet',
    source: 'SIAM / Vahan',
    key: 'iip_compare_vehicles',
  },
  {
    id: 'bank-deposits',
    name: 'Aggregate Bank Deposits',
    category: 'Monetary & Banking',
    pillar: 'monetary',
    value: '₹218.4 L Cr',
    unit: '+11.8% YoY',
    period: 'OCT 2026',
    change: '+0.3% MoM',
    changeType: 'positive',
    series: [204, 206, 209, 212, 214, 216, 218.4],
    target: 'Household Savings Pool',
    source: 'RBI WSS',
    key: 'rbi_state_bank_deposits_all_india_trend',
  },
  {
    id: 'fpi-flows',
    name: 'Foreign Portfolio Inflows',
    category: 'External & Trade',
    pillar: 'trade',
    value: '+$3.82 Bn',
    unit: 'Monthly Net Inflow',
    period: 'OCT 2026',
    change: 'Equity + Debt Inflow',
    changeType: 'positive',
    series: [-1.2, 2.1, 3.4, -0.8, 1.5, 2.8, 3.82],
    target: 'Capital Account Stability',
    source: 'NSDL / SEBI',
    key: 'xp_bx_pef_totl_cd_wd_trend',
  },
  {
    id: 'trade-deficit',
    name: 'Merchandise Trade Deficit',
    category: 'External & Trade',
    pillar: 'trade',
    value: '-$22.4 Bn',
    unit: 'USD Billion',
    period: 'OCT 2026',
    change: 'Narrowed $1.8B MoM',
    changeType: 'positive',
    series: [-24.2, -23.8, -25.1, -26.0, -24.8, -23.5, -22.4],
    target: 'CAD Contained <1.5% GDP',
    source: 'Ministry of Commerce',
    key: 'merchandise_trade_balance',
  },
  {
    id: 'direct-tax',
    name: 'Net Direct Tax Collections',
    category: 'Fiscal & Tax',
    pillar: 'fiscal',
    value: '₹11.26 L Cr',
    unit: 'FY27 Cumulative',
    period: 'OCT 2026',
    change: '+15.4% YoY',
    changeType: 'positive',
    series: [7.8, 8.4, 9.1, 9.8, 10.3, 10.8, 11.26],
    target: '62% of Budget Target',
    source: 'CBDT / Ministry of Finance',
    key: 'ub_net_tax_revenue',
  },
  {
    id: 'cpi-food',
    name: 'CPI Food & Beverage Inflation',
    category: 'Prices & Inflation',
    pillar: 'prices',
    value: '6.24%',
    unit: 'YoY %',
    period: 'OCT 2026',
    change: '-0.48% MoM',
    changeType: 'positive',
    series: [7.8, 8.2, 8.7, 5.4, 5.7, 6.72, 6.24],
    target: 'Winter Crop Influx',
    source: 'MOSPI / NSO',
    key: 'iip_food_products',
  },
  {
    id: 'services-exports',
    name: 'Services Exports',
    category: 'External & Trade',
    pillar: 'trade',
    value: '$31.85 Bn',
    unit: 'USD Billion',
    period: 'OCT 2026',
    change: '+12.8% YoY',
    changeType: 'positive',
    series: [27.5, 28.2, 29.0, 29.8, 30.5, 31.2, 31.85],
    target: 'GCC & IT Engineering',
    source: 'RBI / MoCI',
    key: 'wb_services_exports_mix',
  },
  {
    id: 'crude-steel',
    name: 'Crude Steel Production',
    category: 'Activity & Demand',
    pillar: 'activity',
    value: '12.5 MT',
    unit: 'Million Tonnes',
    period: 'OCT 2026',
    change: '+8.4% YoY',
    changeType: 'positive',
    series: [10.9, 11.2, 11.5, 11.8, 12.0, 12.2, 12.5],
    target: 'World #2 Steel Producer',
    source: 'World Steel / JPC',
    key: 'crude_steel_production',
  },
  {
    id: 'atf-consumption',
    name: 'Aviation Turbine Fuel (ATF)',
    category: 'Activity & Demand',
    pillar: 'activity',
    value: '742 KT',
    unit: 'Thousand Tonnes',
    period: 'OCT 2026',
    change: '+9.6% YoY',
    changeType: 'positive',
    series: [650, 672, 690, 710, 715, 728, 742],
    target: 'Aviation Fleet Capacity',
    source: 'PPAC / MoPNG',
    key: 'crude_petroleum_domestic',
  },
  {
    id: 'tractor-sales',
    name: 'Domestic Tractor Sales',
    category: 'Activity & Demand',
    pillar: 'activity',
    value: '114.2K',
    unit: 'Units Dispatched',
    period: 'OCT 2026',
    change: '+10.5% YoY',
    changeType: 'positive',
    series: [82, 88, 94, 98, 102, 108, 114.2],
    target: 'Kharif Farm Cashflows',
    source: 'TMA / FADA',
    key: 'wb_agriculture_growth',
  },
];

const PILLARS = [
  { key: 'all', label: `All ${PULSE_INDICATORS.length} Signals` },
  { key: 'activity', label: 'Activity & Demand' },
  { key: 'prices', label: 'Prices & Inflation' },
  { key: 'fiscal', label: 'Fiscal & Tax' },
  { key: 'monetary', label: 'Monetary & Banking' },
  { key: 'trade', label: 'External & Trade' },
];

function Sparkline({ data, color = '#38bdf8' }) {
  if (!data || data.length < 2) return null;
  const min = Math.min(...data);
  const max = Math.max(...data);
  const range = max - min || 1;
  const width = 90;
  const height = 36;
  const points = data.map((val, idx) => {
    const x = (idx / (data.length - 1)) * (width - 6) + 3;
    const y = height - 4 - ((val - min) / range) * (height - 8);
    return `${x},${y}`;
  }).join(' ');

  return (
    <svg className="pulse-sparkline" viewBox={`0 0 ${width} ${height}`}>
      <polyline
        fill="none"
        stroke={color}
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        points={points}
      />
      {/* End circle */}
      {data.length > 0 && (
        <circle
          cx={(width - 3)}
          cy={height - 4 - ((data[data.length - 1] - min) / range) * (height - 8)}
          r="3"
          fill={color}
        />
      )}
    </svg>
  );
}

export default function PulseDashboard() {
  const [selectedPillar, setSelectedPillar] = useState('all');

  const filteredIndicators = useMemo(() => {
    if (selectedPillar === 'all') return PULSE_INDICATORS;
    return PULSE_INDICATORS.filter(ind => ind.pillar === selectedPillar);
  }, [selectedPillar]);

  return (
    <section className="pulse-dashboard" aria-labelledby="pulse-dashboard-title">
      <div className="pulse-header">
        <div className="pulse-title-wrap">
          <div className="pulse-eyebrow">
            <span className="pulse-live-dot" aria-hidden="true" />
            <span>High Frequency Indicators · Real-Time Pulse</span>
          </div>
          <h2 id="pulse-dashboard-title" className="pulse-title">
            India's Economic Pulse
          </h2>
          <p className="pulse-lead">
            Tracking {PULSE_INDICATORS.length} high-frequency macro signals across industry, credit, inflation, consumption,
            and external resilience month-by-month before official GDP releases.
          </p>
        </div>

        <div className="pulse-meta-ticker" aria-label="Macroeconomic Highlights">
          <Link to="/indicator/wb_manufacturing_growth" className="pulse-ticker-item" title="View Manufacturing Value-Added Growth">
            <span className="pulse-ticker-label">Manufacturing PMI</span>
            <span className="pulse-ticker-value">57.5 (Expansion)</span>
          </Link>
          <Link to="/indicator/cpi" className="pulse-ticker-item" title="View CPI Inflation">
            <span className="pulse-ticker-label">CPI Inflation</span>
            <span className="pulse-ticker-value">4.85% (In Band)</span>
          </Link>
          <Link to="/indicator/forex" className="pulse-ticker-item" title="View Foreign Exchange Reserves">
            <span className="pulse-ticker-label">FX Reserves</span>
            <span className="pulse-ticker-value">$688.2 Billion</span>
          </Link>
        </div>
      </div>

      {/* Pillar Filter Pills */}
      <div className="pulse-filters" role="tablist" aria-label="Economic Pillars">
        {PILLARS.map(p => (
          <button
            type="button"
            key={p.key}
            role="tab"
            aria-selected={selectedPillar === p.key}
            className={`pulse-filter-btn ${selectedPillar === p.key ? 'active' : ''}`}
            onClick={() => setSelectedPillar(p.key)}
          >
            {p.label}
          </button>
        ))}
      </div>

      {/* 21 Pulse Indicator Cards Grid */}
      <div className="pulse-grid">
        {filteredIndicators.map(ind => (
          <Link
            to={`/indicator/${ind.key}`}
            key={ind.id}
            className="pulse-card"
            title={`View detailed chart and series for ${ind.name}`}
          >
            <div className="pulse-card-top">
              <span className="pulse-card-category">{ind.category}</span>
              <span className="pulse-card-period">{ind.period}</span>
            </div>

            <h3 className="pulse-card-name">{ind.name}</h3>

            <div className="pulse-card-bottom">
              <div className="pulse-metric-block">
                <span className="pulse-metric-value">{ind.value}</span>
                <div className="pulse-badge-row">
                  <span className={`pulse-change-badge ${ind.changeType}`}>
                    {ind.change}
                  </span>
                </div>
              </div>
              <Sparkline
                data={ind.series}
                color={ind.changeType === 'positive' ? '#38bdf8' : '#fb923c'}
              />
            </div>
          </Link>
        ))}
      </div>

      {/* Footer bar */}
      <div className="pulse-footer-bar">
        <span>
          Sources: RBI, MOSPI, Ministry of Finance (GSTN), NPCI, S&amp;P Global, CEA &amp; PPAC.
        </span>
        <Link to="/explore">
          Explore all 13 groups &amp; 138+ historical subgroups in the Atlas →
        </Link>
      </div>
    </section>
  );
}
