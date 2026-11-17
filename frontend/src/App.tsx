// src/App.tsx
// @ts-nocheck

import { Routes, Route, Navigate } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import CommandCenter from './pages/CommandCenter';
import CameraDetection from './pages/CameraDetection';
import HospitalPortal from './pages/HospitalPortal';
import SimulationLab from './pages/SimulationLab';
import Analytics from './pages/Analytics';
import Login from './pages/Login';

function App() {
  return (
    <div className="flex min-h-screen bg-background text-white">
      <Sidebar />
      <main className="flex-1 overflow-auto p-4">
        <Routes>
          <Route path="/" element={<Navigate to="/command" replace />} />
          <Route path="/command" element={<CommandCenter />} />
          <Route path="/camera" element={<CameraDetection />} />
          <Route path="/hospital" element={<HospitalPortal />} />
          <Route path="/simulation" element={<SimulationLab />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/login" element={<Login />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
