import explainers from '../data/group-explainers.json';
import { pickSubgroupVerse, pickVerse } from '../scripture.js';
import ScriptureVerse from './ScriptureVerse.jsx';
import ChartView from './ChartView.jsx';
import { chartModes } from '../format.js';
import SubgroupArticle from './SubgroupArticle.jsx';

function SourceList({ sources }) {
  if (!sources.length) return <span>Source links and notes are attached to the indicator charts.</span>;
  const chips = list => <ul className="explainer-sources">{list.map(name => <li key={name}>{name}</li>)}</ul>;
  return (
    <>
      {chips(sources.slice(0, 5))}
      {sources.length > 5 && (
        <details className="explainer-sources-more">
          <summary>+{sources.length - 5} more publishers</summary>
          {chips(sources.slice(5))}
        </details>
      )}
    </>
  );
}
const stats = article => [
  { value: article.indicatorCount, label: 'indicator series' },
  { value: article.subgroupCount ?? article.groupSubgroupCount, label: 'topic lenses' },
  { value: article.sources.length, label: 'named sources' },
];

function NumberStrip({ article }) {
  return <dl className="explainer-number-strip">{stats(article).map(item => (
    <div key={item.label}><dt>{item.label}</dt><dd>{item.value.toLocaleString('en-IN')}</dd></div>
  ))}</dl>;
}

function PatternBody({ article, groupArticle, group }) {
  const paragraphs = article.paragraphs.filter(Boolean);
  const siblings = groupArticle.subgroups;
  switch (article.pattern) {
    case 'question-answer':
      return <div className="explainer-qa">
        <section><h3>What does this cover?</h3><p>{paragraphs[0] || article.dek}</p></section>
        <section><h3>How should it be read?</h3><p>{paragraphs[1] || 'Read each measure with its reporting period and source note.'}</p></section>
        <NumberStrip article={article} />
      </div>;
    case 'reading-journey':
      return <div className="explainer-journey"><ol>{(article.name ? [{ name: article.name, dek: article.dek }] : siblings).map((item, index) => (
        <li key={item.name}><span className="explainer-step">{String(index + 1).padStart(2, '0')}</span><div><h3>{item.name}</h3><p>{item.dek}</p></div></li>
      ))}</ol><p>{paragraphs[1]}</p></div>;
    case 'by-the-numbers':
      return <div className="explainer-numbers"><p>{paragraphs[0] || article.dek}</p><NumberStrip article={article} /><p>{paragraphs[1]}</p></div>;
    case 'two-lenses': {
      const first = article.name ? { name: article.name, dek: article.dek } : siblings[0];
      const second = article.name
        ? { name: group, dek: groupArticle.dek }
        : (siblings.find(item => item.name !== first?.name) || siblings[0]);
      return <div className="explainer-split">
        {[first, second].filter(Boolean).map((item, index) => <section key={`${item.name}-${index}`}><span>{index ? 'Wider context' : 'Focused lens'}</span><h3>{item.name}</h3><p>{item.dek}</p></section>)}
        <NumberStrip article={article} />
      </div>;
    }
    case 'pull-quote':
      return <div className="explainer-essay"><blockquote>{paragraphs[0] || article.dek}</blockquote><div>{paragraphs.slice(1).map((text, index) => <p key={index}>{text}</p>)}</div><NumberStrip article={article} /></div>;
    case 'annotated-captions':
      return <div className="explainer-captions">{(article.name ? [{ name: article.name, dek: article.dek, indicatorCount: article.indicatorCount }] : siblings.slice(0, 4)).map((item, index) => (
        <figure key={item.name}><span className="explainer-caption-index">Lens {String(index + 1).padStart(2, '0')}</span><figcaption><strong>{item.name}</strong><span>{item.dek}</span><small>{item.indicatorCount ?? 0} indicator series</small></figcaption></figure>
      ))}</div>;
    default:
      return <div className="explainer-lede"><div><p>{paragraphs[0] || article.dek}</p><p>{paragraphs[1]}</p></div><NumberStrip article={article} /></div>;
  }
}

const CENTRAL_CHART_TYPES = new Set(['voter-roll', 'journey-map', 'categorical-map', 'point-map', 'fiscal-matrix', 'fiscal-compare', 'fiscal-spending', 'budget-anatomy']);
const CENTRAL_SUBGROUPS = new Set([
  'Union Budget: Receipts, Spending & Deficits', 'How India Borrows & Shares Revenue', 'State Finances & GSDP',
  'State Fiscal Explorer & Welfare', 'Live Results, Rolls & Recent Elections', 'Epics: Mahabharata & Ramayana',
  'Vedic & Upanishadic Journeys', 'Buddhist Journeys', 'Jain Journeys', 'Sikh Journeys', 'Folk & Story Traditions',
]);

export default function ExplainerArticle({ category, subgroup, indicators = [] }) {
  if (!category) return null;
  const groupEntry = explainers.groups.find(item => item.name === category.name);
  if (!groupEntry) return null;
  const groupArticle = groupEntry.article;
  const subgroupArticle = subgroup && groupArticle.subgroups.find(item => item.name === subgroup.name);
  const article = subgroupArticle ? { ...subgroupArticle, groupSubgroupCount: groupArticle.subgroupCount, groupIndicatorCount: groupArticle.indicatorCount } : groupArticle;
  const verse = subgroupArticle
    ? pickSubgroupVerse(category.name, subgroup.name, groupArticle.subgroups.map(item => item.name))
    : pickVerse(category.name, category.name);
  const central = subgroupArticle && (indicators.find(item => CENTRAL_CHART_TYPES.has(item.chart_type))
    || (CENTRAL_SUBGROUPS.has(subgroup.name) ? indicators[0] : null));
  if (central && subgroupArticle.sections?.length) {
    const preview = central.preview || { labels: [], datasets: [] };
    const { initial } = chartModes({ ...central, labels: preview.labels, datasets: preview.datasets });
    const chart = <div className="subgroup-article-chart"><ChartView title={central.title} labels={preview.labels} datasets={preview.datasets} type={initial} indexAxis={central.index_axis} suffix={central.suffix} color={central.color} /></div>;
    return <SubgroupArticle
      headline={subgroupArticle.headline}
      dek={subgroupArticle.dek}
      sections={subgroupArticle.sections.map(section => ({ ...section, content: section.chart ? chart : null }))}
      keyNumbers={subgroupArticle.keyNumbers || []}
      verse={verse}
      sources={subgroupArticle.sources}
      kicker={`${category.name} · Data guide`}
      className="generated-subgroup-article"
      headingLevel={2}
    />;
  }
  return (
    <article className={`group-explainer pattern-${article.pattern}`} aria-label={`${subgroup?.name || category.name} explainer`}>
      <header className="explainer-heading">
        <p className="explainer-kicker">Topic introduction <span>· {subgroup ? 'Subgroup explainer' : 'Group explainer'}</span></p>
        <h2>{article.headline}</h2>
        <p className="explainer-dek">{article.dek}</p>
        <figure className="explainer-epigraph"><blockquote lang="sa">{article.verse.text}</blockquote><figcaption><span>{article.verse.transliteration}</span><span>{article.verse.meaning}</span></figcaption></figure>
        <ScriptureVerse verse={verse} />
      </header>
      <PatternBody article={article} groupArticle={groupArticle} group={category.name} />
      <footer className="explainer-foot"><p><strong>What to watch</strong> {article.watch}</p><div className="explainer-sources-block"><strong>Sources</strong> <SourceList sources={article.sources} /></div></footer>
    </article>
  );
}
