// camera-detection.js – handles verification queue and mock video upload
import { fetchVerificationQueue } from './api.js';

// Create a queue item element with Confirm/Dismiss buttons
function createItem(item) {
  const div = document.createElement('div');
  div.className = 'incident-item';
  div.style.display = 'flex';
  div.style.justifyContent = 'space-between';
  div.style.alignItems = 'center';
  const info = document.createElement('span');
  info.innerHTML = `<strong>${item.detection_id || 'N/A'}</strong> – ${item.camera_id || ''} – ${item.status || ''}`;
  const actions = document.createElement('div');
  const confirmBtn = document.createElement('button');
  confirmBtn.textContent = 'Confirm';
  confirmBtn.className = 'button';
  confirmBtn.style.marginRight = '0.5rem';
  const dismissBtn = document.createElement('button');
  dismissBtn.textContent = 'Dismiss';
  dismissBtn.className = 'button';
  // Handlers simply remove the item from UI (mock behaviour)
  confirmBtn.onclick = () => {
    div.remove();
    console.log(`Detection ${item.detection_id} confirmed`);
  };
  dismissBtn.onclick = () => {
    div.remove();
    console.log(`Detection ${item.detection_id} dismissed`);
  };
  actions.appendChild(confirmBtn);
  actions.appendChild(dismissBtn);
  div.appendChild(info);
  div.appendChild(actions);
  return div;
}

async function loadQueue() {
  const queue = await fetchVerificationQueue();
  const container = document.getElementById('verification-queue');
  container.innerHTML = '';
  if (!queue || queue.length === 0) {
    container.textContent = 'No pending items.';
    return;
  }
  queue.forEach(item => container.appendChild(createItem(item)));
}

// Mock video upload – adds a fake detection to the queue UI
function handleUpload(event) {
  const file = event.target.files[0];
  if (!file) return;
  console.log('Uploaded video:', file.name);
  // Create a fake detection entry
  const fake = {
    detection_id: `DET-${Date.now()}`,
    camera_id: 'CAM-99',
    status: 'PENDING',
  };
  const container = document.getElementById('verification-queue');
  container.appendChild(createItem(fake));
}

function initUploadControl() {
  const uploadDiv = document.createElement('div');
  uploadDiv.style.marginBottom = '1rem';
  uploadDiv.innerHTML = `<label>Upload video for detection: <input type="file" id="video-upload" accept="video/*" /></label>`;
  const content = document.querySelector('.content');
  content.insertBefore(uploadDiv, content.firstChild);
  document.getElementById('video-upload').addEventListener('change', handleUpload);
}

async function init() {
  initUploadControl();
  await loadQueue();
}

init();
