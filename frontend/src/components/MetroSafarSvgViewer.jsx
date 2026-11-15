import { useEffect, useRef, useState, useMemo, useCallback } from 'react';
import { METRO_SAFAR_SVGS } from '../data/metroSafarSvgs.js';
import './MetroSafarSvgViewer.css';

export const CITY_SVG_MAP = {
  'delhi-ncr': { file: 'delhi-metro-map.svg', name: 'Delhi-NCR (DMRC & RRTS)' },
  'mumbai': { file: 'mumbai-metro-map.svg', name: 'Mumbai Metro (MMRDA)' },
  'bengaluru': { file: 'bangalore-metro-map.svg', name: 'Bengaluru Metro (Namma Metro)' },
  'kolkata': { file: 'kolkata-metro-map.svg', name: 'Kolkata Metro (KMRCL)' },
  'chennai': { file: 'chennai-metro-map.svg', name: 'Chennai Metro (CMRL)' },
  'hyderabad': { file: 'hyderabad-metro-map.svg', name: 'Hyderabad Metro (HMRL)' },
  'ahmedabad': { file: 'ahmedabad-metro-map.svg', name: 'Ahmedabad Metro (GMRC)' },
  'pune': { file: 'pune-metro-map.svg', name: 'Pune Metro (Maha Metro)' },
  'kochi': { file: 'kochi-metro-map.svg', name: 'Kochi Metro (KMRL)' },
  'lucknow': { file: 'lucknow-metro-map.svg', name: 'Lucknow Metro (UPMRC)' },
  'nagpur': { file: 'nagpur-metro-map.svg', name: 'Nagpur Metro (Maha Metro)' },
  'kanpur': { file: 'kanpur-metro-map.svg', name: 'Kanpur Metro (UPMRC)' },
  'jaipur': { file: 'jaipur-metro-map.svg', name: 'Jaipur Metro (JMRC)' },
  'noida': { file: 'noida-metro-map.svg', name: 'Noida Metro (Aqua Line NMRC)' },
  'gurgaon': { file: 'gurgaon-metro-map.svg', name: 'Rapid Metro Gurugram' },
  'navi-mumbai': { file: 'navi-mumbai-metro-map.svg', name: 'Navi Mumbai Metro (CIDCO)' },
  'delhi-meerut-rrts': { file: 'delhi-meerut-rrts-metro-map.svg', name: 'Delhi-Meerut Namo Bharat RRTS' },
};

