import random
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger("jarvis.risk")

MAX_OPEN_POSITIONS = 10
MAX_POSITIONS_PER_PAIR = 3
MAX_DAILY_DRAWDOWN_PCT = 10.0
MAX_ACCOUNT_DRAWDOWN_PCT = 20.0
MAX_CONSECUTIVE_LOSSES = 5
DEFAULT_RISK_PER_TRADE_PCT = 1.0
STOP_LOSS_BUFFER_PCT = 0.0005


class RiskViolation(Exception):
    pass


class DrawdownGuard:
    def __init__(self, initial_balance: float):
        self.initial_balance = initial_balance
        self.peak_balance = initial_balance
        self.daily_start_balance = initial_balance
        self.daily_start_date = datetime.utcnow().date()
        self.consecutive_losses = 0
        self.trades_today = 0

    def update(self, balance: float):
        today = datetime.utcnow().date()
        if today != self.daily_start_date:
            self.daily_start_balance = balance
            self.daily_start_date = today
            self.trades_today = 0
        self.peak_balance = max(self.peak_balance, balance)
        self.trades_today += 1

    def check_drawdown(self, balance: float):
        self.update(balance)
        account_dd = ((self.peak_balance - balance) / self.peak_balance) * 100
        daily_dd = ((self.daily_start_balance - balance) / self.daily_start_balance) * 100
        if account_dd > MAX_ACCOUNT_DRAWDOWN_PCT:
            raise RiskViolation(f"Account drawdown {account_dd:.1f}% exceeds limit {MAX_ACCOUNT_DRAWDOWN_PCT}%")
        if daily_dd > MAX_DAILY_DRAWDOWN_PCT:
            raise RiskViolation(f"Daily drawdown {daily_dd:.1f}% exceeds limit {MAX_DAILY_DRAWDOWN_PCT}%")
        return True

    def record_loss(self):
        self.consecutive_losses += 1
        if self.consecutive_losses >= MAX_CONSECUTIVE_LOSSES:
            raise RiskViolation(f"Consecutive losses {self.consecutive_losses} >= {MAX_CONSECUTIVE_LOSSES}. Trading halted.")

    def record_win(self):
        self.consecutive_losses = 0


class PositionSizer:
    @staticmethod
    def calculate_lot_size(
        equity: float,
        entry: float,
        stop_loss: float,
        pair: str = "EUR/USD",
        risk_pct: float = DEFAULT_RISK_PER_TRADE_PCT,
    ) -> float:
        if entry <= 0 or stop_loss <= 0:
            raise RiskViolation("Invalid entry or stop loss")
        risk_amount = equity * (risk_pct / 100.0)
        sl_distance = abs(entry - stop_loss)
        if sl_distance == 0:
            raise RiskViolation("Stop loss distance is zero")
        pip_value = 0.0001 if "JPY" not in pair else 0.01
        if pair in ("BTC/USD", "ETH/USD", "SOL/USD"):
            pip_value = 1.0
        pips = sl_distance / pip_value
        lot_size = risk_amount / (pips * pip_value * 10)
        lot_size = round(max(0.01, min(lot_size, 10.0)), 2)
        return lot_size

    @staticmethod
    def calculate_tp_sl(entry: float, direction: str = "BUY", risk_reward_ratio: float = 2.0) -> Tuple[float, float]:
        if direction.upper() == "BUY":
            sl = entry * (1 - STOP_LOSS_BUFFER_PCT)
            tp = entry + (entry - sl) * risk_reward_ratio
        else:
            sl = entry * (1 + STOP_LOSS_BUFFER_PCT)
            tp = entry - (sl - entry) * risk_reward_ratio
        return round(tp, 5), round(sl, 5)


class MaxExposure:
    def __init__(self):
        self.open_positions: Dict[str, List[dict]] = {}

    def check(self, pair: str, direction: str, size: float, open_count: int) -> bool:
        if open_count >= MAX_OPEN_POSITIONS:
            raise RiskViolation(f"Max open positions {MAX_OPEN_POSITIONS} reached")
        pair_positions = self.open_positions.get(pair, [])
        same_direction = sum(1 for p in pair_positions if p.get("direction") == direction.upper())
        if same_direction >= MAX_POSITIONS_PER_PAIR:
            raise RiskViolation(f"Max {MAX_POSITIONS_PER_PAIR} {direction} positions for {pair}")
        return True

    def register(self, pair: str, direction: str, size: float, trade_id: int):
        if pair not in self.open_positions:
            self.open_positions[pair] = []
        self.open_positions[pair].append({"direction": direction.upper(), "size": size, "id": trade_id})

    def deregister(self, pair: str, trade_id: int):
        if pair in self.open_positions:
            self.open_positions[pair] = [p for p in self.open_positions[pair] if p.get("id") != trade_id]
            if not self.open_positions[pair]:
                del self.open_positions[pair]


class CircuitBreaker:
    def __init__(self):
        self.tripped = False
        self.trip_reason = ""

    def check(self) -> bool:
        if self.tripped:
            raise RiskViolation(f"Circuit breaker active: {self.trip_reason}")
        return True

    def trip(self, reason: str):
        self.tripped = True
        self.trip_reason = reason
        logger.warning(f"Circuit breaker tripped: {reason}")

    def reset(self):
        self.tripped = False
        self.trip_reason = ""


class RiskManager:
    def __init__(self, initial_balance: float = 10000.0):
        self.drawdown_guard = DrawdownGuard(initial_balance)
        self.exposure = MaxExposure()
        self.circuit_breaker = CircuitBreaker()
        self.initial_balance = initial_balance

    def validate_trade(self, pair: str, direction: str, size: float, entry: float, stop_loss: float, current_balance: float, open_positions: int) -> dict:
        self.drawdown_guard.check_drawdown(current_balance)
        self.circuit_breaker.check()
        self.exposure.check(pair, direction, size, open_positions)
        if size <= 0:
            raise RiskViolation("Lot size must be positive")
        if size > 10:
            raise RiskViolation("Max lot size is 10")
        max_loss = size * 1000 * (abs(entry - stop_loss) / entry) if entry > 0 else size * 50
        if max_loss > current_balance * 0.05:
            raise RiskViolation(f"Max loss {max_loss:.2f} exceeds 5% of balance")
        recommended_size = PositionSizer.calculate_lot_size(current_balance, 1.0, entry, stop_loss, pair)
        if size > recommended_size * 3:
            logger.warning(f"Requested lot {size} >> recommended {recommended_size:.2f}")
        return {"recommended_size": recommended_size, "max_loss": max_loss}

    def check_trade(self, pair: str, direction: str, size: float, entry: float, stop_loss: float, current_balance: float, open_positions: int) -> dict:
        return self.validate_trade(pair, direction, size, entry, stop_loss, current_balance, open_positions)

    def record_trade_outcome(self, pnl: float):
        if pnl < 0:
            self.drawdown_guard.record_loss()
            if self.drawdown_guard.consecutive_losses >= MAX_CONSECUTIVE_LOSSES - 1:
                self.circuit_breaker.trip(f"{MAX_CONSECUTIVE_LOSSES} consecutive losses")
        else:
            self.drawdown_guard.record_win()
