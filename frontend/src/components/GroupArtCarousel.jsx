import { useState, useEffect } from 'react';
import { assetUrl } from '../config.js';
import './GroupArtCarousel.css';

const SLIDE_INTERVAL_MS = 5500;

export default function GroupArtCarousel({ groupSlug, title = 'Living Historical Artworks' }) {
  const isIvc = groupSlug?.includes('indus');
  const isEmpires = groupSlug?.includes('empire');

  const artworks = isIvc ? [
    { file: 'indus-valley.svg', title: 'Metropolises & Citadels', desc: 'Mohenjo-daro & Harappa: Baked brick citadels, Great Bath, and orthogonal grid urbanism' },
    { file: 'ivc-artifacts.svg', title: 'Bronze & Steatite Statuary', desc: 'Naturalistic lost-wax bronze Dancing Girl and the steatite Priest-King sculpture' },
    { file: 'indus-trade.svg', title: 'Maritime Seafaring & Lothal Dockyard', desc: 'Tidal lock-gate dockyard at Lothal and Meluhha maritime commerce with Mesopotamia and Dilmun' },
    { file: 'indus-script.svg', title: 'The Indus Epigraphic Script', desc: 'Dholavira 10-glyph citadel signboard and Right-to-Left sign positional concordance' },
    { file: 'ivc-excavations.svg', title: 'Excavation Sites & Stratigraphy', desc: '49+ excavated sites across 9 modern nations from the Oxus to the Arabian Sea' },
  ] : isEmpires ? [
    { file: 'ancient-empires.svg', title: 'Imperial Standards & Lion Capital', desc: 'The Ashokan Sarnath quad-lion capital, symbol of pan-Indian sovereignty (600 BCE – 850 CE)' },
    { file: 'mahajanapadas.svg', title: '16 Mahajanapadas & Early Republics', desc: 'Magadha, Kosala, Vatsa, Avanti, and the Licchavi oligarchic Vajji gana-sangha' },
    { file: 'magadha-nanda.svg', title: 'Magadha & Nanda Empire', desc: 'First pan-North Indian empire with 200,000 standing infantry and 4,000 war elephants' },
    { file: 'alexander-campaign.svg', title: "Alexander's Macedonian Frontier", desc: 'Battle of the Hydaspes (326 BCE), altars at the Hyphasis, and the Indus river descent' },
    { file: 'maurya-empire.svg', title: 'Mauryan Pan-Indian Zenith', desc: 'Emperor Ashoka the Great, Brahmi Rock Edicts, and 5 million sq km imperial hegemony' },
    { file: 'indo-greek.svg', title: 'Indo-Greek Kingdom & Shungas', desc: 'King Menander I (Milinda), bilingual silver drachms, and Gandharan Hellenistic synthesis' },
    { file: 'satavahana-empire.svg', title: 'Satavahana Deccan Hegemony', desc: 'Lord of the Three Seas (Trisamudradhipati), Gautamiputra Satakarni, and Amaravati stupas' },
    { file: 'kushan-empire.svg', title: 'Kushan Empire & The Silk Road', desc: 'Emperor Kanishka I, Rabatak inscription, and trans-Eurasian trade crossroad' },
    { file: 'gupta-empire.svg', title: 'Gupta Classical Golden Age', desc: 'Samudragupta, Chandragupta II Vikramaditya, Aryabhata, and Classical Sanskrit flowering' },
    { file: 'harsha-empire.svg', title: 'Vardhana Empire of Harsha', desc: 'Kannauj assembly, Chinese pilgrim Xuanzang, and the historic Battle of the Narmada' },
    { file: 'southern-dynasties.svg', title: 'Classical Southern Dynasties', desc: 'Chola, Chera, Pandya, and Pallava maritime fleets, Sangam epics, and temple architecture' },
  ] : [];

  const [currentIndex, setCurrentIndex] = useState(0);
  const [paused, setPaused] = useState(false);

  useEffect(() => {
    if (paused || artworks.length < 2) return undefined;
    const timer = setInterval(() => {
      setCurrentIndex(prev => (prev + 1) % artworks.length);
    }, SLIDE_INTERVAL_MS);
    return () => clearInterval(timer);
  }, [paused, artworks.length]);

  if (!artworks.length) return null;

  const current = artworks[currentIndex];

  return (
    <section
      className="group-art-carousel"
      aria-label={`${title} Carousel`}
      onPointerEnter={() => setPaused(true)}
      onPointerLeave={() => setPaused(false)}
      onFocus={() => setPaused(true)}
      onBlur={() => setPaused(false)}
    >
      <div className="art-carousel-display">
        <div className="art-carousel-img-frame">
          <img
            key={current.file}
            src={assetUrl(`art/${current.file}`)}
            alt={current.title}
            className="art-carousel-img animate-fade"
            loading="eager"
            decoding="async"
          />
          <div className="art-carousel-overlay">
            <span className="art-live-badge">
              <span className="live-dot" /> LIVE ROTATING ARTWORK ({currentIndex + 1} of {artworks.length})
            </span>
            <h4 className="art-current-title">{current.title}</h4>
            <p className="art-current-desc">{current.desc}</p>
          </div>
        </div>
      </div>

      {/* Selector Pills / Thumbnails */}
      <nav className="art-carousel-nav" aria-label="Artwork slides">
        {artworks.map((art, idx) => (
          <button
            key={art.file}
            type="button"
            className={`art-nav-pill ${currentIndex === idx ? 'active' : ''}`}
            onClick={() => setCurrentIndex(idx)}
            aria-label={`View artwork: ${art.title}`}
          >
            <span className="pill-num">{idx + 1}</span>
            <span className="pill-name">{art.title}</span>
          </button>
        ))}
      </nav>
    </section>
  );
}
