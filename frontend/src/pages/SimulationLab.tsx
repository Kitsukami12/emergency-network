// src/pages/SimulationLab.tsx
// @ts-nocheck
import React, { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { fetchAmbulances, fetchAccidents, dispatch, fetchRoute } from '../api/client';
import { Ambulance, Accident, Location } from '../api/types';
import { MapContainer, TileLayer, Marker, Polyline, Popup } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { colors } from '../theme';
import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from 'recharts';

// Fix Leaflet icon issue
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

export default function SimulationLab() {
  const [numAccidents, setNumAccidents] = useState(5);
  const [numAmbulances, setNumAmbulances] = useState(10);
  const [duration, setDuration] = useState(60); // seconds
  const [seed, setSeed] = useState(42);
  const [strategy, setStrategy] = useState('hungarian');
  const [playbackSpeed, setPlaybackSpeed] = useState(1);
  const queryClient = useQueryClient();

  const { data: ambulances = [] } = useQuery(['ambulances'], fetchAmbulances);
  const { data: accidents = [] } = useQuery(['accidents'], fetchAccidents);

  const dispatchMutation = useMutation(() => dispatch(strategy), {
    onSuccess: () => queryClient.invalidateQueries(['accidents', 'ambulances']),
  });

  const handleStart = () => {
    // In mock mode we simply call dispatch; real backend also supports same endpoint.
    dispatchMutation.mutate();
  };

  // Build simple stats for analytics bar chart
  const stats = [
    { name: 'Hungarian', avg: Math.round(5 + Math.random() * 5) },
    { name: 'Nearest', avg: Math.round(7 + Math.random() * 5) },
  ];

  const center: Location = { lat: 22.7196, lon: 75.8577 };

  return (
    <div className="flex flex-col gap-4">
      <h2 className="text-2xl" style={{ color: colors.accent }}>Simulation Lab</h2>
      <div className="grid md:grid-cols-2 gap-4">
        {/* Controls */}
        <section className="bg-panel border border-border rounded p-4">
          <h3 className="font-semibold mb-2" style={{ color: colors.accent }}>Parameters</h3>
          <div className="flex flex-col gap-2">
            <label>Number of emergencies</label>
            <input type="number" min={1} max={20} value={numAccidents} onChange={(e) => setNumAccidents(+e.target.value)} className="p-1 rounded bg-background text-white" />
            <label>Number of ambulances</label>
            <input type="number" min={1} max={30} value={numAmbulances} onChange={(e) => setNumAmbulances(+e.target.value)} className="p-1 rounded bg-background text-white" />
            <label>Duration (seconds)</label>
            <input type="number" min={10} max={300} value={duration} onChange={(e) => setDuration(+e.target.value)} className="p-1 rounded bg-background text-white" />
            <label>Random seed</label>
            <input type="number" value={seed} onChange={(e) => setSeed(+e.target.value)} className="p-1 rounded bg-background text-white" />
            <label>Strategy</label>
            <select value={strategy} onChange={(e) => setStrategy(e.target.value)} className="p-1 rounded bg-background text-white">
              <option value="hungarian">Hungarian</option>
              <option value="nearest">Nearest Ambulance</option>
            </select>
            <button
              className="mt-2 px-4 py-2 rounded bg-accent text-black disabled:opacity-50"
              onClick={handleStart}
              disabled={dispatchMutation.isLoading}
            >
              {dispatchMutation.isLoading ? 'Running…' : 'Start Simulation'}
            </button>
          </div>
        </section>
        {/* Analytics chart placeholder */}
        <section className="bg-panel border border-border rounded p-4">
          <h3 className="font-semibold mb-2" style={{ color: colors.accent }}>Strategy Comparison</h3>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={stats}>
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="avg" fill={colors.accent} />
            </BarChart>
          </ResponsiveContainer>
        </section>
      </div>

      {/* Map playback – show current ambulances and accidents */}
      <div className="h-96 rounded bg-panel border border-border overflow-hidden">
        // @ts-ignore
      <MapContainer center={[center.lat, center.lon]} zoom={13} style={{ height: '100%', width: '100%' }}>
          <TileLayer
            url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
            attribution='&copy; <a href="https://carto.com/">CARTO</a>'
          />
          {ambulances.map((a) => (
            <Marker key={a.ambulance_id} position={[a.location.lat, a.location.lon]} />
          ))}
          {accidents.map((acc) => (
            <Marker key={acc.accident_id} position={[acc.location.lat, acc.location.lon]} />
          ))}
        </MapContainer>
      </div>
    </div>
  );
}
