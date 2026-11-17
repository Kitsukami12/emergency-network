// hospital-portal.js – populates Hospital Portal page with mock data and Leaflet maps

import L from "https://unpkg.com/leaflet@1.9.4/dist/leaflet-src.esm.js";
import { fetchHospitals, fetchAccidents, fetchAmbulances } from "./api.js";

/** Initialise the page once the DOM is ready */
async function initHospitalPortal() {
  // ---------- Hospital selector & KPI pills ----------
  const hospitals = await fetchHospitals();
  const selector = document.getElementById("hospital-selector");
  if (selector) {
    // clear any existing options (the markup already has a few static ones)
    selector.innerHTML = "";
    hospitals.forEach((h) => {
      const opt = document.createElement("option");
      opt.value = h.hospital_id;
      opt.textContent = h.name;
      selector.appendChild(opt);
    });
    // select first hospital by default
    if (hospitals.length) selector.value = hospitals[0].hospital_id;
  }

  // Populate KPI pills (ICU beds, Red bays, Surge status)
  const icuEl = document.getElementById("icu-beds");
  const redBaysEl = document.getElementById("red-bays");
  const surgeEl = document.getElementById("surge-status");

  if (icuEl && hospitals.length) {
    const first = hospitals[0];
    icuEl.textContent = `${first.icu_beds} / ${first.total_beds} BEDS AVAIL`;
  }
  // Red bays and surge status are mock‑only – provide static values that match design
  if (redBaysEl) redBaysEl.textContent = "2 READY (BAY 02, 05)";
  if (surgeEl) surgeEl.textContent = "CODE GREEN • OPTIMAL";

  // ---------- Load incidents & ambulances ----------
  const [accidents, ambulances] = await Promise.all([fetchAccidents(), fetchAmbulances()]);

  // Helper to create a Leaflet map inside a given container id and centre it on a location
  function createMap(containerId, centre) {
    const map = L.map(containerId, {
      zoomControl: false,
      attributionControl: false,
    }).setView([centre.lat, centre.lon], 15);
    L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", {
      attribution: "© <a href='https://carto.com/'>CARTO</a>",
    }).addTo(map);
    return map;
  }

  // Initialise maps for each incident card based on severity
  accidents.forEach((acc) => {
    let mapId = null;
    if (acc.severity === "HIGH") mapId = "map-high";
    else if (acc.severity === "CRITICAL") mapId = "map-critical";
    else if (acc.severity === "MEDIUM") mapId = "map-medium"; // not present in current markup but safe
    if (!mapId) return;

    const map = createMap(mapId, acc.location);

    // Accident marker (red circle)
    L.circleMarker([acc.location.lat, acc.location.lon], {
      radius: 8,
      color: "#ef4444",
      fillColor: "#ef4444",
      fillOpacity: 0.9,
    })
      .addTo(map)
      .bindPopup(`${acc.accident_id}<br>${acc.severity}<br>${acc.status}`);

    // Ambulance markers – show all ambulances for demo purposes
    ambulances.forEach((amb) => {
      const color = {
        AVAILABLE: "#22c55e",
        DISPATCHED: "#22d3ee",
        AT_SCENE: "#f97317",
        TRANSPORTING: "#f59e0b",
        AT_HOSPITAL: "#38bdf8",
        RETURNING: "#818cf8",
        OFFLINE: "#64748b",
      }[amb.status] || "#999";
      L.circleMarker([amb.location.lat, amb.location.lon], {
        radius: 6,
        color,
        fillColor: color,
        fillOpacity: 0.9,
      })
        .addTo(map)
        .bindPopup(`${amb.ambulance_id}<br>${amb.status}`);
    });
  });

  // Populate incident‑specific fields (IDs, assigned ambulances, etc.)
  const incidentMap = {};
  accidents.forEach((a) => (incidentMap[a.accident_id] = a));

  // Critical card – IDs are hard‑coded in the HTML (ACC‑8F04BD55). Replace with mock if it exists.
  const criticalIdEl = document.getElementById("incident-id-critical");
  const criticalAmbEl = document.getElementById("assigned-ambulance-critical");
  if (criticalIdEl) {
    const crit = accidents.find((a) => a.severity === "CRITICAL") || accidents[0];
    criticalIdEl.textContent = crit.accident_id;
    if (criticalAmbEl) criticalAmbEl.textContent = crit.assigned_ambulance_id || "--";
  }

  // High card – IDs are hard‑coded (ACC‑91C024E1). Update similarly.
  const highIdEl = document.getElementById("incident-id-high");
  const highAmbEl = document.getElementById("assigned-ambulance-high");
  if (highIdEl) {
    const high = accidents.find((a) => a.severity === "HIGH") || accidents[1];
    highIdEl.textContent = high.accident_id;
    if (highAmbEl) highAmbEl.textContent = high.assigned_ambulance_id || "--";
  }

  // Optional: add event listener to hospital selector to refresh KPI values (not required for mock).
}

document.addEventListener("DOMContentLoaded", initHospitalPortal);
