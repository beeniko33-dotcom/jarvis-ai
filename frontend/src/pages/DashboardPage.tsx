import { useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';

interface Ticker {
  symbol: string;
  price: number | null;
  bid: number | null;
  ask: number | null;
  change: number | null;
}

export default function DashboardPage() {
  const { token } = useAuth();
  const [tickers, setTickers] = useState<Ticker[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    const load = async () => {
      try {
        const res = await fetch('/market/ticker');
        const data = await res.json();
        const list =
          data.pairs?.map((p: Ticker) => ({
            symbol: p.symbol,
            price: p.price ?? null,
            bid: p.bid ?? null,
            ask: p.ask ?? null,
            change: p.change ?? null,
          })) ?? [];
        if (!cancelled) {
          setTickers(list);
          setLoading(false);
        }
      } catch (e) {
        console.error(e);
        if (!cancelled) setLoading(false);
      }
    };
    load();
    const id = setInterval(load, 10000);
    return () => {
      cancelled = true;
      clearInterval(id);
    };
  }, [token]);

  return (
    <div className="dashboard">
      <h2>Market Overview</h2>
      {loading ? (
        <p>Loading...</p>
      ) : (
        <div className="ticker-grid">
          {tickers.map(t => (
            <div key={t.symbol} className="ticker-card">
              <div className="ticker-symbol">{t.symbol}</div>
              <div className="ticker-price">{t.price ?? '—'}</div>
              <div className="ticker-change">
                {typeof t.change === 'number'
                  ? `${t.change >= 0 ? '+' : ''}${(t.change * 100).toFixed(2)}%`
                  : '—'}
              </div>
            </div>
          ))}
        </div>
      )}
      <p className="muted">Auto-refreshes every 10s from /market/ticker</p>
    </div>
  );
}
