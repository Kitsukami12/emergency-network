// src/pages/CommandCenter.tsx
// @ts-nocheck
import React, { useState } from 'react';
import { useQuery, useQueries, useMutation, useQueryClient } from '@tanstack/react-query';
import { MapContainer, Marker, Polyline, Popup, useMap } from 'react-leaflet';
import IncidentMedia from '../components/IncidentMedia';
import { FONT, NOTIFIED, SEV, SelectedHospital, Stat, Stepper, T, ago, useAssignments, useSiteNames } from '../components/IncidentExtras';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import BaseMap from '../components/BaseMap';
import KpiCard from '../components/KpiCard';
import { colors } from '../theme';
import {
  api, isMock, fetchAccidents, fetchAmbulances, fetchRoute, dispatch, advanceAccident,
  severityColorMap, ambulanceStatusColorMap,
} from '../api/client';

const CENTER = [22.7196, 75.8577];
const SEV_ORDER = { CRITICAL: 0, HIGH: 1, MEDIUM: 2, LOW: 3 };
const NEXT = { AMBULANCE_ASSIGNED: 'EN_ROUTE', EN_ROUTE: 'ARRIVED', ARRIVED: 'RESOLVED' };
const LABEL = {
  DETECTED: 'Detected', ASSESSING: 'Assessing', NEEDS_VERIFICATION: 'Needs verification',
  AWAITING_AMBULANCE: 'Awaiting ambulance', AMBULANCE_ASSIGNED: 'Ambulance assigned',
  EN_ROUTE: 'En route', ARRIVED: 'Arrived', RESOLVED: 'Resolved', CANCELLED: 'Cancelled',
};
const API_BASE = import.meta.env.VITE_API_BASE || '';

const dot = (color, size, ring) => L.divIcon({
  className: '', iconSize: [size, size], iconAnchor: [size / 2, size / 2],
  html: `<div style="width:${size}px;height:${size}px;border-radius:50%;background:${color};border:2px solid ${ring ? '#fff' : 'rgba(0,0,0,.55)'};box-shadow:0 0 ${ring ? 12 : 0}px ${color}"></div>`,
});

function FlyTo({ target }) {
  const map = useMap();
  React.useEffect(() => {
    if (target) map.flyTo(target, Math.max(map.getZoom(), 14), { duration: 0.6 });
  }, [target]);
  return null;
}

