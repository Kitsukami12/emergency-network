// src/api/mock.ts
import type {
  Accident,
  Ambulance,
  Hospital,
  RouteResult,
  Notification,
  Severity,
  AccidentStatus,
  AmbulanceStatus,
  Location,
  CameraFeed,
  VerificationItem,
} from './types';

const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

export const severityColorMap: Record<Severity, string> = {
  LOW: '#22C55E',
  MEDIUM: '#F59E0B',
  HIGH: '#F97316',
  CRITICAL: '#EF4444',
};

export const ambulanceStatusColorMap: Record<AmbulanceStatus, string> = {
  AVAILABLE: '#22C55E',
  DISPATCHED: '#22D3EE',
  AT_SCENE: '#F97316',
  TRANSPORTING: '#F59E0B',
  AT_HOSPITAL: '#38BDF8',
  RETURNING: '#818CF8',
  OFFLINE: '#64748B',
};

// Initial Hospitals
let hospitals: Hospital[] = [
  {
    hospital_id: 'my-hospital',
    name: 'MY Hospital (Govt. Medical College - Level 1 Trauma)',
    location: { lat: 22.7165, lon: 75.8672 },
    icu_available: 3,
    icu_total: 14,
    resus_ready: 2,
    surge_status: 'CODE GREEN • OPTIMAL',
    bays: [
      { id: 'BAY 01', type: 'RESUS', status: 'OCCUPIED', detail: 'SURGERY' },
      { id: 'BAY 02', type: 'RESUS', status: 'PRE_ALERT', detail: 'ETA 01:15' },
      { id: 'BAY 03', type: 'SURGICAL', status: 'AVAILABLE', detail: 'READY' },
      { id: 'BAY 04', type: 'ORTHO', status: 'STAGED', detail: 'ACC-91C024E1' },
      { id: 'BAY 05', type: 'ISOLATION', status: 'AVAILABLE', detail: 'READY' },
      { id: 'BAY 06', type: 'GENERAL', status: 'STERILIZATION', detail: 'CLEANING' },
    ],
  },
  {
    hospital_id: 'apollo',
    name: 'Apollo Hospital (Vijay Nagar - Level 2 Trauma)',
    location: { lat: 22.7533, lon: 75.8937 },
    icu_available: 5,
    icu_total: 18,
    resus_ready: 3,
    surge_status: 'CODE GREEN • OPTIMAL',
  },
  {
    hospital_id: 'bombay-hospital',
    name: 'Bombay Hospital Indore',
    location: { lat: 22.7612, lon: 75.8942 },
    icu_available: 4,
    icu_total: 16,
    resus_ready: 2,
    surge_status: 'CODE GREEN • OPTIMAL',
  },
  {
    hospital_id: 'choithram',
    name: 'Choithram Hospital & Research Centre',
    location: { lat: 22.6985, lon: 75.8423 },
    icu_available: 2,
    icu_total: 12,
    resus_ready: 1,
    surge_status: 'CODE YELLOW • ELEVATED',
  },
  {
    hospital_id: 'shalby',
    name: 'Shalby Hospital (Jankinagar)',
    location: { lat: 22.7092, lon: 75.8711 },
    icu_available: 6,
    icu_total: 15,
    resus_ready: 2,
    surge_status: 'CODE GREEN • OPTIMAL',
  },
  {
    hospital_id: 'nakshatra',
    name: 'Nakshatra Hospital',
    location: { lat: 22.723, lon: 75.855 },
    icu_available: 2,
    icu_total: 8,
    resus_ready: 1,
    surge_status: 'CODE GREEN • OPTIMAL',
  },
];

