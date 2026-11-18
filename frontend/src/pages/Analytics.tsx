// src/pages/Analytics.tsx
// @ts-nocheck
import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchAccidents, fetchHospitals } from '../api/client';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LabelList } from 'recharts';
import { colors, fonts } from '../theme';
import { Severity } from '../api/types';

const ORDER = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'];
const SEV_COLOR = { CRITICAL: colors.critical, HIGH: colors.high, MEDIUM: colors.medium, LOW: colors.low };
const STATUS_PALETTE = [colors.accent, colors.low, colors.medium, colors.high, colors.critical, colors.muted];

const tooltipStyle = {
  contentStyle: {
    background: colors.panel,
    border: `1px solid ${colors.border}`,
    borderRadius: 8,
    color: colors.text,
    fontFamily: fonts.mono,
    fontSize: 12,
  },
  itemStyle: { color: colors.text },
  cursor: { fill: colors.raised, opacity: 0.6 },
};

function Card({ title, note, children, style }) {
  return (
    <section
      style={{
        background: colors.panel,
        border: `1px solid ${colors.border}`,
        borderRadius: 12,
        padding: 20,
        ...style,
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: 14 }}>
        <div style={{ fontFamily: fonts.mono, fontSize: 12, color: colors.muted }}>
          <span style={{ color: colors.accent }}>// </span>
          {title}
        </div>
        {note && <div style={{ fontSize: 12, color: colors.faint }}>{note}</div>}
      </div>
      {children}
    </section>
  );
}

function Kpi({ label, value, hint, color }) {
  return (
    <div
      style={{
        background: colors.panel,
        border: `1px solid ${colors.border}`,
        borderTop: `3px solid ${color}`,
        borderRadius: 12,
        padding: '16px 18px',
      }}
    >
      <div style={{ fontSize: 13, color: colors.muted }}>{label}</div>
      <div style={{ fontSize: 34, fontWeight: 700, lineHeight: 1.15, marginTop: 4, color: colors.text, fontVariantNumeric: 'tabular-nums' }}>
        {value}
      </div>
      <div style={{ fontSize: 12, color: colors.faint, marginTop: 2 }}>{hint}</div>
    </div>
  );
}

function Swatch({ color }) {
  return <span style={{ width: 10, height: 10, borderRadius: 3, background: color, display: 'inline-block', flexShrink: 0 }} />;
}

