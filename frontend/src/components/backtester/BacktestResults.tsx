import { useMemo } from 'react';
import type { BacktestResult } from '../../types/backtest';

interface BacktestResultsProps {
  result: BacktestResult | null;
  loading: boolean;
}

export default function BacktestResults({ result, loading }: BacktestResultsProps) {
  const metrics = useMemo(() => {
    if (!result) return null;
    return {
      netPnl: result.netPnl.toFixed(2),
      returnPct: result.returnPct.toFixed(2),
      winRate: result.winRate.toFixed(1),
      profitFactor: result.profitFactor.toFixed(2),
      maxDrawdown: result.maxDrawdownPct.toFixed(2),
      totalTrades: result.totalTrades,
      wins: result.winningTrades,
      losses: result.losingTrades,
    };
  }, [result]);

  if (loading) return <div className="results-loading">Running backtest...</div>;
  if (!result || !metrics) return <div className="results-empty">No results yet.</div>;

  return (
    <div className="backtest-results">
      <h3>Backtest Results</h3>
      <div className="metrics-grid">
        <Metric label="Net PnL" value={`$${metrics.netPnl}`} highlight={result.netPnl >= 0} />
        <Metric label="Return %" value={`${metrics.returnPct}%`} highlight={result.returnPct >= 0} />
        <Metric label="Win Rate" value={`${metrics.winRate}%`} />
        <Metric label="Profit Factor" value={metrics.profitFactor} />
        <Metric label="Max Drawdown" value={`${metrics.maxDrawdown}%`} warn />
        <Metric label="Total Trades" value={metrics.totalTrades.toString()} />
        <Metric label="Wins / Losses" value={`${metrics.wins} / ${metrics.losses}`} />
      </div>
      <EquityChart curve={result.equityCurve} />
    </div>
  );
}

function Metric({ label, value, highlight, warn }: { label: string; value: string; highlight?: boolean; warn?: boolean }) {
  return (
    <div className={`metric ${highlight ? 'positive' : ''} ${warn ? 'warning' : ''}`}>
      <span className="metric-label">{label}</span>
      <span className="metric-value">{value}</span>
    </div>
  );
}

function EquityChart({ curve }: { curve: number[] }) {
  if (!curve || curve.length < 2) return null;
  const width = 600;
  const height = 200;
  const min = Math.min(...curve);
  const max = Math.max(...curve);
  const range = max - min || 1;
  const stepX = width / (curve.length - 1);
  const points = curve.map((v, i) => `${(i * stepX).toFixed(1)},${(height - ((v - min) / range) * height).toFixed(1)}`).join(' ');

  return (
    <div className="equity-chart">
      <h4>Equity Curve</h4>
      <svg viewBox={`0 0 ${width} ${height}`} preserveAspectRatio="none" className="equity-svg">
        <polyline fill="none" stroke="#00d4aa" strokeWidth="2" points={points} />
      </svg>
    </div>
  );
}
