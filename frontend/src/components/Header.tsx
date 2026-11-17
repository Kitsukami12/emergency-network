// src/components/Header.tsx
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

export default function Header() {
  const [timeStr, setTimeStr] = useState('');

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      const time = now.toLocaleTimeString('en-GB', { hour12: false });
      setTimeStr(`${time} IST`);
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="h-14 bg-panel border-b border-border flex items-center justify-between px-4 select-none">
      {/* Left: Brand */}
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded bg-accent/10 border border-accent/40 flex items-center justify-center text-accent">
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z" />
          </svg>
        </div>
        <div>
          <h1 className="text-xs font-bold tracking-wider text-white uppercase font-sans">
            AI EMERGENCY RESPONSE NETWORK
          </h1>
          <p className="text-[10px] text-gray-400 font-mono tracking-wide">
            INDORE METRO • SECTOR 4
          </p>
        </div>
      </div>

      {/* Middle: Tactical Status Badges */}
      <div className="hidden md:flex items-center gap-3">
        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-[#0B1728] border border-accent/30 text-accent text-[11px] font-mono">
          <span className="w-2 h-2 rounded-full bg-low animate-pulse" />
          <span>LIVE • CCTV MESH ACTIVE</span>
        </div>

        <div className="px-2.5 py-1 rounded bg-[#0B1728] border border-accent/30 text-accent text-[11px] font-mono tracking-wide">
          DECISION-SUPPORT PROTOTYPE
        </div>

        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-[#0B1728] border border-border text-gray-300 text-[11px] font-mono">
          <svg className="w-3.5 h-3.5 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>{timeStr || '14:32:08 IST'}</span>
        </div>
      </div>

      {/* Right: Operator Badge */}
      <div className="flex items-center gap-3">
        <div className="text-right">
          <div className="text-xs font-medium text-gray-200">A. Sharma (Lead Dispatcher)</div>
          <div className="text-[10px] text-low font-mono flex items-center justify-end gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-low" />
            ON DUTY
          </div>
        </div>

        <Link
          to="/login"
          title="Operator Session / Switch Profile"
          className="w-7 h-7 rounded bg-accent/20 border border-accent/40 flex items-center justify-center text-accent hover:bg-accent hover:text-black transition-colors"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M12 4v16m8-8H4" />
          </svg>
        </Link>
      </div>
    </header>
  );
}