// Initial 12 Ambulances in Indore
let ambulances: Ambulance[] = [
  { ambulance_id: 'A07', base_name: 'MY Hospital Hub', location: { lat: 22.7032, lon: 75.8582 }, status: 'DISPATCHED', type: 'ALS', paramedic: 'Rajesh V. (Paramedic-1)', vital_sync: 'STREAM SYNCED (SpO2 88%)', current_sector: 'Sector 4 • Bhawarkua' },
  { ambulance_id: 'A02', base_name: 'Bhawarkua Depot', location: { lat: 22.6974, lon: 75.8615 }, status: 'DISPATCHED', type: 'ALS', paramedic: 'Sanjay M.', vital_sync: 'CONNECTED (98%)', current_sector: 'Sector 4' },
  { ambulance_id: 'A12', base_name: 'Palasia Center', location: { lat: 22.7215, lon: 75.8795 }, status: 'DISPATCHED', type: 'BLS', paramedic: 'Anita K.', vital_sync: 'NORMAL', current_sector: 'Sector 2 Annex' },
  { ambulance_id: 'A09', base_name: 'Rajwada Emergency Post', location: { lat: 22.7188, lon: 75.8562 }, status: 'AT_SCENE', type: 'ALS', paramedic: 'Vikram S.', vital_sync: 'AT SCENE', current_sector: 'Sector 1' },
  { ambulance_id: 'A03', base_name: 'Radisson Bypass Depot', location: { lat: 22.7485, lon: 75.8955 }, status: 'DISPATCHED', type: 'ALS', paramedic: 'Mohit P.', vital_sync: 'STABLE (96%)', current_sector: 'Ring Road Bypass' },
  { ambulance_id: 'A19', base_name: 'MYH Standby', location: { lat: 22.7165, lon: 75.8672 }, status: 'AVAILABLE', type: 'ALS', paramedic: 'Priya N.', vital_sync: 'STANDBY', current_sector: 'Sector 4' },
  { ambulance_id: 'A01', base_name: 'Vijay Nagar Hub', location: { lat: 22.7525, lon: 75.8912 }, status: 'AVAILABLE', type: 'ALS', paramedic: 'Arun T.', vital_sync: 'STANDBY', current_sector: 'Sector 3' },
  { ambulance_id: 'A04', base_name: 'Chhotigwaltoli Post', location: { lat: 22.7142, lon: 75.8718 }, status: 'AVAILABLE', type: 'BLS', paramedic: 'Deepak J.', vital_sync: 'STANDBY', current_sector: 'Sector 4' },
  { ambulance_id: 'A05', base_name: 'Bengali Square Post', location: { lat: 22.7155, lon: 75.9085 }, status: 'AVAILABLE', type: 'ALS', paramedic: 'Kavita R.', vital_sync: 'STANDBY', current_sector: 'Sector 5' },
  { ambulance_id: 'A08', base_name: 'Rau Interchange Base', location: { lat: 22.6685, lon: 75.8195 }, status: 'AVAILABLE', type: 'BLS', paramedic: 'Ramesh G.', vital_sync: 'STANDBY', current_sector: 'Sector 6' },
  { ambulance_id: 'A10', base_name: 'Choithram Annex', location: { lat: 22.6955, lon: 75.8415 }, status: 'AVAILABLE', type: 'ALS', paramedic: 'Dinesh B.', vital_sync: 'STANDBY', current_sector: 'Sector 2' },
  { ambulance_id: 'A11', base_name: 'Rajendra Nagar Post', location: { lat: 22.6845, lon: 75.8325 }, status: 'AVAILABLE', type: 'BLS', paramedic: 'Sunil C.', vital_sync: 'STANDBY', current_sector: 'Sector 2' },
];