export default function CommandCenter() {
  const qc = useQueryClient();
  const [selId, setSelId] = useState(null);
  const [strategy, setStrategy] = useState('hungarian');
  const [msg, setMsg] = useState('');
  const say = (t) => { setMsg(t); setTimeout(() => setMsg(''), 5000); };

  const { data: accidents = [], isLoading } = useQuery({ queryKey: ['accidents'], queryFn: fetchAccidents, refetchInterval: 3000 });
  const { data: ambulances = [] } = useQuery({ queryKey: ['ambulances'], queryFn: fetchAmbulances, refetchInterval: 3000 });
  const refresh = () => ['accidents', 'ambulances', 'notifications'].forEach((k) => qc.invalidateQueries({ queryKey: [k] }));

  const live = accidents.filter((a) => !['RESOLVED', 'CANCELLED'].includes(a.status));
  const ambById = Object.fromEntries(ambulances.map((a) => [a.ambulance_id, a]));
  const responding = live
    .filter((a) => ['AMBULANCE_ASSIGNED', 'EN_ROUTE'].includes(a.status) && ambById[a.assigned_ambulance_id])
    .slice(0, 15);                                         // cap routing calls
  const routeQs = useQueries({
    queries: responding.map((a) => ({
      queryKey: ['route', a.accident_id, a.assigned_ambulance_id],
      queryFn: () => fetchRoute(ambById[a.assigned_ambulance_id].location, a.location),
      staleTime: 10 * 60 * 1000, retry: false,
    })),
  });
  const routes = {};
  responding.forEach((a, i) => { if (routeQs[i]?.data) routes[a.accident_id] = routeQs[i].data; });

  const count = (f) => accidents.filter(f).length;
  const etas = Object.values(routes).map((r) => r.estimated_time_min).filter(Boolean);
  const avgEta = etas.length ? `${(etas.reduce((s, x) => s + x, 0) / etas.length).toFixed(1)} min` : '–';
  const pending = count((a) => a.status === 'AWAITING_AMBULANCE' || a.status === 'NEEDS_VERIFICATION');

  const dispatchM = useMutation({
    mutationFn: () => dispatch(strategy),
    onSuccess: (out) => {
      const n = Array.isArray(out) ? out.length : 0;
      say(n ? `Dispatched ${n} ambulance(s) using ${strategy}` : pending ? 'NO AVAILABLE AMBULANCE' : 'Nothing pending');
      refresh();
    },
    onError: () => say('Dispatch failed'),
  });
  const advanceM = useMutation({ mutationFn: (id) => advanceAccident(id), onSuccess: refresh });

  const simulate = async () => {
    if (isMock) return say('Simulate needs the real backend (VITE_USE_MOCK=false)');
    const sev = ['LOW', 'MEDIUM', 'MEDIUM', 'HIGH', 'CRITICAL'][Math.floor(Math.random() * 5)];
    try {
      const r = await api.post('/accidents', {
        location: { lat: CENTER[0] + (Math.random() - 0.5) * 0.08, lon: CENTER[1] + (Math.random() - 0.5) * 0.08 },
        severity: sev, source: 'manual', description: 'Simulated accident (dashboard)',
      });
      setSelId(r.data.accident_id); refresh();
    } catch (e) { say('Could not create incident'); }
  };
  const reset = async () => {
    if (isMock || !window.confirm('Delete ALL incidents and notifications and free every ambulance?')) return;
    try { await api.post('/demo/reset'); setSelId(null); qc.removeQueries({ queryKey: ['route'] }); refresh(); say('Demo reset'); }
    catch (e) { say('Reset failed'); }
  };

  const sel = accidents.find((a) => a.accident_id === selId);
  const selRoute = sel && routes[sel.accident_id];
  const feed = [...live].sort((a, b) => (SEV_ORDER[a.severity] ?? 9) - (SEV_ORDER[b.severity] ?? 9)
    || new Date(b.reported_at) - new Date(a.reported_at)).slice(0, 40);
  const frame = sel?.frame_path && !isMock ? `${API_BASE}/frames/${sel.frame_path.split('/').pop()}` : null;
  const btn = 'px-3 py-1.5 rounded border border-border text-sm hover:opacity-80';
  const assignments = useAssignments();
  const siteNames = useSiteNames();

const free = ambulances.filter((a) => String(a.status).toUpperCase() === 'AVAILABLE').length;
  const critical = count((a) => a.severity === 'CRITICAL' && !['RESOLVED', 'CANCELLED'].includes(a.status));
  const selHosp = sel ? assignments[sel.accident_id] : null;
  const title = (a) => siteNames[a.camera_id] || (a.source === 'camera' ? a.camera_id : 'Reported incident');
  const ctl = { padding: '7px 14px', borderRadius: 6, border: `1px solid ${T.line}`, background: T.panel, color: T.text, fontSize: 14, cursor: 'pointer', fontFamily: 'inherit' };
  const primary = { ...ctl, background: T.accent, borderColor: T.accent, color: T.casing, fontWeight: 700 };
  const row = (k, v) => (
    <div key={k} style={{ display: 'flex', justifyContent: 'space-between', gap: 12, fontSize: 13 }}>
      <span style={{ color: T.muted }}>{k}</span>
      <span style={{ textAlign: 'right' }}>{v}</span>
    </div>
  );

  return (
    <div style={{ fontFamily: FONT, color: T.text, display: 'flex', flexDirection: 'column', gap: 14 }}>
      <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between', gap: 16 }}>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 28 }}>
          <Stat n={live.length} label="active incidents" />
          <Stat n={pending} label="waiting for an ambulance" color={pending > 0 ? SEV.MEDIUM : undefined} />
          <Stat n={count((a) => ['AMBULANCE_ASSIGNED', 'EN_ROUTE'].includes(a.status))} label="responding" />
          <Stat n={free} label="ambulances free" />
          <Stat n={avgEta} label="average ETA (estimated)" />
          {critical > 0 && <Stat n={critical} label="critical" color={SEV.CRITICAL} />}
        </div>
        <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: 8 }}>
          {msg && <span style={{ fontSize: 13, color: T.accent }}>{msg}</span>}
          <select value={strategy} onChange={(e) => setStrategy(e.target.value)} style={ctl} aria-label="Dispatch strategy">
            <option value="hungarian">Hungarian</option>
            <option value="nearest">Nearest</option>
          </select>
          <button style={primary} onClick={() => dispatchM.mutate()}>Dispatch pending ({pending})</button>
          <button style={ctl} onClick={simulate}>Simulate accident</button>
          <button style={ctl} onClick={reset}>Reset demo</button>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1fr) 380px', gap: 14, height: 'calc(100vh - 190px)', minHeight: 560 }}>
        <div style={{ borderRadius: 10, overflow: 'hidden', border: `1px solid ${T.line}` }}>
          <MapContainer center={CENTER} zoom={13} style={{ height: '100%', width: '100%' }}>
            <BaseMap />
            <FlyTo target={sel ? [sel.location.lat, sel.location.lon] : null} />
            <SelectedHospital hospital={selHosp} from={sel ? [sel.location.lat, sel.location.lon] : null} />
            {ambulances.map((amb) => (
              <Marker key={amb.ambulance_id} position={[amb.location.lat, amb.location.lon]}
                icon={dot(ambulanceStatusColorMap[amb.status] || '#4c9aff', 11, false)}>
                <Popup><strong>{amb.ambulance_id}</strong><br />{amb.status}</Popup>
              </Marker>
            ))}
            {live.map((a) => (
              <Marker key={a.accident_id} position={[a.location.lat, a.location.lon]}
                icon={dot(SEV[a.severity] || '#ccc', a.accident_id === selId ? 24 : 18, a.accident_id === selId)}
                eventHandlers={{ click: () => setSelId(a.accident_id) }}>
                <Popup><strong>{title(a)}</strong><br />{a.severity}, {LABEL[a.status] || a.status}</Popup>
              </Marker>
            ))}
            {responding.map((a) => {
              const r = routes[a.accident_id];
              const amb = ambById[a.assigned_ambulance_id];
              const pts = r?.coordinates?.length > 1 ? r.coordinates.map((c) => [c.lat, c.lon])
                : [[amb.location.lat, amb.location.lon], [a.location.lat, a.location.lon]];
              const on = a.accident_id === selId;
              return [
                <Polyline key={a.accident_id + '-casing'} positions={pts}
                  pathOptions={{ color: T.casing, weight: on ? 15 : 11, opacity: 0.9, lineCap: 'round', lineJoin: 'round' }} />,
                <Polyline key={a.accident_id} positions={pts}
                  pathOptions={{ color: SEV[a.severity] || T.accent, weight: on ? 9 : 6, opacity: 1, lineCap: 'round', lineJoin: 'round', dashArray: r ? null : '6 8' }} />,
              ];
            })}
          </MapContainer>
        </div>

        <aside style={{ background: T.panel, border: `1px solid ${T.line}`, borderRadius: 10, overflow: 'auto' }}>
          <div style={{ padding: '12px 14px', borderBottom: `1px solid ${T.line}`, fontSize: 13, color: T.muted }}>
            Incidents, most severe first
          </div>
          {isLoading ? (
            <div style={{ padding: 16, color: T.muted }}>Loading…</div>
          ) : feed.length === 0 ? (
            <div style={{ padding: 16, color: T.muted }}>No active incidents. Use Simulate accident, or start a camera agent.</div>
          ) : feed.map((a) => {
            const open = a.accident_id === selId;
            const hosp = assignments[a.accident_id];
            const r = routes[a.accident_id];
            const sevColor = SEV[a.severity] || T.muted;
            return (
              <div key={a.accident_id} onClick={() => setSelId(open ? null : a.accident_id)}
                style={{ borderLeft: `4px solid ${sevColor}`, borderBottom: `1px solid ${T.line}`, background: open ? T.raised : 'transparent', padding: '12px 14px', cursor: 'pointer' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', gap: 8 }}>
                  <strong style={{ fontSize: 15 }}>{title(a)}</strong>
                  <span style={{ fontSize: 12, color: T.muted, whiteSpace: 'nowrap' }}>{ago(a.reported_at)}</span>
                </div>
                <div style={{ fontSize: 13, marginTop: 2 }}>
                  <span style={{ color: sevColor, fontWeight: 700 }}>{a.severity}</span>
                  <span style={{ color: T.muted, marginLeft: 8 }}>{LABEL[a.status] || a.status}</span>
                </div>
                <div style={{ marginTop: 8 }}><Stepper status={a.status} color={sevColor} labels={open} /></div>
                {!open && (a.assigned_ambulance_id || hosp) && (
                  <div style={{ fontSize: 12, color: T.muted, marginTop: 6, display: 'flex', flexWrap: 'wrap', gap: 12 }}>
                    {a.assigned_ambulance_id && <span>Ambulance {a.assigned_ambulance_id}</span>}
                    {hosp && <span>Hospital: {hosp.hospital}</span>}
                  </div>
                )}
                {open && (
                  <div onClick={(e) => e.stopPropagation()} style={{ marginTop: 12, display: 'flex', flexDirection: 'column', gap: 10, cursor: 'default' }}>
                    {!isMock && <IncidentMedia accidentId={a.accident_id} />}
                    {a.description && <div style={{ fontSize: 12, color: T.muted }}>{a.description}</div>}
                    {row('Hospital', hosp ? `${hosp.hospital}, ${NOTIFIED[hosp.notification_status] || hosp.notification_status}` : 'Not notified yet')}
                    {hosp && hosp.scene_to_hospital_min != null && row('Scene to hospital', `${hosp.scene_to_hospital_min} min`)}
                    {row('Ambulance', a.assigned_ambulance_id || 'Not assigned yet')}
                    {row('Ambulance ETA', r ? `${r.estimated_time_min} min, ${r.distance_km} km` : '–')}
                    {row('Vehicles involved', a.vehicle_count ?? 'not measured')}
                    {row('People nearby (approx.)', a.people_count ?? 'not measured')}
                    {row('Detection confidence', a.detection_confidence != null ? Math.round(a.detection_confidence * 100) + '%' : 'not measured')}
                    {row('Road and weather', `${a.road_type || '–'}, ${a.weather?.summary || '–'}${a.weather?.temperature_c != null ? `, ${a.weather.temperature_c} °C` : ''}`)}
                    <div style={{ fontSize: 11, color: T.muted }}>Severity is a rule-based estimate, not a medical assessment.</div>
                    <div style={{ display: 'flex', gap: 8 }}>
                      {a.status === 'AWAITING_AMBULANCE' && <button style={primary} onClick={() => dispatchM.mutate()}>Dispatch now</button>}
                      {NEXT[a.status] && <button style={ctl} onClick={() => advanceM.mutate(a.accident_id)}>Mark {LABEL[NEXT[a.status]].toLowerCase()}</button>}
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </aside>
      </div>
    </div>
  );
}