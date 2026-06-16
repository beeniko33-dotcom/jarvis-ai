export interface StrategyConfig {
  id: string;
  name: string;
  parameters: Record<string, number | string | boolean>;
}

export interface BacktestRequest {
  pair: string;
  timeframe: string;
  start: string;
  end: string;
  initialCapital: number;
  strategy: StrategyConfig;
}

export interface BacktestTrade {
  id: number;
  pair: string;
  direction: 'BUY' | 'SELL';
  entry: number;
  exit: number;
  size: number;
  pnl: number;
  openedAt: string;
  closedAt: string;
}

export interface BacktestResult {
  initialCapital: number;
  finalBalance: number;
  netPnl: number;
  returnPct: number;
  totalTrades: number;
  winningTrades: number;
  losingTrades: number;
  winRate: number;
  profitFactor: number;
  maxDrawdownPct: number;
  equityCurve: number[];
  trades: BacktestTrade[];
}

export interface BacktestResultsResponse {
  results: Array<{
    id: string;
    request: Record<string, unknown>;
    result: BacktestResult;
  }>;
}