export default function MetroSafarSvgViewer({ cityKey = 'delhi-ncr' }) {
  const containerRef = useRef(null);
  const svgWrapperRef = useRef(null);

  // Pan / Zoom state
  const [transform, setTransform] = useState({ x: 0, y: 0, scale: 1 });
  const [searchQuery, setSearchQuery] = useState('');
  const [matchCount, setMatchCount] = useState(0);

  const cityInfo = CITY_SVG_MAP[cityKey] || CITY_SVG_MAP['delhi-ncr'];
  const svgContent = METRO_SAFAR_SVGS[cityKey] || METRO_SAFAR_SVGS['delhi-ncr'] || '';

  // Reset transform when cityKey changes
  useEffect(() => {
    setTransform({ x: 0, y: 0, scale: 1 });
    setSearchQuery('');
    setMatchCount(0);
  }, [cityKey]);

  // Pan & Zoom Handlers
  const dragRef = useRef({ dragging: false, startX: 0, startY: 0, moved: 0 });

  const handleMouseDown = e => {
    if (e.target.closest('.metrosafar-controls') || e.target.closest('.metrosafar-search-card')) return;
    dragRef.current = {
      dragging: true,
      startX: e.clientX - transform.x,
      startY: e.clientY - transform.y,
      moved: 0,
    };
  };

  const handleMouseMove = e => {
    if (!dragRef.current.dragging) return;
    const newX = e.clientX - dragRef.current.startX;
    const newY = e.clientY - dragRef.current.startY;
    setTransform(prev => ({ ...prev, x: newX, y: newY }));
  };

  const handleMouseUp = () => {
    dragRef.current.dragging = false;
  };

  const handleWheel = e => {
    e.preventDefault();
    const factor = e.deltaY < 0 ? 1.15 : 0.88;
    setTransform(prev => ({
      ...prev,
      scale: Math.max(0.4, Math.min(6, prev.scale * factor)),
    }));
  };

  const zoomIn = () => setTransform(prev => ({ ...prev, scale: Math.min(6, prev.scale * 1.25) }));
  const zoomOut = () => setTransform(prev => ({ ...prev, scale: Math.max(0.4, prev.scale * 0.8) }));
  const resetZoom = () => setTransform({ x: 0, y: 0, scale: 1 });

  const downloadSvg = () => {
    const blob = new Blob([svgContent], { type: 'image/svg+xml;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${cityKey}-metro-map-metrosafar.svg`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  // Highlight Search Matches in SVG DOM
  useEffect(() => {
    if (!svgWrapperRef.current || !searchQuery.trim()) {
      if (svgWrapperRef.current) {
        const highlighted = svgWrapperRef.current.querySelectorAll('.station-search-hit');
        highlighted.forEach(el => el.classList.remove('station-search-hit'));
      }
      setMatchCount(0);
      return;
    }

    const q = searchQuery.toLowerCase().trim();
    const textNodes = svgWrapperRef.current.querySelectorAll('text, tspan');
    let count = 0;
    let firstMatch = null;

    textNodes.forEach(node => {
      const text = (node.textContent || '').toLowerCase();
      if (q.length >= 2 && text.includes(q)) {
        node.classList.add('station-search-hit');
        count++;
        if (!firstMatch) firstMatch = node;
      } else {
        node.classList.remove('station-search-hit');
      }
    });

    setMatchCount(count);

    if (firstMatch && containerRef.current) {
      try {
        const rect = firstMatch.getBoundingClientRect();
        const cRect = containerRef.current.getBoundingClientRect();
        const dx = cRect.left + cRect.width / 2 - (rect.left + rect.width / 2);
        const dy = cRect.top + cRect.height / 2 - (rect.top + rect.height / 2);
        setTransform(prev => ({
          ...prev,
          x: prev.x + dx,
          y: prev.y + dy,
          scale: Math.max(prev.scale, 1.8),
        }));
      } catch (e) {
        // Mock environment safe
      }
    }
  }, [searchQuery, svgContent]);

  return (
    <div
      className="metrosafar-viewer-container"
      ref={containerRef}
      onMouseDown={handleMouseDown}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onWheel={handleWheel}
    >
      {/* Search Bar Floating Card */}
      <div className="metrosafar-search-card">
        <div className="search-input-wrapper">
          <span className="search-icon">🔍</span>
          <input
            type="text"
            className="station-search-input"
            placeholder={`Search station in ${cityInfo.name}...`}
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
          />
          {searchQuery && (
            <button
              type="button"
              className="clear-search-btn"
              onClick={() => setSearchQuery('')}
            >
              ✕
            </button>
          )}
        </div>
        {searchQuery.trim().length >= 2 && (
          <div className="search-status-bar">
            {matchCount > 0
              ? `Found ${matchCount} station match${matchCount > 1 ? 'es' : ''} on map`
              : 'No matching stations found on this map'}
          </div>
        )}
      </div>

      {/* Official Top-Left Legend & Title */}
      <div className="metrosafar-legend-box" aria-label="Route Map Legend">
        <div className="ms-legend-title">{cityInfo.name} Metro Route Map</div>
        <div className="ms-legend-sub">Authentic Vector Transit Map · metrosafar.com</div>
      </div>

      {/* Floating Canvas Controls */}
      <div className="metrosafar-controls">
        <button type="button" onClick={zoomIn} title="Zoom In">+</button>
        <button type="button" onClick={zoomOut} title="Zoom Out">−</button>
        <button type="button" onClick={resetZoom} title="Reset View">↺</button>
        <button type="button" className="download-btn" onClick={downloadSvg} title="Download Original SVG">
          ⤓ SVG Map
        </button>
      </div>

      {/* Official Attribution Badge */}
      <div className="metrosafar-badge metro-safar-badge">
        <div className="brand-text">Metro सफ़र (Metro Safar)</div>
        <div className="brand-url">metrosafar.com</div>
      </div>

      {/* Authentic SVG Map Canvas */}
      <div
        className="metrosafar-svg-stage"
        style={{
          transform: `translate(${transform.x}px, ${transform.y}px) scale(${transform.scale})`,
          transformOrigin: 'center center',
        }}
        ref={svgWrapperRef}
        dangerouslySetInnerHTML={{ __html: svgContent }}
      />
    </div>
  );
}
