"""
JARVIS Trader AI - Risk Management Service
Production-grade risk controls for autonomous trading.
"""
import os
import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

try:
    import redis
    HAS_REDIS = True
except ImportError:
    HAS_REDIS = False

try:
    from cryptography.fernet import Fernet
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False

try:
    import ccxt
    HAS_CCXT = True
except ImportError:
    HAS_CCXT = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("jarvis.risk")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./risk.db")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
JWT_SECRET = os.getenv("JWT_SECRET_KEY", "change-me")
CIRCUIT_BREAKER_THRESHOLD = int(os.getenv("CIRCUIT_BREAKER_THRESHOLD", "5"))
MAX_DRAWDOWN_PCT = float(os.getenv("MAX_DRAWDOWN_PCT", "10.0"))
MAX_EXPOSURE_USD = float(os.getenv("MAX_EXPOSURE_USD", "50000"))
MAX_POSITION_PCT = float(os.getenv("MAX_POSITION_PCT", "2.0"))
MAX_DAILY_LOSS_PCT = float(os.getenv("MAX_DAILY_LOSS_PCT", "5.0"))

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

if HAS_REDIS:
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
else:
    redis_client = None

cipher = None
if HAS_CRYPTO:
    cipher = Fernet(Fernet.generate_key())


class PositionDB(Base):
    __tablename__ = "positions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    exchange = Column(String)
    symbol = Column(String, index=True)
    side = Column(String)
    size = Column(Float)
    entry_price = Column(Float)
    mark_price = Column(Float)
    unrealized_pnl = Column(Float, default=0.0)
    leverage = Column(Integer, default=1)
    status = Column(String, default="open")
    opened_at = Column(DateTime, default=datetime.utcnow)
    closed_at = Column(DateTime, nullable=True)


class RiskEventDB(Base):
    __tablename__ = "risk_events"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    event_type = Column(String)
    severity = Column(String)
    message = Column(Text)
    meta = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


Base.metadata.create_all(bind=engine)


class Side(str, Enum):
    LONG = "LONG"
    SHORT = "SHORT"
    BUY = "BUY"
    SELL = "SELL"


class CircuitBreakerState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class CircuitBreaker:
    name: str
    failure_threshold: int = 5
    recovery_timeout: int = 60
    state: CircuitBreakerState = CircuitBreakerState.CLOSED
    failure_count: int = 0
    last_failure: Optional[datetime] = None

    def allow_request(self) -> bool:
        if self.state == CircuitBreakerState.CLOSED:
            return True
        if self.state == CircuitBreakerState.OPEN:
            if self.last_failure and (datetime.utcnow() - self.last_failure).total_seconds() > self.recovery_timeout:
                self.state = CircuitBreakerState.HALF_OPEN
                return True
            return False
        return True

    def record_success(self):
        self.failure_count = 0
        self.state = CircuitBreakerState.CLOSED

    def record_failure(self):
        self.failure_count += 1
        self.last_failure = datetime.utcnow()
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN
            logger.warning(f"Circuit breaker '{self.name}' opened")


@dataclass
class UserRiskState:
    user_id: str
    daily_pnl: float = 0.0
    daily_trades: int = 0
    consecutive_losses: int = 0
    peak_equity: float = 0.0
    current_equity: float = 0.0
    last_reset: str = field(default_factory=lambda: datetime.utcnow().date().isoformat())
    cooldown_until: Optional[datetime] = None


