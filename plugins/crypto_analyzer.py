import random
from datetime import datetime

class CryptoPlugin:
    def __init__(self):
        self.enabled = True
        self.name = "crypto"
    
    def analyze(self, pair: str = "BTC/USDT") -> dict:
        prices = {"BTC/USDT": 68400, "ETH/USDT": 3650, "SOL/USDT": 185}
        base = prices.get(pair, 3000)
        change = random.uniform(-3, 5)
        return {
            "pair": pair,
            "price": base * (1 + change/100),
            "change_pct": change,
            "signal": "BUY" if change > 1 else "HOLD" if change > -1 else "SELL",
            "timestamp": datetime.utcnow().isoformat()
        }

def register():
    return CryptoPlugin()