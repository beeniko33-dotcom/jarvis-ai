import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';

interface TradeRequest {
  pair: string;
  direction: 'BUY' | 'SELL';
  size: number;
  entry?: number;
  take_profit?: number;
  stop_loss?: number;
  risk_percent?: number;
}

export default function TradePage() {
  const { token } = useAuth();
  const [pair, setPair] = useState('BTC/USDT');
  const [direction, setDirection] = useState<'BUY' | 'SELL'>('BUY');
  const [size, setSize] = useState(0.1);
  const [entry, setEntry] = useState('');
  const [tp, setTp] = useState('');
  const [sl, setSl] = useState('');
  const [risk, setRisk] = useState(1);
  const [result, setResult] = useState<any | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await fetch('/trade/execute', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          pair,
          direction,
          size,
          entry: entry ? Number(entry) : undefined,
          take_profit: tp ? Number(tp) : undefined,
          stop_loss: sl ? Number(sl) : undefined,
          risk_percent: risk,
        } satisfies TradeRequest),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: 'Trade failed' }));
        throw new Error(err.detail || 'Trade failed');
      }
      const data = await res.json();
      setResult(data.trade);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Trade failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="trade-page">
      <h2>New Trade</h2>
      <form className="trade-form" onSubmit={submit}>
        <div className="field">
          <label>Pair</label>
          <select value={pair} onChange={e => setPair(e.target.value)}>
            {['BTC/USDT', 'ETH/USDT', 'EUR/USD', 'GBP/USD', 'USD/JPY'].map(p => (
              <option key={p} value={p}>{p}</option>
            ))}
          </select>
        </div>
        <div className="field">
          <label>Direction</label>
          <select value={direction} onChange={e => setDirection(e.target.value as any)}>
            <option value="BUY">BUY</option>
            <option value="SELL">SELL</option>
          </select>
        </div>
        <div className="field">
          <label>Size</label>
          <input type="number" step="any" value={size} onChange={e => setSize(Number(e.target.value))} />
        </div>
        <div className="field">
          <label>Entry</label>
          <input type="number" step="any" value={entry} onChange={e => setEntry(e.target.value)} placeholder="market" />
        </div>
        <div className="field">
          <label>Take Profit</label>
          <input type="number" step="any" value={tp} onChange={e => setTp(e.target.value)} placeholder="optional" />
        </div>
        <div className="field">
          <label>Stop Loss</label>
          <input type="number" step="any" value={sl} onChange={e => setSl(e.target.value)} placeholder="optional" />
        </div>
        <div className="field">
          <label>Risk %</label>
          <input type="number" step="any" value={risk} onChange={e => setRisk(Number(e.target.value))} />
        </div>
        <button type="submit" disabled={loading}>{loading ? 'Submitting...' : 'Execute Trade'}</button>
      </form>
      {error && <p className="error">{error}</p>}
      {result && (
        <div className="trade-result">
          <h3>Trade Submitted</h3>
          <pre>{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
