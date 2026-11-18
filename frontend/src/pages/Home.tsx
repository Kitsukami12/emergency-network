// src/pages/Home.tsx
// Landing page. Opens after login. All figures on this page are illustrative, not live data.
import type { CSSProperties } from 'react';
import { Link } from 'react-router-dom';
import { colors, fonts } from '../theme';

function Logo({ size }: { size: number }) {
  return (
    <span
      aria-hidden="true"
      style={{
        width: size,
        height: size,
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        borderRadius: 8,
        background: colors.accent,
        color: colors.background,
        fontSize: size * 0.72,
        fontWeight: 700,
        lineHeight: 1,
      }}
    >
      +
    </span>
  );
}

const ROUTE = 'M80,400 L80,220 L330,220 L330,150 L400,150 L400,60';

const steps = [
  { title: 'Detect', body: 'Cameras watch the road and flag a likely collision from the video feed.' },
  { title: 'Verify', body: 'Uncertain detections wait in a queue until a dispatcher confirms or dismisses them.' },
  { title: 'Dispatch', body: 'The network assigns an ambulance using the Hungarian method or nearest-first.' },
  { title: 'Notify', body: 'The receiving hospital gets an incoming notification before the ambulance arrives.' },
];

const views = [
  { to: '/command', title: 'Command Center', body: 'Live map, incident feed and the recording from before impact.' },
  { to: '/camera', title: 'Camera & Detection', body: 'Upload a video and review the needs-verification queue.' },
  { to: '/hospital', title: 'Hospital Portal', body: 'Choose a hospital and watch its incoming notifications.' },
  { to: '/simulation', title: 'Simulation Lab', body: 'Compare Hungarian and nearest assignment on a seeded scenario.' },
  { to: '/analytics', title: 'Analytics', body: 'See how incidents split across severity levels.' },
];

const wrap: CSSProperties = { maxWidth: 1180, margin: '0 auto', padding: '0 24px' };

const primary: CSSProperties = {
  display: 'inline-flex',
  alignItems: 'center',
  gap: 8,
  padding: '12px 20px',
  borderRadius: 8,
  background: colors.accent,
  color: colors.background,
  fontWeight: 700,
  fontSize: 15,
  textDecoration: 'none',
};

const ghost: CSSProperties = {
  display: 'inline-flex',
  alignItems: 'center',
  padding: '12px 20px',
  borderRadius: 8,
  border: `1px solid ${colors.border}`,
  background: 'transparent',
  color: colors.text,
  fontWeight: 700,
  fontSize: 15,
  textDecoration: 'none',
};

function Legend({ color, label }: { color: string; label: string }) {
  return (
    <span style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
      <span style={{ width: 8, height: 8, borderRadius: 999, background: color }} />
      {label}
    </span>
  );
}

