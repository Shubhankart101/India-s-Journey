import { useState } from 'react';
import scriptData from '../data/indus-script.json';
import './IndusScriptDecoder.css';

export default function IndusScriptDecoder() {
  const { meta, signs, famous_inscriptions } = scriptData;

  const [selectedInscId, setSelectedInscId] = useState(famous_inscriptions[0]?.id || 'dholavira-signboard');
  const [activeTheoryId, setActiveTheoryId] = useState('dravidian');
  const [activeTab, setActiveTab] = useState('inscriptions'); // 'inscriptions' | 'builder' | 'theories'
  const [customSequence, setCustomSequence] = useState(['M-342', 'M-102', 'M-211']);
  const [selectedSign, setSelectedSign] = useState(signs[0] || null);

  const currentInscription = famous_inscriptions.find(item => item.id === selectedInscId) || famous_inscriptions[0];
  const inscSigns = (currentInscription?.sign_sequence || currentInscription?.signs || []).map(item => {
    if (typeof item === 'string') {
      return signs.find(s => s.id === item) || { id: item, name: 'Indus Sign', svg_path: 'M20 20 L60 60 M60 20 L20 60', dravidian_reading: 'rebus' };
    }
    return item;
  });

  const handleAddSignToCustom = (signId) => {
    if (customSequence.length < 10) {
      setCustomSequence([...customSequence, signId]);
    }
  };

  const handleRemoveSign = (index) => {
    setCustomSequence(customSequence.filter((_, idx) => idx !== index));
  };

  const handleClearCustom = () => {
    setCustomSequence([]);
  };

  return (
    <div className="indus-decoder-container">
      {/* Header */}
      <header className="indus-decoder-header">
        <div className="decoder-tag">EPIGRAPHIC WORKBENCH & LINGUISTIC DECODER</div>
        <h2>The Indus Valley Script Decipherment Workbench</h2>
        <p className="decoder-lead">
          Decode the 4,000-year-old enigmatic Harappan writing system. Analyze corpus statistics,
          explore famous excavated seal inscriptions, and examine the leading decipherment hypotheses.
        </p>

        {/* Corpus Stats Bar */}
        <div className="decoder-stats-strip">
          <div className="decoder-stat-pill">
            <span className="stat-val">{meta.corpus_stats.total_inscriptions}</span>
            <span className="stat-lbl">Known Inscriptions</span>
          </div>
          <div className="decoder-stat-pill">
            <span className="stat-val">{meta.corpus_stats.unique_signs}</span>
            <span className="stat-lbl">Unique Signs</span>
          </div>
          <div className="decoder-stat-pill">
            <span className="stat-val">{meta.corpus_stats.average_inscription_length}</span>
            <span className="stat-lbl">Avg Signs / Seal</span>
          </div>
          <div className="decoder-stat-pill">
            <span className="stat-val">{meta.corpus_stats.dominant_direction.split(' ')[0]}</span>
            <span className="stat-lbl">86.5% Right-to-Left</span>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav className="decoder-tab-nav" aria-label="Script Explorer Sections">
        <button
          type="button"
          className={`decoder-tab-btn ${activeTab === 'inscriptions' ? 'active' : ''}`}
          onClick={() => setActiveTab('inscriptions')}
        >
          Famous Excavated Inscriptions ({famous_inscriptions.length})
        </button>
        <button
          type="button"
          className={`decoder-tab-btn ${activeTab === 'builder' ? 'active' : ''}`}
          onClick={() => setActiveTab('builder')}
        >
          Interactive Signboard Builder ({signs.length} Glyphs)
        </button>
        <button
          type="button"
          className={`decoder-tab-btn ${activeTab === 'theories' ? 'active' : ''}`}
          onClick={() => setActiveTab('theories')}
        >
          Decipherment Hypotheses ({meta.theories.length})
        </button>
      </nav>

      {/* TAB 1: FAMOUS INSCRIPTIONS */}
      {activeTab === 'inscriptions' && currentInscription && (
        <section className="decoder-inscriptions-view" aria-label="Famous Inscriptions Analysis">
          <div className="inscriptions-selector">
            {famous_inscriptions.map(insc => (
              <button
                key={insc.id}
                type="button"
                className={`insc-pill ${insc.id === selectedInscId ? 'active' : ''}`}
                onClick={() => setSelectedInscId(insc.id)}
              >
                <strong>{insc.title || insc.name}</strong>
                <span>{insc.site} • {insc.date}</span>
              </button>
            ))}
          </div>

          <div className="inscription-card">
            <div className="insc-header">
              <div>
                <span className="insc-sub">{currentInscription.site} • {currentInscription.date}</span>
                <h3 className="insc-title">{currentInscription.title || currentInscription.name}</h3>
                <p className="insc-context">{currentInscription.context}</p>
              </div>
              <div className="rtl-direction-banner" title="Indus Script reading direction is predominant Right to Left">
                <span className="rtl-arrow">←</span>
                <span>Reading Order: <strong>Right-to-Left</strong> ({currentInscription.reading_direction})</span>
              </div>
            </div>

            {/* Inscription Display Strip */}
            <div className="glyph-display-strip" role="group" aria-label="Right to left sign sequence">
              <div className="strip-direction-indicator">
                <span>Start Reading (Right)</span>
                <span className="arrow-line">← ← ←</span>
                <span>End Reading (Left)</span>
              </div>

              <div className="glyphs-row rtl-flow">
                {inscSigns.map((sign, idx) => (
                  <div key={idx} className="glyph-box">
                    <span className="glyph-pos">#{idx + 1}</span>
                    <div className="glyph-svg-wrap">
                      <svg viewBox="0 0 80 80" className="glyph-svg" aria-hidden="true">
                        <path d={sign.svg_path || 'M20 20 L60 60 M60 20 L20 60'} fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
                      </svg>
                    </div>
                    <span className="glyph-id">{sign.id}</span>
                    <span className="glyph-name">{sign.name}</span>
                    <span className="glyph-val" title="Rebus Dravidian Interpretation">
                      <em>{sign.dravidian_reading || sign.dravidian_val || sign.name}</em>
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Decipherment Analysis Tabs inside Inscription */}
            <div className="insc-analysis-grid">
              <div className="analysis-col">
                <h4>Epigraphic & Structural Analysis</h4>
                <p>{currentInscription.interpretation}</p>
              </div>
              <div className="analysis-col">
                <h4>Sign Concordance Insights</h4>
                <ul className="insights-list">
                  <li><strong>Total Glyphs:</strong> {inscSigns.length} standardized signs.</li>
                  <li><strong>Directionality:</strong> Verified via right-side sign cramming and overlapping incisions on terracotta sealings.</li>
                  <li><strong>Linguistic Sign Pattern:</strong> Positional clustering matches noun/proper-name + patronymic/genitive case endings.</li>
                </ul>
              </div>
            </div>
          </div>
        </section>
      )}

      {/* TAB 2: INTERACTIVE SIGNBOARD BUILDER */}
      {activeTab === 'builder' && (
        <section className="decoder-builder-view" aria-label="Interactive Signboard Builder">
          <div className="builder-header-info">
            <p className="builder-desc">
              Build your own Indus seal inscription by clicking signs from the concordance palette below.
              Observe how Harappan scribes composed right-to-left texts with terminal grammatical suffixes!
            </p>
            <div className="builder-actions">
              <button type="button" className="btn-builder" onClick={handleClearCustom} disabled={customSequence.length === 0}>
                Clear Signboard
              </button>
            </div>
          </div>

          {/* User Signboard Ribbon */}
          <div className="user-signboard-container">
            <div className="signboard-wood-frame">
              <div className="signboard-top-label">
                <span>← READING DIRECTION: RIGHT TO LEFT ({customSequence.length}/10 signs)</span>
              </div>

              <div className="user-glyphs-row rtl-flow">
                {customSequence.length === 0 ? (
                  <div className="empty-signboard-hint">
                    Click any glyph below to add signs to this signboard
                  </div>
                ) : (
                  customSequence.map((signId, idx) => {
                    const signObj = signs.find(s => s.id === signId) || { id: signId, name: 'Sign', svg_path: '' };
                    return (
                      <div key={idx} className="builder-glyph-token" onClick={() => handleRemoveSign(idx)} title="Click to remove">
                        <span className="token-pos">{idx + 1}</span>
                        <svg viewBox="0 0 80 80" className="glyph-svg">
                          <path d={signObj.svg_path} fill="none" stroke="currentColor" strokeWidth="3.2" strokeLinecap="round" strokeLinejoin="round" />
                        </svg>
                        <span className="token-id">{signObj.id}</span>
                        <span className="token-remove-tip">×</span>
                      </div>
                    );
                  })
                )}
              </div>
            </div>
          </div>

          {/* Sign Palette Grid */}
          <div className="signs-palette-section">
            <div className="palette-header">
              <h3>Standard Indus Sign Palette (Mahadevan Concordance)</h3>
              <span className="palette-tip">Click a sign to append to your inscription ribbon</span>
            </div>

            <div className="palette-grid">
              {signs.map(sign => (
                <div
                  key={sign.id}
                  className={`palette-card ${selectedSign?.id === sign.id ? 'selected' : ''}`}
                  onClick={() => {
                    setSelectedSign(sign);
                    handleAddSignToCustom(sign.id);
                  }}
                  role="button"
                  tabIndex={0}
                  onKeyDown={e => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      e.preventDefault();
                      setSelectedSign(sign);
                      handleAddSignToCustom(sign.id);
                    }
                  }}
                  aria-label={`${sign.name} (${sign.id})`}
                >
                  <div className="palette-svg-wrap">
                    <svg viewBox="0 0 80 80" className="glyph-svg">
                      <path d={sign.svg_path} fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                  </div>
                  <div className="palette-meta">
                    <span className="p-id">{sign.id}</span>
                    <span className="p-name">{sign.name}</span>
                    <span className="p-freq">{sign.frequency} occurrences</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Selected Sign Deep Dive Inspector */}
          {selectedSign && (
            <div className="sign-deep-dive">
              <div className="deep-dive-header">
                <svg viewBox="0 0 80 80" className="deep-dive-svg">
                  <path d={selectedSign.svg_path} fill="none" stroke="currentColor" strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
                <div>
                  <span className="deep-dive-badge">{selectedSign.id} • Mahadevan Corpus</span>
                  <h4>{selectedSign.name}</h4>
                  {selectedSign.name_hi && <p className="deep-dive-hi">{selectedSign.name_hi}</p>}
                </div>
              </div>
              <p className="deep-dive-desc">{selectedSign.description}</p>
              <div className="deep-dive-grid">
                <div className="dive-box">
                  <span className="dive-k">Corpus Frequency</span>
                  <span className="dive-v">{selectedSign.frequency} times (Rank #{selectedSign.frequency > 500 ? '1-3' : 'Top 15'})</span>
                </div>
                <div className="dive-box">
                  <span className="dive-k">Dominant Position</span>
                  <span className="dive-v">{selectedSign.position || (selectedSign.positional ? (selectedSign.positional.terminal > 50 ? 'Terminal (End of Signboard)' : selectedSign.positional.initial > 30 ? 'Initial (Start)' : 'Medial (Middle)') : 'Variable')}</span>
                </div>
                <div className="dive-box">
                  <span className="dive-k">Dravidian Rebus Value</span>
                  <span className="dive-v">{selectedSign.dravidian_reading || selectedSign.dravidian_val || 'kō / mīn'}</span>
                </div>
                <div className="dive-box">
                  <span className="dive-k">Indo-Aryan Reading</span>
                  <span className="dive-v">{selectedSign.rao_reading || selectedSign.indo_aryan_reading || 'pā / maha'}</span>
                </div>
              </div>
            </div>
          )}
        </section>
      )}

      {/* TAB 3: DECIPHERMENT THEORIES COMPARISON */}
      {activeTab === 'theories' && (
        <section className="decoder-theories-view" aria-label="Decipherment Hypotheses">
          <div className="theories-tabs">
            {meta.theories.map(t => (
              <button
                key={t.id}
                type="button"
                className={`theory-tab-btn ${t.id === activeTheoryId ? 'active' : ''}`}
                onClick={() => setActiveTheoryId(t.id)}
              >
                {t.name}
              </button>
            ))}
          </div>

          {(() => {
            const currentTheory = meta.theories.find(t => t.id === activeTheoryId) || meta.theories[0];
            return (
              <div className="theory-detail-card">
                <div className="theory-main-head">
                  <span className="theory-kicker">SCIENTIFIC DECIPHERMENT PARADIGM</span>
                  <h3>{currentTheory.name}</h3>
                  <p className="theory-proponents"><strong>Key Proponents:</strong> {currentTheory.proponents}</p>
                </div>

                <div className="theory-body-grid">
                  <div className="theory-col">
                    <h4>Linguistic / Epigraphic Framework</h4>
                    <p>{currentTheory.framework}</p>
                  </div>
                  <div className="theory-col">
                    <h4>Core Arguments & Evidentiary Support</h4>
                    <p>{currentTheory.strengths}</p>
                  </div>
                </div>

                <div className="theory-status-bar">
                  <strong>Consensus Status in Archeology:</strong> {currentTheory.status}
                </div>
              </div>
            );
          })()}
        </section>
      )}
    </div>
  );
}
