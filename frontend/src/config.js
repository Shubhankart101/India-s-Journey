// Static GitHub Pages mirror of the dashboard: always available even when this app is down.
export const BACKUP_URL = import.meta.env.VITE_BACKUP_URL || 'https://shubhankart101.github.io/India-s-Journey/';
export const BACKUP_STATUS_URL = import.meta.env.VITE_BACKUP_STATUS_URL || `${BACKUP_URL.replace(/\/?$/, '/')}status.html`;
export const API_DOCS_URL = '/api/docs/';
