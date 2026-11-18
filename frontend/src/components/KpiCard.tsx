// src/components/KpiCard.tsx
import React from 'react';
import { colors } from '../theme';

type Severity = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

type Props = {
  title: string;
  value: number | string;
  severity?: Severity;
};

export default function KpiCard({ title, value, severity }: Props) {
  const borderColor = severity ? {
    LOW: colors.low,
    MEDIUM: colors.medium,
    HIGH: colors.high,
    CRITICAL: colors.critical,
  }[severity] : colors.border;

  return (
    <div className="p-4 rounded bg-panel border" style={{ borderColor }}>
      <h3 className="text-sm text-gray-400 mb-1">{title}</h3>
      <p className="text-2xl font-mono" style={{ color: severity ? borderColor : '#e6edf3' }}>{value}</p>
    </div>
  );
}
