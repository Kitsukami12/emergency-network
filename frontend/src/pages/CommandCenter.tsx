// (no ts-nocheck)
import React from 'react';
import type { Accident, Ambulance, Location, Severity } from '../api/types';
import { fetchAccidents, fetchAmbulances, severityColorMap, ambulanceStatusColorMap } from '../api/client';
import { useQuery } from '@tanstack/react-query';
import KpiCard from '../components/KpiCard';
import { MapContainer, TileLayer, Marker, Polyline, Popup } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { colors } from '../theme';
// Fix default icon issue
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png';
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';

delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});

const center: Location = { lat: 22.7196, lon: 75.8577 };

export default function CommandCenter() {
  const { data: accidents = [], isLoading: accidentsLoading } = useQuery<Accident[]>({
    queryKey: ['accidents'],
    queryFn: fetchAccidents,
    refetchInterval: 2000,
  });
  const { data: ambulances = [], isLoading: ambLoading } = useQuery<Ambulance[]>({
    queryKey: ['ambulances'],
    queryFn: fetchAmbulances,
    refetchInterval: 2000,
  });

  // KPI calculations
  const totalIncidents = accidents.length;
  const pending = accidents.filter((a) => a.status === 'AWAITING_AMBULANCE' || a.status === 'NEEDS_VERIFICATION').length;
  const assigned = accidents.filter((a) => !!a.assigned_ambulance_id).length;
  const resolved = accidents.filter((a) => a.status === 'RESOLVED').length;
  const critical = accidents.filter((a) => a.severity === 'CRITICAL').length;
  const averageResponse = (() => {
    const resolvedAcc = accidents.filter((a) => a.status === 'RESOLVED');
    if (resolvedAcc.length === 0) return '–';
    // mock: use random estimate
    return `${Math.round(5 + Math.random() * 10)} min`;
  })();

  // Map markers
  const accidentMarkers = accidents.map((a) => (
    <Marker
      key={a.accident_id}
      position={[a.location.lat, a.location.lon]}
      icon={L.divIcon({
        className: 'custom-accident-marker',
        html: `<div style=\"background:${severityColorMap[a.severity as Severity]};width:12px;height:12px;border-radius:50%;\"></div>`,
      })}
    >
      <Popup>
        <strong>{a.accident_id}</strong><br />{a.severity}<br />{a.status}
      </Popup>
    </Marker>
  ));

  const ambulanceMarkers = ambulances.map((amb) => (
    <Marker
      key={amb.ambulance_id}
      position={[amb.location.lat, amb.location.lon]}
      icon={L.divIcon({
        className: 'custom-ambulance-marker',
        html: `<div style=\"background:${ambulanceStatusColorMap[amb.status]};width:10px;height:10px;border-radius:50%;\"></div>`,
      })}
    >
      <Popup>
        <strong>{amb.ambulance_id}</strong><br />{amb.status}
      </Popup>
    </Marker>
  ));

  // Simple polyline between accidents and assigned ambulances
  const polylines = accidents
    .filter((a) => a.assigned_ambulance_id)
    .map((a) => {
      const amb = ambulances.find((b) => b.ambulance_id === a.assigned_ambulance_id);
      if (!amb) return null;
      return (
        <Polyline
          key={a.accident_id}
          positions={[[a.location.lat, a.location.lon], [amb.location.lat, amb.location.lon]]}
          color={severityColorMap[a.severity]}
        />
      );
    })
    .filter(Boolean);

  return (
    <div className="flex flex-col gap-4">
      {/* KPI Row */}
      <div className="grid grid-cols-3 md:grid-cols-6 gap-4">
        <KpiCard title="Total Incidents" value={totalIncidents} />
        <KpiCard title="Pending" value={pending} severity="MEDIUM" />
        <KpiCard title="Assigned" value={assigned} severity="LOW" />
        <KpiCard title="Resolved" value={resolved} severity="LOW" />
        <KpiCard title="Critical" value={critical} severity="CRITICAL" />
        <KpiCard title="Avg Response" value={averageResponse} severity="HIGH" />
      </div>

      {/* Map */}
      <div className="h-96 rounded bg-panel border border-border overflow-hidden">
        <MapContainer center={[center.lat, center.lon]} zoom={13} style={{ height: '100%', width: '100%' }}>
          <TileLayer url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png" attribution="© <a href='https://carto.com/'>CARTO</a>" />
          {accidentMarkers}
          {ambulanceMarkers}
          {polylines}
        </MapContainer>
      </div>

      {/* Incident Feed */}
      <div className="grid md:grid-cols-2 gap-4">
        <section className="overflow-auto max-h-64 border border-border rounded bg-panel p-2">
          <h3 className="text-lg font-semibold mb-2" style={{ color: colors.accent }}>Incident Feed</h3>
          {accidentsLoading ? (
            <p className="text-gray-400">Loading…</p>
          ) : (
            <ul className="space-y-2">
              {accidents.map((a) => (
                <li key={a.accident_id} className="p-2 rounded" style={{ backgroundColor: severityColorMap[a.severity] + '20' }}>
                  <strong>{a.accident_id}</strong> – {a.severity} – {a.status}
                </li>
              ))}
            </ul>
          )}
        </section>
        {/* Detail panel placeholder */}
        <section className="border border-border rounded bg-panel p-2">
          <h3 className="text-lg font-semibold mb-2" style={{ color: colors.accent }}>Incident Detail</h3>
          <p className="text-gray-400">Select an incident on the map or feed to view details.</p>
        </section>
      </div>
    </div>
  );
}
