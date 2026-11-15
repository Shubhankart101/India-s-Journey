import { useMemo, useState } from 'react';
import './PeerInfographic.css';

export const INFOGRAPHICS_DATA = {
  'agri-exporters': {
    eyebrow: 'Global Benchmark & Decadal Shift · 2014 to 2024',
    title: 'India Farm Growth Vs Top 20 Agri Exporters (2014 to 2024)',
    subtitle: 'Comparing India’s agricultural superpower production volume against global export value and decadal expansion across the world’s top agricultural trading nations.',
    callouts: [
      { metric: '2.4% Share', label: 'Global Agri Export Share', note: 'Rank #8 worldwide in exports' },
      { metric: '+62.2%', label: 'Decadal Export Growth', note: '$32.8B (2014) → $53.2B peak' },
      { metric: '#1 / #2 Global', label: 'Production Standing', note: '#1 Milk & Pulses, #2 Rice & Wheat' },
      { metric: '4.1% CAGR', label: 'Farm GVA Real Growth', note: 'Consistent decade-long expansion', highlight: true },
    ],
    insight: 'The Core Paradox: India is the world\'s second largest producer of food by absolute volume, yet accounts for less than 2.5% of world agricultural export value. While top exporters like the US, the Netherlands, and Brazil command immense margins through high-value food processing, cold-chain logistics, and predictable export policies, India’s export basket has historically remained concentrated in bulk commodities (non-basmati rice, marine products, sugar, spices) subject to frequent domestic price-stabilization export bans.',
    peers: [
      { rank: 1, country: 'United States', val2014: 144.2, val2024: 178.5, cagr: '+23.8%', share: '10.2%' },
      { rank: 2, country: 'Brazil', val2014: 78.4, val2024: 128.2, cagr: '+63.5%', share: '7.3%' },
      { rank: 3, country: 'Netherlands', val2014: 82.5, val2024: 124.6, cagr: '+51.0%', share: '7.1%' },
      { rank: 4, country: 'Germany', val2014: 71.3, val2024: 92.4, cagr: '+29.6%', share: '5.3%' },
      { rank: 5, country: 'China', val2014: 64.1, val2024: 88.0, cagr: '+37.3%', share: '5.0%' },
      { rank: 6, country: 'France', val2014: 66.8, val2024: 84.1, cagr: '+25.9%', share: '4.8%' },
      { rank: 7, country: 'Canada', val2014: 47.3, val2024: 68.4, cagr: '+44.6%', share: '3.9%' },
      { rank: 8, country: 'India 🇮🇳', val2014: 32.8, val2024: 53.2, cagr: '+62.2%', share: '2.4%', isIndia: true },
      { rank: 9, country: 'Spain', val2014: 43.2, val2024: 64.5, cagr: '+49.3%', share: '3.7%' },
      { rank: 10, country: 'Indonesia', val2014: 30.1, val2024: 46.8, cagr: '+55.5%', share: '2.7%' },
      { rank: 11, country: 'Italy', val2014: 41.5, val2024: 58.6, cagr: '+41.2%', share: '3.3%' },
      { rank: 12, country: 'Belgium', val2014: 37.2, val2024: 52.1, cagr: '+40.1%', share: '3.0%' },
      { rank: 13, country: 'Australia', val2014: 38.6, val2024: 49.3, cagr: '+27.7%', share: '2.8%' },
      { rank: 14, country: 'Poland', val2014: 26.4, val2024: 47.8, cagr: '+81.1%', share: '2.7%' },
      { rank: 15, country: 'Thailand', val2014: 36.1, val2024: 44.5, cagr: '+23.3%', share: '2.5%' },
      { rank: 16, country: 'Argentina', val2014: 34.2, val2024: 42.1, cagr: '+23.1%', share: '2.4%' },
      { rank: 17, country: 'Mexico', val2014: 25.4, val2024: 44.2, cagr: '+74.0%', share: '2.5%' },
      { rank: 18, country: 'United Kingdom', val2014: 27.8, val2024: 32.4, cagr: '+16.5%', share: '1.8%' },
      { rank: 19, country: 'Vietnam', val2014: 22.1, val2024: 39.4, cagr: '+78.3%', share: '2.2%' },
      { rank: 20, country: 'New Zealand', val2014: 21.4, val2024: 29.8, cagr: '+39.3%', share: '1.7%' },
    ],
    source: 'WTO International Trade Statistics, UN Comtrade & APEDA Agricultural Export Database (2014–2024)',
  },
  'electronics-mfg': {
    eyebrow: 'Industrial Transformation · 2014 to 2024',
    title: 'India Electronics & Hardware Manufacturing vs Asian Peers (2014 to 2024)',
    subtitle: 'Tracking India’s smartphone, mobile assembly, and precision electronics export surge under Production Linked Incentive (PLI) schemes versus East Asian manufacturing hubs.',
    callouts: [
      { metric: '$29.1 Bn', label: 'Electronics Exports (2024)', note: 'Surging from $6.5B in 2014' },
      { metric: '+347%', label: 'Decadal Export Growth', note: 'Fastest in major Asian economies', highlight: true },
      { metric: '99%', label: 'Domestic Phone Assembly', note: 'Import substitution from 22% in 2014' },
      { metric: '#5 Global', label: 'Smartphone Assembly Rank', note: 'Apple & Samsung production hubs' },
    ],
    insight: 'The Electronics Pivot: In 2014, India was heavily import-dependent, importing over 78% of all consumed mobile handsets and assembling merely 60 million units annually. By 2024, annual domestic mobile manufacturing scaled past 330 million units, with electronics exports leaping to $29.1 Billion—becoming India’s fifth-largest export category driven by global value chain integration.',
    peers: [
      { rank: 1, country: 'China', val2014: 570.0, val2024: 890.0, cagr: '+56.1%', share: '32.0%' },
      { rank: 2, country: 'Taiwan', val2014: 110.0, val2024: 205.0, cagr: '+86.4%', share: '7.4%' },
      { rank: 3, country: 'South Korea', val2014: 125.0, val2024: 168.0, cagr: '+34.4%', share: '6.0%' },
      { rank: 4, country: 'Vietnam', val2014: 36.5, val2024: 122.0, cagr: '+234.2%', share: '4.4%' },
      { rank: 5, country: 'Malaysia', val2014: 62.0, val2024: 98.0, cagr: '+58.1%', share: '3.5%' },
      { rank: 6, country: 'India 🇮🇳', val2014: 6.5, val2024: 29.1, cagr: '+347.7%', share: '1.1%', isIndia: true },
      { rank: 7, country: 'Thailand', val2014: 32.0, val2024: 46.0, cagr: '+43.8%', share: '1.6%' },
      { rank: 8, country: 'Philippines', val2014: 24.0, val2024: 38.0, cagr: '+58.3%', share: '1.4%' },
      { rank: 9, country: 'Indonesia', val2014: 9.0, val2024: 15.5, cagr: '+72.2%', share: '0.6%' },
    ],
    source: 'Ministry of Electronics & Information Technology (MeitY), DGFT & ITC Trade Map (2014–2024)',
  },
  'upi-payments': {
    eyebrow: 'Digital Public Infrastructure · 2016 to 2024',
    title: 'India UPI vs Top Global Real-Time Payment Networks',
    subtitle: 'Analyzing global instant payment volumes where India’s Unified Payments Interface commands nearly half of all real-time digital transactions recorded globally.',
    callouts: [
      { metric: '131 Billion', label: 'Annual UPI Transactions', note: 'Calendar Year 2024 total', highlight: true },
      { metric: '49%', label: 'Share of Global Instant Txns', note: 'ACI Worldwide Real-Time Report' },
      { metric: '₹200+ L Cr', label: 'Annual Transacted Value', note: 'Over $2.4 Trillion USD equivalent' },
      { metric: 'Zero MDR', label: 'Merchant Fee Model', note: 'Public good rails for 350M+ users' },
    ],
    insight: 'Digital Public Goods at Scale: Launched in 2016 with just 21 banks and 100,000 monthly transactions, UPI expanded by over 130,000x over eight years. India processed more real-time transactions in 2024 than the next four countries (Brazil, China, Thailand, and South Korea) combined, demonstrating the leapfrogging power of open protocol digital public infrastructure.',
    peers: [
      { rank: 1, country: 'India (UPI) 🇮🇳', val2014: 0.1, val2024: 131.2, cagr: '+131100%', share: '48.5%', isIndia: true },
      { rank: 2, country: 'Brazil (Pix)', val2014: 0.0, val2024: 42.0, cagr: 'New (2020)', share: '15.5%' },
      { rank: 3, country: 'China (e-CNY / IBPS)', val2014: 2.5, val2024: 18.5, cagr: '+640%', share: '6.8%' },
      { rank: 4, country: 'Thailand (PromptPay)', val2014: 0.0, val2024: 10.4, cagr: 'New (2017)', share: '3.8%' },
      { rank: 5, country: 'South Korea', val2014: 4.8, val2024: 8.2, cagr: '+70.8%', share: '3.0%' },
      { rank: 6, country: 'United Kingdom (FPS)', val2014: 1.1, val2024: 4.5, cagr: '+309%', share: '1.7%' },
      { rank: 7, country: 'United States (FedNow/RTP)', val2014: 0.2, val2024: 1.8, cagr: '+800%', share: '0.7%' },
    ],
    source: 'National Payments Corporation of India (NPCI) & ACI Worldwide Prime-Time for Real-Time Report (2024)',
  },
};

