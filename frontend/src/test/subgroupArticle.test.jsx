import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import SubgroupArticle from '../components/SubgroupArticle.jsx';

describe('SubgroupArticle', () => {
  it('renders numbered narrative, key numbers, an inline chart and cited sources', () => {
    render(<SubgroupArticle
      headline="A focused data guide"
      dek="A short introduction."
      sections={[
        { title: 'The measure', text: 'Read the measure carefully.' },
        { title: 'The chart', text: 'Compare the published values.', content: <div role="img" aria-label="Interactive chart">Chart</div> },
      ]}
      keyNumbers={[{ label: 'Series', value: '12' }]}
      verse={{ tradition: 'Test source', lang: 'sa', text: 'सत्यमेव जयते', english: 'Truth alone triumphs.', source: 'Test citation' }}
      sources={[{ name: 'Official dataset', url: 'https://example.org/data', licence: 'Open data' }]}
    />);
    expect(screen.getByRole('heading', { name: 'A focused data guide' })).toBeInTheDocument();
    expect(screen.getByText('01')).toBeInTheDocument();
    expect(screen.getByText('02')).toBeInTheDocument();
    expect(screen.getByRole('img', { name: 'Interactive chart' })).toBeInTheDocument();
    expect(screen.getByText('12')).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Official dataset ↗' })).toHaveAttribute('href', 'https://example.org/data');
  });
});
