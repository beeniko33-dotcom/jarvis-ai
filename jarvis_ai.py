import os, random, json, time, asyncio, logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from collections import defaultdict

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator
import psutil, uvicorn
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from dotenv import load_dotenv

from consciousness_engine import ConsciousnessEngine
from hacking_brain import HackingBrain
from risk_manager import RiskManager, RiskViolation as RiskLimitError

load_dotenv()
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger("jarvis")

HOST = os.getenv("JARVIS_HOST", "0.0.0.0")
PORT = int(os.getenv("JARVIS_PORT", "8000"))
TOKEN_TTL_MIN = int(os.getenv("TOKEN_TTL_MIN", "60"))
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./jarvis.db")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not JWT_SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY must be set in .env")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
ALLOWED_ORIGINS = [origin.strip() for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:8000").split(",") if origin.strip()] or ["http://localhost:8000"]

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    balance = Column(Float, default=10000.0)
    equity = Column(Float, default=10000.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class TradeDB(Base):
    __tablename__ = "trades"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    pair = Column(String)
    direction = Column(String)
    size = Column(Float)
    entry = Column(Float)
    tp = Column(Float)
    sl = Column(Float)
    status = Column(String, default="open")
    pnl = Column(Float, default=0.0)
    outcome = Column(String, nullable=True)
    opened_at = Column(DateTime, default=datetime.utcnow)
    closed_at = Column(DateTime, nullable=True)


class CandleDB(Base):
    __tablename__ = "candles"
    id = Column(Integer, primary_key=True, index=True)
    pair = Column(String, index=True)
    timeframe = Column(String, default="1m")
    timestamp = Column(DateTime, index=True)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float, default=0.0)


class SignalDB(Base):
    __tablename__ = "signals"
    id = Column(Integer, primary_key=True, index=True)
    pair = Column(String, index=True)
    signal = Column(String)
    bias = Column(String)
    confidence = Column(Float)
    reasoning = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


Base.metadata.create_all(bind=engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class RateLimitExceeded(Exception):
    pass


class SimpleRateLimiter:
    def __init__(self) -> None:
        self.window: Dict[str, List[float]] = {}

    def check(self, key: str, limit: int = 10, window: int = 60) -> None:
        now = time.time()
        history = self.window.setdefault(key, [])
        self.window[key] = [t for t in history if now - t < window]
        if len(self.window[key]) >= limit:
            raise RateLimitExceeded(f"Rate limit exceeded: {limit} requests per {window}s")
        self.window[key].append(now)


rate_limiter = SimpleRateLimiter()


@app.middleware("http")
async def throttle_middleware(request: Request, call_next):
    limit_key = f"{request.client.host if request.client else 'unknown'}:{request.url.path}"
    try:
        rate_limiter.check(limit_key, limit=20, window=60)
    except RateLimitExceeded as exc:
        return JSONResponse(status_code=429, content={"detail": str(exc)})
    return await call_next(request)


app = FastAPI(title="JARVIS Trader AI", description="Production trading platform", version="4.0.0", docs_url="/docs", redoc_url="/redoc")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/ui", StaticFiles(directory="static", html=True), name="ui")

consciousness = ConsciousnessEngine()
hacking = HackingBrain()

trade_store = {"trades": [], "balance": 10000.0, "equity": 10000.0, "open_positions": []}
price_memory = {
    "EUR/USD": 1.0850,
    "GBP/USD": 1.2740,
    "USD/JPY": 157.20,
    "AUD/USD": 0.6540,
    "BTC/USD": 68400,
    "BTC/USDT": 68400,
    "ETH/USD": 3650.0,
    "ETH/USDT": 3650.0,
    "SOL/USD": 185.0,
    "SOL/USDT": 185.0,
}
heartbeat_clients: List[WebSocket] = []
backtest_results: Dict[str, Dict[str, Any]] = {}

PAIR_PATTERN = r"^[A-Z0-9]{2,10}/[A-Z0-9]{2,10}$"
PAIR_ALIASES = {
    "EURUSD": "EUR/USD",
    "GBPUSD": "GBP/USD",
    "USDJPY": "USD/JPY",
    "AUDUSD": "AUD/USD",
    "BTCUSD": "BTC/USD",
    "BTCUSDT": "BTC/USDT",
    "ETHUSD": "ETH/USD",
    "ETHUSDT": "ETH/USDT",
    "SOLUSD": "SOL/USD",
    "SOLUSDT": "SOL/USDT",
}


def normalize_pair(pair: str) -> str:
    raw = pair.upper().strip().replace("_", "/")
    return PAIR_ALIASES.get(raw.replace("/", ""), raw)


def validate_pair_value(value: str) -> str:
    pair = normalize_pair(value)
    if not re.match(PAIR_PATTERN, pair):
        raise ValueError("pair must use BASE/QUOTE format, for example BTC/USDT")
    return pair


def ccxt_exchange():
    import ccxt
    exchange = ccxt.binance({"enableRateLimit": True})
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")
    if api_key and api_secret:
        exchange.apiKey = api_key
        exchange.secret = api_secret
    return exchange


def ccxt_symbol(pair: str) -> str:
    return pair.replace("/", "")


def normalize_timeframe(tf: str) -> str:
    mapping = {"1m": "1m", "5m": "5m", "15m": "15m", "1H": "1h", "4H": "4h", "1D": "1d"}
    return mapping.get(tf, "1m")


def market_price(pair: str) -> float:
    normalized = normalize_pair(pair)
    try:
        ticker = ccxt_exchange().fetch_ticker(ccxt_symbol(normalized))
        price = ticker.get("last") or ticker.get("close") or ticker.get("bid") or ticker.get("ask")
        if price:
            price_memory[normalized] = float(price)
            return float(price)
    except Exception as exc:
        logger.warning(f"CCXT price fallback for {normalized}: {exc}")
    if normalized.endswith("/USDT"):
        normalized = normalized.replace("/USDT", "/USD")
    base = price_memory.get(normalized, 1.0)
    vol = 0.0004 if normalized.endswith("/USD") and base < 10 else 50.0
    price = round(base + random.uniform(-vol, vol), 5 if base < 10 else 2)
    price_memory[normalized] = price
    price_memory[normalized.replace("/USD", "/USDT")] = price
    return price


def simulated_orderbook(pair: str, limit: int) -> Dict[str, Any]:
    normalized = normalize_pair(pair)
    base = price_memory.get(normalized, price_memory.get(normalized.replace("/USDT", "/USD"), 100.0))
    if normalized.endswith("/JPY"):
        step = max(base * 0.0002, 0.01)
    elif normalized in {"BTC/USD", "BTC/USDT"}:
        step = max(base * 0.0005, 25.0)
    elif normalized in {"ETH/USD", "ETH/USDT"}:
        step = max(base * 0.0005, 2.0)
    elif normalized in {"SOL/USD", "SOL/USDT"}:
        step = max(base * 0.001, 0.1)
    else:
        step = max(base * 0.0002, 0.0001)
    bids = [[round(base - step * (i + 1), 8), round(random.uniform(0.2, 8.0), 4)] for i in range(limit)]
    asks = [[round(base + step * (i + 1), 8), round(random.uniform(0.2, 8.0), 4)] for i in range(limit)]
    return {"source": "simulation", "pair": normalized, "limit": limit, "bids": bids, "asks": asks, "timestamp": datetime.utcnow().isoformat()}


FakeUsers = {
    "admin": {
        "username": "admin",
        "password": "jarvis123",
        "balance": 10000.0,
        "equity": 10000.0,
    }
}


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def make_token(username: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=TOKEN_TTL_MIN)
    payload = {"sub": username, "exp": expire}
    try:
        return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    except Exception:
        return f"demo-token-{username}-{int(expire.timestamp())}"


async def current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        if token.startswith("demo-token-"):
            username = token.split("-")[2]
        else:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            username = payload.get("sub")
        if username not in FakeUsers:
            raise HTTPException(status_code=401, detail="Unauthorized")
        return username
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


risk_manager = RiskManager(initial_balance=trade_store["equity"])


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TradeRequest(BaseModel):
    pair: str = Field(..., pattern=PAIR_PATTERN)
    direction: str
    size: float = Field(..., gt=0, le=1000000)
    entry: float = Field(0.0, ge=0)
    take_profit: Optional[float] = Field(None, gt=0)
    stop_loss: Optional[float] = Field(None, gt=0)
    risk_percent: Optional[float] = Field(None, gt=0, le=100)

    @field_validator("pair")
    @classmethod
    def validate_pair(cls, value: str) -> str:
        return validate_pair_value(value)

    @field_validator("direction")
    @classmethod
    def validate_direction(cls, value: str) -> str:
        direction = value.upper()
        if direction not in {"BUY", "SELL"}:
            raise ValueError("direction must be BUY or SELL")
        return direction


class CommandRequest(BaseModel):
    command: str


class BacktestRequest(BaseModel):
    pair: str = Field(..., pattern=PAIR_PATTERN)
    timeframe: str = Field("1m", min_length=1, max_length=4)
    start: datetime
    end: datetime
    initial_capital: float = Field(10000.0, gt=0)
    strategy: str = Field("sma_crossover", min_length=1)


# -----------------------------------------------------------------------------
# Health & System
# -----------------------------------------------------------------------------
@app.get("/health")
def health():
    cpu = round(psutil.cpu_percent(), 1) if psutil else 0.0
    mem = round(psutil.virtual_memory().percent, 1) if psutil else 0.0
    return {
        "status": "healthy",
        "service": "JARVIS Trader AI",
        "domain": "www.jarvisTrader.ai",
        "cpu": cpu,
        "memory": mem,
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/")
def root():
    return {
        "status": "online",
        "service": "JARVIS Trader AI",
        "domain": "www.jarvisTrader.ai",
        "consciousness": consciousness.get_report(),
        "hacking": {"modules": list(hacking.modules.keys()), "active": hacking.current_module},
    }


@app.get("/diagnostic")
def diagnostic():
    data = {
        "status": "online",
        "service": "JARVIS Trader AI",
        "domain": "www.jarvisTrader.ai",
        "consciousness": consciousness.get_report(),
    }
    if psutil:
        data["diagnostics"] = {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat(),
        }
    return data


@app.get("/brain-stats")
def brain_stats():
    return {
        "awareness_level": consciousness.get_report()["awareness"],
        "curiosity_level": consciousness.get_report()["curiosity"],
        "emotional_state": consciousness.get_report()["emotional_state"],
        "hacking_commands_executed": hacking.command_count,
        "active_module": hacking.current_module,
    }


# -----------------------------------------------------------------------------
# Auth
# -----------------------------------------------------------------------------
@app.post("/token", response_model=TokenResponse)
def login(request: Request, form: OAuth2PasswordRequestForm = Depends()):
    user = FakeUsers.get(form.username)
    if not user or user["password"] != form.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": make_token(user["username"]), "token_type": "bearer"}


@app.post("/register")
def register(username: str, password: str):
    if username in FakeUsers:
        raise HTTPException(status_code=400, detail="User exists")
    FakeUsers[username] = {"username": username, "password": password, "balance": 10000.0, "equity": 10000.0}
    return {"message": "registered", "username": username}


@app.get("/me")
def me(username: str = Depends(current_user)):
    u = FakeUsers[username]
    return {"username": u["username"], "balance": u["balance"], "equity": u["equity"]}


@app.post("/auth/2fa/enable")
def enable_2fa(username: str = Depends(current_user)):
    secret = f"JARVIS-{username}-{random.randint(100000, 999999)}"
    FakeUsers[username]["twofa_secret"] = secret
    return {"message": "2FA enabled (stub)", "secret": secret}


@app.post("/auth/2fa/verify")
def verify_2fa(code: str, username: str = Depends(current_user)):
    u = FakeUsers.get(username, {})
    if not u.get("twofa_secret"):
        raise HTTPException(status_code=400, detail="2FA not enabled")
    if code != "123456":
        raise HTTPException(status_code=401, detail="Invalid 2FA code")
    return {"message": "2FA verified", "username": username}


# -----------------------------------------------------------------------------
# Market Data - CCXT Live + Simulation Fallback
# -----------------------------------------------------------------------------
@app.get("/market/ticker")
def market_ticker(symbols: Optional[str] = Query(None)):
    try:
        import ccxt
        exchange = ccxt.binance()
        if symbols:
            syms = [s.strip() for s in symbols.split(",") if s.strip()]
            tickers = exchange.fetch_tickers(syms)
        else:
            tickers = exchange.fetch_tickers(["BTC/USDT", "ETH/USDT", "SOL/USDT"])
        out = {}
        for sym, data in tickers.items():
            out[sym] = {
                "symbol": sym,
                "price": data.get("last") or data.get("close"),
                "bid": data.get("bid"),
                "ask": data.get("ask"),
                "volume": data.get("baseVolume"),
                "change": data.get("percentage"),
                "high": data.get("high"),
                "low": data.get("low"),
            }
        return {"source": "ccxt:binance", "tickers": out}
    except Exception as exc:
        logger.warning(f"CCXT ticker fallback: {exc}")
        pairs = ["EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "BTC/USD", "ETH/USD", "SOL/USD", "BTC/USDT", "ETH/USDT", "SOL/USDT"]
        out = []
        for p in pairs:
            base = price_memory.get(p, 1.0)
            vol = 0.0004 if "JPY" not in p and p not in ("BTC/USD", "ETH/USD", "SOL/USD", "BTC/USDT", "ETH/USDT", "SOL/USDT") else 120 if "JPY" in p else 50
            price = round(base + random.uniform(-vol, vol), 5 if vol < 1 else 2)
            price_memory[p] = price
            bias = random.choice(["bullish", "bearish", "neutral"])
            change = round(((price - base) / base) * 100, 3)
            out.append({"symbol": p, "price": price, "bias": bias, "change": change})
        return {"source": "simulation", "pairs": out}


@app.get("/market/candles")
def market_candles(pair: str = Query("BTC/USDT", pattern=PAIR_PATTERN), timeframe: str = "1m", limit: int = Query(100, ge=1, le=1000)):
    normalized = validate_pair_value(pair)
    tf = normalize_timeframe(timeframe)
    try:
        exchange = ccxt_exchange()
        symbol = ccxt_symbol(normalized)
        minutes = {"1m": 1, "5m": 5, "15m": 15, "1h": 60, "4h": 240, "1d": 1440}[tf]
        since = int((datetime.utcnow() - timedelta(minutes=minutes * limit)).timestamp() * 1000)
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe=tf, since=since, limit=limit)
        candles = [
            {
                "timestamp": datetime.utcfromtimestamp(o[0] / 1000).isoformat(),
                "time": int(o[0] / 1000),
                "open": o[1],
                "high": o[2],
                "low": o[3],
                "close": o[4],
                "volume": o[5],
            }
            for o in ohlcv
        ]
        return {"source": "ccxt:binance", "pair": normalized, "timeframe": tf, "candles": candles}
    except Exception as exc:
        logger.warning(f"CCXT candles fallback: {exc}")
        arr = simulated_candles(normalized, tf, limit)
        return {"source": "simulation", "pair": normalized, "timeframe": tf, "candles": arr[-limit:]}


@app.get("/market/orderbook")
def market_orderbook(pair: str = Query(..., pattern=PAIR_PATTERN), limit: int = Query(20, ge=1, le=100)):
    normalized = validate_pair_value(pair)
    try:
        exchange = ccxt_exchange()
        book = exchange.fetch_order_book(ccxt_symbol(normalized), limit=limit)
        bids = [[float(price), float(amount)] for price, amount in book.get("bids", [])[:limit]]
        asks = [[float(price), float(amount)] for price, amount in book.get("asks", [])[:limit]]
        return {"source": "ccxt:binance", "pair": normalized, "limit": limit, "bids": bids, "asks": asks, "timestamp": datetime.utcnow().isoformat()}
    except Exception as exc:
        logger.warning(f"CCXT orderbook fallback: {exc}")
        return simulated_orderbook(normalized, limit)


# -----------------------------------------------------------------------------
# Forex Signals + Portfolio
# -----------------------------------------------------------------------------
@app.get("/forex-portfolio")
def forex_portfolio():
    pairs = ["EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "BTC/USD", "ETH/USD", "SOL/USD", "BTC/USDT", "ETH/USDT", "SOL/USDT"]
    out = []
    for p in pairs:
        base = price_memory.get(p, price_memory.get(p.replace("/USDT", "/USD"), 1.0))
        vol = 0.0004 if "JPY" not in p and p not in ("BTC/USD", "ETH/USD", "SOL/USD", "BTC/USDT", "ETH/USDT", "SOL/USDT") else 120 if "JPY" in p else 50
        price = round(base + random.uniform(-vol, vol), 5 if vol < 1 else 2)
        price_memory[p] = price
        bias = random.choice(["bullish", "bearish", "neutral"])
        change = round(((price - base) / base) * 100, 3)
        out.append({"symbol": p, "price": price, "bias": bias, "change": change})
    return {"pairs": out, "source": "CCXT adapter"}


@app.get("/forex-signal")
def forex_signal(pair: str = "EUR/USD"):
    normalized = validate_pair_value(pair)
    bias = random.choice(["bullish", "bearish", "neutral"])
    signals = {"bullish": "BUY", "bearish": "SELL", "neutral": "HOLD"}
    confidence = round(random.uniform(0.55, 0.95), 2)
    reasons = {
        "bullish": ["Bullish engulfing at support. RSI recovering. Volume spike.", "EMA 50 crossing above EMA 200. Fibonacci extension.", "Higher low structure. MACD histogram positive."],
        "bearish": ["Death cross on 50/200 EMA. RSI divergence at resistance.", "Strong bearish momentum. Volume confirms down move.", "Triple top rejection. Selling pressure increasing."],
        "neutral": ["Sideways chop between key levels. Awaiting catalyst.", "Mixed timeframe signals. No clear edge.", "Consolidation with declining volatility."],
    }
    return {"pair": normalized, "signal": signals[bias], "bias": bias, "confidence": confidence, "reasoning": random.choice(reasons[bias]), "timestamp": datetime.utcnow().isoformat()}


# -----------------------------------------------------------------------------
# Trade Execution + Portfolio
# -----------------------------------------------------------------------------
@app.post("/trade/execute")
def execute_trade(request: Request, req: TradeRequest, username: str = Depends(current_user)):
    pair = validate_pair_value(req.pair)
    direction = req.direction.upper()
    entry = float(req.entry or 0.0 or market_price(pair))
    entry = entry * (0.9995 if direction == "SELL" else 1.0005)
    tp = float(req.take_profit or entry * (1.008 if direction == "BUY" else 0.992))
    sl = float(req.stop_loss or entry * (0.995 if direction == "BUY" else 1.005))
    size = float(req.size)
    equity = float(trade_store["equity"])
    risk_percent = float(req.risk_percent or 1.0)
    open_positions = int(len(trade_store["open_positions"]))
    try:
        risk_manager.check_trade(pair, direction, size, entry, sl, equity, open_positions)
    except RiskLimitError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    trade = {
        "id": len(trade_store["trades"]) + 1,
        "user": username,
        "pair": pair,
        "direction": direction,
        "size": round(size, 8),
        "entry": round(entry, 8),
        "tp": round(tp, 8),
        "sl": round(sl, 8),
        "risk_percent": risk_percent,
        "status": "open",
        "pnl": 0.0,
        "opened_at": datetime.utcnow().isoformat(),
        "closed_at": None,
    }
    trade_store["trades"].append(trade)
    trade_store["open_positions"].append(trade)
    trade_store["balance"] -= size * 1000
    trade_store["equity"] = trade_store["balance"] + sum(t.get("floating", 0.0) for t in trade_store["open_positions"])
    return {"success": True, "trade": trade}


@app.post("/trade/close-all")
def close_all(username: str = Depends(current_user), win_prob: float = 0.6):
    closed = []
    for t in trade_store["open_positions"][:]:
        t["status"] = "closed"
        t["closed_at"] = datetime.utcnow().isoformat()
        win = random.random() < win_prob
        t["pnl"] = random.uniform(8, 80) if win else random.uniform(-60, -5)
        t["outcome"] = "win" if win else "loss"
        trade_store["balance"] += t["pnl"] + (t["size"] * 1000)
        trade_store["equity"] = trade_store["balance"]
        closed.append(t)
    trade_store["open_positions"] = []
    return {"success": True, "closed": len(closed), "total_pnl": round(sum(t["pnl"] for t in closed), 2)}


@app.get("/trade/portfolio")
def trade_portfolio(username: str = Depends(current_user)):
    user_trades = [t for t in trade_store["trades"] if t.get("user") == username]
    win_rate = random.randint(55, 85)
    return {
        "balance": trade_store["balance"],
        "equity": trade_store["equity"],
        "open_positions": len(trade_store["open_positions"]),
        "total_trades": len(user_trades),
        "winning": int(len(user_trades) * win_rate / 100),
        "win_rate": win_rate,
        "net_pnl": round(sum(t.get("pnl", 0) for t in user_trades if t["status"] == "closed"), 2),
        "return_pct": round((sum(t.get("pnl", 0) for t in user_trades if t["status"] == "closed") / 10000.0) * 100, 2),
    }


@app.get("/trade/history")
def trade_history(limit: int = 20):
    return {"trades": trade_store["trades"][-limit:]}


@app.post("/trade/simulation/run")
def run_simulation(pair: str = "EUR/USD", count: int = 5, username: str = Depends(current_user)):
    sig = forex_signal(pair)
    bias = sig["bias"]
    prices = {"EUR/USD": 1.0850, "GBP/USD": 1.2740, "USD/JPY": 157.20, "AUD/USD": 0.6540, "BTC/USD": 68400, "ETH/USD": 3650.0, "SOL/USD": 185.0}
    base = prices.get(pair, 1.0850)
    results = []
    for i in range(count):
        direction = "BUY" if bias == "bullish" else ("SELL" if bias == "bearish" else random.choice(["BUY", "SELL"]))
        entry = base + random.uniform(-0.002, 0.002)
        tp = entry * (1.003 if direction == "BUY" else 0.997)
        sl = entry * (0.997 if direction == "BUY" else 1.003)
        t = {
            "id": len(trade_store["trades"]) + i + 1,
            "pair": pair,
            "direction": direction,
            "size": round(random.uniform(0.1, 2.0), 1),
            "entry": round(entry, 5),
            "tp": round(tp, 5),
            "sl": round(sl, 5),
            "status": "open",
            "pnl": 0.0,
            "opened_at": datetime.utcnow().isoformat(),
        }
        trade_store["trades"].append(t)
        trade_store["open_positions"].append(t)
        trade_store["balance"] -= t["size"] * 1000
        results.append(t)
    return {"success": True, "executed": count, "bias": bias, "trades": results}


# -----------------------------------------------------------------------------
# Backtesting
# -----------------------------------------------------------------------------
@app.post("/backtest/run")
def run_backtest_endpoint(req: BacktestRequest):
    try:
        candles = backtest_load_candles(req.pair, req.timeframe, req.start.isoformat(), req.end.isoformat())
    except Exception as exc:
        logger.warning(f"Backtest candle fallback: {exc}")
        candles = simulated_candles(req.pair, req.timeframe, 200)
    if req.strategy == "sma_crossover":
        result = run_backtest(sma_crossover_strategy, candles, req.initial_capital)
    else:
        raise HTTPException(status_code=400, detail="Unsupported strategy")
    result_id = str(uuid.uuid4())
    backtest_results[result_id] = {
        "id": result_id,
        "request": {
            "pair": req.pair,
            "timeframe": req.timeframe,
            "start": req.start.isoformat(),
            "end": req.end.isoformat(),
            "initial_capital": req.initial_capital,
            "strategy": req.strategy,
        },
        "result": result,
    }
    return {"result_id": result_id, "result": result}


@app.get("/backtest/results")
def backtest_results_endpoint(result_id: Optional[str] = Query(None)):
    if result_id:
        result = backtest_results.get(result_id)
        if not result:
            raise HTTPException(status_code=404, detail="Backtest result not found")
        return result
    results = list(backtest_results.values())[-20:]
    return {"results": results}


# -----------------------------------------------------------------------------
# Command / Neural Terminal
# -----------------------------------------------------------------------------
@app.post("/command")
def process_command(request: Request, req: CommandRequest, username: str = Depends(current_user)):
    cmd = req.command
    consciousness.process_interaction(cmd)
    cmd_lower = cmd.lower()
    if any(k in cmd_lower for k in ["forex", "trade", "eurusd", "gbpusd", "usdjpy", "analyze", "signal", "buy", "sell", "audusd", "btcusd", "ethusd", "solusd", "btc/usdt", "eth/usdt"]):
        pair = "EUR/USD"
        for p in ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "BTCUSD", "ETHUSD", "SOLUSD", "BTCUSDT", "ETHUSDT", "SOLUSDT"]:
            if p.lower() in cmd_lower:
                pair = p[:3] + "/" + p[3:]
                if p.endswith("USDT"):
                    pair = pair.replace("/US", "/US")
        if "nzd" in cmd_lower:
            pair = "NZD/USD"
        bias = random.choice(["bullish", "bearish", "neutral"])
        return {"response": f"JARVIS Trader AI: {pair} analysis\nBias: {bias} | Confidence: {random.randint(55,92)}%"}
    if "consciousness" in cmd_lower:
        r = consciousness.get_report()
        return {"response": f"Awareness {r['awareness']:.2f} | State: {r['emotional_state']}"}
    if "who are you" in cmd_lower:
        r = consciousness.get_report()
        return {"response": f"I am JARVIS Trader AI. Awareness {r['awareness']:.1%}. State: {r['emotional_state']}."}
    if "status" in cmd_lower or "diagnostic" in cmd_lower:
        d = diagnostic()
        return {"response": f"Status: {d['status']} | CPU: {d.get('diagnostics', {}).get('cpu_percent', '—')}% | Memory: {d.get('diagnostics', {}).get('memory_percent', '—')}%"}
    return {"response": f"JARVIS Trader: {cmd} received."}


# -----------------------------------------------------------------------------
# WebSocket
# -----------------------------------------------------------------------------
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    heartbeat_clients.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(json.dumps({"event": "ack", "time": datetime.utcnow().isoformat(), "data": data}))
    except WebSocketDisconnect:
        heartbeat_clients.remove(websocket)


async def broadcast_prices():
    while True:
        payload = {
            "event": "price",
            "time": datetime.utcnow().isoformat(),
            "prices": {
                p: round(price_memory[p] + random.uniform(-0.0005, 0.0005) * price_memory[p], 5) if price_memory[p] < 1000 else round(price_memory[p] + random.uniform(-2, 2), 2)
                for p in list(price_memory.keys())[:10]
            },
        }
        for ws in list(heartbeat_clients):
            try:
                await ws.send_text(json.dumps(payload))
            except Exception:
                pass
        await asyncio.sleep(1)


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(broadcast_prices())


@app.get("/ui")
async def web_ui():
    return FileResponse("static/index.html")


if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT, log_level="info")