function RouteMap() {
  return (
    <div style={{ background: colors.panel, border: `1px solid ${colors.border}`, borderRadius: 14, overflow: 'hidden' }}>
      <svg viewBox="0 0 560 440" width="100%" role="img" aria-label="Illustration of an ambulance driving to an incident and then to a hospital" style={{ display: 'block' }}>
        <defs>
          <pattern id="grid" width="28" height="28" patternUnits="userSpaceOnUse">
            <path d="M28 0H0V28" fill="none" stroke={colors.border} strokeWidth="0.6" opacity="0.55" />
          </pattern>
        </defs>
        <rect width="560" height="440" fill={colors.background} />
        <rect width="560" height="440" fill="url(#grid)" />

        {/* roads */}
        <g fill="none" stroke={colors.raised} strokeWidth="14" strokeLinecap="round" strokeLinejoin="round">
          <path d="M-10,300 L180,300 L180,150 L400,150 L400,60 L570,60" />
          <path d="M80,450 L80,220 L330,220 L330,450" />
          <path d="M-10,100 L240,100 L240,-10" />
          <path d="M480,450 L480,150 L570,150" />
        </g>
        <g fill="none" stroke={colors.border} strokeWidth="1" strokeDasharray="6 8">
          <path d="M-10,300 L180,300 L180,150 L400,150 L400,60 L570,60" />
          <path d="M80,450 L80,220 L330,220 L330,450" />
          <path d="M-10,100 L240,100 L240,-10" />
          <path d="M480,450 L480,150 L570,150" />
        </g>

        {/* ambulance route */}
        <path d={ROUTE} fill="none" stroke={colors.accent} strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" strokeDasharray="2 9" opacity="0.9">
          <animate attributeName="stroke-dashoffset" from="0" to="-110" dur="3s" repeatCount="indefinite" />
        </path>

        {/* cameras */}
        {[
          [180, 300],
          [240, 100],
          [480, 150],
        ].map(([x, y]) => (
          <g key={`${x}-${y}`}>
            <circle cx={x} cy={y} r="16" fill="none" stroke={colors.accent} strokeWidth="1" opacity="0.35" />
            <rect x={x - 5} y={y - 5} width="10" height="10" rx="2" fill={colors.panel} stroke={colors.accent} strokeWidth="1.5" />
          </g>
        ))}

        {/* hospital */}
        <rect x="388" y="36" width="24" height="24" rx="5" fill={colors.low} />
        <path d="M398,41h4v5h5v4h-5v5h-4v-5h-5v-4h5z" fill={colors.background} transform="translate(0,-1)" />
        <text x="424" y="52" fill={colors.muted} fontFamily={fonts.mono} fontSize="11">hospital</text>

        {/* incident */}
        <circle cx="330" cy="220" r="8" fill={colors.critical} />
        <circle cx="330" cy="220" r="8" fill="none" stroke={colors.critical} strokeWidth="2">
          <animate attributeName="r" from="8" to="34" dur="2s" repeatCount="indefinite" />
          <animate attributeName="opacity" from="0.7" to="0" dur="2s" repeatCount="indefinite" />
        </circle>
        <text x="346" y="204" fill={colors.muted} fontFamily={fonts.mono} fontSize="11">incident</text>

        {/* ambulance */}
        <g>
          <circle r="11" fill={colors.accent} opacity="0.25" />
          <circle r="5.5" fill={colors.accent} stroke={colors.background} strokeWidth="2" />
          <animateMotion dur="8s" repeatCount="indefinite" path={ROUTE} />
        </g>
      </svg>
      <div
        style={{
          display: 'flex',
          flexWrap: 'wrap',
          justifyContent: 'space-between',
          gap: 8,
          padding: '10px 14px',
          borderTop: `1px solid ${colors.border}`,
          fontFamily: fonts.mono,
          fontSize: 11,
          color: colors.muted,
        }}
      >
        <span style={{ display: 'inline-flex', gap: 14, flexWrap: 'wrap' }}>
          <Legend color={colors.critical} label="incident" />
          <Legend color={colors.accent} label="ambulance" />
          <Legend color={colors.low} label="hospital" />
        </span>
        <span style={{ color: colors.faint }}>illustration, not live data</span>
      </div>
    </div>
  );
}