class RiskEngine:
    def __init__(self):
        self.breakers: Dict[str, CircuitBreaker] = {}
        self.user_states: Dict[str, UserRiskState] = {}
        self._load_state()

    def _load_state(self):
        if redis_client is None:
            return
        try:
            raw = redis_client.get("risk_engine_state")
            if raw:
                data = json.loads(raw)
                for uid, s in data.get("user_states", {}).items():
                    self.user_states[uid] = UserRiskState(**s)
        except Exception as exc:
            logger.warning(f"State load failed: {exc}")

    def _persist_state(self):
        if redis_client is None:
            return
        try:
            data = {
                "user_states": {uid: s.__dict__ for uid, s in self.user_states.items()},
            }
            redis_client.set("risk_engine_state", json.dumps(data), ex=3600)
        except Exception as exc:
            logger.warning(f"State persist failed: {exc}")

    def _get_user_state(self, user_id: str) -> UserRiskState:
        today = datetime.utcnow().date().isoformat()
        if user_id not in self.user_states or self.user_states[user_id].last_reset != today:
            self.user_states[user_id] = UserRiskState(user_id=user_id, last_reset=today)
        return self.user_states[user_id]

    def check_daily_loss(self, user_id: str, current_equity: float, initial_equity: float) -> Tuple[bool, str]:
        state = self._get_user_state(user_id)
        state.current_equity = current_equity
        state.peak_equity = max(state.peak_equity, current_equity)
        daily_loss_pct = ((initial_equity - current_equity) / initial_equity) * 100 if initial_equity > 0 else 0
        if daily_loss_pct >= MAX_DAILY_LOSS_PCT:
            return False, f"Daily loss limit reached: {daily_loss_pct:.2f}% >= {MAX_DAILY_LOSS_PCT}%"
        return True, "OK"

    def check_drawdown(self, user_id: str, current_equity: float) -> Tuple[bool, str]:
        state = self._get_user_state(user_id)
        if state.peak_equity <= 0:
            return True, "OK"
        drawdown_pct = ((state.peak_equity - current_equity) / state.peak_equity) * 100
        if drawdown_pct >= MAX_DRAWDOWN_PCT:
            return False, f"Max drawdown exceeded: {drawdown_pct:.2f}% >= {MAX_DRAWDOWN_PCT}%"
        return True, "OK"

    def calculate_position_size(self, equity: float, entry: float, stop_loss: float, risk_pct: float = 1.0) -> float:
        risk_amount = equity * (risk_pct / 100.0)
        sl_distance = abs(entry - stop_loss)
        if sl_distance == 0 or entry == 0:
            return 0.0
        position_value = risk_amount / (sl_distance / entry)
        max_position = equity * (MAX_POSITION_PCT / 100.0)
        return min(position_value, max_position)

    def check_exposure(self, user_id: str, symbol: str, side: str, size: float, mark_price: float) -> Tuple[bool, str]:
        notional = abs(size * mark_price)
        if notional > MAX_EXPOSURE_USD:
            return False, f"Exposure limit exceeded: ${notional:,.2f} > ${MAX_EXPOSURE_USD:,.2f}"
        if redis_client is not None:
            key = f"exposure:{user_id}:{symbol}:{side}"
            try:
                current = float(redis_client.get(key) or 0)
                if current + notional > MAX_EXPOSURE_USD:
                    return False, f"Symbol exposure limit exceeded for {symbol}"
                redis_client.setex(key, 3600, str(current + notional))
            except Exception as exc:
                logger.warning(f"Exposure check failed: {exc}")
        return True, "OK"

    def record_trade(self, user_id: str, pnl: float):
        state = self._get_user_state(user_id)
        state.daily_pnl += pnl
        state.daily_trades += 1
        state.current_equity += pnl
        state.peak_equity = max(state.peak_equity, state.current_equity)
        if pnl < 0:
            state.consecutive_losses += 1
            if state.consecutive_losses >= CIRCUIT_BREAKER_THRESHOLD:
                state.cooldown_until = datetime.utcnow() + timedelta(hours=1)
                logger.warning(f"User {user_id} hit consecutive loss threshold, cooldown activated")
        else:
            state.consecutive_losses = max(0, state.consecutive_losses - 1)
        self._persist_state()

    def is_cooldown_active(self, user_id: str) -> bool:
        state = self._get_user_state(user_id)
        if state.cooldown_until and datetime.utcnow() < state.cooldown_until:
            return True
        if state.cooldown_until and datetime.utcnow() >= state.cooldown_until:
            state.cooldown_until = None
            self._persist_state()
        return False


