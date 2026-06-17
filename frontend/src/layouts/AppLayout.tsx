import { Outlet, Link } from 'react-router-dom';

export default function AppLayout() {
  return (
    <div className="app-layout">
      <header className="app-header">
        <h1>JARVIS Trader AI</h1>
        <nav className="app-nav">
          <Link to="/dashboard">Dashboard</Link>
          <Link to="/market">Market</Link>
          <Link to="/trade">Trade</Link>
          <Link to="/portfolio">Portfolio</Link>
          <Link to="/signal">Signal</Link>
          <Link to="/backtest">Backtest</Link>
          <Link to="/onboarding">Onboarding</Link>
          <Link to="/live">Live</Link>
          <Link to="/risk">Risk</Link>
          <Link to="/exchange">Exchange</Link>
          <Link to="/command">Command</Link>
          <Link to="/brain">Brain</Link>
          <Link to="/diagnostic">Diagnostic</Link>
        </nav>
        <span className="badge">www.jarvisTrader.ai</span>
      </header>
      <main className="app-main">
        <Outlet />
      </main>
    </div>
  );
}
