import React from 'react';
import { Outlet } from 'react-router-dom';

export default function AppLayout() {
  return (
    <div className="app-layout">
      <header className="app-header">
        <h1>JARVIS Trader AI</h1>
        <span className="badge">www.jarvisTrader.ai</span>
      </header>
      <main className="app-main">
        <Outlet />
      </main>
    </div>
  );
}
