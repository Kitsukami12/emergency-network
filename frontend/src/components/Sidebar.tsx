// src/components/Sidebar.tsx
import React from 'react';
import { NavLink } from 'react-router-dom';
import { colors } from '../theme';

const links = [
  { to: '/command', label: 'Command Center' },
  { to: '/camera', label: 'Camera & Detection' },
  { to: '/hospital', label: 'Hospital Portal' },
  { to: '/simulation', label: 'Simulation Lab' },
  { to: '/analytics', label: 'Analytics' },
  { to: '/login', label: 'Login' },
];

export default function Sidebar() {
  return (
    <nav className="w-64 bg-panel border-r border-border flex flex-col p-4">
      <h2 className="text-xl font-bold mb-6" style={{ color: colors.accent }}>ER Network</h2>
      <ul className="flex flex-col gap-2">
        {links.map((l) => (
          <li key={l.to}>
            <NavLink
              to={l.to}
              className={({ isActive }) =>
                `block px-3 py-2 rounded hover:bg-background ${isActive ? 'bg-background font-semibold' : ''}`
              }
            >
              {l.label}
            </NavLink>
          </li>
        ))}
      </ul>
    </nav>
  );
}
