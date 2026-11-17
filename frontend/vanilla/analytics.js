// analytics.js – builds Chart.js visualizations from mock data
import { fetchAccidents, fetchAmbulances } from './api.js';

function severityDistribution(accidents) {
  const counts = { HIGH: 0, MEDIUM: 0, LOW: 0 };
  accidents.forEach(a => {
    const sev = a.severity?.toUpperCase() || 'LOW';
    if (counts[sev] !== undefined) counts[sev]++;
    else counts['LOW']++;
  });
  return counts;
}

function statusOverTime(accidents) {
  // Simple per-accident timeline: count of statuses per minute (mock)
  const timeline = {};
  accidents.forEach(a => {
    const minute = Math.floor(Math.random() * 10); // mock minute
    const status = a.status || 'UNKNOWN';
    if (!timeline[minute]) timeline[minute] = {};
    timeline[minute][status] = (timeline[minute][status] || 0) + 1;
  });
  const labels = Object.keys(timeline).sort((a, b) => a - b);
  const statusSet = new Set();
  labels.forEach(m => Object.keys(timeline[m]).forEach(s => statusSet.add(s)));
  const datasets = [];
  statusSet.forEach(status => {
    const data = labels.map(m => timeline[m][status] || 0);
    const color = status === 'COMPLETED' ? 'green' : status === 'IN_PROGRESS' ? 'orange' : 'red';
    datasets.push({ label: status, data, borderColor: color, fill: false });
  });
  return { labels, datasets };
}

function ambulanceUtilization(ambulances) {
  const used = ambulances.filter(a => a.status && a.status !== 'AVAILABLE').length;
  const total = ambulances.length;
  return { used, notUsed: total - used };
}

async function renderCharts() {
  const accidents = await fetchAccidents();
  const ambulances = await fetchAmbulances();

  // Severity pie chart
  const sevCounts = severityDistribution(accidents);
  new Chart(document.getElementById('severityChart'), {
    type: 'pie',
    data: {
      labels: Object.keys(sevCounts),
      datasets: [{ data: Object.values(sevCounts), backgroundColor: ['#ef4444', '#f59e0b', '#10b981'] }],
    },
    options: { responsive: true },
  });

  // Status line chart
  const statusData = statusOverTime(accidents);
  new Chart(document.getElementById('statusChart'), {
    type: 'line',
    data: statusData,
    options: { responsive: true },
  });

  // Ambulance bar chart
  const ambUtil = ambulanceUtilization(ambulances);
  new Chart(document.getElementById('ambulanceChart'), {
    type: 'bar',
    data: {
      labels: ['In Use', 'Available'],
      datasets: [{ label: 'Ambulances', data: [ambUtil.used, ambUtil.notUsed], backgroundColor: ['#2563eb', '#22c55e'] }],
    },
    options: { responsive: true },
  });
}

renderCharts();