// Initial 7 Accidents
let accidents: Accident[] = [
  {
    accident_id: 'ACC-8F04BD55',
    location: { lat: 22.6912, lon: 75.8654 },
    severity: 'HIGH',
    description: 'Two-vehicle collision involving SUV and auto-rickshaw near Bhawarkua BRTS intersection.',
    status: 'AMBULANCE_ASSIGNED',
    assigned_ambulance_id: 'A07',
    reported_at: new Date(Date.now() - 134000).toISOString(),
    source: 'camera',
    camera_id: 'CAM-IND-082',
    detection_confidence: 0.942,
    severity_confidence: 0.87,
    vehicle_count: 2,
    people_count: 4,
    vehicles_summary: '2 (SUV + Auto-rickshaw)',
    location_name: 'Bhawarkua Sq, AB Road',
    distance_km: 2.8,
    eta_min: 1.25,
    road_type: 'BRTS Dedicated Corridor',
    timeline: [
      { text: 'Accident detected', time: 'T-00:02:14' },
      { text: 'Severity = HIGH (Conf: 94.2%)', time: 'T-00:02:08' },
      { text: 'Ambulance A07 assigned via Hungarian', time: 'T-00:01:45' },
      { text: 'Dynamic route calculated (AB Road Spine)', time: 'T-00:01:30' },
      { text: 'Hospital pre-alert sent to MY Hospital', time: 'T-00:01:18' },
    ],
  },
  {
    accident_id: 'ACC-7B29CD11',
    location: { lat: 22.6995, lon: 75.8592 },
    severity: 'CRITICAL',
    description: 'High impact collision with structural deformation and heavy smoke.',
    status: 'EN_ROUTE',
    assigned_ambulance_id: 'A02',
    reported_at: new Date(Date.now() - 240000).toISOString(),
    source: 'camera',
    camera_id: 'CAM-IND-082',
    detection_confidence: 0.965,
    severity_confidence: 0.93,
    vehicle_count: 3,
    people_count: 6,
    vehicles_summary: '3 (Sedan + Truck + Motorbike)',
    location_name: 'Bhawarkua AB Road North',
    distance_km: 1.9,
    eta_min: 2.5,
    timeline: [
      { text: 'Optical Anomaly Triggered', time: 'T-00:04:00' },
      { text: 'Multi-Camera Triangulation confirmed', time: 'T-00:03:45' },
      { text: 'Ambulance A02 dispatched', time: 'T-00:03:10' },
    ],
  },
  {
    accident_id: 'ACC-4C91FF02',
    location: { lat: 22.7245, lon: 75.8825 },
    severity: 'MEDIUM',
    description: 'Sideswipe incident between two passenger cars causing lane obstruction.',
    status: 'AWAITING_AMBULANCE',
    assigned_ambulance_id: null,
    reported_at: new Date(Date.now() - 480000).toISOString(),
    source: 'manual',
    detection_confidence: 0.81,
    vehicle_count: 2,
    people_count: 2,
    vehicles_summary: '2 (Sedan + Hatchback)',
    location_name: 'Palasia Point (Old AB Road)',
    timeline: [
      { text: 'Manual emergency call received', time: 'T-00:08:00' },
      { text: 'Incident queued for Hungarian allocation', time: 'T-00:07:45' },
    ],
  },
  {
    accident_id: 'ACC-1A40EE89',
    location: { lat: 22.7188, lon: 75.8555 },
    severity: 'LOW',
    description: 'Minor fender bender near historic Rajwada gate. Traffic slowing.',
    status: 'ARRIVED',
    assigned_ambulance_id: 'A09',
    reported_at: new Date(Date.now() - 960000).toISOString(),
    source: 'camera',
    camera_id: 'CAM-IND-045',
    detection_confidence: 0.78,
    vehicle_count: 2,
    people_count: 1,
    vehicles_summary: '2 (Auto-rickshaw + Scooter)',
    location_name: 'Rajwada Circle',
    timeline: [
      { text: 'Incident detected by CAM-IND-045', time: 'T-00:16:00' },
      { text: 'Ambulance A09 arrived on scene', time: 'T-00:05:20' },
    ],
  },
  {
    accident_id: 'ACC-91C024E1',
    location: { lat: 22.722, lon: 75.881 },
    severity: 'HIGH',
    description: 'Motorcycle collided with commercial van at flyover descent.',
    status: 'AMBULANCE_ASSIGNED',
    assigned_ambulance_id: 'A12',
    reported_at: new Date(Date.now() - 320000).toISOString(),
    source: 'camera',
    camera_id: 'CAM-IND-045',
    detection_confidence: 0.89,
    vehicle_count: 2,
    people_count: 2,
    vehicles_summary: '1 Bike + 1 Van',
    location_name: 'Palasia Point, Old AB Road Intersection',
    distance_km: 5.4,
    eta_min: 8.85,
  },
  {
    accident_id: 'ACC-7A339B10',
    location: { lat: 22.751, lon: 75.8965 },
    severity: 'MEDIUM',
    description: 'Car skidded into guard rail on Ring Road bypass.',
    status: 'EN_ROUTE',
    assigned_ambulance_id: 'A03',
    reported_at: new Date(Date.now() - 520000).toISOString(),
    source: 'camera',
    camera_id: 'CAM-IND-112',
    detection_confidence: 0.85,
    vehicle_count: 1,
    people_count: 1,
    vehicles_summary: 'Sedan Side-impact',
    location_name: 'Radisson Square Bypass (Service Lane)',
    distance_km: 8.9,
    eta_min: 15.6,
  },
  {
    accident_id: 'ACC-5B12DE33',
    location: { lat: 22.729, lon: 75.872 },
    severity: 'LOW',
    description: 'Obstacle in middle lane detected by traffic monitoring camera.',
    status: 'NEEDS_VERIFICATION',
    assigned_ambulance_id: null,
    reported_at: new Date(Date.now() - 110000).toISOString(),
    source: 'camera',
    camera_id: 'CAM-IND-014',
    detection_confidence: 0.65,
    vehicle_count: 1,
    people_count: 0,
    vehicles_summary: 'Two-wheeler debris',
    location_name: 'MG Road Junction',
  },
];

