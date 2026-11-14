import { useEffect, useState } from 'react';
import './IndependenceClock.css';

// 15 August 1947, 00:00:00 IST (UTC+05:30) is 14 August 1947, 18:30:00 UTC
const INDEPENDENCE_EPOCH = Date.UTC(1947, 7, 14, 18, 30, 0);

function computeElapsed() {
  const now = Date.now();
  const diffMs = Math.max(0, now - INDEPENDENCE_EPOCH);

  // Exact calendar differences
  const start = new Date(INDEPENDENCE_EPOCH);
  const current = new Date(now);

  let years = current.getUTCFullYear() - start.getUTCFullYear();
  let months = current.getUTCMonth() - start.getUTCMonth();
  let days = current.getUTCDate() - start.getUTCDate();
  let hours = current.getUTCHours() - start.getUTCHours();
  let minutes = current.getUTCMinutes() - start.getUTCMinutes();
  let seconds = current.getUTCSeconds() - start.getUTCSeconds();

  if (seconds < 0) {
    seconds += 60;
    minutes -= 1;
  }
  if (minutes < 0) {
    minutes += 60;
    hours -= 1;
  }
  if (hours < 0) {
    hours += 24;
    days -= 1;
  }
  if (days < 0) {
    // days in previous month
    const prevMonth = new Date(current.getUTCFullYear(), current.getUTCMonth(), 0);
    days += prevMonth.getUTCDate();
    months -= 1;
  }
  if (months < 0) {
    months += 12;
    years -= 1;
  }

  // Also total days elapsed for historical context
  const totalDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
  const totalSeconds = Math.floor(diffMs / 1000);

  return { years, months, days, hours, minutes, seconds, totalDays, totalSeconds };
}

export default function IndependenceClock() {
  const [elapsed, setElapsed] = useState(computeElapsed);

  useEffect(() => {
    const timer = setInterval(() => {
      setElapsed(computeElapsed());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const pad = num => String(num).padStart(2, '0');

  return (
    <div className="independence-clock" role="region" aria-label="Time since India's Independence">
      <div className="ic-header">
        <span className="ic-badge">
          <span className="ic-pulse" aria-hidden="true" />
          HISTORICAL CHRONOMETER
        </span>
        <span className="ic-title">Free India Tryst with Destiny · 15 August 1947, 00:00:00 IST</span>
      </div>

      <div className="ic-display">
        <div className="ic-unit">
          <span className="ic-value">{elapsed.years}</span>
          <span className="ic-label">Years</span>
        </div>
        <span className="ic-sep" aria-hidden="true">:</span>

        <div className="ic-unit">
          <span className="ic-value">{pad(elapsed.months * 30 + elapsed.days)}</span>
          <span className="ic-label">Days</span>
        </div>
        <span className="ic-sep" aria-hidden="true">:</span>

        <div className="ic-unit">
          <span className="ic-value">{pad(elapsed.hours)}</span>
          <span className="ic-label">Hours</span>
        </div>
        <span className="ic-sep" aria-hidden="true">:</span>

        <div className="ic-unit">
          <span className="ic-value">{pad(elapsed.minutes)}</span>
          <span className="ic-label">Minutes</span>
        </div>
        <span className="ic-sep" aria-hidden="true">:</span>

        <div className="ic-unit highlight">
          <span className="ic-value">{pad(elapsed.seconds)}</span>
          <span className="ic-label">Seconds</span>
        </div>
      </div>

      <div className="ic-footer">
        <p className="ic-quote">
          “At the stroke of the midnight hour, when the world sleeps, India will awake to life and freedom.”
        </p>
        <span className="ic-total">
          <strong>{elapsed.totalDays.toLocaleString('en-IN')}</strong> total days of sovereign democracy
        </span>
      </div>
    </div>
  );
}
