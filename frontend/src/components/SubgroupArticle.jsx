import ScriptureVerse from './ScriptureVerse.jsx';
import './SubgroupArticle.css';

export default function SubgroupArticle({
  headline,
  dek = '',
  kicker = 'A data guide',
  sections = [],
  keyNumbers = [],
  quote,
  verse,
  sources = [],
  className = '',
  sectionClassName = '',
  headingLevel = 1,
  after = null,
  lead = null,
  chipSources = false,
  quoteAfterSection = -1,
}) {
  const blocks = sections.length ? sections : (dek ? [{ title: 'The subject', text: dek }] : []);
  const Headline = headingLevel === 1 ? 'h1' : 'h2';
  const inlineQuote = quoteAfterSection >= 0 && quote;
  const sourceName = source => (typeof source === 'string' ? source : source.name || source.label || source.url);
  const chips = list => <ul className="explainer-sources">{list.map(name => <li key={name}>{name}</li>)}</ul>;
  return (
    <article className={`subgroup-article ${className}`.trim()} aria-label={headline}>
      <header className="subgroup-article-hero">
        <p className="subgroup-article-kicker">{kicker}</p>
        <Headline>{headline}</Headline>
        {dek && <p className="subgroup-article-dek">{dek}</p>}
        {quote && !inlineQuote && <blockquote className="subgroup-article-quote">{quote}</blockquote>}
        {keyNumbers.length > 0 && <dl className="subgroup-article-numbers">
          {keyNumbers.map(item => <div key={`${item.label}-${item.value}`}>
            <dt>{item.label}</dt><dd>{item.value}</dd>{item.note && <dd className="subgroup-article-number-note">{item.note}</dd>}
          </div>)}
        </dl>}
        {verse && quoteAfterSection < 0 && <ScriptureVerse verse={verse} className="subgroup-article-verse" />}
      </header>
      {lead}
      <div className="subgroup-article-sections">
        {blocks.map((section, index) => {
          const id = `subgroup-section-${index + 1}`;
          return <section className={`subgroup-article-section ${sectionClassName}`.trim()} key={`${section.title || 'section'}-${index}`} aria-labelledby={id}>
            <span className="subgroup-article-index" aria-hidden="true">{String(index + 1).padStart(2, '0')}</span>
            <div className="subgroup-article-section-body">
              <h2 id={id}>{section.title || `Section ${index + 1}`}</h2>
              {section.text && <p>{section.text}</p>}
              {section.quote && <blockquote className="subgroup-article-quote">{section.quote}</blockquote>}
              {section.content}
              {inlineQuote && index === Math.min(quoteAfterSection, blocks.length - 1) && <blockquote className="subgroup-article-quote subgroup-article-pull">{quote}</blockquote>}
            </div>
          </section>;
        })}
      </div>
      {quoteAfterSection >= 0 && verse && <ScriptureVerse verse={verse} className="subgroup-article-verse" />}
      {after}
      {sources.length > 0 && <footer className="subgroup-article-sources">
        <h2>Sources &amp; notes</h2>
        {chipSources ? <>
          {chips(sources.slice(0, 5).map(sourceName))}
          {sources.length > 5 && <details className="explainer-sources-more">
            <summary>+{sources.length - 5} more publishers</summary>
            {chips(sources.slice(5).map(sourceName))}
          </details>}
        </> : <ul>{sources.map((source, index) => {
          const name = sourceName(source);
          return <li key={`${name}-${index}`}>
            {source.url ? <a href={source.url} target="_blank" rel="noreferrer">{name} ↗</a> : name}
            {source.licence && <small>{source.licence}</small>}
          </li>;
        })}</ul>}
      </footer>}
    </article>
  );
}