export default function PeerInfographic({ id = 'agri-exporters' }) {
  const [metricMode, setMetricMode] = useState('val2024'); // 'val2024' | 'cagr'
  const data = INFOGRAPHICS_DATA[id] || INFOGRAPHICS_DATA['agri-exporters'];

  const maxVal = useMemo(() => {
    return Math.max(...data.peers.map(p => p.val2024));
  }, [data]);

  return (
    <article className="peer-infographic-card" aria-label={data.title}>
      {/* Header */}
      <div className="peer-info-header">
        <span className="peer-info-eyebrow">
          <span>📊</span>
          <span>{data.eyebrow}</span>
        </span>
        <h3 className="peer-info-title">{data.title}</h3>
        <p className="peer-info-subtitle">{data.subtitle}</p>
      </div>

      {/* Callouts */}
      <div className="peer-callouts-grid">
        {data.callouts.map((c, idx) => (
          <div key={idx} className={`peer-callout-box ${c.highlight ? 'highlight' : ''}`}>
            <span className="peer-callout-metric">{c.metric}</span>
            <span className="peer-callout-label">{c.label}</span>
            <span className="peer-callout-note">{c.note}</span>
          </div>
        ))}
      </div>

      {/* Insight Banner */}
      <div className="peer-insight-banner">
        <strong>Strategic Analysis: </strong>
        {data.insight}
      </div>

      {/* Mode Toggles */}
      <div style={{ display: 'flex', gap: '8px', marginBottom: '16px' }}>
        <button
          type="button"
          className={`btn ${metricMode === 'val2024' ? 'btn-primary' : 'btn-ghost'}`}
          style={{ fontSize: '0.8rem', padding: '6px 14px' }}
          onClick={() => setMetricMode('val2024')}
        >
          Latest Value ($ Billion / Bn Txn)
        </button>
        <button
          type="button"
          className={`btn ${metricMode === 'cagr' ? 'btn-primary' : 'btn-ghost'}`}
          style={{ fontSize: '0.8rem', padding: '6px 14px' }}
          onClick={() => setMetricMode('cagr')}
        >
          Decadal Expansion Rate (%)
        </button>
      </div>

      {/* Table */}
      <div className="peer-table-container">
        <table className="peer-table">
          <thead>
            <tr>
              <th style={{ width: '60px' }}>Rank</th>
              <th>Country / System</th>
              <th style={{ width: '120px' }}>2014 Baseline</th>
              <th style={{ width: '260px' }}>2024 Value &amp; Bar</th>
              <th style={{ width: '110px' }}>Decadal Shift</th>
              <th style={{ width: '100px' }}>Global Share</th>
            </tr>
          </thead>
          <tbody>
            {data.peers.map(p => {
              const barPercent = Math.round((p.val2024 / maxVal) * 100);
              return (
                <tr key={p.country} className={p.isIndia ? 'peer-row-highlight' : ''}>
                  <td>
                    <span className="peer-rank-badge">{p.rank}</span>
                  </td>
                  <td>
                    <strong>{p.country}</strong>
                  </td>
                  <td>{p.val2014}</td>
                  <td>
                    <span className="peer-bar-track">
                      <span className="peer-bar-fill" style={{ width: `${barPercent}%` }} />
                    </span>
                    <strong>{p.val2024}</strong>
                  </td>
                  <td>
                    <span style={{ color: p.isIndia ? '#f59e0b' : '#38bdf8', fontWeight: 700 }}>
                      {p.cagr}
                    </span>
                  </td>
                  <td>{p.share}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Footer Source */}
      <div className="peer-info-footer">
        <span><strong>Official Sources:</strong> {data.source}</span>
        <span>India's Journey Atlas · Peer Benchmark Explorer</span>
      </div>
    </article>
  );
}
