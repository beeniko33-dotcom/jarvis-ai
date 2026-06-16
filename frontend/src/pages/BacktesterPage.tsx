import { useState } from 'react';
import { useBacktest, useBacktestForm, DEFAULT_STRATEGIES } from '../lib/useBacktest';
import BacktestResults from '../components/backtester/BacktestResults';
import type { BacktestResult } from '../types/backtest';

export default function BacktesterPage() {
  const form = useBacktestForm('BTC/USDT', '1m');
  const { runBacktest, loading, error } = useBacktest();
  const [result, setResult] = useState<BacktestResult | null>(null);

  const handleRun = async () => {
    const res = await runBacktest({
      pair: form.pair,
      timeframe: form.timeframe,
      start: form.start,
      end: form.end,
      initialCapital: form.initialCapital,
      strategy: form.strategy,
    });
    setResult(res.result);
  };

  return (
    <div className="backtester-page">
      <h2>Backtester</h2>
      <div className="backtester-layout">
        <section className="backtester-config">
          <div className="field">
            <label>Pair</label>
            <select value={form.pair} onChange={e => form.setPair(e.target.value)}>
              <option value="BTC/USDT">BTC/USDT</option>
              <option value="ETH/USDT">ETH/USDT</option>
              <option value="EUR/USD">EUR/USD</option>
              <option value="GBP/USD">GBP/USD</option>
              <option value="USD/JPY">USD/JPY</option>
            </select>
          </div>
          <div className="field">
            <label>Timeframe</label>
            <select value={form.timeframe} onChange={e => form.setTimeframe(e.target.value)}>
              <option value="1m">1m</option>
              <option value="5m">5m</option>
              <option value="15m">15m</option>
              <option value="1H">1H</option>
              <option value="4H">4H</option>
              <option value="1D">1D</option>
            </select>
          </div>
          <div className="field">
            <label>Start</label>
            <input type="date" value={form.start} onChange={e => form.setStart(e.target.value)} />
          </div>
          <div className="field">
            <label>End</label>
            <input type="date" value={form.end} onChange={e => form.setEnd(e.target.value)} />
          </div>
          <div className="field">
            <label>Initial capital</label>
            <input
              type="number"
              value={form.initialCapital}
              onChange={e => form.setInitialCapital(Number(e.target.value))}
              min={100}
              step={1000}
            />
          </div>
          <div className="field">
            <label>Strategy</label>
            <select
              value={form.strategy.id}
              onChange={e => form.setStrategy(DEFAULT_STRATEGIES.find(s => s.id === e.target.value) || DEFAULT_STRATEGIES[0])}
            >
              {DEFAULT_STRATEGIES.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
            </select>
          </div>
          {form.strategy.id === 'sma_crossover' && (
            <div className="field">
              <label>Fast SMA</label>
              <input type="number" value={10} readOnly />
              <label>Slow SMA</label>
              <input type="number" value={20} readOnly />
            </div>
          )}
          <button onClick={handleRun} disabled={loading}>
            {loading ? 'Running...' : 'Run backtest'}
          </button>
          {error && <p className="error">{error}</p>}
        </section>
        <section className="backtester-output">
          <BacktestResults result={result} loading={loading} />
        </section>
      </div>
    </div>
  );
}
