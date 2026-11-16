import { describe, it, expect } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import PulseArticleView from '../components/PulseArticleView.jsx';
import PulsePage from '../pages/PulsePage.jsx';
import pulseArticles from '../data/pulse-articles.json';

describe('Pulse High-Frequency Articles and Interactive Charts', () => {
  it('loads all 21 high-frequency pulse indicators in the json catalog', () => {
    expect(pulseArticles).toHaveLength(21);
    pulseArticles.forEach(art => {
      expect(art.slug).toBeDefined();
      expect(art.idx).toMatch(/^\d{2}$/);
      expect(art.title).toBeTruthy();
      expect(art.kicker).toBeTruthy();
      expect(art.lead).toBeTruthy();
      expect(art.stats).toHaveLength(4);
      expect(art.chart.labels.length).toBeGreaterThan(10);
      expect(Object.keys(art.chart.series).length).toBeGreaterThan(0);
    });
  });

  it('renders interactive article view with title, tabs, stats and SVG crosshair', () => {
    const article = pulseArticles.find(a => a.slug === 'pmi');
    const onClose = () => {};
    const onSelect = () => {};

    render(
      <PulseArticleView
        article={article}
        allArticles={pulseArticles}
        onClose={onClose}
        onSelectArticle={onSelect}
      />
    );

    // Masthead elements
    expect(screen.getByText("The Economy’s Pulse")).toBeInTheDocument();
    expect(screen.getByText("01")).toBeInTheDocument();
    expect(screen.getByText(/Business Activity/i)).toBeInTheDocument();

    // Chart views Segmented tabs
    expect(screen.getByRole('tab', { name: /Both/i })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /Manufacturing/i })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /Services/i })).toBeInTheDocument();

    // Switching views
    fireEvent.click(screen.getByRole('tab', { name: /Manufacturing/i }));
    expect(screen.getByRole('tab', { name: /Manufacturing/i })).toHaveClass('active');

    // 4 Key Stats cards
    expect(screen.getAllByText("Manufacturing").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("Services").length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("Expansion Run")).toBeInTheDocument();

    // Editorial notes section
    expect(screen.getByText("What you're looking at")).toBeInTheDocument();
  });

  it('renders dedicated PulsePage with 21 cards grid and macro ticker', () => {
    render(
      <MemoryRouter initialEntries={['/pulse']}>
        <Routes>
          <Route path="pulse" element={<PulsePage />} />
          <Route path="pulse/:slug" element={<PulsePage />} />
        </Routes>
      </MemoryRouter>
    );

    expect(screen.getByText(/India's Economic Pulse/i)).toBeInTheDocument();
    expect(screen.getByText(/Tracking 21 high-frequency macroeconomic signals/i)).toBeInTheDocument();

    // Ticker items
    expect(screen.getByText(/MANUFACTURING PMI/i)).toBeInTheDocument();
    expect(screen.getAllByText(/GROSS GST/i).length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText(/FX RESERVES/i)).toBeInTheDocument();

    // 21 cards are displayed
    const articlesCount = screen.getAllByText(/Article Available/i);
    expect(articlesCount).toHaveLength(21);
  });

  it('renders publish in article kit with Substack markdown, caption, and iframe code', () => {
    const article = pulseArticles.find(a => a.slug === 'cpi');
    render(
      <PulseArticleView
        article={article}
        allArticles={pulseArticles}
        onClose={() => {}}
        onSelectArticle={() => {}}
      />
    );

    // Open publish modal
    const publishBtn = screen.getByRole('button', { name: /Publish in Article/i });
    expect(publishBtn).toBeInTheDocument();
    fireEvent.click(publishBtn);

    expect(screen.getByText(/ARTICLE FRIENDLY PUBLISH KIT/i)).toBeInTheDocument();
    expect(screen.getByText(/Substack \/ Muckrack Markdown Hyperlink/i)).toBeInTheDocument();
    expect(screen.getByText(/Substack Graphic Caption \(Polity & Policy Style\)/i)).toBeInTheDocument();
    expect(screen.getByText(/Interactive HTML Embed Code \(Iframe\)/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Copy Markdown/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Copy Caption/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Copy HTML Embed/i })).toBeInTheDocument();
  });

  it('renders clean embed mode without external navigation chrome', () => {
    const article = pulseArticles.find(a => a.slug === 'pmi');
    render(
      <PulseArticleView
        article={article}
        allArticles={pulseArticles}
        isEmbed={true}
      />
    );

    // Embed header and brand link
    expect(screen.getByText("The Economy’s Pulse")).toBeInTheDocument();
    expect(screen.getByText(/⚡ India's Journey · Economic Pulse/i)).toBeInTheDocument();
    expect(screen.getByText(/Open Full Interactive Story & Data ↗/i)).toBeInTheDocument();
    // Modal chrome should NOT be rendered
    expect(screen.queryByText("Back to Indicators")).not.toBeInTheDocument();
  });
});
