import { act, render } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import ArtBackdrop from '../components/ArtBackdrop.jsx';
import { AMBIENT_ART } from '../art.js';

describe('ArtBackdrop', () => {
  afterEach(() => vi.useRealTimers());

  it('keeps a single scene static', () => {
    vi.useFakeTimers();
    const { container } = render(<ArtBackdrop art="economy.svg" interval={1000} />);
    act(() => { vi.advanceTimersByTime(5000); });
    expect(container.querySelector('.art-backdrop')).toHaveAttribute('data-art', 'economy.svg');
    expect(container.querySelector('.art-motes')).toBeInTheDocument();
  });

  it('rotates through a playlist and cross-fades between scenes', () => {
    vi.useFakeTimers();
    const { container } = render(<ArtBackdrop art={AMBIENT_ART} interval={3000} />);
    const backdrop = container.querySelector('.art-backdrop');
    expect(backdrop).toHaveAttribute('data-art', AMBIENT_ART[0]);
    act(() => { vi.advanceTimersByTime(3000); });
    expect(backdrop).toHaveAttribute('data-art', AMBIENT_ART[1]);
    expect(backdrop.querySelectorAll('img')).toHaveLength(2);
    act(() => { vi.advanceTimersByTime(1200); });
    expect(backdrop.querySelectorAll('img')).toHaveLength(1);
    act(() => { vi.advanceTimersByTime(1800 + 3000 * (AMBIENT_ART.length - 2)); });
    expect(backdrop).toHaveAttribute('data-art', AMBIENT_ART[0]);
  });

  it('ships every ambient scene as a public asset', async () => {
    const { existsSync } = await import('node:fs');
    const { resolve } = await import('node:path');
    AMBIENT_ART.forEach(file => {
      expect(existsSync(resolve(__dirname, '../../public/art', file))).toBe(true);
      expect(existsSync(resolve(__dirname, '../../../docs/assets', file))).toBe(true);
    });
  });
});
