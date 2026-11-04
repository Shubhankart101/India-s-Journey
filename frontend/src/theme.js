import { useSyncExternalStore } from 'react';

// Shares the static site's localStorage key so a chosen theme follows the user across both.
const KEY = 'ij-theme';

export const THEMES = [
  { id: 'light', label: 'Light', meta: '#f5f5f7' },
  { id: 'dark', label: 'Dark', meta: '#000000' },
  { id: 'newspaper', label: 'Newspaper', meta: '#f4f0e6' },
  { id: 'pamphlet', label: 'Pamphlet', meta: '#fff1c1' },
];

export const CHART_COLORS = {
  dark: { ink: '#f5f5f7', muted: '#a1a1a6', grid: 'rgba(255, 255, 255, 0.08)', legend: '#d2d2d7', sliceBorder: '#1c1c1e' },
  light: { ink: '#1d1d1f', muted: '#515154', grid: 'rgba(0, 0, 0, 0.08)', legend: '#3a3a3c', sliceBorder: '#ffffff' },
  newspaper: { ink: '#111111', muted: '#3b3b3b', grid: 'rgba(0, 0, 0, 0.12)', legend: '#222222', sliceBorder: '#fbf8f1' },
  pamphlet: { ink: '#1b1b1b', muted: '#2f2f2f', grid: 'rgba(27, 27, 27, 0.14)', legend: '#1b1b1b', sliceBorder: '#1b1b1b' },
};

const isTheme = value => THEMES.some(theme => theme.id === value);
const listeners = new Set();

function readStored() {
  try {
    const saved = localStorage.getItem(KEY);
    return isTheme(saved) ? saved : 'dark';
  } catch {
    return 'dark';
  }
}

let current = readStored();

export function applyTheme(theme = current) {
  document.documentElement.dataset.theme = theme;
  document.querySelector('meta[name="theme-color"]')?.setAttribute('content', THEMES.find(item => item.id === theme).meta);
}

export function getTheme() {
  return current;
}

export function setTheme(theme) {
  if (!isTheme(theme) || theme === current) return;
  current = theme;
  applyTheme(theme);
  try { localStorage.setItem(KEY, theme); } catch { /* private mode: keep for this visit */ }
  listeners.forEach(listener => listener());
}

function subscribe(listener) {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

export function useTheme() {
  return useSyncExternalStore(subscribe, getTheme, getTheme);
}