// Initial Hospital Notifications
let notifications: Notification[] = [
  {
    notification_id: 'N-8F04',
    hospital_id: 'my-hospital',
    accident_id: 'ACC-8F04BD55',
    severity: 'CRITICAL',
    status: 'PENDING',
    created_at: new Date(Date.now() - 90000).toISOString(),
    eta_min: 1.25,
    ambulance_id: 'A07',
    ambulance_type: 'ALS Unit',
    location_name: 'Bhawarkua Square (South BRTS Corridor)',
    distance_km: 2.8,
    casualties: '4 (2 Severe)',
    vehicles: 'SUV + Auto',
    dynamics: 'High G-Force',
    paramedic: 'Rajesh V. (Paramedic-1)',
    vital_sync: 'STREAM SYNCED (SpO2 88%)',
  },
  {
    notification_id: 'N-91C0',
    hospital_id: 'my-hospital',
    accident_id: 'ACC-91C024E1',
    severity: 'HIGH',
    status: 'ACKNOWLEDGED',
    created_at: new Date(Date.now() - 210000).toISOString(),
    eta_min: 8.85,
    ambulance_id: 'A12',
    ambulance_type: 'BLS Unit',
    location_name: 'Palasia Point, Old AB Road Intersection',
    distance_km: 5.4,
    casualties: '2 (1 Polytrauma)',
    vehicles: '1 Bike + 1 Van',
    dynamics: 'Non-compliant helmet',
    paramedic: 'Anita K.',
    vital_sync: 'STREAM SYNCED (SpO2 95%)',
  },
  {
    notification_id: 'N-7A33',
    hospital_id: 'my-hospital',
    accident_id: 'ACC-7A339B10',
    severity: 'MEDIUM',
    status: 'ACKNOWLEDGED',
    created_at: new Date(Date.now() - 350000).toISOString(),
    eta_min: 15.6,
    ambulance_id: 'A03',
    ambulance_type: 'ALS Unit',
    location_name: 'Radisson Square Bypass (Service Lane)',
    distance_km: 8.9,
    casualties: '1 (Minor/Moderate)',
    vehicles: 'Sedan Side-impact',
    dynamics: 'Airbag Deployed',
    paramedic: 'Mohit P.',
    vital_sync: 'Stable Vital Signs',
  },
];

