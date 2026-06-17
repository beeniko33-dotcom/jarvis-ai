import { useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';

export default function PortfolioPage() {
  const { token } = useAuth();
  const [positions, setPositions] = useState<any[]>([]);
  const [history, setHistory] = useState<any[]>([]);
  const [forex, setForex] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      try {
        const headers = { Authorization: `Bearer ${token}` };
        const [posRes, histRes, forexRes] = await Promise.all([
          fetch('/trade/portfolio', { headers }),
          fetch('/trade/history?limit=20', { headers }),
          fetch('/forex-portfolio'),
        ]);
        if (!posRes.ok || !histRes.ok || !forexRes.ok) throw new Error('Failed to load portfolio');
        const posData = await posRes.json();
        const histData = await histRes.json();
        const forexData = await forexRes.json();
        setPositions(posData.positions || []);
        setHistory(histData.trades || []);
        setForex(forexData.pairs || []);
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Portfolio unavailable');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [token]);

  if (loading) return <div className="portfolio-page"><h2>Portfolio</h2><p>Loading...</p></div>;
  if (error) return <div className="portfolio-page"><h2>Portfolio</h2><p className="error">{error}</p></div>;

  return (
    <div className="portfolio-page">
      <h2>Portfolio</h2>
      <section className="portfolio-section">
        <h3>Open Positions</h3>
        {positions.length === 0 ? <p>No open positions</p> : positions.map((p: any) => (
          <div key={p.id} className="portfolio-card">
            <strong>{p.pair}</strong>
            <span>{p.direction}</span>
            <span>{p.size}</span>
            <span>{p.entry}</span>
          </div>
        ))}
      </section>
      <section className="portfolio-section">
        <h3>Forex Watchlist</h3>
        {forex.map((p: any) => (
          <div key={p.symbol} className="portfolio-card">
            <strong>{p.symbol}</strong>
            <span>{p.price}</span>
            <span>{p.bias}</span>
            <span>{p.change}%</span>
          </div>
        ))}
      </section>
      <section className="portfolio-section">
        <h3>Recent History</h3>
        {history.length === 0 ? <p>No trade history</p> : history.map((t: any) => (
          <div key={t.id} className="portfolio-card">
            <strong>{t.pair}</strong>
            <span>{t.direction}</span>
            <span>{t.status}</span>
          </div>
        ))}
      </section>
    </div>
  );
}
