import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';

interface SignalResponse {
  session: string;
  user: string;
  year: number;
  pair: string;
  timeframe: string;
  strategy: string;
  initial_capital: number;
  risk_percent: number;
  signal: {
    pair: string;
    signal: string;
    bias: string;
    confidence: number;
    reasoning: string;
    timestamp: string;
  };
  backtest_summary: {
    net_pnl: number;
    return_pct: number;
    win_rate: number;
    max_drawdown_pct: number;
    total_trades: number;
  };
  status: string;
}

export default function OnboardingPage() {
  const { token } = useAuth();
  const [pair, setPair] = useState('BTC/USDT');
  const [timeframe, setTimeframe] = useState('1m');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<SignalResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await fetch('/signal/initialize', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          pair,
          timeframe,
          strategy: 'sma_crossover',
          initial_capital: 10000,
          risk_percent: 1.0,
          session_name: 'default-onboarding-2026',
        }),
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Failed to initialize signal');
      }
      const data: SignalResponse = await res.json();
      setResult(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Initialization failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="onboarding-page">
      <h2>2026 Onboarding: Initialize Signal</h2>
      <form className="onboarding-form" onSubmit={handleSubmit}>
        <div className="field">
          <label>Pair</label>
          <select value={pair} onChange={e => setPair(e.target.value)}>
            {['BTC/USDT', 'ETH/USDT', 'EUR/USD', 'GBP/USD', 'USD/JPY'].map(p => (
              <option key={p} value={p}>{p}</option>
            ))}
          </select>
        </div>
        <div className="field">
          <label>Timeframe</label>
          <select value={timeframe} onChange={e => setTimeframe(e.target.value)}>
            {['1m', '5m', '15m', '1H', '4H', '1D'].map(t => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
        </div>
        <button type="submit" disabled={loading} className="btn-primary">
          {loading ? 'Initializing...' : 'Start 2026 Session'}
        </button>
      </form>
      {error && <p className="error">{error}</p>}
      {result && (
        <div className="onboarding-result">
          <h3>Session Initialized</h3>
          <p><strong>Session:</strong> {result.session}</p>
          <p><strong>User:</strong> {result.user}</p>
          <p><strong>Pair:</strong> {result.pair}</p>
          <p><strong>Signal:</strong> {result.signal.signal} (confidence: {(result.signal.confidence * 100).toFixed(0)}%)</p>
          <p><strong>Reasoning:</strong> {result.signal.reasoning}</p>
          <div className="backtest-summary">
            <h4>Backtest Summary</h4>
            <p>Net PnL: ${result.backtest_summary.net_pnl}</p>
            <p>Return: {result.backtest_summary.return_pct}%</p>
            <p>Win Rate: {result.backtest_summary.win_rate}%</p>
            <p>Max Drawdown: {result.backtest_summary.max_drawdown_pct}%</p>
            <p>Total Trades: {result.backtest_summary.total_trades}</p>
          </div>
        </div>
      )}
    </div>
  );
}
