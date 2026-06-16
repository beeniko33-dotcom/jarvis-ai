import { useState } from 'react';
import type { StrategyConfig } from '../../types/backtest';
import { DEFAULT_STRATEGIES } from '../../lib/useBacktest';

interface BacktesterFormProps {
  onRun: (config: {
    pair: string;
    timeframe: string;
    start: string;
    end: string;
    initialCapital: number;
    strategy: StrategyConfig;
  }) => void;
  loading: boolean;
}

const PRESET_PAIRS = [
  { label: 'BTC/USDT', value: 'BTC/USDT' },
  { label: 'ETH/USDT', value: 'ETH/USDT' },
  { label: 'EUR/USD', value: 'EUR/USD' },
  { label: 'GBP/USD', value: 'GBP/USD' },
  { label: 'USD/JPY', value: 'USD/JPY' },
];

const TIMEFRAMES = ['1m', '5m', '15m', '1H', '4H', '1D'];

export default function BacktesterForm({ onRun, loading }: BacktesterFormProps) {
  const [pair, setPair] = useState(PRESET_PAIRS[0].value);
  const [timeframe, setTimeframe] = useState('1m');
  const [start, setStart] = useState(new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10));
  const [end, setEnd] = useState(new Date().toISOString().slice(0, 10));
  const [initialCapital, setInitialCapital] = useState(10000);
  const [strategy, setStrategy] = useState<StrategyConfig>(DEFAULT_STRATEGIES[0]);
  const [strategyParams, setStrategyParams] = useState<Record<string, number>>({ fast: 10, slow: 20 });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onRun({
      pair,
      timeframe,
      start,
      end,
      initialCapital,
      strategy: { ...strategy, parameters: strategyParams },
    });
  };

  return (
    <form className="backtest-form" onSubmit={handleSubmit}>
      <div className="form-group">
        <label>Pair</label>
        <select value={pair} onChange={e => setPair(e.target.value)}>
          {PRESET_PAIRS.map(p => <option key={p.value} value={p.value}>{p.label}</option>)}
        </select>
      </div>

      <div className="form-group">
        <label>Timeframe</label>
        <select value={timeframe} onChange={e => setTimeframe(e.target.value)}>
          {TIMEFRAMES.map(t => <option key={t} value={t}>{t}</option>)}
        </select>
      </div>

      <div className="form-group">
        <label>Start Date</label>
        <input type="date" value={start} onChange={e => setStart(e.target.value)} />
      </div>

      <div className="form-group">
        <label>End Date</label>
        <input type="date" value={end} onChange={e => setEnd(e.target.value)} />
      </div>

      <div className="form-group">
        <label>Initial Capital ($)</label>
        <input
          type="number"
          value={initialCapital}
          onChange={e => setInitialCapital(Number(e.target.value))}
          min={100}
          step={1000}
        />
      </div>

      <div className="form-group">
        <label>Strategy</label>
        <select
          value={strategy.id}
          onChange={e => setStrategy(DEFAULT_STRATEGIES.find(s => s.id === e.target.value) || DEFAULT_STRATEGIES[0])}
        >
          {DEFAULT_STRATEGIES.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
        </select>
      </div>

      {strategy.id === 'sma_crossover' && (
        <div className="form-group">
          <label>Fast SMA</label>
          <input
            type="number"
            value={strategyParams.fast}
            onChange={e => setStrategyParams({ ...strategyParams, fast: Number(e.target.value) })}
            min={2}
            max={200}
          />
          <label>Slow SMA</label>
          <input
            type="number"
            value={strategyParams.slow}
            onChange={e => setStrategyParams({ ...strategyParams, slow: Number(e.target.value) })}
            min={5}
            max={500}
          />
        </div>
      )}

      <button type="submit" disabled={loading} className="btn-primary">
        {loading ? 'Running...' : 'Run Backtest'}
      </button>
    </form>
  );
}