export default function Home() {
  return (
    <div style={{ minHeight: '100vh', background: colors.background, color: colors.text }}>
      <header style={{ borderBottom: `1px solid ${colors.border}`, background: colors.panel }}>
        <div style={{ ...wrap, height: 60, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <Logo size={30} />
            <span style={{ fontWeight: 700, fontSize: 16 }}>ER Network</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <Link to="/login" className="btn-ghost" style={{ ...ghost, padding: '8px 14px', fontSize: 13 }}>
              Operator login
            </Link>
            <Link to="/command" className="btn-primary" style={{ ...primary, padding: '8px 14px', fontSize: 13 }}>
              Open console
            </Link>
          </div>
        </div>
      </header>

      <section style={{ ...wrap, padding: '72px 24px 64px' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: 48, alignItems: 'center' }}>
          <div>
            <div
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: 8,
                padding: '5px 12px',
                borderRadius: 999,
                border: `1px solid ${colors.border}`,
                background: colors.panel,
                fontFamily: fonts.mono,
                fontSize: 12,
                color: colors.muted,
              }}
            >
              <span style={{ width: 7, height: 7, borderRadius: 999, background: colors.low }} />
              Decision-support prototype for Indore
            </div>
            <h1 style={{ fontSize: 'clamp(34px, 5vw, 56px)', lineHeight: 1.08, fontWeight: 700, letterSpacing: '-0.02em', margin: '20px 0 18px' }}>
              From the first frame of a crash to the nearest ambulance.
            </h1>
            <p style={{ fontSize: 18, lineHeight: 1.6, color: colors.muted, maxWidth: 540, margin: 0 }}>
              Cameras flag collisions, a dispatcher verifies them, and the network picks the best ambulance and warns the
              hospital. One console for the whole response.
            </p>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 12, marginTop: 32 }}>
              <Link to="/command" className="btn-primary" style={primary}>
                Open command center
              </Link>
              <Link to="/simulation" className="btn-ghost" style={ghost}>
                Run a simulation
              </Link>
            </div>
          </div>
          <RouteMap />
        </div>
      </section>

      <section style={{ borderTop: `1px solid ${colors.border}`, borderBottom: `1px solid ${colors.border}`, background: colors.panel }}>
        <div style={{ ...wrap, padding: '56px 24px' }}>
          <h2 style={{ fontSize: 28, fontWeight: 700, letterSpacing: '-0.01em', margin: '0 0 32px' }}>How a response runs</h2>
          <ol style={{ listStyle: 'none', margin: 0, padding: 0, display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(230px, 1fr))', gap: 16 }}>
            {steps.map((s, i) => (
              <li key={s.title} style={{ padding: 20, borderRadius: 12, border: `1px solid ${colors.border}`, background: colors.background }}>
                <div style={{ fontFamily: fonts.mono, fontSize: 12, color: colors.accent, marginBottom: 10 }}>step {i + 1}</div>
                <div style={{ fontSize: 18, fontWeight: 700, marginBottom: 6 }}>{s.title}</div>
                <div style={{ color: colors.muted, lineHeight: 1.55 }}>{s.body}</div>
              </li>
            ))}
          </ol>
        </div>
      </section>

      <section style={{ ...wrap, padding: '56px 24px 40px' }}>
        <h2 style={{ fontSize: 28, fontWeight: 700, letterSpacing: '-0.01em', margin: '0 0 8px' }}>Jump into a view</h2>
        <p style={{ color: colors.muted, margin: '0 0 28px' }}>Each screen covers one part of the response.</p>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: 16 }}>
          {views.map((v) => (
            <Link
              key={v.to}
              to={v.to}
              className="card-link"
              style={{
                display: 'block',
                padding: 20,
                borderRadius: 12,
                border: `1px solid ${colors.border}`,
                background: colors.panel,
                color: colors.text,
                textDecoration: 'none',
              }}
            >
              <div style={{ fontSize: 17, fontWeight: 700, marginBottom: 6 }}>{v.title}</div>
              <div style={{ color: colors.muted, lineHeight: 1.55 }}>{v.body}</div>
              <div style={{ marginTop: 14, fontFamily: fonts.mono, fontSize: 12, color: colors.accent }}>{v.to}</div>
            </Link>
          ))}
        </div>
      </section>

      <footer style={{ borderTop: `1px solid ${colors.border}` }}>
        <div style={{ ...wrap, padding: '20px 24px', fontFamily: fonts.mono, fontSize: 11, color: colors.faint, lineHeight: 1.7 }}>
          ETAs are estimates, not guaranteed. Ambulance positions are simulated. Incident severity is an estimate, not
          medical severity. Human verification is required.
        </div>
      </footer>
    </div>
  );
}