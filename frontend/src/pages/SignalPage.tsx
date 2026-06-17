import { useState } from 'react';

export default function SignalPage() {
  const [pair, setPair] = useState('EUR/USD');
  const [signal, setSignal] = useState<any | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`/forex-signal?pair=${encodeURIComponent(pair)}`);
      if (!res.ok) throw new Error('Failed to load signal');
      setSignal(await res.json());
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Signal unavailable');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="signal-page">
      <h2>AI Signal</h2>
      <div className="signal-form">
        <select value={pair} onChange={e => setPair(e.target.value)}>
          {['EUR/USD', 'GBP/USD', 'USD/JPY', 'AUD/USD', 'BTC/USDT', 'ETH/USDT'].map(p => (
            <option key={p} value={p}>{p}</option>
          ))}
        </select>
        <button onClick={load} disabled={loading}>{loading ? 'Loading...' : 'Generate Signal'}</button>
      </div>
      {error && <p className="error">{error}</p>}
      {signal && (
        <div className="signal-card">
          <h3>{signal.pair}</h3>
          <p><strong>Signal:</strong> {signal.signal}</p>
          <p><strong>Bias:</strong> {signal.bias}</p>
          <p><strong>Confidence:</strong> {Math.round(signal.confidence * 100)}%</p>
          <p><strong>Reasoning:</strong> {signal.reasoning}</p>
        </div>
      )}
    </div>
  );
}
