// api.js – wrapper that decides between mock data and real backend
import { getMockAccidents, getMockAmbulances, getMockHospitals, getMockNotifications, getMockCameraFeeds, getMockVerificationQueue, getMockSimulationParams } from './mockData.js';

export async function fetchAccidents() {
  if (window.AppConfig.useMock) {
    return getMockAccidents();
  }
  const resp = await fetch(`${window.AppConfig.apiBase}/accidents`);
  return resp.json();
}
export async function fetchAmbulances() {
  if (window.AppConfig.useMock) {
    return getMockAmbulances();
  }
  const resp = await fetch(`${window.AppConfig.apiBase}/ambulances`);
  return resp.json();
}
export async function fetchHospitals() {
  if (window.AppConfig.useMock) {
    return getMockHospitals();
  }
  const resp = await fetch(`${window.AppConfig.apiBase}/hospitals`);
  return resp.json();
}
export async function fetchNotifications() {
  if (window.AppConfig.useMock) {
    return getMockNotifications();
  }
  const resp = await fetch(`${window.AppConfig.apiBase}/notifications`);
  return resp.json();
}
export async function fetchCameraFeeds() {
  if (window.AppConfig.useMock) {
    return getMockCameraFeeds();
  }
  const resp = await fetch(`${window.AppConfig.apiBase}/camera_feeds`);
  return resp.json();
}
export async function fetchVerificationQueue() {
  if (window.AppConfig.useMock) {
    return getMockVerificationQueue();
  }
  const resp = await fetch(`${window.AppConfig.apiBase}/verification_queue`);
  return resp.json();
}
export async function fetchSimulationParams() {
  if (window.AppConfig.useMock) {
    return getMockSimulationParams();
  }
  const resp = await fetch(`${window.AppConfig.apiBase}/simulation_params`);
  return resp.json();
}
