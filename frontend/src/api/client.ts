// src/api/client.ts
import axios from 'axios';
import type {
  Accident,
  Ambulance,
  Hospital,
  RouteResult,
  Notification,
  Severity,
  AccidentStatus,
  Location,
} from './types';
import * as mock from './mock';

export const isMock = import.meta.env.VITE_USE_MOCK !== 'false';

const API_BASE = import.meta.env.VITE_API_BASE || '';

export const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const severityColorMap = mock.severityColorMap;
export const ambulanceStatusColorMap = mock.ambulanceStatusColorMap;

// Fetch Accidents
export const fetchAccidents = async (): Promise<Accident[]> => {
  if (isMock) return mock.fetchAccidents();
  try {
    const res = await api.get<Accident[]>('/accidents');
    return res.data;
  } catch (err) {
    console.warn('Real backend /accidents failed, falling back to mock:', err);
    return mock.fetchAccidents();
  }
};

// Fetch Ambulances
export const fetchAmbulances = async (): Promise<Ambulance[]> => {
  if (isMock) return mock.fetchAmbulances();
  try {
    const res = await api.get<Ambulance[]>('/ambulances');
    return res.data;
  } catch (err) {
    console.warn('Real backend /ambulances failed, falling back to mock:', err);
    return mock.fetchAmbulances();
  }
};

// Fetch Hospitals
export const fetchHospitals = async (): Promise<Hospital[]> => {
  if (isMock) return mock.fetchHospitals();
  try {
    const res = await api.get<Hospital[]>('/hospitals');
    return res.data;
  } catch (err) {
    console.warn('Real backend /hospitals failed, falling back to mock:', err);
    return mock.fetchHospitals();
  }
};

// Fetch Notifications
export const fetchNotifications = async (hospitalId?: string): Promise<Notification[]> => {
  if (isMock) return mock.fetchNotifications(hospitalId);
  try {
    const res = await api.get<Notification[]>('/notifications', {
      params: { hospital_id: hospitalId },
    });
    return res.data;
  } catch (err) {
    console.warn('Real backend /notifications failed, falling back to mock:', err);
    return mock.fetchNotifications(hospitalId);
  }
};

// Fetch Route
export const fetchRoute = async (from: Location, to: Location): Promise<RouteResult> => {
  if (isMock) return mock.fetchRoute(from, to);
  try {
    const res = await api.get<RouteResult>('/route', {
      params: {
        from_lat: from.lat,
        from_lon: from.lon,
        to_lat: to.lat,
        to_lon: to.lon,
      },
    });
    return res.data;
  } catch (err) {
    console.warn('Real backend /route failed, falling back to mock:', err);
    return mock.fetchRoute(from, to);
  }
};

// Patch Accident Status
export const patchAccidentStatus = async (
  id: string,
  newStatus: AccidentStatus
): Promise<Accident> => {
  if (isMock) return mock.patchAccidentStatus(id, newStatus);
  try {
    const res = await api.patch<Accident>(`/accidents/${id}/status`, { new_status: newStatus });
    return res.data;
  } catch (err) {
    console.warn('Real backend patch status failed, using mock:', err);
    return mock.patchAccidentStatus(id, newStatus);
  }
};

// Advance Accident
export const advanceAccident = async (id: string): Promise<Accident> => {
  if (isMock) return mock.advanceAccident(id);
  try {
    const res = await api.post<Accident>(`/accidents/${id}/advance`);
    return res.data;
  } catch (err) {
    console.warn('Real backend advance failed, using mock:', err);
    return mock.advanceAccident(id);
  }
};

// Dispatch Strategy
export const dispatch = async (strategy: string = 'hungarian') => {
  if (isMock) return mock.dispatch(strategy);
  try {
    const res = await api.post('/dispatch', null, { params: { strategy } });
    return res.data;
  } catch (err) {
    console.warn('Real backend dispatch failed, using mock:', err);
    return mock.dispatch(strategy);
  }
};

// Update Notification Status
export const updateNotificationStatus = async (
  nid: string,
  status: 'PENDING' | 'ACKNOWLEDGED' | 'ACCEPTED' | 'DECLINED'
) => {
  if (isMock) return mock.updateNotificationStatus(nid, status);
  try {
    const res = await api.post(`/notifications/${nid}/status`, { status });
    return res.data;
  } catch (err) {
    console.warn('Real backend update notification failed, using mock:', err);
    return mock.updateNotificationStatus(nid, status);
  }
};

// Verify Incident
export const verifyIncident = async (id: string): Promise<Accident> => {
  if (isMock) return mock.verifyIncident(id);
  try {
    const res = await api.patch<Accident>(`/accidents/${id}/status`, {
      new_status: 'AWAITING_AMBULANCE',
    });
    return res.data;
  } catch {
    return mock.verifyIncident(id);
  }
};

// Override Severity
export const overrideSeverity = async (id: string, newSeverity: Severity): Promise<Accident> => {
  return mock.overrideSeverity(id, newSeverity);
};

// Reassign Ambulance
export const reassignAmbulance = async (
  accidentId: string,
  newAmbId: string
): Promise<Accident> => {
  return mock.reassignAmbulance(accidentId, newAmbId);
};

// Cancel Accident
export const cancelAccident = async (id: string): Promise<Accident> => {
  if (isMock) return mock.cancelAccident(id);
  try {
    const res = await api.patch<Accident>(`/accidents/${id}/status`, { new_status: 'CANCELLED' });
    return res.data;
  } catch {
    return mock.cancelAccident(id);
  }
};

// Camera & Detection Functions
export const fetchCameraFeeds = mock.fetchCameraFeeds;
export const fetchVerificationQueue = mock.fetchVerificationQueue;
export const confirmVerificationItem = mock.confirmVerificationItem;
export const dismissVerificationItem = mock.dismissVerificationItem;
export const uploadCCTVClip = mock.uploadCCTVClip;
