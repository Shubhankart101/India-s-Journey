import { THEMES, setTheme, useTheme } from '../theme.js';

export default function ThemeSelect({ className = '' }) {
  const theme = useTheme();
  return (
    <select className={`theme-select ${className}`.trim()} aria-label="Display theme" value={theme} onChange={event => setTheme(event.target.value)}>
      {THEMES.map(item => <option key={item.id} value={item.id}>{item.label}</option>)}
    </select>
  );
}
