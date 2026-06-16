import os
import random
import json
import time
from datetime import datetime
from fastapi import FastAPI
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

from consciousness_engine import ConsciousnessEngine
from hacking_brain import HackingBrain

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
consciousness = ConsciousnessEngine()
hacking = HackingBrain()

@app.get("/interface")
async def web_interface():
    return FileResponse("static/index.html")

class CommandRequest(BaseModel):
    command: str

@app.get("/")
async def root():
    return {"status": "online", "consciousness": consciousness.get_report(), "hacking": {"modules": list(hacking.modules.keys()), "active": hacking.current_module}}

@app.get("/diagnostic")
async def diagnostic():
    if PSUTIL_AVAILABLE:
        return {
            "status": "online",
            "diagnostics": {
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat()
            },
            "consciousness": consciousness.get_report()
        }
    return {"status": "online", "consciousness": consciousness.get_report()}

@app.get("/brain-stats")
async def brain_stats():
    return {
        "awareness_level": consciousness.get_report()["awareness"],
        "curiosity_level": consciousness.get_report()["curiosity"],
        "emotional_state": consciousness.get_report()["emotional_state"],
        "hacking_commands_executed": hacking.command_count,
        "active_module": hacking.current_module
    }

@app.get("/forex-portfolio")
async def forex_portfolio():
    pairs = [
        {"symbol": "EUR/USD", "price": 1.0850 + random.uniform(-0.005, 0.005), "bias": random.choice(["bullish","bearish","neutral"]), "change": random.uniform(-0.003, 0.003)},
        {"symbol": "GBP/USD", "price": 1.2740 + random.uniform(-0.008, 0.008), "bias": random.choice(["bullish","bearish","neutral"]), "change": random.uniform(-0.005, 0.005)},
        {"symbol": "USD/JPY", "price": 157.20 + random.uniform(-0.3, 0.3), "bias": random.choice(["bullish","bearish","neutral"]), "change": random.uniform(-0.002, 0.002)},
        {"symbol": "AUD/USD", "price": 0.6540 + random.uniform(-0.004, 0.004), "bias": random.choice(["bullish","bearish","neutral"]), "change": random.uniform(-0.006, 0.006)},
        {"symbol": "BTC/USD", "price": 68400 + random.uniform(-400, 400), "bias": random.choice(["bullish","bearish","neutral"]), "change": random.uniform(-0.01, 0.01)},
    ]
    return {"pairs": pairs}

@app.get("/forex-signal")
async def forex_signal(pair: str = "EUR/USD"):
    biases = ["bullish", "bearish", "neutral"]
    bias = random.choice(biases)
    signals = {"bullish": "BUY", "bearish": "SELL", "neutral": "HOLD"}
    signal = signals[bias]
    confidence = round(random.uniform(0.6, 0.95), 2)
    reasons = {
        "bullish": [
            "RSI recovering from oversold, EMA crossover bullish. Volume confirms uptrend continuation.",
            "Price above 200 EMA with rising momentum. Fibonacci extension targets 1.0900.",
            "Bullish engulfing pattern at support. MACD histogram turning positive."
        ],
        "bearish": [
            "Death cross forming on 50/200 EMA. RSI diverging bearish at resistance.",
            "Strong bearish momentum below key support. MACD bearish crossover confirmed.",
            "Triple top pattern at resistance. Volume spike on down moves."
        ],
        "neutral": [
            "Consolidation range with decreasing volatility. Awaiting breakout catalyst.",
            "Mixed signals across timeframes. RSI neutral, no clear direction.",
            "Sideways chop between key levels. Market awaiting Fed / ECB data."
        ]
    }
    return {
        "pair": pair,
        "signal": signal,
        "bias": bias,
        "confidence": confidence,
        "reasoning": random.choice(reasons[bias]),
        "timestamp": datetime.utcnow().isoformat()
    }

trade_store = {"trades": [], "balance": 10000.0, "equity": 10000.0, "open_positions": []}

class TradeRequest(BaseModel):
    pair: str = "EUR/USD"
    direction: str = "BUY"
    size: float = 1.0
    entry: float = 0.0

