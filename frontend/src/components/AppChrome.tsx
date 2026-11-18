// src/components/AppChrome.tsx
// Top command bar + bottom status bar for every console screen.
import { useEffect, useState } from 'react';
import type { CSSProperties } from 'react';
import { Link, NavLink } from 'react-router-dom';
import { colors, fonts } from '../theme';

const tabs = [
  { to: '/command', label: 'Command Center' },
  { to: '/camera', label: 'Camera & Detection' },
  { to: '/hospital', label: 'Hospital Portal' },
  { to: '/simulation', label: 'Simulation Lab' },
  { to: '/analytics', label: 'Analytics' },
];

function tab(isActive: boolean): CSSProperties {
  return {
    display: 'flex',
    alignItems: 'center',
    height: '100%',
    padding: '0 14px',
    fontSize: 14,
    fontWeight: isActive ? 700 : 400,
    color: isActive ? colors.text : colors.muted,
    borderBottom: `2px solid ${isActive ? colors.accent : 'transparent'}`,
    textDecoration: 'none',
    whiteSpace: 'nowrap',
  };
}

export function Logo({ size = 28 }: { size?: number }) {
  return (
    <div
      style={{
        width: size,
        height: size,
        borderRadius: 7,
        background: colors.accent,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        flexShrink: 0,
      }}
    >
      <svg width={size * 0.62} height={size * 0.62} viewBox="0 0 24 24" fill={colors.background} aria-hidden="true">
        <path d="M10 3h4v7h7v4h-7v7h-4v-7H3v-4h7z" />
      </svg>
    </div>
  );
}

export function TopBar() {
  return (
    <header
      style={{
        height: 52,
        flexShrink: 0,
        display: 'flex',
        alignItems: 'stretch',
        gap: 8,
        padding: '0 16px',
        background: colors.panel,
        borderBottom: `1px solid ${colors.border}`,
        userSelect: 'none',
      }}
    >
      <Link
        to="/"
        title="Back to home"
        style={{ display: 'flex', alignItems: 'center', gap: 10, textDecoration: 'none', color: colors.text, paddingRight: 12 }}
      >
        <Logo />
        <span style={{ fontWeight: 700, fontSize: 15 }}>ER Network</span>
      </Link>

      <nav className="tabs-scroll" aria-label="Main navigation" style={{ display: 'flex', alignItems: 'stretch', overflowX: 'auto', flex: 1, minWidth: 0 }}>
        {tabs.map((t) => (
          <NavLink key={t.to} to={t.to} className="tab-link" style={({ isActive }) => tab(isActive)}>
            {t.label}
          </NavLink>
        ))}
      </nav>

      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
        <div
          className="hidden md:flex"
          style={{
            alignItems: 'center',
            gap: 6,
            padding: '4px 10px',
            borderRadius: 999,
            border: `1px solid ${colors.border}`,
            background: colors.background,
            fontFamily: fonts.mono,
            fontSize: 11,
            color: colors.text,
          }}
        >
          <span style={{ width: 7, height: 7, borderRadius: 999, background: colors.low }} className="animate-pulse" />
          live
        </div>
        <Link
          to="/login"
          style={{
            padding: '6px 12px',
            borderRadius: 6,
            border: `1px solid ${colors.border}`,
            color: colors.text,
            fontSize: 13,
            textDecoration: 'none',
            whiteSpace: 'nowrap',
          }}
        >
          Operator login
        </Link>
      </div>
    </header>
  );
}

export function StatusBar() {
  const [now, setNow] = useState('');

  useEffect(() => {
    const tick = () => setNow(new Date().toLocaleTimeString('en-GB', { hour12: false }) + ' IST');
    tick();
    const id = setInterval(tick, 1000);
    return () => clearInterval(id);
  }, []);

  return (
    <footer
      style={{
        height: 28,
        flexShrink: 0,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: 16,
        padding: '0 16px',
        background: colors.panel,
        borderTop: `1px solid ${colors.border}`,
        fontFamily: fonts.mono,
        fontSize: 11,
        color: colors.faint,
        userSelect: 'none',
      }}
    >
      <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
        decision-support prototype · ETAs are estimates · ambulance positions are simulated · human verification required
      </span>
      <span style={{ color: colors.muted, whiteSpace: 'nowrap' }}>{now}</span>
    </footer>
  );
}