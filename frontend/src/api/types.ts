// src/api/types.ts
export interface Location {
  lat: number;
  lon: number;
}

export type Severity = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";

export type AccidentStatus =
  | "DETECTED"
  | "ASSESSING"
  | "NEEDS_VERIFICATION"
  | "AWAITING_AMBULANCE"
  | "AMBULANCE_ASSIGNED"
  | "EN_ROUTE"
  | "ARRIVED"
  | "RESOLVED"
  | "CANCELLED";

export type AmbulanceStatus =
  | "AVAILABLE"
  | "DISPATCHED"
  | "AT_SCENE"
  | "TRANSPORTING"
  | "AT_HOSPITAL"
  | "RETURNING"
  | "OFFLINE";

export interface Weather {
  temperature_c?: number;
  precipitation_mm?: number;
  visibility_m?: number;
  wind_kph?: number;
  weather_code?: number;
  summary?: string;
}

export interface TimelineEvent {
  text: string;
  time: string;
}

export interface Accident {
  accident_id: string;
  location: Location;
  severity: Severity;
  description?: string;
  status: AccidentStatus;
  assigned_ambulance_id?: string | null;
  reported_at: string; // ISO string
  source?: string;
  camera_id?: string;
  detection_confidence?: number;
  severity_confidence?: number;
  vehicle_count?: number;
  people_count?: number;
  vehicles_summary?: string;
  location_name?: string;
  distance_km?: number;
  eta_min?: number;
  timeline?: TimelineEvent[];
  weather?: Weather;
  road_type?: string;
}

export interface Ambulance {
  ambulance_id: string;
  base_name: string;
  location: Location;
  status: AmbulanceStatus;
  type?: "ALS" | "BLS";
  paramedic?: string;
  vital_sync?: string;
  current_sector?: string;
}

export interface HospitalBay {
  id: string;
  type: string;
  status: "AVAILABLE" | "OCCUPIED" | "PRE_ALERT" | "STAGED" | "STERILIZATION";
  detail?: string;
}

export interface Hospital {
  hospital_id: string;
  name: string;
  location: Location;
  icu_available?: number;
  icu_total?: number;
  resus_ready?: number;
  surge_status?: string;
  bays?: HospitalBay[];
}

export interface RouteResult {
  distance_km: number;
  estimated_time_min: number;
  source?: string;
  coordinates: Location[];
}

export interface Notification {
  notification_id: string;
  hospital_id: string;
  accident_id: string;
  severity: Severity;
  status: "PENDING" | "ACKNOWLEDGED" | "ACCEPTED" | "DECLINED";
  created_at?: string;
  eta_min?: number;
  ambulance_id?: string;
  ambulance_type?: string;
  location_name?: string;
  distance_km?: number;
  casualties?: string;
  vehicles?: string;
  dynamics?: string;
  paramedic?: string;
  vital_sync?: string;
}

export interface CameraFeed {
  camera_id: string;
  name: string;
  sector: string;
  status: "WATCHING" | "CRITICAL" | "OFFLINE" | "ANOMALY";
  fps: number;
  latency_ms: number;
  bitrate_mbps: number;
  resolution: string;
  codec: string;
  prob_pct: number;
  anomaly_text?: string;
  vehicle_count?: number;
  flow_index?: number;
  pedestrian_count?: number;
  avg_speed_kmh?: number;
  location: Location;
  bounding_boxes: {
    label: string;
    conf?: number;
    color: string;
    x: number;
    y: number;
    w: number;
    h: number;
    detail?: string;
  }[];
}

export interface VerificationItem {
  detection_id: string;
  location_name: string;
  score_pct: number;
  inference_type: string;
  camera_id: string;
  time_ago: string;
  status: "PENDING" | "CONFIRMED" | "DISMISSED";
}

export interface SimulationParams {
  numAccidents: number;
  numAmbulances: number;
  durationMinutes: number;
  seed: number;
  strategy: "nearest" | "hungarian" | "compare";
  congestionLayer: "normal" | "monsoon" | "brts";
  simulateErQueue: boolean;
}

export interface SimulationStats {
  resolved: number;
  active: number;
  queued: number;
  avgResponseMin: number;
  hungarianEffPct: number;
  meanTtaSavedSec: number;
  idleConflicts: number;
}