// Camera Agent Network feeds
export const mockCameraFeeds: CameraFeed[] = [
  {
    camera_id: 'CAM-IND-082',
    name: 'Bhawarkua Square NW View (Sector 4)',
    sector: 'Zone 2: Bhawarkua',
    status: 'CRITICAL',
    fps: 60,
    latency_ms: 18,
    bitrate_mbps: 6.2,
    resolution: '1080p60',
    codec: 'H.265',
    prob_pct: 94.2,
    anomaly_text: 'CRITICAL INCIDENT DETECTED',
    vehicle_count: 84,
    flow_index: 42.1,
    avg_speed_kmh: 18.5,
    location: { lat: 22.6891, lon: 75.8654 },
    bounding_boxes: [
      { label: 'CRASH DETECTED 94.2%', conf: 0.942, color: '#EF4444', x: 28, y: 35, w: 38, h: 42, detail: 'ID #TR-482 Δv: -64 km/h' },
      { label: 'VEHICLE: SUV', conf: 0.96, color: '#22D3EE', x: 42, y: 22, w: 25, h: 28, detail: 'V: 12 KM/H [BRAKING]' },
      { label: 'DEBRIS FIELD', conf: 0.88, color: '#F97316', x: 18, y: 48, w: 32, h: 24, detail: 'AREA: 14.8m²' },
    ],
  },
  {
    camera_id: 'CAM-IND-014',
    name: 'Vijay Nagar Square Junction (East)',
    sector: 'Zone 1: Vijay Nagar',
    status: 'WATCHING',
    fps: 60,
    latency_ms: 14,
    bitrate_mbps: 5.8,
    resolution: '1080p60',
    codec: 'H.265',
    prob_pct: 8.0,
    anomaly_text: 'FLOW NORMAL • HIGH DENSITY',
    vehicle_count: 142,
    flow_index: 88.4,
    avg_speed_kmh: 38.2,
    location: { lat: 22.7533, lon: 75.8937 },
    bounding_boxes: [
      { label: 'BUS: CITY METRO', conf: 0.95, color: '#22D3EE', x: 22, y: 30, w: 40, h: 32, detail: '38 KM/H • NOMINAL' },
      { label: 'SEDAN', conf: 0.92, color: '#22D3EE', x: 65, y: 40, w: 24, h: 25, detail: '42 KM/H • NOMINAL' },
    ],
  },
  {
    camera_id: 'CAM-IND-045',
    name: 'Palasia Geeta Bhawan Crossing',
    sector: 'Zone 3: Palasia',
    status: 'WATCHING',
    fps: 30,
    latency_ms: 16,
    bitrate_mbps: 4.9,
    resolution: '1080p30',
    codec: 'H.265',
    prob_pct: 14.0,
    anomaly_text: 'PEDESTRIAN CORRIDOR MONITORING',
    vehicle_count: 68,
    flow_index: 75.0,
    pedestrian_count: 6,
    location: { lat: 22.7214, lon: 75.8812 },
    bounding_boxes: [
      { label: 'PEDESTRIAN CLUSTER: 6', conf: 0.91, color: '#22C55E', x: 20, y: 45, w: 30, h: 25, detail: 'ZEBRA ACTIVE' },
    ],
  },
  {
    camera_id: 'CAM-IND-112',
    name: 'Radisson Square Ring Road Bypass',
    sector: 'Zone 5: Bypass',
    status: 'WATCHING',
    fps: 60,
    latency_ms: 15,
    bitrate_mbps: 6.4,
    resolution: '1080p60',
    codec: 'H.265',
    prob_pct: 5.0,
    anomaly_text: 'HIGH-SPEED CORRIDOR • CLEAR',
    vehicle_count: 95,
    flow_index: 92.0,
    avg_speed_kmh: 62.4,
    location: { lat: 22.7598, lon: 75.9088 },
    bounding_boxes: [
      { label: 'HEAVY TRANSPORT: TRUCK', conf: 0.97, color: '#22D3EE', x: 45, y: 38, w: 35, h: 38, detail: '58 KM/H' },
    ],
  },
  {
    camera_id: 'CAM-IND-099',
    name: 'Bypass Industrial Gate',
    sector: 'Zone 5: Bypass',
    status: 'OFFLINE',
    fps: 0,
    latency_ms: 0,
    bitrate_mbps: 0,
    resolution: 'N/A',
    codec: 'N/A',
    prob_pct: 0,
    anomaly_text: 'SIGNAL LOST // RECONNECTING',
    location: { lat: 22.785, lon: 75.92 },
    bounding_boxes: [],
  },
  {
    camera_id: 'CAM-IND-061',
    name: 'Chhotigwaltoli Station Approach',
    sector: 'Zone 4: Rajwada',
    status: 'WATCHING',
    fps: 30,
    latency_ms: 22,
    bitrate_mbps: 3.8,
    resolution: '1080p30',
    codec: 'H.264',
    prob_pct: 11.0,
    location: { lat: 22.716, lon: 75.868 },
    bounding_boxes: [],
  },
];

