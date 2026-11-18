// src/components/Header.tsx
import { useState, useEffect } from 'react';
import type { CSSProperties } from 'react';
import { useLocation } from 'react-router-dom';
import { colors, fonts } from '../theme';

const pill: CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: 6,
  padding: '3px 9px',
  borderRadius: 3,
  background: colors.background,
  border: `1px solid ${colors.border}`,
  fontFamily: fonts.mono,
  fontSize: 11,
  color: colors.muted,
  whiteSpace: 'nowrap',
};

export default function Header() {
  const { pathname } = useLocation();
  const [timeStr, setTimeStr] = useState('');

  useEffect(() => {
    const tick = () => setTimeStr(new Date().toLocaleTimeString('en-GB', { hour12: false }) + ' IST');
    tick();
    const id = setInterval(tick, 1000);
    return () => clearInterval(id);
  }, []);

  const view = pathname.replace(/^\//, '') || 'command';

  return (
    <header
      style={{
        height: 48,
        flexShrink: 0,
        background: colors.panel,
        borderBottom: `1px solid ${colors.border}`,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 16px',
        userSelect: 'none',
        fontFamily: fonts.mono,
        fontSize: 13,
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', minWidth: 0 }}>
        <span style={{ color: colors.muted }}>dispatch@indore</span>
        <span style={{ color: colors.faint }}>:</span>
        <span style={{ color: colors.accent }}>~/{view}</span>
        <span style={{ color: colors.muted, marginLeft: 6 }}>$</span>
        <span className="cursor" />
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <div className="hidden lg:flex items-center gap-2">
          <div style={{ ...pill, color: colors.text }}>
            <span style={{ width: 7, height: 7, borderRadius: 999, background: colors.low }} className="animate-pulse" />
            live
          </div>
          <div style={{ ...pill, color: colors.accent, borderColor: colors.accent + '55' }}>decision-support prototype</div>
          <div style={pill}>{timeStr}</div>
        </div>
        <div style={{ ...pill, color: colors.text }}>
          <span style={{ width: 7, height: 7, borderRadius: 999, background: colors.low }} />
          dispatcher-desk
        </div>
      </div>
    </header>
  );
}