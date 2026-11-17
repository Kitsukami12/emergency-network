// src/pages/Login.tsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { colors } from '../theme';

export default function Login() {
  const [pin, setPin] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Very simple check – in real app the backend validates via Basic auth.
    if (pin.trim().length === 0) {
      setError('Enter PIN');
      return;
    }
    // Save to localStorage to simulate session persistence.
    localStorage.setItem('emergency_pin', pin);
    navigate('/command');
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-background text-white">
      <div className="bg-panel border border-border rounded p-8 w-96">
        <h2 className="text-2xl mb-4" style={{ color: colors.accent }}>Operator Login</h2>
        <form onSubmit={handleSubmit} className="flex flex-col gap-3">
          <label className="text-gray-300">PIN / Password</label>
          <input
            type="password"
            value={pin}
            onChange={(e) => setPin(e.target.value)}
            className="p-2 rounded bg-background text-white focus:outline-none"
          />
          {error && <p className="text-red-500 text-sm">{error}</p>}
          <button type="submit" className="mt-2 px-4 py-2 rounded bg-accent text-black disabled:opacity-50">
            Login
          </button>
        </form>
        <hr className="my-4 border-border" />
        <div className="text-sm text-gray-400">
          <p>Decision‑support prototype</p>
          <p>ETAs are estimates, not guaranteed.</p>
          <p>Ambulance positions are simulated.</p>
          <p>Incident severity is an estimate, not medical severity.</p>
          <p>Human verification is required.</p>
        </div>
      </div>
    </div>
  );
}
