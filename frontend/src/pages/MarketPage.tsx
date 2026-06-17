import { useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';

interface Ticker {
  symbol: string;
  price: number | null;
  bid: number | null;
  ask: number | null;
  change: number | null;
}

export default function MarketPage() {
  const { token } = useAuth();
  const [tickers, setTickers] = useState<Ticker[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    try {
      const res = await fetch('/market/ticker');
      if (!res.ok) throw new Error('Failed to load market data');
      const data = await res.json();
      const list =
        data.pairs?.map((p: Ticker) => ({
          symbol: p.symbol,
          price: p.price ?? null,
          bid: p.bid ?? null,
          ask: p.ask ?? null,
          change: p.change ?? null,
        })) ?? [];
      setTickers(list);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Market data unavailable');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    const id = setInterval(load, 10000);
    return () => clearInterval(id);
  }, [token]);

  return (
    <div className="market-page">
      <h2>Market Overview</h2>
      {error && <p className="error">{error}</p>}
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
