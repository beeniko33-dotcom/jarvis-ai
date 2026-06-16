import random
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Callable

logger = logging.getLogger("jarvis.backtest")

Trade = dict  # {pair, direction, entry, exit, size, pnl, opened_at, closed_at}


def ccxt_symbol(pair: str) -> str:
    return pair.replace("/", "")


def normalize_timeframe(tf: str) -> str:
    mapping = {"1m": "1m", "5m": "5m", "15m": "15m", "1H": "1h", "4H": "4h", "1D": "1d"}
    return mapping.get(tf, "1m")


def simulated_candles(pair: str, timeframe: str = "1m", count: int = 100) -> List[dict]:
    cfg = {"BTC/USD": (68400, 150), "ETH/USD": (3650, 15), "EUR/USD": (1.0850, 0.0004), "GBP/USD": (1.2740, 0.0006), "USD/JPY": (157.20, 0.06)}
    base, vol = cfg.get(pair, (1.0, 0.01))
    arr = []
    now = datetime.utcnow()
    price = base
    for i in range(count):
        o = price + random.uniform(-vol * 0.3, vol * 0.3)
        c = o + random.uniform(-vol, vol)
        h = max(o, c) + abs(random.uniform(0, vol * 0.5))
        l = min(o, c) - abs(random.uniform(0, vol * 0.5))
        arr.append({
            "timestamp": (now - timedelta(minutes=count - i)).isoformat(),
            "open": round(o, 5), "high": round(h, 5), "low": round(l, 5), "close": round(c, 5), "volume": round(random.uniform(10, 1000), 2)
        })
        price = c
    return arr


def sma_crossover_strategy(candles: list, fast: int = 10, slow: int = 20) -> List[Trade]:
    return simple_sma_crossover(candles, fast=fast, slow=slow)


def load_candles(pair: str, timeframe: str = "1m", start: str = "", end: str = "", count: int = 100) -> List[dict]:
    try:
        import ccxt
        exchange = ccxt.binance()
        symbol = ccxt_symbol(pair)
        tf = normalize_timeframe(timeframe)
        since = exchange.parse8601(start) if start else exchange.parse8601((datetime.utcnow() - timedelta(minutes=count)).isoformat())
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe=tf, since=since, limit=count)
        candles = [
            {"timestamp": datetime.utcfromtimestamp(o[0] / 1000).isoformat(), "open": o[1], "high": o[2], "low": o[3], "close": o[4], "volume": o[5]}
            for o in ohlcv
        ]
        return candles
    except Exception as e:
        logger.warning(f"CCXT candles fallback: {e}")
        return simulated_candles(pair, timeframe, count)


def simple_sma_crossover(candles: list, fast: int = 10, slow: int = 20) -> List[Trade]:
    trades = []
    closes = [c["close"] for c in candles]
    position = None
    for i in range(slow, len(closes)):
        sma_fast = sum(closes[i - fast + 1 : i + 1]) / fast
        sma_slow = sum(closes[i - slow + 1 : i + 1]) / slow
        price = closes[i]
        if position is None:
            if sma_fast > sma_slow:
                position = {"direction": "BUY", "entry": price, "index": i}
            elif sma_fast < sma_slow:
                position = {"direction": "SELL", "entry": price, "index": i}
        else:
            if position["direction"] == "BUY" and sma_fast < sma_slow:
                pnl = (price - position["entry"]) * 100
                trades.append({**position, "exit": price, "pnl": pnl, "opened_at": candles[position["index"]]["timestamp"], "closed_at": candles[i]["timestamp"]})
                position = None
            elif position["direction"] == "SELL" and sma_fast > sma_slow:
                pnl = (position["entry"] - price) * 100
                trades.append({**position, "exit": price, "pnl": pnl, "opened_at": candles[position["index"]]["timestamp"], "closed_at": candles[i]["timestamp"]})
                position = None
    return trades


def run_backtest(
    candles: list,
    strategy_func: Callable = simple_sma_crossover,
    initial_capital: float = 10000.0,
    commission_pct: float = 0.1,
) -> dict:
    trades: List[Trade] = strategy_func(candles)
    equity_curve = [initial_capital]
    balance = initial_capital
    wins = 0
    peak = initial_capital
    max_dd = 0.0
    gross_profit = 0.0
    gross_loss = 0.0

    for t in trades:
        pnl = t["pnl"] - (abs(t["pnl"]) * commission_pct / 100)
        t["pnl"] = round(pnl, 2)
        balance += pnl
        equity_curve.append(balance)
        if pnl > 0:
            wins += 1
            gross_profit += pnl
        else:
            gross_loss += abs(pnl)
        peak = max(peak, balance)
        dd = ((peak - balance) / peak) * 100
        max_dd = max(max_dd, dd)

    total = len(trades)
    win_rate = (wins / total * 100) if total else 0
    profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else float("inf")
    net_pnl = balance - initial_capital
    return_pct = ((balance - initial_capital) / initial_capital) * 100

    return {
        "initial_capital": initial_capital,
        "final_balance": round(balance, 2),
        "net_pnl": round(net_pnl, 2),
        "return_pct": round(return_pct, 2),
        "total_trades": total,
        "winning_trades": wins,
        "losing_trades": total - wins,
        "win_rate": round(win_rate, 1),
        "profit_factor": round(profit_factor, 2),
        "max_drawdown_pct": round(max_dd, 2),
        "equity_curve": equity_curve,
        "trades": trades[-50:],
    }
