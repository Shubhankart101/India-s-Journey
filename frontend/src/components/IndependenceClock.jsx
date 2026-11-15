import { useEffect, useState } from 'react';
import './IndependenceClock.css';

// 15 August 1947, 00:00:00 IST (UTC+05:30) is 14 August 1947, 18:30:00 UTC
const INDEPENDENCE_EPOCH = Date.UTC(1947, 7, 14, 18, 30, 0);

function getIstDate(dateObj = new Date()) {
  const utc = dateObj.getTime() + dateObj.getTimezoneOffset() * 60000;
  return new Date(utc + 5.5 * 3600000);
}

function computeElapsed() {
  const now = new Date();
  const diffMs = Math.max(0, now.getTime() - INDEPENDENCE_EPOCH);

  // Exact calendar differences in IST
  const start = new Date(1947, 7, 15, 0, 0, 0);
  const current = getIstDate(now);

  let years = current.getFullYear() - start.getFullYear();
  let months = current.getMonth() - start.getMonth();
  let days = current.getDate() - start.getDate();
  let hours = current.getHours() - start.getHours();
  let minutes = current.getMinutes() - start.getMinutes();
  let seconds = current.getSeconds() - start.getSeconds();

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
    const prevMonthLastDay = new Date(current.getFullYear(), current.getMonth(), 0).getDate();
    days += prevMonthLastDay;
    months -= 1;
  }
  if (months < 0) {
    months += 12;
    years -= 1;
  }

  const totalDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
  const totalSeconds = Math.floor(diffMs / 1000);

  return {
    years,
    months,
    days,
    hours,
    minutes,
    seconds,
    totalDays,
    totalSeconds,
    istNow: current,
  };
}

// Split-flap mechanical flip digit pair
function FlipCard({ value, label, highlight = false }) {
  const str = String(Math.max(0, value || 0)).padStart(2, '0');
  const d1 = str[0];
  const d2 = str[1];

  return (
    <div className={`flip-unit ${highlight ? 'flip-highlight' : ''}`}>
      <div className="flip-pair">
        <div className="flip-digit">
          <span className="flip-num">{d1}</span>
          <span className="flip-crease" aria-hidden="true" />
          <span className="flip-hinge left" aria-hidden="true" />
          <span className="flip-hinge right" aria-hidden="true" />
        </div>
        <div className="flip-digit">
          <span className="flip-num">{d2}</span>
          <span className="flip-crease" aria-hidden="true" />
          <span className="flip-hinge left" aria-hidden="true" />
          <span className="flip-hinge right" aria-hidden="true" />
        </div>
      </div>
      <span className="flip-label">{label}</span>
    </div>
  );
}

// Precision Analog Watch Face with Live Indian Standard Time
function IstWatch({ date }) {
  const hours = date.getHours();
  const minutes = date.getMinutes();
  const seconds = date.getSeconds();
  const ms = date.getMilliseconds ? date.getMilliseconds() : 0;

  // Exact clock hand angles
  const secAngle = (seconds + ms / 1000) * 6; // 360 / 60
  const minAngle = (minutes + seconds / 60) * 6;
  const hourAngle = ((hours % 12) + minutes / 60) * 30; // 360 / 12

  const timeString = date.toLocaleTimeString('en-IN', {
    hour12: true,
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });

  const dateString = date.toLocaleDateString('en-IN', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  });

  return (
    <div className="ist-watch-container" aria-label={`Current Indian Standard Time: ${timeString}`}>
      <div className="ist-watch-dial" aria-hidden="true">
        {/* Watch bezel and hour markers */}
        <div className="watch-face">
          <span className="watch-num num-12">12</span>
          <span className="watch-num num-3">3</span>
          <span className="watch-num num-6">6</span>
          <span className="watch-num num-9">9</span>

          {/* Tick marks */}
          <span className="watch-tick tick-1" />
          <span className="watch-tick tick-2" />
          <span className="watch-tick tick-4" />
          <span className="watch-tick tick-5" />
          <span className="watch-tick tick-7" />
          <span className="watch-tick tick-8" />
          <span className="watch-tick tick-10" />
          <span className="watch-tick tick-11" />

          {/* Ashoka Chakra insignia at center */}
          <div className="watch-chakra-hub" />

          {/* Clock hands */}
          <div className="watch-hand hour-hand" style={{ transform: `rotate(${hourAngle}deg)` }} />
          <div className="watch-hand min-hand" style={{ transform: `rotate(${minAngle}deg)` }} />
          <div className="watch-hand sec-hand" style={{ transform: `rotate(${secAngle}deg)` }} />
          <div className="watch-center-pin" />
        </div>
      </div>

      <div className="ist-watch-info">
        <div className="ist-badge">
          <span className="ist-pulse" aria-hidden="true" />
          <span>INDIAN STANDARD TIME (IST · UTC+05:30)</span>
        </div>
        <div className="ist-time-text">{timeString}</div>
        <div className="ist-date-text">{dateString} · New Delhi Standard Observatory</div>
      </div>
    </div>
  );
}

export default function IndependenceClock() {
  const [data, setData] = useState(computeElapsed);

  useEffect(() => {
    const timer = setInterval(() => {
      setData(computeElapsed());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="independence-clock" role="region" aria-label="Time since India's Independence">
      <div className="ic-header">
        <span className="ic-badge">
          <span className="ic-pulse" aria-hidden="true" />
          HISTORICAL CHRONOMETER
        </span>
        <span className="ic-title">Free India Tryst with Destiny · 15 August 1947, 00:00:00 IST</span>
      </div>

      {/* Mechanical Flip-Flap Countdown Board with 6 Units: Years, Months, Days, Hours, Minutes, Seconds */}
      <div className="flip-board" aria-label="Elapsed time flip chronometer">
        <FlipCard value={data.years} label="YEARS" />
        <span className="flip-sep" aria-hidden="true">:</span>
        <FlipCard value={data.months} label="MONTHS" />
        <span className="flip-sep" aria-hidden="true">:</span>
        <FlipCard value={data.days} label="DAYS" />
        <span className="flip-sep" aria-hidden="true">:</span>
        <FlipCard value={data.hours} label="HOURS" />
        <span className="flip-sep" aria-hidden="true">:</span>
        <FlipCard value={data.minutes} label="MINUTES" />
        <span className="flip-sep" aria-hidden="true">:</span>
        <FlipCard value={data.seconds} label="SECONDS" highlight />
      </div>

      {/* Live Analog & Digital Indian Standard Time Watch */}
      <IstWatch date={data.istNow} />

      <div className="ic-footer">
        <p className="ic-quote">
          “At the stroke of the midnight hour, when the world sleeps, India will awake to life and freedom.”
        </p>
        <span className="ic-total">
          <strong>{data.totalDays.toLocaleString('en-IN')}</strong> total days of sovereign democracy ({data.totalSeconds.toLocaleString('en-IN')} seconds)
        </span>
      </div>
    </div>
  );
}