// Verification Queue items
let verificationQueue: VerificationItem[] = [
  {
    detection_id: 'DET-9041',
    location_name: 'MG Road / Treasure Island',
    score_pct: 68,
    inference_type: 'Near-miss / side-scrape',
    camera_id: 'CAM-IND-014',
    time_ago: '45s ago',
    status: 'PENDING',
  },
  {
    detection_id: 'DET-9038',
    location_name: 'Rajwada Circle',
    score_pct: 54,
    inference_type: 'Two-wheeler slide / obstacle',
    camera_id: 'CAM-IND-045',
    time_ago: '2m ago',
    status: 'PENDING',
  },
  {
    detection_id: 'DET-9035',
    location_name: 'Bhawarkua BRTS Lane',
    score_pct: 72,
    inference_type: 'Pedestrian sudden avoidance',
    camera_id: 'CAM-IND-082',
    time_ago: '4m ago',
    status: 'PENDING',
  },
];

// Simulated real-time ambulance movement along Indore corridors
setInterval(() => {
  ambulances = ambulances.map((amb) => {
    if (amb.status === 'DISPATCHED' || amb.status === 'TRANSPORTING') {
      const deltaLat = (Math.random() - 0.48) * 0.0004;
      const deltaLon = (Math.random() - 0.48) * 0.0004;
      return {
        ...amb,
        location: {
          lat: amb.location.lat + deltaLat,
          lon: amb.location.lon + deltaLon,
        },
      };
    }
    return amb;
  });
}, 2000);

// API Functions
export const fetchAccidents = async (): Promise<Accident[]> => {
  await delay(120);
  return [...accidents];
};

export const fetchAmbulances = async (): Promise<Ambulance[]> => {
  await delay(100);
  return [...ambulances];
};

export const fetchHospitals = async (): Promise<Hospital[]> => {
  await delay(100);
  return [...hospitals];
};

export const fetchNotifications = async (hospitalId?: string): Promise<Notification[]> => {
  await delay(100);
  if (!hospitalId || hospitalId === 'all') return [...notifications];
  return notifications.filter((n) => n.hospital_id === hospitalId);
};

export const fetchCameraFeeds = async (): Promise<CameraFeed[]> => {
  await delay(100);
  return [...mockCameraFeeds];
};

export const fetchVerificationQueue = async (): Promise<VerificationItem[]> => {
  await delay(80);
  return [...verificationQueue];
};

