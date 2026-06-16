import { useState, useCallback } from 'react';
import type { BacktestRequest, BacktestResult, BacktestResultsResponse, StrategyConfig } from '../types/backtest';
import { useAuth } from '../contexts/AuthContext';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export function useBacktest() {
  const { token } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const runBacktest = useCallback(async (req: BacktestRequest): Promise<{ resultId: string; result: BacktestResult }> => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_URL}/backtest/run`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          pair: req.pair,
          timeframe: req.timeframe,
          start: req.start,
          end: req.end,
          initial_capital: req.initialCapital,
          strategy: req.strategy.id,
        }),
      });
      if (!res.ok) throw new Error('Backtest failed');
      return await res.json();
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Backtest failed');
      throw e;
    } finally {
      setLoading(false);
    }
  }, [token]);

  const getResults = useCallback(async (resultId?: string): Promise<BacktestResultsResponse> => {
    const url = resultId ? `${API_URL}/backtest/results?result_id=${resultId}` : `${API_URL}/backtest/results`;
    const res = await fetch(url, {
      headers: { 'Authorization': `Bearer ${token}` },
    });
    if (!res.ok) throw new Error('Failed to fetch results');
    return res.json();
  }, [token]);

  return { runBacktest, getResults, loading, error };
}

export const DEFAULT_STRATEGIES: StrategyConfig[] = [
  {
    id: 'sma_crossover',
    name: 'SMA Crossover',
    parameters: { fast: 10, slow: 20 },
  },
];

export function useBacktestForm(defaultPair = 'BTC/USDT', defaultTimeframe = '1m') {
  const [pair, setPair] = useState(defaultPair);
  const [timeframe, setTimeframe] = useState(defaultTimeframe);
  const [start, setStart] = useState(() => new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10));
  const [end, setEnd] = useState(() => new Date().toISOString().slice(0, 10));
  const [initialCapital, setInitialCapital] = useState(10000);
  const [strategy, setStrategy] = useState<StrategyConfig>(DEFAULT_STRATEGIES[0]);

  const reset = useCallback(() => {
    setPair(defaultPair);
    setTimeframe(defaultTimeframe);
    setStart(new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10));
    setEnd(new Date().toISOString().slice(0, 10));
    setInitialCapital(10000);
    setStrategy(DEFAULT_STRATEGIES[0]);
  }, [defaultPair, defaultTimeframe]);

  return {
    pair, setPair,
    timeframe, setTimeframe,
    start, setStart,
    end, setEnd,
    initialCapital, setInitialCapital,
    strategy, setStrategy,
    reset,
  };
}
