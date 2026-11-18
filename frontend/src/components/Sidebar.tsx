// src/components/Sidebar.tsx
import { NavLink } from 'react-router-dom';
import type { CSSProperties } from 'react';
import { colors, fonts } from '../theme';

const links = [
  { to: '/command', label: 'command-center' },
  { to: '/camera', label: 'camera-detection' },
  { to: '/hospital', label: 'hospital-portal' },
  { to: '/simulation', label: 'simulation-lab' },
  { to: '/analytics', label: 'analytics' },
];

function item(isActive: boolean): CSSProperties {
  return {
    display: 'flex',
    alignItems: 'center',
    gap: 8,
    padding: '8px 10px',
    fontFamily: fonts.mono,
    fontSize: 13,
    fontWeight: isActive ? 700 : 400,
    color: isActive ? colors.text : colors.muted,
    background: isActive ? colors.raised : 'transparent',
    borderLeft: `2px solid ${isActive ? colors.accent : 'transparent'}`,
    textDecoration: 'none',
  };
}

function Entry({ to, label }: { to: string; label: string }) {
  return (
    <NavLink to={to} className="nav-link" style={({ isActive }) => item(isActive)}>
      {({ isActive }) => (
        <>
          <span style={{ color: isActive ? colors.accent : colors.faint, width: 10 }}>{isActive ? '>' : ' '}</span>
          <span>{label}</span>
        </>
      )}
    </NavLink>
  );
}

export default function Sidebar() {
  return (
    <nav
      aria-label="Main navigation"
      style={{
        width: 224,
        flexShrink: 0,
        background: colors.panel,
        borderRight: `1px solid ${colors.border}`,
        display: 'flex',
        flexDirection: 'column',
        fontFamily: fonts.mono,
      }}
    >
      <div style={{ padding: '16px 14px 14px', borderBottom: `1px solid ${colors.border}` }}>
        <div style={{ display: 'flex', alignItems: 'center', fontSize: 15, fontWeight: 700, color: colors.text }}>
          <span style={{ color: colors.accent }}>$&nbsp;</span>er-network
          <span className="cursor" />
        </div>
        <div style={{ fontSize: 11, color: colors.faint, marginTop: 4 }}>indore / madhya-pradesh</div>
      </div>

      <div style={{ padding: '14px 14px 6px', fontSize: 11, color: colors.faint }}>// views</div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 2, padding: '0 8px' }}>
        {links.map((l) => (
          <Entry key={l.to} to={l.to} label={l.label} />
        ))}
      </div>

      <div style={{ marginTop: 'auto', padding: 8 }}>
        <Entry to="/login" label="operator-login" />
        <div
          style={{
            margin: '10px 4px 6px',
            paddingTop: 10,
            borderTop: `1px solid ${colors.border}`,
            fontSize: 11,
            lineHeight: 1.5,
            color: colors.faint,
          }}
        >
          # ETAs are estimates.
          <br /># ambulance positions are simulated.
        </div>
      </div>
    </nav>
  );
}