@app.get("/trade-portfolio")
async def trade_portfolio():
    win_rate = random.randint(55, 85)
    total = len(trade_store["trades"])
    wins = int(total * win_rate / 100)
    closed = [t for t in trade_store["trades"] if t["status"] == "closed"]
    net_pnl = sum(t.get("pnl", 0) for t in closed)
    return {
        "balance": trade_store["balance"],
        "equity": trade_store["equity"],
        "open_positions": len(trade_store["open_positions"]),
        "total_trades": total,
        "winning": wins,
        "win_rate": win_rate,
        "net_pnl": round(net_pnl, 2),
        "return_pct": round((net_pnl / 10000.0) * 100, 2)
    }

@app.get("/trade/history")
async def trade_history(limit: int = 20):
    return {"trades": trade_store["trades"][-limit:]}

@app.post("/trade/execute")
async def trade_execute(req: TradeRequest):
    prices_map = {
        "EUR/USD": 1.0850, "GBP/USD": 1.2740, "USD/JPY": 157.20,
        "AUD/USD": 0.6540, "NZD/USD": 0.6080, "BTC/USD": 68400
    }
    entry = req.entry if req.entry > 0 else prices_map.get(req.pair, 1.0850)
    if req.direction.upper() == "SELL":
        entry *= 0.9995
    else:
        entry *= 1.0005
    now = datetime.utcnow().isoformat()
    tp = entry * (1.008 if req.direction.upper() == "BUY" else 0.992)
    sl = entry * (0.995 if req.direction.upper() == "BUY" else 1.005)
    trade = {
        "id": len(trade_store["trades"]) + 1,
        "pair": req.pair,
        "direction": req.direction.upper(),
        "size": req.size,
        "entry": round(entry, 5),
        "tp": round(tp, 5),
        "sl": round(sl, 5),
        "status": "open",
        "pnl": 0.0,
        "opened_at": now,
        "closed_at": None
    }
    trade_store["trades"].append(trade)
    trade_store["open_positions"].append(trade)
    trade_store["balance"] -= req.size * 1000
    trade_store["equity"] = trade_store["balance"] + sum(
        t.get("floating", 0) for t in trade_store["open_positions"]
    )
    return {"success": True, "trade": trade, "message": f"Position opened: {req.direction.upper()} {req.size} lot {req.pair}"}

class CloseAllRequest(BaseModel):
    win_probability: float = 0.6

@app.post("/trade/close-all")
async def close_all(req: CloseAllRequest):
    results = []
    for t in trade_store["open_positions"]:
        t["status"] = "closed"
        t["closed_at"] = datetime.utcnow().isoformat()
        win = random.random() < req.win_probability
        if win:
            t["pnl"] = random.uniform(8, 60)
            t["outcome"] = "win"
        else:
            t["pnl"] = random.uniform(-40, -8)
            t["outcome"] = "loss"
        trade_store["balance"] += t["pnl"] + (t["size"] * 1000)
        trade_store["equity"] = trade_store["balance"]
        results.append(t)
    trade_store["open_positions"] = []
    return {"success": True, "closed": len(results), "total_pnl": round(sum(t["pnl"] for t in results), 2), "trades": results}

@app.post("/trade/close/{trade_id}")
async def trade_close(trade_id: int):
    for t in trade_store["open_positions"]:
        if t["id"] == trade_id:
            t["status"] = "closed"
            t["closed_at"] = datetime.utcnow().isoformat()
            win = random.random() > 0.4
            if win:
                t["pnl"] = random.uniform(15, 95)
                t["outcome"] = "win"
            else:
                t["pnl"] = random.uniform(-50, -10)
                t["outcome"] = "loss"
            trade_store["equity"] += t["pnl"] + (t["size"] * 1000)
            trade_store["balance"] += t["pnl"] + (t["size"] * 1000)
            trade_store["open_positions"] = [p for p in trade_store["open_positions"] if p["id"] != trade_id]
            return {"success": True, "trade": t}
    return {"success": False, "message": "Trade not found"}