risk_engine = RiskEngine()
app = FastAPI(title="JARVIS Risk Service", version="1.0.0")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class PositionRequest(BaseModel):
    user_id: str = Field(..., min_length=1)
    exchange: str = Field(..., min_length=1)
    symbol: str = Field(..., min_length=1)
    side: Side
    size: float = Field(..., gt=0)
    entry_price: float = Field(..., gt=0)
    leverage: int = Field(1, ge=1, le=125)
    current_equity: float = Field(..., gt=0)
    initial_equity: float = Field(..., gt=0)
    risk_percent: float = Field(1.0, gt=0, le=100)


class RiskCheckResponse(BaseModel):
    approved: bool
    position_size: float
    max_position: float
    risk_amount: float
    reasons: List[str] = []
    warnings: List[str] = []


@app.get("/health")
def health():
    try:
        redis_client.ping()
        redis_status = "connected"
    except Exception:
        redis_status = "disconnected"
    return {
        "status": "healthy",
        "service": "risk",
        "redis": redis_status,
        "breakers": {k: v.state for k, v in risk_engine.breakers.items()},
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.post("/risk/check-position", response_model=RiskCheckResponse)
def check_position(req: PositionRequest):
    reasons = []
    warnings = []

    if risk_engine.is_cooldown_active(req.user_id):
        reasons.append("User in cooldown period after consecutive losses")

    ok, msg = risk_engine.check_daily_loss(req.user_id, req.current_equity, req.initial_equity)
    if not ok:
        reasons.append(msg)

    ok, msg = risk_engine.check_drawdown(req.user_id, req.current_equity)
    if not ok:
        reasons.append(msg)

    ok, msg = risk_engine.check_exposure(req.user_id, req.symbol, req.side.value, req.size, req.entry_price)
    if not ok:
        reasons.append(msg)

    position_size = risk_engine.calculate_position_size(req.current_equity, req.entry_price, req.entry_price * 0.99, req.risk_percent)
    max_position = req.current_equity * (MAX_POSITION_PCT / 100.0)
    risk_amount = req.current_equity * (req.risk_percent / 100.0)

    if req.size * req.entry_price > max_position:
        warnings.append(f"Position size exceeds {MAX_POSITION_PCT}% of equity")

    approved = len(reasons) == 0
    return RiskCheckResponse(
        approved=approved,
        position_size=round(position_size, 8),
        max_position=round(max_position, 2),
        risk_amount=round(risk_amount, 2),
        reasons=reasons,
        warnings=warnings,
    )


@app.post("/risk/record-pnl")
def record_pnl(user_id: str = Header(..., alias="X-User-ID"), pnl: float = Header(..., alias="X-PnL")):
    risk_engine.record_trade(user_id, pnl)
    return {"status": "recorded", "user_id": user_id, "pnl": pnl}


@app.get("/risk/state/{user_id}")
def get_user_risk_state(user_id: str):
    state = risk_engine._get_user_state(user_id)
    return {
        "user_id": state.user_id,
        "daily_pnl": state.daily_pnl,
        "daily_trades": state.daily_trades,
        "consecutive_losses": state.consecutive_losses,
        "peak_equity": state.peak_equity,
        "current_equity": state.current_equity,
        "cooldown_active": risk_engine.is_cooldown_active(user_id),
    }


@app.post("/risk/breaker/{breaker_name}/reset")
def reset_breaker(breaker_name: str):
    if breaker_name in risk_engine.breakers:
        risk_engine.breakers[breaker_name].record_success()
        return {"status": "reset", "breaker": breaker_name}
    risk_engine.breakers[breaker_name] = CircuitBreaker(name=breaker_name)
    return {"status": "created", "breaker": breaker_name}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000, log_level="info")
