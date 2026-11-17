// src/pages/Analytics.tsx
// @ts-nocheck
import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchAccidents, fetchHospitals } from '../api/client';
import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { colors } from '../theme';
import { Severity } from '../api/types';

export default function Analytics() {
  const { data: accidents = [], isLoading: aLoading } = useQuery(['accidents'], fetchAccidents);
  const { data: hospitals = [], isLoading: hLoading } = useQuery(['hospitals'], fetchHospitals);

  // Aggregations
  const severityCounts = accidents.reduce<Record<Severity, number>>((acc, cur) => {
    acc[cur.severity] = (acc[cur.severity] || 0) + 1;
    return acc;
  }, { LOW: 0, MEDIUM: 0, HIGH: 0, CRITICAL: 0 });

  const barData = Object.entries(severityCounts).map(([sev, count]) => ({ name: sev, count }));
  const pieData = barData;
  const pieColors = [colors.low, colors.medium, colors.high, colors.critical];

  return (
    <div className="flex flex-col gap-4">
      <h2 className="text-2xl" style={{ color: colors.accent }}>Analytics</h2>
      <section className="bg-panel border border-border rounded p-4">
        <h3 className="font-semibold mb-2" style={{ color: colors.accent }}>Severity Distribution</h3>
        {aLoading ? (
          <p className="text-gray-400">Loading…</p>
        ) : (
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={barData} layout="vertical" margin={{ top: 20, right: 30, left: 40, bottom: 20 }}>
              <XAxis type="number" />
              <YAxis dataKey="name" type="category" />
              <Tooltip />
              <Bar dataKey="count" fill={colors.accent} />
            </BarChart>
          </ResponsiveContainer>
        )}
      </section>

      <section className="bg-panel border border-border rounded p-4">
        <h3 className="font-semibold mb-2" style={{ color: colors.accent }}>Severity Share (Pie)</h3>
        {aLoading ? (
          <p className="text-gray-400">Loading…</p>
        ) : (
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie data={pieData} dataKey="count" nameKey="name" cx="50%" cy="50%" outerRadius={80} label>
                {pieData.map((_, idx) => (
                  <Cell key={`cell-${idx}`} fill={pieColors[idx % pieColors.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        )}
      </section>
    </div>
  );
}