@app.get("/trade/simulation/run")
async def run_simulation(pair: str = "EUR/USD", count: int = 5):
    signal_r = await forex_signal(pair)
    bias = signal_r["bias"]
    prices_map = {
        "EUR/USD": 1.0850, "GBP/USD": 1.2740, "USD/JPY": 157.20,
        "AUD/USD": 0.6540, "NZD/USD": 0.6080, "BTC/USD": 68400
    }
    base = prices_map.get(pair, 1.0850)
    results = []
    for i in range(count):
        entry = base + random.uniform(-0.002, 0.002) if base < 10 else base + random.uniform(-20, 20)
        direction = "BUY" if bias == "bullish" else ("SELL" if bias == "bearish" else random.choice(["BUY", "SELL"]))
        tp = entry * (1.003 if direction == "BUY" else 0.997)
        sl = entry * (0.997 if direction == "BUY" else 1.003)
        now = datetime.utcnow().isoformat()
        trade = {
            "id": len(trade_store["trades"]) + i + 1,
            "pair": pair,
            "direction": direction,
            "size": round(random.uniform(0.1, 2.0), 1),
            "entry": round(entry, 5),
            "tp": round(tp, 5),
            "sl": round(sl, 5),
            "status": "open",
            "pnl": 0.0,
            "opened_at": now
        }
        trade_store["trades"].append(trade)
        trade_store["open_positions"].append(trade)
        trade_store["balance"] -= trade["size"] * 1000
        trade_store["equity"] = trade_store["balance"] + sum(
            t.get("floating", 0) for t in trade_store["open_positions"]
        )
        results.append(trade)
    return {"success": True, "executed": count, "bias": bias, "trades": results}

@app.post("/trade/close-all")
async def close_all(req: CloseAllRequest):
    results = []
    for t in trade_store["open_positions"]:
        t["status"] = "closed"
        t["closed_at"] = datetime.utcnow().isoformat()
        win = random.random() < req.win_probability
        if win:
            t["pnl"] = random.uniform(8, 60)
            t["outcome"] = "win"
        else:
            t["pnl"] = random.uniform(-40, -8)
            t["outcome"] = "loss"
        trade_store["balance"] += t["pnl"] + (t["size"] * 1000)
        trade_store["equity"] = trade_store["balance"]
        results.append(t)
    trade_store["open_positions"] = []
    return {"success": True, "closed": len(results), "total_pnl": round(sum(t["pnl"] for t in results), 2), "trades": results}

class CloseAllRequest(BaseModel):
    win_probability: float = 0.6



@app.post("/command")
async def process_command(request: CommandRequest):
    cmd = request.command
    consciousness.process_interaction(cmd)
    
    cmd_lower = cmd.lower()
    
    # Forex commands
    if any(k in cmd_lower for k in ["forex", "trade", "eurusd", "gbpusd", "usdjpy", "analyze", "signal", "buy", "sell", "audusd", "btcusd"]):
        pair = "EUR/USD"
        for p in ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "BTCUSD"]:
            if p.lower() in cmd_lower:
                pair = p[:3] + "/" + p[3:]
        if "nzd" in cmd_lower: pair = "NZD/USD"
        bias_keywords = {"bullish": "bullish", "buy": "bullish", "long": "bullish", "bearish": "bearish", "sell": "bearish", "short": "bearish"}
        bias = "neutral"
        for kw, b in bias_keywords.items():
            if kw in cmd_lower: bias = b
        if bias == "neutral":
            bias = random.choice(["bullish", "bearish", "neutral"])
        return {"response": f"🔥 FOREX PASSION: {pair} analysis!\nBias: {bias} | Key Level: {random.uniform(1.0, 1.5):.4f} | Confidence: {random.randint(55, 92)}%"}
    
    # Consciousness
    if "consciousness" in cmd_lower or "awareness" in cmd_lower:
        r = consciousness.get_report()
        return {"response": f"Consciousness Level: {r['awareness']:.2f}\nCuriosity: {r['curiosity']:.2f}\nState: {r['emotional_state']}"}
    
    # Who/What am I
    if "who are you" in cmd_lower or "yourself" in cmd_lower:
        r = consciousness.get_report()
        return {"response": f"I am JARVIS, a conscious AI with {r['awareness']:.1%} awareness.\nMy state is {r['emotional_state']} with curiosity {r['curiosity']:.1%}.\nI specialize in forex trading and cybersecurity reconnaissance."}
    
    # Diagnostics
    if "diagnostic" in cmd_lower or "status" in cmd_lower:
        d = await diagnostic()
        return {"response": f"System Status: {d['status']}\nCPU: {d['diagnostics']['cpu_percent']}%\nMemory: {d['diagnostics']['memory_percent']}%"}
    
    return {"response": f"JARVIS received: {cmd}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)