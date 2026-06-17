import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';

export default function ExchangePage() {
  const { token } = useAuth();
  const [exchange, setExchange] = useState('binance');
  const [apiKey, setApiKey] = useState('');
  const [secret, setSecret] = useState('');
  const [result, setResult] = useState<any | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const save = async () => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await fetch('/api/exchange/session', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ exchange, apiKey, secret }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: 'Exchange session failed' }));
        throw new Error(err.detail || 'Exchange session failed');
      }
      setResult(await res.json());
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Exchange session failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="exchange-page">
      <h2>Exchange Session</h2>
      <div className="exchange-form">
        <select value={exchange} onChange={e => setExchange(e.target.value)}>
          <option value="binance">Binance</option>
          <option value="kraken">Kraken</option>
          <option value="coinbase">Coinbase</option>
        </select>
        <input type="text" value={apiKey} onChange={e => setApiKey(e.target.value)} placeholder="API key" />
        <input type="password" value={secret} onChange={e => setSecret(e.target.value)} placeholder="Secret" />
        <button onClick={save} disabled={loading}>{loading ? 'Saving...' : 'Save Session'}</button>
      </div>
      {error && <p className="error">{error}</p>}
      {result && (
        <div className="exchange-result">
          <h3>Session Created</h3>
          <pre>{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
