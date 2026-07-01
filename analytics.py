import os
import json
from datetime import datetime
from typing import Dict, Any, Optional

class AnalyticsHook:
    def __init__(self):
        self.events: list = []
    
    def track(self, event: str, data: Dict[str, Any] = None):
        entry = {
            "event": event,
            "data": data or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        self.events.append(entry)
        return entry
    
    def get_events(self, limit: int = 100) -> list:
        return self.events[-limit:]

analytics = AnalyticsHook()

def on_trade_executed(trade: Dict[str, Any]):
    return analytics.track("trade_executed", trade)

def on_signal_generated(pair: str, signal: str):
    return analytics.track("signal_generated", {"pair": pair, "signal": signal})

def on_consciousness_evolve(old_state: Dict, new_state: Dict):
    return analytics.track("consciousness_evolve", {"from": old_state, "to": new_state})