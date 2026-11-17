// mockData.js – provides mock data used by the vanilla UI
// The data mirrors the structures in backend/mock.ts but is trimmed for brevity.

/** @typedef {{ accident_id:string, location:{lat:number,lon:number}, severity:string, status:string, assigned_ambulance_id?:string|null }} Accident */
/** @typedef {{ ambulance_id:string, location:{lat:number,lon:number}, status:string }} Ambulance */

export function getMockAccidents() {
  /** @type {Accident[]} */
  const accidents = [
    {
      accident_id: 'ACC-0001',
      location: { lat: 22.71, lon: 75.85 },
      severity: 'HIGH',
      status: 'AWAITING_AMBULANCE',
      assigned_ambulance_id: null,
    },
    {
      accident_id: 'ACC-0002',
      location: { lat: 22.72, lon: 75.86 },
      severity: 'MEDIUM',
      status: 'EN_ROUTE',
      assigned_ambulance_id: 'AMB-01',
    },
  ];
  return Promise.resolve(accidents);
}

export function getMockAmbulances() {
  /** @type {Ambulance[]} */
  const ambulances = [
    {
      ambulance_id: 'AMB-01',
      location: { lat: 22.70, lon: 75.84 },
      status: 'DISPATCHED',
    },
    {
      ambulance_id: 'AMB-02',
      location: { lat: 22.73, lon: 75.88 },
      status: 'AVAILABLE',
    },
  ];
  return Promise.resolve(ambulances);
}

// Stub functions for other screens – return empty arrays for now.
export function getMockHospitals() {
  /** @typedef {{hospital_id:string, name:string, location:{lat:number,lon:number}, icu_beds:number, total_beds:number}} Hospital */
  /** @type {Hospital[]} */
  const hospitals = [
    {
      hospital_id: 'HOSP-01',
      name: 'City General Hospital',
      location: { lat: 22.715, lon: 75.855 },
      icu_beds: 12,
      total_beds: 120,
    },
    {
      hospital_id: 'HOSP-02',
      name: 'Northside Medical Center',
      location: { lat: 22.725, lon: 75.865 },
      icu_beds: 8,
      total_beds: 80,
    },
  ];
  return Promise.resolve(hospitals);
}
export function getMockNotifications() { return Promise.resolve([]); }
export function getMockCameraFeeds() { return Promise.resolve([]); }
export function getMockVerificationQueue() {
  /** @type {any[]} */
  const queue = [
    {
      detection_id: 'DET-001',
      camera_id: 'CAM-01',
      status: 'PENDING',
    },
    {
      detection_id: 'DET-002',
      camera_id: 'CAM-02',
      status: 'PENDING',
    },
  ];
  return Promise.resolve(queue);
}

export function getMockSimulationParams() { return Promise.resolve({
  numAccidents: 5,
  numAmbulances: 4,
  durationSeconds: 30,
  strategy: 'nearest', // options: nearest, round_robin
}); }
