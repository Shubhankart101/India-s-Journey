import { useTheme } from '../theme.js';

// One slim dateline for the printed editions; the rest of the 1947 look is pure CSS.
export default function VintageChrome() {
  const theme = useTheme();
  if (theme !== 'newspaper' && theme !== 'pamphlet') return null;
  return (
    <div className="vintage-dateline" aria-hidden="true">
      <span>New Delhi · 15 August 1947 · Price one anna</span>
      <span lang="hi">भारत स्वतंत्र हुआ</span>
    </div>
  );
}
