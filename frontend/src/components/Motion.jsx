import { useEffect, useRef, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';

export const prefersReducedMotion = () =>
  typeof window !== 'undefined' && Boolean(window.matchMedia?.('(prefers-reduced-motion: reduce)').matches);

const canObserve = () => typeof window !== 'undefined' && 'IntersectionObserver' in window && !prefersReducedMotion();

/** Thin gradient bar along the top edge that tracks how far the page has been scrolled. */
export function ScrollProgress() {
  const ref = useRef(null);
  useEffect(() => {
    let frame = 0;
    const paint = () => {
      frame = 0;
      const max = document.documentElement.scrollHeight - window.innerHeight;
      ref.current?.style.setProperty('--progress', String(max > 0 ? Math.min(window.scrollY / max, 1) : 0));
    };
    const schedule = () => { if (!frame) frame = requestAnimationFrame(paint); };
    paint();
    window.addEventListener('scroll', schedule, { passive: true });
    window.addEventListener('resize', schedule);
    return () => {
      window.removeEventListener('scroll', schedule);
      window.removeEventListener('resize', schedule);
      if (frame) cancelAnimationFrame(frame);
    };
  }, []);
  return <div ref={ref} className="scroll-progress" aria-hidden="true" />;
}

/** True once the page has scrolled past `offset` pixels. */
export function useScrolled(offset = 12) {
  const [scrolled, setScrolled] = useState(false);
  useEffect(() => {
    const update = () => setScrolled(window.scrollY > offset);
    update();
    window.addEventListener('scroll', update, { passive: true });
    return () => window.removeEventListener('scroll', update);
  }, [offset]);
  return scrolled;
}

export function ScrollTopButton() {
  const visible = useScrolled(500);
  return (
    <button
      type="button"
      className={`scroll-top${visible ? ' visible' : ''}`}
      aria-label="Back to top"
      tabIndex={visible ? 0 : -1}
      onClick={() => window.scrollTo({ top: 0, behavior: prefersReducedMotion() ? 'auto' : 'smooth' })}
    >
      ↑
    </button>
  );
}

const REVEAL_SELECTOR = '.section, .page-hero, .group-tile, .card, .picture-card, .article-list li, .stat-row > div, .marquee';

/**
 * Fades and lifts content into view as it scrolls in, for every page. Elements are tagged automatically
 * (including ones that render later), so pages need no wrappers. Without IntersectionObserver, or with
 * reduced motion, nothing is hidden.
 */
export function useAutoReveal() {
  const location = useLocation();
  useEffect(() => {
    if (!canObserve()) return undefined;
    const root = document.getElementById('main');
    if (!root) return undefined;
    const io = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-visible');
        io.unobserve(entry.target);
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    const tag = () => {
      root.querySelectorAll(REVEAL_SELECTOR).forEach((node, index) => {
        if (node.dataset.reveal) return;
        node.dataset.reveal = '1';
        const box = node.getBoundingClientRect();
        // Anything already on screen shows at once; only below-the-fold content animates in.
        if (box.top < window.innerHeight) { node.classList.add('is-visible'); return; }
        node.style.setProperty('--reveal-delay', `${(index % 4) * 70}ms`);
        node.classList.add('reveal');
        io.observe(node);
      });
    };
    tag();
    const mo = new MutationObserver(tag);
    mo.observe(root, { childList: true, subtree: true });
    return () => { mo.disconnect(); io.disconnect(); };
  }, [location.pathname]);
}

/**
 * Cursor-following glow on cards: one delegated listener sets --mx/--my on whichever card is under the pointer.
 */
export function usePointerSpotlight() {
  useEffect(() => {
    if (prefersReducedMotion() || !window.matchMedia?.('(hover: hover)').matches) return undefined;
    const onMove = event => {
      const card = event.target.closest?.('.card, .group-tile, .picture-card, .glass');
      if (!card) return;
      const box = card.getBoundingClientRect();
      card.style.setProperty('--mx', `${event.clientX - box.left}px`);
      card.style.setProperty('--my', `${event.clientY - box.top}px`);
    };
    document.addEventListener('pointermove', onMove, { passive: true });
    return () => document.removeEventListener('pointermove', onMove);
  }, []);
}

/** Counts up from 0 to `value` the first time it scrolls into view; renders the final value when motion is off. */
export function CountUp({ value, duration = 1400, format = n => Math.round(n).toLocaleString('en-IN') }) {
  const ref = useRef(null);
  const [shown, setShown] = useState(() => (canObserve() ? 0 : value));
  useEffect(() => {
    if (!canObserve()) { setShown(value); return undefined; }
    let frame = 0;
    const io = new IntersectionObserver(([entry]) => {
      if (!entry.isIntersecting) return;
      io.disconnect();
      const start = performance.now();
      const step = now => {
        const t = Math.min((now - start) / duration, 1);
        setShown(value * (1 - (1 - t) ** 3));
        if (t < 1) frame = requestAnimationFrame(step);
      };
      frame = requestAnimationFrame(step);
    });
    if (ref.current) io.observe(ref.current);
    return () => { io.disconnect(); if (frame) cancelAnimationFrame(frame); };
  }, [value, duration]);
  if (shown === value) return <span ref={ref} className="count-up">{format(value)}</span>;
  return (
    <span ref={ref} className="count-up">
      <span aria-hidden="true">{format(shown)}</span>
      <span className="sr-only">{format(value)}</span>
    </span>
  );
}

/** Types and deletes each phrase in turn with a blinking caret. Screen readers get the full list once. */
export function Typewriter({ phrases, typeMs = 70, holdMs = 1800 }) {
  const [state, setState] = useState({ index: 0, length: 0, deleting: false });
  const motion = !prefersReducedMotion();
  useEffect(() => {
    if (!motion || phrases.length === 0) return undefined;
    const phrase = phrases[state.index % phrases.length];
    let delay = state.deleting ? typeMs / 2 : typeMs;
    let next;
    if (!state.deleting && state.length === phrase.length) { delay = holdMs; next = { ...state, deleting: true }; }
    else if (state.deleting && state.length === 0) next = { index: (state.index + 1) % phrases.length, length: 0, deleting: false };
    else next = { ...state, length: state.length + (state.deleting ? -1 : 1) };
    const timer = setTimeout(() => setState(next), delay);
    return () => clearTimeout(timer);
  }, [state, phrases, typeMs, holdMs, motion]);
  const phrase = phrases[state.index % (phrases.length || 1)] || '';
  return (
    <span className="typewriter">
      <span className="sr-only">{phrases.join(', ')}</span>
      <span aria-hidden="true">
        <span className="typewriter-text">{motion ? phrase.slice(0, state.length) : phrases[0]}</span>
        <span className="caret" />
      </span>
    </span>
  );
}

/** Endless scrolling strip of links; pauses on hover/focus. The duplicate copy is hidden from assistive tech. */
export function Marquee({ items, reverse = false, label }) {
  if (!items.length) return null;
  const row = hidden => items.map(item => (
    <Link key={`${hidden ? 'b' : 'a'}-${item.to}`} to={item.to} className="marquee-item" tabIndex={hidden ? -1 : undefined}>
      {item.art && <img src={`/art/${item.art}`} alt="" loading="lazy" />}
      <span>{item.label}</span>
    </Link>
  ));
  return (
    <nav className={`marquee${reverse ? ' reverse' : ''}`} aria-label={label}>
      <div className="marquee-track">
        <div className="marquee-group">{row(false)}</div>
        <div className="marquee-group" aria-hidden="true">{row(true)}</div>
      </div>
    </nav>
  );
}
