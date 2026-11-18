// src/App.tsx
import type { ReactNode } from 'react';
import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { TopBar, StatusBar } from './components/AppChrome';
import Home from './pages/Home';
import CommandCenter from './pages/CommandCenter';
import CameraDetection from './pages/CameraDetection';
import HospitalPortal from './pages/HospitalPortal';
import SimulationLab from './pages/SimulationLab';
import Analytics from './pages/Analytics';
import Login from './pages/Login';
import { colors } from './theme';

// Console screens share the top bar and status bar.
function Console() {
  const { pathname } = useLocation();
  const isCommand = pathname.startsWith('/command');

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', background: colors.background, color: colors.text }}>
      <TopBar />
      <main
        data-skin={isCommand ? 'off' : 'on'}
        style={{ flex: 1, minHeight: 0, overflow: 'auto', padding: isCommand ? 16 : 24 }}
      >
        <Routes>
          <Route path="/command" element={<CommandCenter />} />
          <Route path="/camera" element={<CameraDetection />} />
          <Route path="/hospital" element={<HospitalPortal />} />
          <Route path="/simulation" element={<SimulationLab />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
      <StatusBar />
    </div>
  );
}

// Login and Home sit outside the console chrome.
function Standalone({ children }: { children: ReactNode }) {
  return (
    <main
      data-skin="on"
      style={{ minHeight: '100vh', display: 'grid', placeItems: 'center', padding: 24, background: colors.background, color: colors.text }}
    >
      {children}
    </main>
  );
}

function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/login" element={<Standalone><Login /></Standalone>} />
      <Route path="/*" element={<Console />} />
    </Routes>
  );
}

export default App;