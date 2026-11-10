import { useEffect, useRef, useState } from 'react';

export function useDebounced(value, delay = 300) {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);
  return debounced;
}

export function useInView(rootMargin = '200px') {
  const ref = useRef(null);
  const [inView, setInView] = useState(false);
  useEffect(() => {
    if (inView || !ref.current) return undefined;
    if (typeof IntersectionObserver === 'undefined') {
      setInView(true);
      return undefined;
    }
    const observer = new IntersectionObserver(entries => {
      if (entries.some(entry => entry.isIntersecting)) {
        setInView(true);
        observer.disconnect();
      }
    }, { rootMargin });
    observer.observe(ref.current);
    return () => observer.disconnect();
  }, [inView, rootMargin]);
  return [ref, inView];
}

// Like useInView but tracks entering and leaving, so offscreen work (charts) can be torn down.
export function useVisible(rootMargin = '600px') {
  const ref = useRef(null);
  const [visible, setVisible] = useState(typeof IntersectionObserver === 'undefined');
  useEffect(() => {
    if (typeof IntersectionObserver === 'undefined' || !ref.current) return undefined;
    const observer = new IntersectionObserver(entries => {
      const last = entries[entries.length - 1];
      setVisible(last.isIntersecting);
    }, { rootMargin });
    observer.observe(ref.current);
    return () => observer.disconnect();
  }, [rootMargin]);
  return [ref, visible];
}

// Reveals a long list in batches as a sentinel nears the viewport; without IntersectionObserver everything shows at once.
export function useBatchedCount(total, resetKey, batch = 12) {
  const hasObserver = typeof IntersectionObserver !== 'undefined';
  const [count, setCount] = useState(batch);
  const sentinel = useRef(null);
  useEffect(() => { setCount(batch); }, [resetKey, batch]);
  const done = !hasObserver || count >= total;
  useEffect(() => {
    if (done || !sentinel.current) return undefined;
    const observer = new IntersectionObserver(entries => {
      if (entries.some(entry => entry.isIntersecting)) setCount(current => current + batch);
    }, { rootMargin: '900px' });
    observer.observe(sentinel.current);
    return () => observer.disconnect();
  }, [done, count, batch]);
  return [hasObserver ? Math.min(count, total) : total, sentinel, done];
}

// Runs an async loader with abort handling; returns { data, error, loading, reload }.
export function useAsync(loader, deps) {
  const [state, setState] = useState({ data: null, error: null, loading: true });
  const [nonce, setNonce] = useState(0);
  useEffect(() => {
    const controller = new AbortController();
    setState(current => ({ ...current, loading: true, error: null }));
    loader(controller.signal)
      .then(data => !controller.signal.aborted && setState({ data, error: null, loading: false }))
      .catch(error => {
        if (error?.name !== 'AbortError' && !controller.signal.aborted) setState({ data: null, error, loading: false });
      });
    return () => controller.abort();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [...deps, nonce]);
  return { ...state, reload: () => setNonce(value => value + 1) };
}

export function useDocumentTitle(title) {
  useEffect(() => {
    document.title = title ? `${title} · India's Journey` : "India's Journey";
  }, [title]);
}