export const fetchRoute = async (from: Location, to: Location): Promise<RouteResult> => {
  await delay(150);
  const dist = Math.hypot(to.lat - from.lat, to.lon - from.lon) * 111.0;
  const time = Math.max(1, Math.round(dist * 2.2));
  const points = 16;
  const coords: Location[] = [];
  for (let i = 0; i <= points; i++) {
    const t = i / points;
    // Slight curve to look realistic like a street route
    const wobble = Math.sin(t * Math.PI) * 0.0015;
    coords.push({
      lat: from.lat + (to.lat - from.lat) * t + wobble,
      lon: from.lon + (to.lon - from.lon) * t - wobble,
    });
  }
  return {
    distance_km: Number(dist.toFixed(2)),
    estimated_time_min: time,
    source: 'OSRM Indore BRTS Graph',
    coordinates: coords,
  };
};

export const verifyIncident = async (id: string): Promise<Accident> => {
  await delay(150);
  const acc = accidents.find((a) => a.accident_id === id);
  if (!acc) throw new Error('Accident not found');
  if (acc.status === 'NEEDS_VERIFICATION' || acc.status === 'DETECTED') {
    acc.status = 'AWAITING_AMBULANCE';
  }
  acc.timeline = acc.timeline || [];
  acc.timeline.push({ text: 'Dispatcher manually verified incident', time: 'Just now' });
  return { ...acc };
};

export const overrideSeverity = async (id: string, newSeverity: Severity): Promise<Accident> => {
  await delay(150);
  const acc = accidents.find((a) => a.accident_id === id);
  if (!acc) throw new Error('Accident not found');
  acc.severity = newSeverity;
  acc.timeline = acc.timeline || [];
  acc.timeline.push({ text: `Dispatcher overrode severity to ${newSeverity}`, time: 'Just now' });
  return { ...acc };
};

export const reassignAmbulance = async (accidentId: string, newAmbId: string): Promise<Accident> => {
  await delay(200);
  const acc = accidents.find((a) => a.accident_id === accidentId);
  if (!acc) throw new Error('Accident not found');
  if (acc.assigned_ambulance_id) {
    const prev = ambulances.find((a) => a.ambulance_id === acc.assigned_ambulance_id);
    if (prev) prev.status = 'AVAILABLE';
  }
  const next = ambulances.find((a) => a.ambulance_id === newAmbId);
  if (next) next.status = 'DISPATCHED';
  acc.assigned_ambulance_id = newAmbId;
  acc.status = 'AMBULANCE_ASSIGNED';
  acc.timeline = acc.timeline || [];
  acc.timeline.push({ text: `Reassigned to Ambulance ${newAmbId}`, time: 'Just now' });
  return { ...acc };
};

export const cancelAccident = async (id: string): Promise<Accident> => {
  await delay(150);
  const acc = accidents.find((a) => a.accident_id === id);
  if (!acc) throw new Error('Accident not found');
  if (acc.assigned_ambulance_id) {
    const amb = ambulances.find((a) => a.ambulance_id === acc.assigned_ambulance_id);
    if (amb) amb.status = 'AVAILABLE';
  }
  acc.status = 'CANCELLED';
  acc.timeline = acc.timeline || [];
  acc.timeline.push({ text: 'Dispatcher cancelled incident', time: 'Just now' });
  return { ...acc };
};

export const patchAccidentStatus = async (id: string, newStatus: AccidentStatus): Promise<Accident> => {
  await delay(150);
  const acc = accidents.find((a) => a.accident_id === id);
  if (!acc) throw new Error('Accident not found');
  acc.status = newStatus;
  return { ...acc };
};

