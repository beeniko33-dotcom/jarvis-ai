export interface RiskLimits {
  maxDailyLossPct: number;
  maxDrawdownPct: number;
  maxExposureUsd: number;
  maxPositionPct: number;
}

export interface PositionRiskRequest {
  userId: string;
  exchange: string;
  symbol: string;
  side: 'LONG' | 'SHORT' | 'BUY' | 'SELL';
  size: number;
  entryPrice: number;
  leverage: number;
  currentEquity: number;
  initialEquity: number;
  riskPercent: number;
}

export interface RiskCheckResponse {
  approved: boolean;
  positionSize: number;
  maxPosition: number;
  riskAmount: number;
  reasons: string[];
  warnings: string[];
}

export interface UserRiskState {
  userId: string;
  dailyPnl: number;
  dailyTrades: number;
  consecutiveLosses: number;
  peakEquity: number;
  currentEquity: number;
  cooldownActive: boolean;
}

export interface CircuitBreakerState {
  [name: string]: 'closed' | 'open' | 'half_open';
}
