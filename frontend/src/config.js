// Static Netlify dashboard, always available even when this app is down; GitHub Pages mirrors it.
export const BACKUP_URL = import.meta.env.VITE_BACKUP_URL || 'https://indiasjourney.netlify.app/';
export const BACKUP_MIRROR_URL = import.meta.env.VITE_BACKUP_MIRROR_URL || 'https://shubhankart101.github.io/India-s-Journey/';
export const API_DOCS_URL = '/api/docs/';
export const WEB_APP_URL = 'https://indias-journey.onrender.com/';
export const POLITYPOLICY_CONTACT_URL = 'https://politypolicy.substack.com/about';

/**
 * Resiliently resolves an asset or API relative path to its public URL.
 * Accounts for GitHub Pages subpath (/India-s-Journey/), preview domains, and localhost.
 */
export function assetUrl(relPath) {
  const clean = String(relPath || '').replace(/^\/+/, '');
  if (typeof window !== 'undefined' && /^\/India-s-Journey/i.test(window.location?.pathname || '')) {
    return `/India-s-Journey/${clean}`;
  }
  const base = import.meta.env?.BASE_URL;
  if (!base || base === './' || base === '.' || base === '/') {
    return `/${clean}`;
  }
  return `${base.endsWith('/') ? base : `${base}/`}${clean}`;
}