export const advanceAccident = async (id: string): Promise<Accident> => {
  await delay(150);
  const acc = accidents.find((a) => a.accident_id === id);
  if (!acc) throw new Error('Accident not found');
  const transitions: Record<AccidentStatus, AccidentStatus> = {
    DETECTED: 'ASSESSING',
    ASSESSING: 'AWAITING_AMBULANCE',
    NEEDS_VERIFICATION: 'AWAITING_AMBULANCE',
    AWAITING_AMBULANCE: 'AMBULANCE_ASSIGNED',
    AMBULANCE_ASSIGNED: 'EN_ROUTE',
    EN_ROUTE: 'ARRIVED',
    ARRIVED: 'RESOLVED',
    RESOLVED: 'RESOLVED',
    CANCELLED: 'CANCELLED',
  };
  acc.status = transitions[acc.status] || acc.status;
  return { ...acc };
};

export const dispatch = async (strategy: string = 'hungarian') => {
  await delay(250);
  let count = 0;
  accidents.forEach((acc) => {
    if (acc.status === 'AWAITING_AMBULANCE' || !acc.assigned_ambulance_id) {
      const free = ambulances.find((a) => a.status === 'AVAILABLE');
      if (free) {
        free.status = 'DISPATCHED';
        acc.assigned_ambulance_id = free.ambulance_id;
        acc.status = 'AMBULANCE_ASSIGNED';
        count++;
      }
    }
  });
  return { strategy, dispatched_count: count, success: true };
};

export const updateNotificationStatus = async (
  nid: string,
  status: 'PENDING' | 'ACKNOWLEDGED' | 'ACCEPTED' | 'DECLINED'
) => {
  await delay(120);
  const n = notifications.find((item) => item.notification_id === nid);
  if (!n) throw new Error('Notification not found');
  n.status = status;
  return { notification_id: nid, status };
};

export const confirmVerificationItem = async (detectionId: string) => {
  await delay(150);
  const item = verificationQueue.find((v) => v.detection_id === detectionId);
  if (item) {
    item.status = 'CONFIRMED';
    // Add to accidents as AWAITING_AMBULANCE
    const newAcc: Accident = {
      accident_id: `ACC-${detectionId.replace('DET-', '')}A1`,
      location: { lat: 22.7196 + (Math.random() - 0.5) * 0.03, lon: 75.8577 + (Math.random() - 0.5) * 0.03 },
      severity: item.score_pct > 70 ? 'HIGH' : 'MEDIUM',
      description: `Confirmed from verification: ${item.inference_type} at ${item.location_name}`,
      status: 'AWAITING_AMBULANCE',
      reported_at: new Date().toISOString(),
      source: 'camera',
      camera_id: item.camera_id,
      detection_confidence: item.score_pct / 100,
      location_name: item.location_name,
    };
    accidents.unshift(newAcc);
  }
  return { detection_id: detectionId, status: 'CONFIRMED' };
};

export const dismissVerificationItem = async (detectionId: string) => {
  await delay(120);
  const item = verificationQueue.find((v) => v.detection_id === detectionId);
  if (item) item.status = 'DISMISSED';
  return { detection_id: detectionId, status: 'DISMISSED' };
};

export const uploadCCTVClip = async (file: File) => {
  await delay(600);
  const newAccident: Accident = {
    accident_id: `ACC-${Math.floor(1000 + Math.random() * 9000)}B7`,
    location: { lat: 22.7196 + (Math.random() - 0.5) * 0.02, lon: 75.8577 + (Math.random() - 0.5) * 0.02 },
    severity: 'HIGH',
    description: `AI inference from uploaded clip: ${file.name}. High deceleration event detected.`,
    status: 'NEEDS_VERIFICATION',
    reported_at: new Date().toISOString(),
    source: 'upload',
    detection_confidence: 0.912,
    severity_confidence: 0.87,
    vehicle_count: 2,
    people_count: 3,
    location_name: 'Bhawarkua Arterial Sector 4',
  };
  accidents.unshift(newAccident);
  return {
    success: true,
    file_name: file.name,
    accident: newAccident,
  };
};
