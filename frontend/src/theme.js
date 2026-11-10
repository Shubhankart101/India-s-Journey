import { useSyncExternalStore } from 'react';

// Shares the static site's localStorage key so a chosen theme follows the user across both.
const KEY = 'ij-theme';

export const THEMES = [
  { id: 'light', label: 'Light', short: 'Lt', meta: '#f5f5f7' },
  { id: 'dark', label: 'Dark', short: 'Dk', meta: '#000000' },
  { id: 'newspaper', label: 'Newspaper', short: 'News', meta: '#f4f0e6' },
  { id: 'pamphlet', label: 'Pamphlet', short: 'Pmph', meta: '#fff1c1' },
  { id: 'military', label: 'Military', short: 'Mil', meta: '#1f2414' },
  { id: 'parliamentary', label: 'Parliamentary', short: 'Parl', meta: '#0f3b2e' },
  { id: 'desi', label: 'Desi', short: 'Desi', meta: '#fff3e0' },
  { id: 'airforce', label: 'Air Force', short: 'IAF', meta: '#0b1f3a' },
  { id: 'navy', label: 'Navy', short: 'Navy', meta: '#f4f6fa' },
  { id: 'police', label: 'Police', short: 'Pol', meta: '#efe3c4' },
];

export const CHART_COLORS = {
  dark: { ink: '#f5f5f7', muted: '#a1a1a6', grid: 'rgba(255, 255, 255, 0.08)', legend: '#d2d2d7', sliceBorder: '#1c1c1e' },
  light: { ink: '#1d1d1f', muted: '#515154', grid: 'rgba(0, 0, 0, 0.08)', legend: '#3a3a3c', sliceBorder: '#ffffff' },
  newspaper: { ink: '#111111', muted: '#3b3b3b', grid: 'rgba(0, 0, 0, 0.12)', legend: '#222222', sliceBorder: '#fbf8f1' },
  pamphlet: { ink: '#1b1b1b', muted: '#2f2f2f', grid: 'rgba(27, 27, 27, 0.14)', legend: '#1b1b1b', sliceBorder: '#1b1b1b' },
  military: { ink: '#ece4c4', muted: '#b8b08a', grid: 'rgba(236, 228, 196, 0.1)', legend: '#d8cfa8', sliceBorder: '#1f2414' },
  parliamentary: { ink: '#f3ead2', muted: '#c9bf9f', grid: 'rgba(243, 234, 210, 0.1)', legend: '#e6dcbc', sliceBorder: '#0f3b2e' },
  desi: { ink: '#3a1030', muted: '#6b2f55', grid: 'rgba(58, 16, 48, 0.12)', legend: '#3a1030', sliceBorder: '#fff3e0' },
  airforce: { ink: '#e8f1fb', muted: '#a9c1dd', grid: 'rgba(232, 241, 251, 0.1)', legend: '#d3e3f5', sliceBorder: '#0b1f3a' },
  navy: { ink: '#0a1f44', muted: '#3c4d6e', grid: 'rgba(10, 31, 68, 0.1)', legend: '#0a1f44', sliceBorder: '#ffffff' },
  police: { ink: '#1b2440', muted: '#4a4636', grid: 'rgba(27, 36, 64, 0.12)', legend: '#1b2440', sliceBorder: '#efe3c4' },
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

const FONT_URL = 'https://fonts.googleapis.com/css2?family=Old+Standard+TT:wght@400;700&family=Playfair+Display:wght@600;700;800&family=UnifrakturMaguntia&family=Special+Elite&family=Rozha+One&family=Stardos+Stencil:wght@400;700&family=Tiro+Devanagari+Hindi&family=Noto+Sans+Devanagari:wght@400;600&family=Noto+Serif+Devanagari:wght@500;700&display=swap';

// Display and Devanagari fonts never block rendering (display=swap, injected after load).
function loadEditionFonts() {
  if (typeof document === 'undefined' || document.getElementById('ij-edition-fonts')) return;
  const add = () => {
    if (document.getElementById('ij-edition-fonts')) return;
    const link = document.createElement('link');
    link.id = 'ij-edition-fonts';
    link.rel = 'stylesheet';
    link.href = FONT_URL;
    document.head.append(link);
  };
  if (document.readyState === 'complete') add();
  else window.addEventListener('load', add, { once: true });
}

export function applyTheme(theme = current) {
  document.documentElement.dataset.theme = theme;
  loadEditionFonts();
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
