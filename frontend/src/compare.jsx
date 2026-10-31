import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';

export const MAX_COMPARE = 4;
const STORAGE_KEY = 'ij-compare';
const CompareContext = createContext(null);

const readStored = () => {
  try {
    const parsed = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
    return Array.isArray(parsed) ? parsed.filter(item => item && item.key).slice(0, MAX_COMPARE) : [];
  } catch {
    return [];
  }
};

export function CompareProvider({ children }) {
  const [items, setItems] = useState(readStored);
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
    } catch {
      // Storage may be unavailable (private mode); the tray still works for this visit.
    }
  }, [items]);

  const has = useCallback(key => items.some(item => item.key === key), [items]);
  const toggle = useCallback(indicator => {
    setItems(current => {
      if (current.some(item => item.key === indicator.key)) return current.filter(item => item.key !== indicator.key);
      if (current.length >= MAX_COMPARE) return current;
      return [...current, { key: indicator.key, title: indicator.title }];
    });
  }, []);
  const clear = useCallback(() => setItems([]), []);
  const value = useMemo(() => ({ items, has, toggle, clear, full: items.length >= MAX_COMPARE }), [items, has, toggle, clear]);
  return <CompareContext.Provider value={value}>{children}</CompareContext.Provider>;
}

export const useCompare = () => {
  const value = useContext(CompareContext);
  if (!value) throw new Error('useCompare must be used inside CompareProvider');
  return value;
};
