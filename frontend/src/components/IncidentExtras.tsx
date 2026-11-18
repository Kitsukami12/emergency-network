// @ts-nocheck
// Small pieces for the Command Center: palette, status figures, lifecycle stepper,
// and the hospital an incident was sent to (from GET /assignments).
import { useQuery } from '@tanstack/react-query';
import L from 'leaflet';
import { Marker, Polyline, Popup } from 'react-leaflet';

const API = import.meta.env.VITE_API_BASE ?? '/api';
const getJson = (path) => fetch(`${API}${path}`).then((r) => (r.ok ? r.json() : Promise.reject(r.status)));

export const T = {
  ink: '#0F1620', panel: '#17212D', raised: '#1E2B3A', line: '#2A3746',
  text: '#E8EDF2', muted: '#8A99A8', accent: '#4CC9F0', casing: '#0A0F16',
};
export const SEV = { CRITICAL: '#E5484D', HIGH: '#F76B15', MEDIUM: '#F5C542', LOW: '#3E9B7A' };
export const FONT = "'Atkinson Hyperlegible', system-ui, -apple-system, sans-serif";

export function useAssignments() {
  const { data } = useQuery({ queryKey: ['assignments'], queryFn: () => getJson('/assignments'), refetchInterval: 4000, retry: false });
  return data ?? {};
}

export function useSiteNames() {
  const { data } = useQuery({ queryKey: ['cameras'], queryFn: () => getJson('/cameras'), staleTime: 60000, retry: false });
  return Object.fromEntries((data ?? []).map((c) => [c.id, c.name]));
}

export function Stat({ n, label, color }) {
  return (
    <div>
      <div style={{ fontSize: 26, fontWeight: 700, lineHeight: 1.1, color: color || T.text, fontVariantNumeric: 'tabular-nums' }}>{n}</div>
      <div style={{ fontSize: 12, color: T.muted, marginTop: 2 }}>{label}</div>
    </div>
  );
}

const STEPS = ['Detected', 'Assigned', 'En route', 'Arrived'];
const STAGE = { AMBULANCE_ASSIGNED: 1, EN_ROUTE: 2, ARRIVED: 3, RESOLVED: 3 };

export function Stepper({ status, color, labels }) {
  const filled = Math.min((STAGE[status] ?? 0) + 1, STEPS.length);
  return (
    <div>
      <div style={{ display: 'flex', gap: 3 }}>
        {STEPS.map((s, i) => (
          <div key={s} style={{ flex: 1, height: 4, borderRadius: 2, background: i < filled ? color : T.line }} />
        ))}
      </div>
      {labels && (
        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 5, fontSize: 11 }}>
          {STEPS.map((s, i) => (
            <span key={s} style={{ color: i < filled ? T.text : T.muted }}>{s}</span>
          ))}
        </div>
      )}
    </div>
  );
}

export function ago(iso) {
  if (!iso) return '';
  const s = Math.max(0, (Date.now() - new Date(iso).getTime()) / 1000);
  if (Number.isNaN(s)) return '';
  if (s < 60) return 'just now';
  if (s < 3600) return `${Math.floor(s / 60)} min ago`;
  return `${Math.floor(s / 3600)} h ago`;
}

export const NOTIFIED = { NEW: 'Sent', ACKNOWLEDGED: 'Acknowledged', ACCEPTED: 'Accepted', DECLINED: 'Declined' };

const hospitalIcon = L.divIcon({
  className: '',
  html: `<div style="width:24px;height:24px;border-radius:50%;background:${T.text};color:${T.ink};display:flex;align-items:center;justify-content:center;font:700 18px/1 sans-serif;border:2px solid ${T.ink}">+</div>`,
  iconSize: [24, 24], iconAnchor: [12, 12],
});

export function SelectedHospital({ hospital, from }) {
  if (!hospital || !from) return null;
  const to = [hospital.lat, hospital.lon];
  return (
    <>
      <Polyline positions={[from, to]} pathOptions={{ color: T.text, weight: 3, opacity: 0.9, dashArray: '2 9', lineCap: 'round' }} />
      <Marker position={to} icon={hospitalIcon}>
        <Popup>
          <strong>{hospital.hospital}</strong><br />
          Scene to hospital: {hospital.scene_to_hospital_min ?? '–'} min<br />
          Dashed line is a straight link, not a route.
        </Popup>
      </Marker>
    </>
  );
}