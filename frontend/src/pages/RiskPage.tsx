import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';

export default function RiskPage() {
  const { token } = useAuth();
  const [pair, setPair] = useState('EUR/USD');
  const [direction, setDirection] = useState('BUY');
  const [size, setSize] = useState(100000);
  const [markPrice, setMarkPrice] = useState(1.08);
  const [result, setResult] = useState<any | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const check = async () => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await fetch('/risk/check-position', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ pair, direction, size, mark_price: markPrice }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: 'Risk check failed' }));
        throw new Error(err.detail || 'Risk check failed');
      }
      setResult(await res.json());
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Risk check failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="risk-page">
      <h2>Risk Check</h2>
      <div className="risk-form">
        <select value={pair} onChange={e => setPair(e.target.value)}>
          {['EUR/USD', 'GBP/USD', 'USD/JPY', 'AUD/USD', 'BTC/USDT', 'ETH/USDT'].map(p => (
            <option key={p} value={p}>{p}</option>
          ))}
        </select>
        <select value={direction} onChange={e => setDirection(e.target.value)}>
          <option value="BUY">BUY</option>
          <option value="SELL">SELL</option>
        </select>
        <input type="number" value={size} onChange={e => setSize(Number(e.target.value))} placeholder="Size" />
        <input type="number" step="any" value={markPrice} onChange={e => setMarkPrice(Number(e.target.value))} placeholder="Mark price" />
        <button onClick={check} disabled={loading}>{loading ? 'Checking...' : 'Check Risk'}</button>
      </div>
      {error && <p className="error">{error}</p>}
      {result && (
        <div className="risk-result">
          <h3>Result</h3>
          <pre>{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
