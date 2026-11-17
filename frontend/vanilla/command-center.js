import L from 'https://unpkg.com/leaflet@1.9.4/dist/leaflet-src.esm.js';

// Helper colour maps (same as original React implementation)
const severityColorMap = {
  LOW: '#22C55E',
  MEDIUM: '#F59E0B',
  HIGH: '#F97316',
  CRITICAL: '#EF4444',
};
const ambulanceStatusColorMap = {
  AVAILABLE: '#22C55E',
  DISPATCHED: '#22D3EE',
  AT_SCENE: '#F97316',
  TRANSPORTING: '#F59E0B',
  AT_HOSPITAL: '#38BDF8',
  RETURNING: '#818CF8',
  OFFLINE: '#64748B',
};

function severityColor(sev) {
  return severityColorMap[sev] || '#ccc';
}
function ambulanceStatusColor(st) {
  return ambulanceStatusColorMap[st] || '#999';
}

async function init() {
  const [accidents, ambulances] = await Promise.all([fetchAccidents(), fetchAmbulances()]);

  // KPI values – update existing elements in the template
  const totalIncidents = accidents.length;
  const pending = accidents.filter(a => a.status === 'AWAITING_AMBULANCE' || a.status === 'NEEDS_VERIFICATION').length;
  const assigned = accidents.filter(a => a.assigned_ambulance_id).length;
  const resolved = accidents.filter(a => a.status === 'RESOLVED').length;
  const critical = accidents.filter(a => a.severity === 'CRITICAL').length;
  const active = accidents.filter(a => a.status !== 'RESOLVED').length;

  // Update KPI elements by their IDs
  const setText = (id, txt) => { const el = document.getElementById(id); if (el) el.textContent = txt; };
  setText('kpi-active-accidents', active);
  setText('kpi-active-accidents-sev', '(' + critical + ')');
  setText('kpi-ambulances-avail', ambulances.filter(am => am.status === 'AVAILABLE').length);
  setText('kpi-ambulances-total', '/' + ambulances.length);
  setText('kpi-dispatched', ambulances.filter(am => am.status === 'DISPATCHED').length);
  setText('kpi-at-scene', ambulances.filter(am => am.status === 'AT_SCENE' || am.status === 'TRANSPORTING').length);
  setText('kpi-avg-rt', '--:--'); // placeholder – mock data not provided
  setText('kpi-awaiting', pending);
  // Additional KPIs (Total Incidents, Pending, Assigned, Resolved, Critical) can be displayed elsewhere if needed


  // Leaflet map – now using imported L
  const map = L.map('map').setView([22.7196, 75.8577], 13);
  L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: "© <a href='https://carto.com/'>CARTO</a>",
  }).addTo(map);

  // Accident markers
  accidents.forEach(a => {
    const marker = L.circleMarker([a.location.lat, a.location.lon], {
      radius: 6,
      color: severityColor(a.severity),
      fillColor: severityColor(a.severity),
      fillOpacity: 0.8,
    }).addTo(map);
    const popup = `<strong>${a.accident_id}</strong><br/>${a.severity}<br/>${a.status}`;
    marker.bindPopup(popup);
  });

  // Ambulance markers
  ambulances.forEach(am => {
    const marker = L.circleMarker([am.location.lat, am.location.lon], {
      radius: 5,
      color: ambulanceStatusColor(am.status),
      fillColor: ambulanceStatusColor(am.status),
      fillOpacity: 0.9,
    }).addTo(map);
    const popup = `<strong>${am.ambulance_id}</strong><br/>${am.status}`;
    marker.bindPopup(popup);
  });

  // Incident feed list
  const feed = document.getElementById('incident-feed');
  accidents.forEach(a => {
    const item = document.createElement('div');
    item.className = 'incident-item';
    item.style.backgroundColor = severityColor(a.severity) + '20';
    item.innerHTML = `<strong>${a.accident_id}</strong> – ${a.severity} – ${a.status}`;
    feed.appendChild(item);
  });
}

init();
