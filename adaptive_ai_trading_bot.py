import logging
import os
import time
import warnings
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import IntEnum
from typing import Deque, Dict, List, Optional, Set, Tuple

import MetaTrader5 as mt5
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.layers import Dense, Dropout, LSTM
from tensorflow.keras.models import Sequential, load_model

warnings.filterwarnings("ignore")

logger = logging.getLogger(__name__)


class Signal(IntEnum):
    SELL = -1
    FLAT = 0
    BUY = 1


@dataclass
class AdaptiveConfig:
    entry_threshold: float = 0.65
    exit_threshold: float = 0.35
    sl_atr_mult: float = 2.0
    tp_atr_mult: float = 4.5
    max_risk_percent: float = 1.0
    min_risk_percent: float = 0.5
    max_risk_percent_cap: float = 2.0
    max_entry_threshold: float = 0.85
    min_entry_threshold: float = 0.55

    def update(self, win_rate: float, profit_factor: float, drawdown: float) -> None:
        if win_rate < 0.45 or drawdown > 0.08:
            self.entry_threshold = min(self.max_entry_threshold, self.entry_threshold + 0.03)
            self.max_risk_percent = max(self.min_risk_percent, self.max_risk_percent * 0.8)
            self.sl_atr_mult = min(3.0, self.sl_atr_mult + 0.3)
        elif win_rate > 0.65 and profit_factor > 1.8:
            self.entry_threshold = max(self.min_entry_threshold, self.entry_threshold - 0.02)
            self.max_risk_percent = min(self.max_risk_percent_cap, self.max_risk_percent * 1.1)

        logger.info(
            "Adaptive params updated -> Entry: %.2f | Risk: %.2f%% | SL: %.2f ATR",
            self.entry_threshold,
            self.max_risk_percent,
            self.sl_atr_mult,
        )


@dataclass
class BotConfig:
    login: int = int(os.getenv("MT5_LOGIN", "0") or 0)
    password: str = os.getenv("MT5_PASSWORD", "")
    server: str = os.getenv("MT5_SERVER", "")
    symbol: str = os.getenv("MT5_SYMBOL", "EURUSD")
    timeframe: int = mt5.TIMEFRAME_H1
    sequence_length: int = 60
    retrain_interval_hours: int = 24
    max_spread_points: int = 30
    lot_min: float = 0.01
    lot_max: float = 10.0
    magic: int = 1234501
    deviation_points: int = 20
    check_interval_seconds: int = 30
    max_daily_loss_percent: float = 5.0
    live_trading: bool = os.getenv("LIVE_TRADING", "false").lower() in {"1", "true", "yes", "on"}
    model_file: str = "lstm_model.h5"
    scaler_file: str = "scaler.npz"
    trade_history: Deque[Dict[str, float]] = field(default_factory=lambda: deque(maxlen=200))
    completed_trade_ids: Set[str] = field(default_factory=set)


@dataclass
class TradeDecision:
    signal: Signal
    probability: float
    atr: float
    spread_points: float
    ta_score: bool