export default function Analytics() {
  const { data: accidents = [], isLoading: aLoading } = useQuery({ queryKey: ['accidents'], queryFn: fetchAccidents });
  const { data: hospitals = [] } = useQuery({ queryKey: ['hospitals'], queryFn: fetchHospitals });

  const counts = accidents.reduce<Record<Severity, number>>(
    (acc, cur) => {
      acc[cur.severity] = (acc[cur.severity] || 0) + 1;
      return acc;
    },
    { LOW: 0, MEDIUM: 0, HIGH: 0, CRITICAL: 0 }
  );

  const total = accidents.length;
  const pct = (n) => (total > 0 ? Math.round((n / total) * 100) : 0);
  const data = ORDER.map((name) => ({ name, count: counts[name] || 0, pct: pct(counts[name] || 0) }));
  const urgent = counts.CRITICAL + counts.HIGH;

  const statusCounts = accidents.reduce((acc, cur) => {
    if (cur.status) acc[cur.status] = (acc[cur.status] || 0) + 1;
    return acc;
  }, {});
  const statusRows = Object.entries(statusCounts).map(([name, count], i) => ({
    name,
    count,
    color: STATUS_PALETTE[i % STATUS_PALETTE.length],
  }));

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16, maxWidth: 1280, margin: '0 auto' }}>
      <div>
        <h1>Analytics</h1>
        <div style={{ color: colors.muted }}>How incidents split by severity across the network.</div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(210px, 1fr))', gap: 16 }}>
        <Kpi label="Total incidents" value={aLoading ? '-' : total} hint="all recorded" color={colors.accent} />
        <Kpi label="Critical" value={aLoading ? '-' : counts.CRITICAL} hint={`${pct(counts.CRITICAL)}% of incidents`} color={colors.critical} />
        <Kpi label="High or critical" value={aLoading ? '-' : urgent} hint={`${pct(urgent)}% need urgent response`} color={colors.high} />
        <Kpi label="Hospitals in network" value={hospitals.length} hint="available for routing" color={colors.low} />
      </div>

      {!aLoading && total === 0 ? (
        <Card title="no incidents yet">
          <div style={{ color: colors.muted }}>
            Nothing to chart. Upload a video in Camera &amp; Detection or run a scenario in the Simulation Lab.
          </div>
        </Card>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(420px, 1fr))', gap: 16 }}>
          <Card title="severity distribution" note="incidents per level">
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={data} layout="vertical" margin={{ top: 4, right: 36, left: 8, bottom: 4 }} barCategoryGap={14}>
                <XAxis type="number" hide domain={[0, 'dataMax']} />
                <YAxis dataKey="name" type="category" axisLine={false} tickLine={false} width={78} />
                <Tooltip {...tooltipStyle} />
                <Bar dataKey="count" radius={[0, 6, 6, 0]}>
                  {data.map((d) => (
                    <Cell key={d.name} fill={SEV_COLOR[d.name]} />
                  ))}
                  <LabelList dataKey="count" position="right" fill={colors.text} fontSize={12} />
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </Card>

          <Card title="severity share" note="percent of all incidents">
            <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: 24 }}>
              <div style={{ position: 'relative', width: 220, height: 220, flexShrink: 0 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie data={data} dataKey="count" nameKey="name" innerRadius={70} outerRadius={100} paddingAngle={3} stroke="none">
                      {data.map((d) => (
                        <Cell key={d.name} fill={SEV_COLOR[d.name]} />
                      ))}
                    </Pie>
                    <Tooltip {...tooltipStyle} />
                  </PieChart>
                </ResponsiveContainer>
                <div
                  style={{
                    position: 'absolute',
                    inset: 0,
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    pointerEvents: 'none',
                  }}
                >
                  <div style={{ fontSize: 34, fontWeight: 700, lineHeight: 1, fontVariantNumeric: 'tabular-nums' }}>{total}</div>
                  <div style={{ fontSize: 12, color: colors.muted, marginTop: 4 }}>incidents</div>
                </div>
              </div>

              <ul style={{ listStyle: 'none', margin: 0, padding: 0, flex: 1, minWidth: 180, display: 'flex', flexDirection: 'column', gap: 10 }}>
                {data.map((d) => (
                  <li key={d.name} style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                    <Swatch color={SEV_COLOR[d.name]} />
                    <span style={{ flex: 1 }}>{d.name}</span>
                    <span style={{ fontFamily: fonts.mono, fontSize: 12, color: colors.muted }}>{d.count}</span>
                    <span style={{ fontFamily: fonts.mono, fontSize: 12, width: 40, textAlign: 'right' }}>{d.pct}%</span>
                  </li>
                ))}
              </ul>
            </div>
          </Card>
        </div>
      )}

      {statusRows.length > 0 && (
        <Card title="incident status" note="where each incident is in its lifecycle">
          <div style={{ display: 'flex', height: 14, borderRadius: 7, overflow: 'hidden', background: colors.raised, gap: 2 }}>
            {statusRows.map((s) => (
              <div key={s.name} title={`${s.name}: ${s.count}`} style={{ flex: s.count, background: s.color }} />
            ))}
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px 24px', marginTop: 14 }}>
            {statusRows.map((s) => (
              <div key={s.name} style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 13 }}>
                <Swatch color={s.color} />
                <span>{s.name.replace(/_/g, ' ').toLowerCase()}</span>
                <span style={{ fontFamily: fonts.mono, fontSize: 12, color: colors.muted }}>{s.count}</span>
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
}