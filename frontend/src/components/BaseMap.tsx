// src/components/BaseMap.tsx
// @ts-nocheck
// Drop-in replacement for <TileLayer .../> inside any react-leaflet <MapContainer>.
// Uses TomTom raster tiles (night/day) plus a live traffic-flow overlay.
// Needs VITE_TOMTOM_KEY in frontend/.env.local; falls back to plain OpenStreetMap without it.
import { LayersControl, TileLayer } from 'react-leaflet';

const KEY = import.meta.env.VITE_TOMTOM_KEY as string | undefined;
const ATTR = '&copy; <a href="https://www.tomtom.com">TomTom</a>, &copy; OpenStreetMap contributors';

export default function BaseMap({ traffic = true }: { traffic?: boolean }) {
  if (!KEY) {
    console.warn('VITE_TOMTOM_KEY is not set: using OpenStreetMap tiles without live traffic.');
    return (
      <TileLayer
        url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution="&copy; OpenStreetMap contributors"
        maxZoom={19}
      />
    );
  }
  const base = (style: string) =>
    `https://{s}.api.tomtom.com/map/1/tile/basic/${style}/{z}/{x}/{y}.png?key=${KEY}`;
  return (
    <LayersControl position="topright">
      <LayersControl.BaseLayer checked name="Night">
        <TileLayer url={base('night')} attribution={ATTR} subdomains={['a', 'b', 'c', 'd']} maxZoom={22} />
      </LayersControl.BaseLayer>
      <LayersControl.BaseLayer name="Day">
        <TileLayer url={base('main')} attribution={ATTR} subdomains={['a', 'b', 'c', 'd']} maxZoom={22} />
      </LayersControl.BaseLayer>
      {traffic && (
        <LayersControl.Overlay checked name="Live traffic">
          <TileLayer
            url={`https://{s}.api.tomtom.com/traffic/map/4/tile/flow/relative-delay/{z}/{x}/{y}.png?key=${KEY}`}
            subdomains={['a', 'b', 'c', 'd']}
            maxZoom={22}
            opacity={0.9}
          />
        </LayersControl.Overlay>
      )}
    </LayersControl>
  );
}