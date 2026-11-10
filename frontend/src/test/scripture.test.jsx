import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it } from 'vitest';
import explainers from '../data/group-explainers.json';
import { CompareProvider } from '../compare.jsx';
import ExplainerArticle from '../components/ExplainerArticle.jsx';
import IndicatorCard from '../components/IndicatorCard.jsx';
import ScriptureVerse from '../components/ScriptureVerse.jsx';
import { candidatesFor, GROUP_THEMES, pickSubgroupVerse, pickVerse, TRADITIONS } from '../scripture.js';
import { summary } from './helpers.jsx';

describe('scripture verses', () => {
  it('picks deterministically and stays inside the group pool', () => {
    expect(pickVerse('gdp_growth', 'Economic')).toBe(pickVerse('gdp_growth', 'Economic'));
    const pool = candidatesFor('Economic');
    expect(pool.length).toBeGreaterThan(0);
    for (let i = 0; i < 40; i += 1) expect(pool).toContain(pickVerse(`key-${i}`, 'Economic'));
    expect(pickVerse('x', 'A New Group').id).toBeTruthy();
    expect(Object.keys(GROUP_THEMES)).toContain('India in Maps');
  });

  it('renders original text with lang and a citation', () => {
    const verse = pickVerse('gdp_growth', 'Economic');
    const { container } = render(<ScriptureVerse verseKey="gdp_growth" group="Economic" />);
    expect(container.querySelector('blockquote')).toHaveAttribute('lang', verse.lang);
    expect(screen.getByText(verse.text)).toBeInTheDocument();
    expect(screen.getByText(verse.english)).toBeInTheDocument();
    expect(screen.getByText(verse.source)).toBeInTheDocument();
    expect(container.querySelector('figure')).toHaveAttribute('data-tradition', verse.tradition);
  });

  it("covers all four traditions across a group's indicators", () => {
    const seen = new Set();
    for (let i = 0; i < 60; i += 1) seen.add(pickVerse(`indicator_${i}`, 'Economic').tradition);
    expect([...seen].sort()).toEqual([...TRADITIONS].sort());
  });

  it('shows a verse on every indicator card', () => {
    const { container } = render(
      <MemoryRouter><CompareProvider><IndicatorCard indicator={summary()} /></CompareProvider></MemoryRouter>,
    );
    expect(container.querySelectorAll('.scripture-verse')).toHaveLength(1);
  });

  it('adds a verse to group and subgroup explainers, never repeating the previous subgroup', () => {
    const { name, article } = explainers.groups[0];
    const names = article.subgroups.map(item => item.name);
    const group = render(<ExplainerArticle category={{ name }} subgroup={null} />);
    expect(group.container.querySelector('.scripture-verse')).not.toBeNull();
    group.unmount();
    const sub = render(<ExplainerArticle category={{ name }} subgroup={{ name: names[1] }} />);
    expect(sub.container.querySelector('.scripture-verse blockquote')).toHaveTextContent(pickSubgroupVerse(name, names[1], names).text);
    for (let i = 1; i < names.length; i += 1) {
      expect(pickSubgroupVerse(name, names[i], names).id).not.toBe(pickVerse(`${name}/${names[i - 1]}`, name).id);
    }
  });
});