class AdaptiveAITradingBot:
    FEATURE_COLUMNS = [
        "open",
        "high",
        "low",
        "close",
        "tick_volume",
        "sma20",
        "sma50",
        "ema12",
        "ema26",
        "rsi",
        "macd",
        "macd_signal",
        "atr",
        "bb_upper",
        "bb_lower",
        "obv",
        "tenkan",
        "kijun",
    ]

    def __init__(self, cfg: BotConfig):
        self.cfg = cfg
        self.adaptive = AdaptiveConfig()
        self.model: Optional[object] = None
        self.scaler: Optional[MinMaxScaler] = None
        self.last_retrain = datetime.utcnow()
        self.last_adaptive_update: Optional[datetime] = None
        self.daily_start_equity = 0.0
        self.daily_start_date = datetime.utcnow().date()
        self.peak_equity = 0.0

    def connect_mt5(self) -> bool:
        if not self.cfg.login or not self.cfg.password or not self.cfg.server:
            logger.error("MT5 credentials are missing. Set MT5_LOGIN, MT5_PASSWORD, and MT5_SERVER.")
            return False
        if not mt5.initialize(login=self.cfg.login, password=self.cfg.password, server=self.cfg.server):
            logger.error("MT5 initialize failed: %s", mt5.last_error())
            return False
        if not mt5.symbol_select(self.cfg.symbol, True):
            logger.error("Failed to select symbol %s: %s", self.cfg.symbol, mt5.last_error())
            mt5.shutdown()
            return False
        logger.info("MT5 connected successfully")
        return True

    def fetch_data(self, n_bars: int = 1000) -> Optional[pd.DataFrame]:
        rates = mt5.copy_rates_from_pos(self.cfg.symbol, self.cfg.timeframe, 0, n_bars)
        if rates is None:
            logger.error("Failed to fetch rates: %s", mt5.last_error())
            return None
        df = pd.DataFrame(rates)
        if df.empty:
            logger.error("Fetched empty rates")
            return None
        df["time"] = pd.to_datetime(df["time"], unit="s")
        return df

    @staticmethod
    def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
        data = df.copy()
        close = data["close"]
        high = data["high"]
        low = data["low"]
        diff = close.diff(1)
        gain = diff.where(diff > 0, 0.0)
        loss = -diff.where(diff < 0, 0.0)
        avg_gain = gain.rolling(14).mean()
        avg_loss = loss.rolling(14).mean()
        rs = avg_gain / avg_loss.replace(0, np.nan)
        data["sma20"] = close.rolling(20).mean()
        data["sma50"] = close.rolling(50).mean()
        data["ema12"] = close.ewm(span=12, adjust=False).mean()
        data["ema26"] = close.ewm(span=26, adjust=False).mean()
        data["rsi"] = 100 - (100 / (1 + rs)).replace([np.inf, -np.inf], np.nan).fillna(50.0)
        data["macd"] = data["ema12"] - data["ema26"]
        data["macd_signal"] = data["macd"].ewm(span=9, adjust=False).mean()
        prev_close = close.shift(1)
        tr = np.maximum.reduce(
            [
                high - low,
                (high - prev_close).abs(),
                (low - prev_close).abs(),
            ]
        )
        data["atr"] = tr.rolling(14).mean()
        data["bb_middle"] = close.rolling(20).mean()
        data["bb_std"] = close.rolling(20).std()
        data["bb_upper"] = data["bb_middle"] + 2 * data["bb_std"]
        data["bb_lower"] = data["bb_middle"] - 2 * data["bb_std"]
        data["obv"] = (np.sign(close.diff()).fillna(0) * data["tick_volume"]).fillna(0).cumsum()
        data["tenkan"] = (high.rolling(9).max() + low.rolling(9).min()) / 2
        data["kijun"] = (high.rolling(26).max() + low.rolling(26).min()) / 2
        return data.dropna()

    def prepare_features(self, df: pd.DataFrame) -> np.ndarray:
        return df[self.FEATURE_COLUMNS].astype(float).values

    def build_lstm_model(self, input_shape: Tuple[int, int]):
        model = Sequential(
            [
                LSTM(96, return_sequences=True, input_shape=input_shape),
                Dropout(0.3),
                LSTM(64),
                Dropout(0.3),
                Dense(32, activation="relu"),
                Dense(1, activation="sigmoid"),
            ]
        )
        model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])
        return model

    def load_or_create_model(self):
        if os.path.exists(self.cfg.model_file):
            model = load_model(self.cfg.model_file)
            logger.info("Loaded existing LSTM model")
            return model
        model = self.build_lstm_model((self.cfg.sequence_length, len(self.FEATURE_COLUMNS)))
        logger.info("Created new LSTM model")
        return model

    def load_scaler(self) -> Optional[MinMaxScaler]:
        if not os.path.exists(self.cfg.scaler_file):
            return None
        try:
            data = np.load(self.cfg.scaler_file)
            scaler = MinMaxScaler()
            scaler.scale_ = data["scale"].astype(float)
            scaler.min_ = data["min"].astype(float)
            scaler.data_min_ = data["data_min"].astype(float)
            scaler.data_max_ = data["data_max"].astype(float)
            scaler.n_features_in_ = int(data["n_features_in"])
            return scaler
        except Exception as exc:
            logger.error("Failed to load scaler %s: %s", self.cfg.scaler_file, exc)
            return None

    def save_scaler(self, scaler: MinMaxScaler) -> None:
        np.savez(
            self.cfg.scaler_file,
            scale=scaler.scale_,
            min=scaler.min_,
            data_min=scaler.data_min_,
            data_max=scaler.data_max_,
            n_features_in=np.array(getattr(scaler, "n_features_in_", 0), dtype=np.int64),
        )

    def train_model(self, model, X: np.ndarray, y: np.ndarray) -> Tuple[object, MinMaxScaler]:
        if len(X) < self.cfg.sequence_length + 20:
            logger.warning("Insufficient training samples: %s", len(X))
            return model, self.scaler or MinMaxScaler()
        scaler = MinMaxScaler()
        X_scaled = scaler.fit_transform(X.reshape(-1, X.shape[-1])).reshape(X.shape)
        early_stop = EarlyStopping(monitor="val_loss", patience=5, restore_best_weights=True)
        model.fit(
            X_scaled,
            y,
            epochs=30,
            batch_size=32,
            validation_split=0.2,
            callbacks=[early_stop],
            verbose=0,
        )
        self.save_scaler(scaler)
        model.save(self.cfg.model_file)
        return model, scaler

    def build_training_set(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        features = self.prepare_features(df)
        X: List[np.ndarray] = []
        y: List[int] = []
        horizon = 12
        for i in range(self.cfg.sequence_length, len(features) - horizon):
            future_close = df["close"].iloc[i + horizon]
            current_close = df["close"].iloc[i]
            X.append(features[i - self.cfg.sequence_length : i])
            y.append(1 if future_close > current_close else 0)
        return np.array(X, dtype=float), np.array(y, dtype=int)

    def maybe_retrain(self, df: pd.DataFrame) -> None:
        now = datetime.utcnow()
        if (now - self.last_retrain).total_seconds() <= self.cfg.retrain_interval_hours * 3600:
            return
        X, y = self.build_training_set(df)
        if len(X) == 0:
            logger.warning("Skipping retrain because training set is empty")
            return
        model = self.load_or_create_model()
        model, scaler = self.train_model(model, X, y)
        self.model = model
        self.scaler = scaler
        self.last_retrain = now
        logger.info("Model retrained successfully with %s samples", len(X))

    def technical_analysis_score(self, df: pd.DataFrame) -> Tuple[bool, bool]:
        latest = df.iloc[-1]
        ma_bull = latest["close"] > latest["sma20"] > latest["sma50"]
        ma_bear = latest["close"] < latest["sma20"] < latest["sma50"]
        rsi_ok = 40 < latest["rsi"] < 70
        rsi_overbought_ok = latest["rsi"] > 30
        macd_bull = latest["macd"] > latest["macd_signal"]
        macd_bear = latest["macd"] < latest["macd_signal"]
        bull = ma_bull and rsi_ok and macd_bull
        bear = ma_bear and rsi_overbought_ok and macd_bear
        return bull, bear

    def generate_signal(self, df: pd.DataFrame) -> TradeDecision:
        if len(df) < self.cfg.sequence_length + 10 or self.model is None or self.scaler is None:
            return TradeDecision(Signal.FLAT, 0.0, 0.0, self.current_spread_points(), False)
        recent = df.iloc[-self.cfg.sequence_length :]
        features = self.prepare_features(recent)
        X = self.scaler.transform(features.reshape(-1, features.shape[-1])).reshape(1, self.cfg.sequence_length, -1)
        probability = float(self.model.predict(X, verbose=0)[0][0])
        bull_ta, bear_ta = self.technical_analysis_score(df)
        if bull_ta:
            final_probability = probability
            signal = Signal.BUY if final_probability > self.adaptive.entry_threshold else Signal.FLAT
        elif bear_ta:
            final_probability = 1.0 - probability
            signal = Signal.SELL if final_probability > self.adaptive.entry_threshold else Signal.FLAT
        else:
            final_probability = probability * 0.6
            signal = Signal.FLAT
        return TradeDecision(
            signal=signal,
            probability=round(final_probability, 4),
            atr=float(df["atr"].iloc[-1]),
            spread_points=self.current_spread_points(),
            ta_score=bool(bull_ta or bear_ta),
        )

    def current_spread_points(self) -> float:
        tick = mt5.symbol_info_tick(self.cfg.symbol)
        info = mt5.symbol_info(self.cfg.symbol)
        if tick is None or info is None:
            return float("inf")
        spread = tick.ask - tick.bid
        return round(spread / info.point, 2)

    def account_equity(self) -> Optional[float]:
        info = mt5.account_info()
        if info is None:
            return None
        equity = float(info.equity)
        return equity if equity > 0 else None

    def check_daily_loss(self, equity: float) -> bool:
        today = datetime.utcnow().date()
        if today != self.daily_start_date:
            self.daily_start_equity = equity
            self.daily_start_date = today
            self.peak_equity = equity
        self.peak_equity = max(self.peak_equity, equity)
        if self.daily_start_equity <= 0:
            self.daily_start_equity = equity
            return True
        daily_loss_pct = ((self.daily_start_equity - equity) / self.daily_start_equity) * 100
        return daily_loss_pct >= self.cfg.max_daily_loss_percent

    def symbol_volume_step(self) -> float:
        info = mt5.symbol_info(self.cfg.symbol)
        if info is None:
            return 0.01
        return max(float(info.volume_step), 0.01)

    def calculate_lot_size(self, equity: float, atr: float) -> Optional[float]:
        if equity <= 0 or atr <= 0:
            return None
        risk_amount = equity * (self.adaptive.max_risk_percent / 100.0)
        tick_value_func = getattr(mt5, "symbol_info_tick_value", None) or getattr(mt5, "symbol_info_tickvalue", None)
        tick_value = 0.0
        if tick_value_func is not None:
            try:
                tick_value = float(tick_value_func(self.cfg.symbol, mt5.ORDER_TYPE_BUY, 1.0) or 0.0)
            except Exception as exc:
                logger.error("Failed to fetch tick value for %s: %s", self.cfg.symbol, exc)
        if tick_value <= 0:
            logger.error("Invalid tick value for %s; refusing to size a position", self.cfg.symbol)
            return None
        raw_lot = risk_amount / (atr * tick_value)
        lot = max(self.cfg.lot_min, min(self.cfg.lot_max, raw_lot))
        step = self.symbol_volume_step()
        rounded_lot = round((lot // step) * step, 2)
        if rounded_lot < self.cfg.lot_min:
            logger.error("Calculated lot %.5f is below minimum %.2f for %s", rounded_lot, self.cfg.lot_min, self.cfg.symbol)
            return None
        return rounded_lot

    def order_request(self, order_type: int, price: float, volume: float, sl: float, tp: float) -> Dict[str, object]:
        return {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.cfg.symbol,
            "volume": volume,
            "type": order_type,
            "price": price,
            "sl": sl,
            "tp": tp,
            "deviation": self.cfg.deviation_points,
            "magic": self.cfg.magic,
            "comment": "AI_MA_Buy" if order_type == mt5.ORDER_TYPE_BUY else "AI_MA_Sell",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

    def open_position(self, decision: TradeDecision, equity: float) -> None:
        tick = mt5.symbol_info_tick(self.cfg.symbol)
        if tick is None:
            logger.error("Failed to fetch tick")
            return
        is_buy = decision.signal == Signal.BUY
        price = tick.ask if is_buy else tick.bid
        order_type = mt5.ORDER_TYPE_BUY if is_buy else mt5.ORDER_TYPE_SELL
        sl = price - self.adaptive.sl_atr_mult * decision.atr if is_buy else price + self.adaptive.sl_atr_mult * decision.atr
        tp = price + self.adaptive.tp_atr_mult * decision.atr if is_buy else price - self.adaptive.tp_atr_mult * decision.atr
        lot = self.calculate_lot_size(equity, decision.atr)
        if lot is None:
            logger.error("Invalid lot size; order rejected")
            return
        request = self.order_request(order_type, price, lot, sl, tp)
        if not self.cfg.live_trading:
            logger.warning(
                "DRY RUN %s | Lot: %.2f | Price: %.5f | SL: %.5f | TP: %.5f | Prob: %.4f",
                "BUY" if is_buy else "SELL",
                lot,
                price,
                sl,
                tp,
                decision.probability,
            )
            return
        result = mt5.order_send(request)
        if result is None:
            logger.error("order_send returned None")
            return
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            direction = "BUY" if is_buy else "SELL"
            logger.info("%s opened | Lot: %.2f | Prob: %.4f | SL: %.5f | TP: %.5f", direction, lot, decision.probability, sl, tp)
            self.cfg.trade_history.append({"type": direction.lower(), "profit": 0.0})
        else:
            logger.error("Order failed: retcode=%s comment=%s", result.retcode, result.comment)

    def close_positions(self) -> None:
        positions = [position for position in self.current_positions() if getattr(position, "magic", 0) == self.cfg.magic]
        if not positions:
            return
        tick = mt5.symbol_info_tick(self.cfg.symbol)
        if tick is None:
            logger.error("Failed to fetch tick while closing positions")
            return
        for position in positions:
            order_type = mt5.ORDER_TYPE_SELL if position.type == mt5.POSITION_TYPE_BUY else mt5.ORDER_TYPE_BUY
            price = tick.bid if position.type == mt5.POSITION_TYPE_BUY else tick.ask
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": self.cfg.symbol,
                "volume": position.volume,
                "type": order_type,
                "position": position.ticket,
                "price": price,
                "deviation": self.cfg.deviation_points,
                "magic": self.cfg.magic,
                "comment": "AI_MA_Exit",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            result = mt5.order_send(request)
            if result is not None and result.retcode == mt5.TRADE_RETCODE_DONE:
                logger.info("Position %s closed", position.ticket)
            else:
                logger.error("Close failed for %s: %s", position.ticket, getattr(result, "comment", mt5.last_error()))

    def current_positions(self) -> List[object]:
        positions = mt5.positions_get(symbol=self.cfg.symbol)
        return [position for position in positions or [] if getattr(position, "magic", 0) == self.cfg.magic]

    def sync_trade_history_from_deals(self) -> None:
        from_date = datetime.utcnow() - timedelta(days=30)
        to_date = datetime.utcnow()
        try:
            deals = mt5.history_deals_get(from_date, to_date, symbol=self.cfg.symbol)
        except Exception as exc:
            logger.warning("Failed to fetch deal history: %s", exc)
            return
        if not deals:
            return
        for deal in deals:
            if getattr(deal, "magic", 0) != self.cfg.magic:
                continue
            deal_id = f"{deal.order}:{deal.position}:{deal.time}:{deal.price}"
            if deal_id in self.cfg.completed_trade_ids:
                continue
            profit = float(getattr(deal, "profit", 0.0) or 0.0) + float(getattr(deal, "swap", 0.0) or 0.0) + float(getattr(deal, "commission", 0.0) or 0.0)
            self.cfg.trade_history.append({"type": "deal", "profit": profit})
            self.cfg.completed_trade_ids.add(deal_id)

    def trade_metrics(self) -> Tuple[float, float, float]:
        self.sync_trade_history_from_deals()
        completed = [trade for trade in self.cfg.trade_history if trade.get("profit", 0.0) != 0.0]
        if not completed:
            return 0.5, 1.0, 0.0
        wins = sum(1 for trade in completed if trade["profit"] > 0)
        gross_profit = sum(max(trade["profit"], 0.0) for trade in completed)
        gross_loss = abs(sum(min(trade["profit"], 0.0) for trade in completed))
        win_rate = wins / len(completed)
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float("inf")
        equity = 0.0
        peak = 0.0
        drawdown = 0.0
        for trade in completed:
            equity += trade["profit"]
            peak = max(peak, equity)
            drawdown = max(drawdown, ((peak - equity) / peak) if peak > 0 else 0.0)
        return win_rate, profit_factor, drawdown

    def maybe_update_adaptive(self, now: datetime) -> None:
        if self.last_adaptive_update is None or (now - self.last_adaptive_update).total_seconds() >= 3600:
            if len(self.cfg.trade_history) > 30:
                win_rate, profit_factor, drawdown = self.trade_metrics()
                self.adaptive.update(win_rate, profit_factor, drawdown)
            self.last_adaptive_update = now

    def run_once(self) -> None:
        equity = self.account_equity()
        if equity is None:
            logger.error("Invalid or unavailable account equity. Pausing until account data is available.")
            time.sleep(3600)
            return
        if self.check_daily_loss(equity):
            logger.warning("Daily loss limit reached. Closing bot-owned positions and pausing for one hour.")
            self.close_positions()
            time.sleep(3600)
            return
        df = self.fetch_data(500)
        if df is None or len(df) < 100:
            time.sleep(self.cfg.check_interval_seconds)
            return
        df = self.add_indicators(df)
        self.maybe_retrain(df)
        decision = self.generate_signal(df)
        spread_ok = decision.spread_points <= self.cfg.max_spread_points
        positions = self.current_positions()
        logger.info(
            "Prediction: %.4f | Signal: %s | ATR: %.5f | Spread: %.1f pts | TA: %s",
            decision.probability,
            decision.signal.name,
            decision.atr,
            decision.spread_points,
            decision.ta_score,
        )
        if not spread_ok:
            logger.warning("Spread too high: %.1f points", decision.spread_points)
            return
        if decision.signal == Signal.BUY and not positions:
            self.open_position(decision, equity)
        elif decision.signal == Signal.SELL and not positions:
            self.open_position(decision, equity)
        elif decision.signal == Signal.FLAT and positions:
            self.close_positions()
        self.maybe_update_adaptive(datetime.utcnow())

    def run(self) -> None:
        if not self.connect_mt5():
            return
        self.model = self.load_or_create_model()
        self.scaler = self.load_scaler()
        logger.info("=== Adaptive AI Trading Bot Started ===")
        while True:
            try:
                self.run_once()
                time.sleep(self.cfg.check_interval_seconds)
            except Exception as exc:
                logger.exception("Error in main loop: %s", exc)
                time.sleep(60)
                terminal = mt5.terminal_info()
                if terminal is None or not terminal.connected:
                    mt5.shutdown()
                    self.connect_mt5()


def configure_logging() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")


def main() -> None:
    configure_logging()
    bot = AdaptiveAITradingBot(BotConfig())
    try:
        bot.run()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    main()
