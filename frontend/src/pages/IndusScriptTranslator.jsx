import { useState, useMemo } from 'react';
import { Link } from 'react-router-dom';
import decryptionData from '../data/indus-script-decryption.json';
import ArtBackdrop from '../components/ArtBackdrop.jsx';
import './IndusScriptTranslator.css';

export default function IndusScriptTranslator() {
  const { seals, keyboard_signs, meta } = decryptionData;

  const [selectedSealId, setSelectedSealId] = useState('M-304');
  const [activeMode, setActiveMode] = useState('famous-seals'); // 'famous-seals' | 'custom-builder'
  const [customSigns, setCustomSigns] = useState(['M-59', 'M-102', 'M-211', 'M-342']);
  const [searchQuery, setSearchQuery] = useState('');
  const [comparisonModel, setComparisonModel] = useState('sanskrit-cryptanalytic'); // 'sanskrit-cryptanalytic' | 'dravidian-rebus' | 'both'

  const currentSeal = useMemo(() => {
    return seals.find(s => s.id === selectedSealId) || seals[0];
  }, [seals, selectedSealId]);

  // Handle adding sign to custom sequence (Right-to-Left, max 8)
  const handleAddSign = (signObj) => {
    if (customSigns.length < 10) {
      setCustomSigns([signObj.id, ...customSigns]);
    }
  };

  const handleRemoveSign = (index) => {
    setCustomSigns(customSigns.filter((_, idx) => idx !== index));
  };

  const handleClear = () => {
    setCustomSigns([]);
  };

  // Dynamically decode custom signs sequence
  const customDecoded = useMemo(() => {
    const sequenceObjs = customSigns.map(id => keyboard_signs.find(s => s.id === id) || {
      id, name: 'Unknown Sign', phonetic_syllable: '?', brahmi_char: '𑀅', devanagari_char: '?', sanskrit_cryptanalytic: '?'
    });

    // Reversed because Indus script reads Right-to-Left
    const syllables = sequenceObjs.map(s => s.phonetic_syllable).join('-');
    const devanagari = sequenceObjs.map(s => s.devanagari_char).join('');
    const brahmi = sequenceObjs.map(s => s.brahmi_char).join(' ');

    return {
      sequenceObjs,
      syllables,
      devanagari,
      brahmi,
      grammatical_gloss: sequenceObjs.map(s => s.sanskrit_cryptanalytic).join(' + ')
    };
  }, [customSigns, keyboard_signs]);

  return (
    <div className="ivc-translator-page">
      <ArtBackdrop art="indus-script.svg" />

      {/* Hero Header */}
      <header className="translator-hero">
        <div className="translator-tag-row">
          <span className="translator-kicker">EPIGRAPHIC CRYPTANALYSIS WORKBENCH</span>
          <span className="source-badge">
            Reference Platform: <a href="https://indusscript.net/" target="_blank" rel="noopener noreferrer">indusscript.net</a>
          </span>
        </div>
        <h1>Indus Valley Script Decryption & Translation Engine</h1>
        <p className="translator-lead">
          Decode the 4,000-year-old writing of the Indus Valley Civilisation. Modelled after the computational
          cryptanalytic framework on <strong>indusscript.net</strong>, explore Right-to-Left grapheme mapping,
          Brahmi-Sanskrit morphological parsing, and side-by-side Dravidian Rebus comparisons.
        </p>

        <div className="translator-quick-links">
          <Link to="/explore?category=indus-valley-civilisation" className="btn btn-ghost">
            ← Explore Indus Valley Civilisation Group
          </Link>
          <a
            href="https://indusscript.net/"
            target="_blank"
            rel="noopener noreferrer"
            className="btn btn-primary external-link"
          >
            Visit Official indusscript.net Repository ↗
          </a>
        </div>
      </header>

      {/* Mode Navigation */}
      <nav className="translator-mode-tabs" aria-label="Decryption Modes">
        <button
          type="button"
          className={`mode-tab-btn ${activeMode === 'famous-seals' ? 'active' : ''}`}
          onClick={() => setActiveMode('famous-seals')}
        >
          Famous Excavated Seals Corpus ({seals.length})
        </button>
        <button
          type="button"
          className={`mode-tab-btn ${activeMode === 'custom-builder' ? 'active' : ''}`}
          onClick={() => setActiveMode('custom-builder')}
        >
          Interactive Sign Keyboard & Custom Decrypter
        </button>
      </nav>

      {/* MODE 1: FAMOUS SEALS CORPUS */}
      {activeMode === 'famous-seals' && currentSeal && (
        <section className="seal-decryption-section">
          {/* Seals Horizontal Picker */}
          <div className="seals-picker-strip">
            <span className="picker-label">Select Excavated Seal:</span>
            <div className="seals-buttons-row">
              {seals.map(seal => (
                <button
                  key={seal.id}
                  type="button"
                  className={`seal-select-btn ${seal.id === selectedSealId ? 'active' : ''}`}
                  onClick={() => setSelectedSealId(seal.id)}
                >
                  <strong>{seal.id}</strong>
                  <span>{seal.site}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Active Seal Translation Card */}
          <div className="decryption-master-card">
            <div className="seal-meta-bar">
              <div>
                <span className="meta-provenance">{currentSeal.site} • {currentSeal.provenance}</span>
                <h2>{currentSeal.seal_no}</h2>
                <span className="meta-location">Preserved at: {currentSeal.current_location}</span>
              </div>
              <div className="reading-indicator-box">
                <span className="arrow-glyph">←</span>
                <div>
                  <strong>Right-to-Left Reading Flow</strong>
                  <small>Standard Harappan Epigraphic Syntax</small>
                </div>
              </div>
            </div>

            {/* Inscription Glyph Ribbon (Right-to-Left) */}
            <div className="inscription-display-ribbon">
              <div className="ribbon-labels">
                <span>Start Reading (Right)</span>
                <span className="arrow-flow">← ← ← ← ←</span>
                <span>End / Suffix (Left)</span>
              </div>

              <div className="glyphs-stage rtl-direction">
                {currentSeal.signs.map((sign, idx) => (
                  <div key={idx} className="glyph-cell">
                    <span className="cell-pos">Sign #{idx + 1}</span>
                    <div className="glyph-vector-box">
                      <svg viewBox="0 0 80 80" className="glyph-svg" aria-hidden="true">
                        <path
                          d={sign.svg_path}
                          fill="none"
                          stroke="currentColor"
                          strokeWidth="3.2"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                        />
                      </svg>
                    </div>
                    <span className="sign-id">{sign.id}</span>
                    <span className="brahmi-equivalent" title="Brahmi Character Equivalent">
                      {sign.brahmi} ({sign.devanagari})
                    </span>
                    <span className="phonetic-syllable">/{sign.syllable}/</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Model Comparison Filter */}
            <div className="comparison-controls">
              <span className="comp-label">Decipherment Methodology:</span>
              <div className="comp-toggle-group">
                <button
                  type="button"
                  className={comparisonModel === 'sanskrit-cryptanalytic' ? 'active' : ''}
                  onClick={() => setComparisonModel('sanskrit-cryptanalytic')}
                >
                  Sanskrit Cryptanalytic (indusscript.net)
                </button>
                <button
                  type="button"
                  className={comparisonModel === 'dravidian-rebus' ? 'active' : ''}
                  onClick={() => setComparisonModel('dravidian-rebus')}
                >
                  Dravidian Rebus (Parpola / Mahadevan)
                </button>
                <button
                  type="button"
                  className={comparisonModel === 'both' ? 'active' : ''}
                  onClick={() => setComparisonModel('both')}
                >
                  Side-by-Side Comparison
                </button>
              </div>
            </div>

            {/* Decoded Translation Output */}
            <div className="translation-result-grid">
              {(comparisonModel === 'sanskrit-cryptanalytic' || comparisonModel === 'both') && (
                <div className="decryption-panel sanskrit-panel">
                  <div className="panel-badge">
                    <span>SANSKRIT CRYPTANALYTIC MODEL</span>
                    <small>indusscript.net / Yajnadevam</small>
                  </div>

                  <div className="panel-main-result">
                    <span className="devanagari-output">{currentSeal.cryptanalytic_decryption.devanagari_reading}</span>
                    <span className="translit-output">{currentSeal.cryptanalytic_decryption.transliterated_sanskrit}</span>
                    <p className="translation-quote">
                      {currentSeal.cryptanalytic_decryption.english_translation}
                    </p>
                  </div>

                  <div className="analysis-breakdown">
                    <h4>Morphological & Grammatical Parse</h4>
                    <p><strong>Morphemes:</strong> <code>{currentSeal.cryptanalytic_decryption.segmented_morphemes}</code></p>
                    <p><strong>Grammar:</strong> {currentSeal.cryptanalytic_decryption.grammatical_breakdown}</p>
                    <p><strong>Contextual Meaning:</strong> {currentSeal.cryptanalytic_decryption.thematic_context}</p>
                  </div>
                </div>
              )}

              {(comparisonModel === 'dravidian-rebus' || comparisonModel === 'both') && (
                <div className="decryption-panel dravidian-panel">
                  <div className="panel-badge">
                    <span>DRAVIDIAN REBUS MODEL</span>
                    <small>Asko Parpola & Iravatham Mahadevan</small>
                  </div>

                  <div className="panel-main-result">
                    <span className="devanagari-output">{currentSeal.dravidian_rebus_reading.reconstruction}</span>
                    <p className="translation-quote">
                      {currentSeal.dravidian_rebus_reading.meaning}
                    </p>
                  </div>

                  <div className="analysis-breakdown">
                    <h4>Rebus Homophonic Principle</h4>
                    <p>
                      Interprets pictograms as phonetic puns based on Proto-Dravidian homophones
                      (e.g., <em>mīn</em> meaning both 'fish' and 'star', <em>kōl</em> meaning both 'arrow' and 'ruler').
                    </p>
                    <p><strong>Academic Status:</strong> Proponents: {currentSeal.dravidian_rebus_reading.proponents}</p>
                  </div>
                </div>
              )}
            </div>

            <div className="epigraphic-footnote">
              <strong>Academic Consensus Note:</strong> {currentSeal.academic_consensus_note}
            </div>
          </div>
        </section>
      )}

      {/* MODE 2: INTERACTIVE GLYPH KEYBOARD & CUSTOM DECRYPTER */}
      {activeMode === 'custom-builder' && (
        <section className="custom-decrypter-section">
          {/* Builder Canvas Ribbon */}
          <div className="custom-canvas-box">
            <div className="canvas-header-bar">
              <span className="canvas-title">
                ← ACTIVE INSCRIPTION RIBBON ({customSigns.length}/10 SIGNS — RIGHT-TO-LEFT)
              </span>
              <button
                type="button"
                className="clear-btn"
                onClick={handleClear}
                disabled={customSigns.length === 0}
              >
                Clear Inscription
              </button>
            </div>

            <div className="custom-glyphs-ribbon rtl-direction">
              {customSigns.length === 0 ? (
                <div className="empty-ribbon-tip">
                  Click any glyph from the keyboard palette below to compose your Harappan seal inscription!
                </div>
              ) : (
                customSigns.map((signId, idx) => {
                  const signObj = keyboard_signs.find(s => s.id === signId) || {
                    id: signId, name: 'Sign', svg_path: '', phonetic_syllable: '?'
                  };
                  return (
                    <div
                      key={idx}
                      className="token-glyph-cell"
                      onClick={() => handleRemoveSign(idx)}
                      title="Click to remove glyph"
                    >
                      <span className="token-index">#{idx + 1}</span>
                      <svg viewBox="0 0 80 80" className="glyph-svg">
                        <path
                          d={signObj.svg_path}
                          fill="none"
                          stroke="currentColor"
                          strokeWidth="3.2"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                        />
                      </svg>
                      <span className="token-id">{signObj.id}</span>
                      <span className="token-phoneme">/{signObj.phonetic_syllable}/</span>
                      <span className="token-del-tip">×</span>
                    </div>
                  );
                })
              )}
            </div>

            {/* Instant Real-Time Cryptanalytic Translation of Custom Ribbon */}
            {customSigns.length > 0 && (
              <div className="custom-live-decryption-strip">
                <div className="live-decryption-col">
                  <span className="live-k">Phonetic Transcription (RTL)</span>
                  <span className="live-v">{customDecoded.syllables}</span>
                </div>
                <div className="live-decryption-col">
                  <span className="live-k">Devanagari Rendering</span>
                  <span className="live-v devanagari-live">{customDecoded.devanagari}</span>
                </div>
                <div className="live-decryption-col">
                  <span className="live-k">Brahmi Equivalent Script</span>
                  <span className="live-v brahmi-live">{customDecoded.brahmi}</span>
                </div>
                <div className="live-decryption-col full-w">
                  <span className="live-k">Sanskrit Cryptanalytic Morphological Gloss</span>
                  <span className="live-v">{customDecoded.grammatical_gloss}</span>
                </div>
              </div>
            )}
          </div>

          {/* Interactive Grapheme Keyboard */}
          <div className="keyboard-palette-card">
            <div className="keyboard-header">
              <div>
                <h3>Standard Indus Grapheme Keyboard (Mahadevan Concordance)</h3>
                <p>Click any sign to append to your inscription ribbon. Hover to inspect phonetic attributes.</p>
              </div>
              <input
                type="search"
                placeholder="Filter signs (e.g. jar, fish, arrow, sun)..."
                value={searchQuery}
                onChange={e => setSearchQuery(e.target.value)}
                className="palette-search-input"
              />
            </div>

            <div className="keyboard-grid">
              {keyboard_signs
                .filter(s => !searchQuery.trim() || s.name.toLowerCase().includes(searchQuery.toLowerCase()) || s.id.toLowerCase().includes(searchQuery.toLowerCase()))
                .map(sign => (
                  <button
                    key={sign.id}
                    type="button"
                    className="key-btn"
                    onClick={() => handleAddSign(sign)}
                  >
                    <div className="key-svg-wrap">
                      <svg viewBox="0 0 80 80" className="glyph-svg">
                        <path
                          d={sign.svg_path}
                          fill="none"
                          stroke="currentColor"
                          strokeWidth="3.2"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                        />
                      </svg>
                    </div>
                    <span className="key-id">{sign.id}</span>
                    <span className="key-syllable">/{sign.phonetic_syllable}/</span>
                    <span className="key-brahmi">{sign.brahmi_char} ({sign.devanagari_char})</span>
                  </button>
                ))}
            </div>
          </div>
        </section>
      )}

      {/* Epigraphic Methodology Reference */}
      <footer className="translator-footer-note">
        <h3>Cryptanalytic & Linguistic Methodology Notes</h3>
        <p>
          This translation tool illustrates the computational research methodology developed by independent cryptographers
          and researchers on <a href="https://indusscript.net/" target="_blank" rel="noopener noreferrer">indusscript.net</a>,
          alongside classic academic corpora from the <em>Corpus of Indus Seals and Inscriptions (CISI)</em> by Asko Parpola and
          Iravatham Mahadevan's <em>The Indus Script: Texts, Concordance and Tables</em> (ASI 1977).
        </p>
        <p>
          Mainstream academic epigraphy maintains that until a verified bilingual inscription (analogous to the Rosetta Stone)
          is excavated, all decipherments remain working scientific hypotheses. Statistical entropy studies (Rao et al., <em>Science</em> 2009)
          rigorously prove that Indus sign sequences match the conditional entropy and structure of human natural language.
        </p>
      </footer>
    </div>
  );
}
