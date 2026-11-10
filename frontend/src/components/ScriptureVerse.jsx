import { pickVerse } from '../scripture.js';

export default function ScriptureVerse({ verseKey, group, verse, className = '' }) {
  const picked = verse || pickVerse(verseKey, group);
  if (!picked) return null;
  return (
    <figure className={`scripture-verse${className ? ` ${className}` : ''}`} data-tradition={picked.tradition}>
      <blockquote lang={picked.lang}>{picked.text}</blockquote>
      <p className="scripture-english">{picked.english}</p>
      <figcaption>
        <span className="scripture-badge"><i className="scripture-dot" aria-hidden="true" />{picked.tradition}</span>
        <cite>{picked.source}</cite>
      </figcaption>
    </figure>
  );
}
