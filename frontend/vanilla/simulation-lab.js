// simulation-lab.js – mock simulation runner
import { fetchSimulationParams, fetchAccidents, fetchAmbulances } from './api.js';
import L from 'https://unpkg.com/leaflet@1.9.4/dist/leaflet-src.esm.js'; // Leaflet ESM import

function initMap() {
  const map = L.map('sim-map').setView([22.71, 75.85], 13);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors',
  }).addTo(map);
  return map;
}

function log(msg) {
  const logDiv = document.getElementById('sim-log');
  const p = document.createElement('p');
  p.textContent = msg;
  logDiv.appendChild(p);
  logDiv.scrollTop = logDiv.scrollHeight;
}

async function startSimulation() {
  const numAccidents = parseInt(document.getElementById('num-accidents').value, 10);
  const numAmbulances = parseInt(document.getElementById('num-ambulances').value, 10);
  const duration = parseInt(document.getElementById('duration').value, 10) * 1000;
  const strategy = document.getElementById('strategy').value;

  log(`Starting simulation: ${numAccidents} accidents, ${numAmbulances} ambulances, ${duration/1000}s, strategy=${strategy}`);

  const map = initMap();
  const ambulances = [];
  for (let i = 0; i < numAmbulances; i++) {
    const amb = L.circleMarker([22.70 + i * 0.001, 75.84 + i * 0.001], { radius: 6, color: 'blue' })
      .bindPopup(`Ambulance ${i + 1}`)
      .addTo(map);
    ambulances.push(amb);
  }

  let accidentCount = 0;
  const interval = setInterval(() => {
    if (accidentCount >= numAccidents) {
      clearInterval(interval);
      log('Simulation completed');
      return;
    }
    const lat = 22.70 + Math.random() * 0.02;
    const lon = 75.84 + Math.random() * 0.02;
    const marker = L.circleMarker([lat, lon], { radius: 5, color: 'red' })
      .bindPopup(`Accident ${accidentCount + 1}`)
      .addTo(map);
    log(`Accident ${accidentCount + 1} at (${lat.toFixed(5)}, ${lon.toFixed(5)})`);
    // Simple assignment: pick first available ambulance
    const amb = ambulances[accidentCount % ambulances.length];
    amb.setLatLng([lat, lon]);
    amb.setStyle({ color: 'orange' });
    log(`Ambulance dispatched to accident ${accidentCount + 1}`);
    accidentCount++;
  }, Math.max(500, duration / numAccidents));
}

document.getElementById('start-sim').addEventListener('click', startSimulation);
