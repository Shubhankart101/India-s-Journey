import { useEffect, useRef, useState } from 'react';
import { ART_INTERVAL_MS } from '../art.js';

const prefersReducedMotion = () =>
  typeof window !== 'undefined' && window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;

/** Cycles through a playlist of scenes, pausing while the tab is hidden or motion is reduced. */
function useArtCycle(art, interval) {
  const list = Array.isArray(art) ? art.filter(Boolean) : [art].filter(Boolean);
  const listKey = list.join('|');
  const [index, setIndex] = useState(0);

  useEffect(() => {
    setIndex(0);
    if (list.length < 2 || prefersReducedMotion()) return undefined;
    const timer = setInterval(() => {
      if (typeof document !== 'undefined' && document.hidden) return;
      setIndex(current => {
        const next = (current + 1) % list.length;
        const preload = new Image();
        preload.src = `/art/${list[(next + 1) % list.length]}`;
        return next;
      });
    }, interval);
    return () => clearInterval(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [listKey, interval]);

  return list[index % Math.max(list.length, 1)];
}

const textFreeCache = new Map();

/** Art SVGs embed a title/caption; strip it so no text floats behind page content. */
function useTextFreeArt(art) {
  const url = art ? `/art/${art}` : '';
  const [src, setSrc] = useState(() => textFreeCache.get(url) || url);
  useEffect(() => {
    if (!url) return undefined;
    if (textFreeCache.has(url)) { setSrc(textFreeCache.get(url)); return undefined; }
    if (!url.endsWith('.svg') || typeof fetch !== 'function' || typeof URL.createObjectURL !== 'function') {
      setSrc(url);
      return undefined;
    }
    let alive = true;
    fetch(url)
      .then(res => (res.ok ? res.text() : Promise.reject(new Error('art'))))
      .then(text => {
        const clean = text.replace(/<text\b[\s\S]*?<\/text>/g, '');
        const blob = URL.createObjectURL(new Blob([clean], { type: 'image/svg+xml' }));
        textFreeCache.set(url, blob);
        if (alive) setSrc(blob);
      })
      .catch(() => { if (alive) setSrc(url); });
    return () => { alive = false; };
  }, [url]);
  return src;
}

function ArtImage({ art }) {
  const src = useTextFreeArt(art);
  return <img src={src} alt="" decoding="async" draggable="false" />;
}

/**
 * Illustrated, animated page backdrop: the SVG scene cross-fades when `art` changes (or rotates when
 * `art` is a playlist), slowly zooms, carries drifting light motes, and shifts with the pointer and
 * scroll for a parallax feel. Purely decorative (aria-hidden).
 */
export default function ArtBackdrop({ art: source, className = '', interval = ART_INTERVAL_MS }) {
  const art = useArtCycle(source, interval);
  const ref = useRef(null);
  const [layers, setLayers] = useState(() => (art ? [{ art, id: 0 }] : []));

  useEffect(() => {
    if (!art) return undefined;
    setLayers(current => {
      const last = current[current.length - 1];
      if (last?.art === art) return current;
      return [...current.slice(-1), { art, id: (last?.id ?? -1) + 1 }];
    });
    const timer = setTimeout(() => setLayers(current => current.slice(-1)), 1200);
    return () => clearTimeout(timer);
  }, [art]);

  useEffect(() => {
    const node = ref.current;
    if (!node || prefersReducedMotion()) return undefined;
    let frame = 0;
    let pointer = { x: 0, y: 0 };
    const paint = () => {
      frame = 0;
      node.style.setProperty('--px', pointer.x.toFixed(3));
      node.style.setProperty('--py', pointer.y.toFixed(3));
      node.style.setProperty('--sy', String(Math.min(window.scrollY, 1500)));
    };
    const schedule = () => { if (!frame) frame = requestAnimationFrame(paint); };
    const onPointer = event => {
      pointer = { x: event.clientX / window.innerWidth - 0.5, y: event.clientY / window.innerHeight - 0.5 };
      schedule();
    };
    window.addEventListener('pointermove', onPointer, { passive: true });
    window.addEventListener('scroll', schedule, { passive: true });
    return () => {
      window.removeEventListener('pointermove', onPointer);
      window.removeEventListener('scroll', schedule);
      if (frame) cancelAnimationFrame(frame);
    };
  }, []);

  return (
    <div ref={ref} className={`art-backdrop ${className}`.trim()} aria-hidden="true" data-art={art || ''}>
      {layers.map(layer => (
        <div key={layer.id} className="art-layer">
          <ArtImage art={layer.art} />
        </div>
      ))}
      <div className="art-motes" />
    </div>
  );
}
