import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import explainers from '../data/group-explainers.json';
import ExplainerArticle from '../components/ExplainerArticle.jsx';

describe('catalog-driven group explainers', () => {
  it('assigns a distinct deterministic pattern to each group and rotates subgroup patterns', () => {
    expect(explainers.groups).toHaveLength(11);
    expect(new Set(explainers.groups.slice(0, 7).map(item => item.article.pattern)).size).toBe(7);
    const group = explainers.groups[0].article;
    expect(group.subgroups[0].pattern).not.toBe(group.pattern);
    expect(group.subgroups[1].pattern).not.toBe(group.subgroups[0].pattern);
  });

  it('renders the group epigraph, data-derived callouts and source line', () => {
    const { name, article } = explainers.groups[0];
    render(<ExplainerArticle category={{ name }} subgroup={null} />);
    expect(screen.getByRole('article', { name: `${name} explainer` })).toHaveClass(`pattern-${article.pattern}`);
    expect(screen.getByText(article.verse.text)).toBeInTheDocument();
    expect(screen.getByText(article.verse.transliteration)).toBeInTheDocument();
    expect(screen.getByRole('article', { name: `${name} explainer` }).querySelector('.explainer-number-strip dd')).toHaveTextContent(String(article.indicatorCount));
    expect(screen.getByText(/What to watch/)).toBeInTheDocument();
  });

  it('selects subgroup-specific article content and preserves the group epigraph', () => {
    const { name, article } = explainers.groups[0];
    const subgroup = article.subgroups[0];
    render(<ExplainerArticle category={{ name }} subgroup={{ name: subgroup.name }} />);
    expect(screen.getByRole('article', { name: `${subgroup.name} explainer` })).toHaveClass(`pattern-${subgroup.pattern}`);
    expect(screen.getByRole('heading', { level: 2, name: subgroup.headline })).toBeInTheDocument();
    expect(screen.getByText(article.verse.text)).toBeInTheDocument();
    expect(screen.getByRole('article', { name: `${subgroup.name} explainer` }).querySelector('.explainer-number-strip dd')).toHaveTextContent(String(subgroup.indicatorCount));
  });
});
