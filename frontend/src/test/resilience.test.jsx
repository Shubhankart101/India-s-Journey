import { act, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import { BACKUP_STATUS_URL, BACKUP_URL } from '../config.js';
import { ErrorBoundary, OfflineBanner } from '../components/Resilience.jsx';
import { ErrorState } from '../components/States.jsx';
import { ApiError } from '../api.js';
import { json, mockApi, renderApp } from './helpers.jsx';

const home = {
  '/api/stats/': { indicators: 1, radial_indicators: 0, categories: 1, data_points: 3 },
  '/api/categories/': [],
  '/api/articles/': { count: 0, next: null, previous: null, results: [] },
};

describe('GitHub Pages backup', () => {
  it('defaults to the public GitHub Pages mirror', () => {
    expect(BACKUP_URL).toBe('https://shubhankart101.github.io/India-s-Journey/');
    expect(BACKUP_STATUS_URL).toBe('https://shubhankart101.github.io/India-s-Journey/status.html');
  });

  it('is linked from the 404 page', async () => {
    mockApi();
    renderApp('/definitely/not/here');
    expect(await screen.findByText('This page wandered off.')).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /backup dashboard/ })).toHaveAttribute('href', BACKUP_URL);
    expect(screen.getByRole('link', { name: 'app status' })).toHaveAttribute('href', BACKUP_STATUS_URL);
  });

  it('is linked from the footer next to the Swagger docs', async () => {
    mockApi(home);
    renderApp('/');
    expect(await screen.findByRole('link', { name: 'Backup site' })).toHaveAttribute('href', BACKUP_URL);
    expect(screen.getByRole('link', { name: 'API docs' })).toHaveAttribute('href', '/api/docs/');
    expect(screen.getByRole('link', { name: 'Status' })).toHaveAttribute('href', BACKUP_STATUS_URL);
  });

  it('is offered by error states only when the server is down', () => {
    const { rerender } = render(<ErrorState error={new ApiError(503, { detail: 'Down' })} />);
    expect(screen.getByRole('link', { name: /backup dashboard/ })).toBeInTheDocument();
    rerender(<ErrorState error={new ApiError(0, null)} />);
    expect(screen.getByRole('link', { name: /backup dashboard/ })).toBeInTheDocument();
    rerender(<ErrorState error={new ApiError(404, { detail: 'Not found.' })} />);
    expect(screen.queryByRole('link', { name: /backup dashboard/ })).not.toBeInTheDocument();
  });

  it('is offered when an indicator page cannot reach the API', async () => {
    mockApi({ '/api/indicators/gdp_growth/': json({ detail: 'Server error' }, 500) });
    renderApp('/indicator/gdp_growth');
    expect(await screen.findByRole('link', { name: /backup dashboard/ })).toHaveAttribute('href', BACKUP_URL);
  });
});

describe('ErrorBoundary', () => {
  it('catches render crashes and offers reload and the backup site', () => {
    const spy = vi.spyOn(console, 'error').mockImplementation(() => {});
    const Boom = () => { throw new Error('kaboom'); };
    render(<ErrorBoundary><Boom /></ErrorBoundary>);
    expect(screen.getByText('This page hit an unexpected error.')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Reload' })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Open backup site' })).toHaveAttribute('href', BACKUP_URL);
    spy.mockRestore();
  });

  it('renders children when nothing fails', () => {
    render(<ErrorBoundary><p>fine</p></ErrorBoundary>);
    expect(screen.getByText('fine')).toBeInTheDocument();
  });
});

describe('OfflineBanner', () => {
  it('appears when the browser goes offline or the API is unreachable, and can be dismissed', async () => {
    render(<OfflineBanner />);
    expect(screen.queryByText("Can't reach the server.")).not.toBeInTheDocument();
    act(() => { window.dispatchEvent(new Event('offline')); });
    expect(screen.getByText("Can't reach the server.")).toBeInTheDocument();
    act(() => { window.dispatchEvent(new Event('online')); });
    expect(screen.queryByText("Can't reach the server.")).not.toBeInTheDocument();
    act(() => { window.dispatchEvent(new Event('api:unreachable')); });
    expect(screen.getByRole('link', { name: 'Use the backup site' })).toHaveAttribute('href', BACKUP_URL);
    await userEvent.click(screen.getByRole('button', { name: 'Dismiss' }));
    expect(screen.queryByText("Can't reach the server.")).not.toBeInTheDocument();
  });

  it('shows in the app shell after a network failure', async () => {
    mockApi(home);
    renderApp('/');
    await screen.findByRole('link', { name: 'Backup site' });
    globalThis.fetch = async () => { throw new TypeError('Failed to fetch'); };
    act(() => { window.dispatchEvent(new Event('api:unreachable')); });
    expect(await screen.findByText("Can't reach the server.")).toBeInTheDocument();
  });
});
