import { useEffect, useRef, useState } from 'react';

const prefersReducedMotion = () =>
  typeof window !== 'undefined' && window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;

/**
 * Illustrated, animated backdrop for heroes: the SVG scene cross-fades when `art` changes, slowly zooms,
 * and shifts with the pointer and scroll for a parallax feel. Purely decorative (aria-hidden).
 */
export default function ArtBackdrop({ art, className = '' }) {
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
      node.style.setProperty('--sy', String(Math.min(window.scrollY, 600)));
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
          <img src={`/art/${layer.art}`} alt="" decoding="async" draggable="false" />
        </div>
      ))}
    </div>
  );
}
