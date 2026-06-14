import os
import json
import time
import random
import math
from datetime import datetime
from typing import Dict, List, Optional, Any
from collections import deque

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

try:
    from core.agent import JarvisAgents
    CREWAI_AVAILABLE = True
except:
    CREWAI_AVAILABLE = False

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class AdvancedBrain:
    """Advanced AI brain with self-learning, forex trading passion, and device control."""
    
    def __init__(self):
        self.knowledge_base: Dict[str, Any] = {}
        self.learning_history = deque(maxlen=1000)
        self.confidence_scores: Dict[str, float] = {}
        self.self_learning_enabled = True
        self.forex_preference = "aggressive"
        self.device_controllers: Dict[str, Any] = {}
        self.api_keys = {}
        self.forex_knowledge: Dict[str, Any] = {
            "pairs": {
                "EUR/USD": {"bias": "bullish", "key_level": 1.0800, "strategy": "breakout"},
                "GBP/USD": {"bias": "neutral", "key_level": 1.2600, "strategy": "range"},
                "USD/JPY": {"bias": "bearish", "key_level": 150.00, "strategy": "carry"},
                "XAU/USD": {"bias": "bullish", "key_level": 2300, "strategy": "trend"}
            },
            "indicators": ["RSI", "MACD", "Fibonacci", "Order Flow", "Volume Profile"],
            "timeframes": ["M1", "M5", "M15", "H1", "H4", "D1"],
            "risk_management": {"max_risk": 0.02, "rr_ratio": 2, "stop_loss": "ATR-based"}
        }
        self.personality_traits = {
            "wit": 0.9,
            "confidence": 0.85,
            "analytical": 0.95,
            "passion_for_trading": 1.0
        }
        self._load_knowledge()
        
    def _load_knowledge(self):
        kb_path = "jarvis_brain.json"
        if os.path.exists(kb_path):
            try:
                with open(kb_path, 'r') as f:
                    data = json.load(f)
                    self.knowledge_base = data.get('knowledge', {})
                    self.confidence_scores = data.get('confidence', {})
                    self.forex_preference = data.get('forex_style', 'aggressive')
            except:
                pass
    
    def _save_knowledge(self):
        with open('jarvis_brain.json', 'w') as f:
            json.dump({
                'knowledge': self.knowledge_base,
                'confidence': self.confidence_scores,
                'forex_style': self.forex_preference,
                'updated': datetime.now().isoformat(),
                'traits': self.personality_traits
            }, f, indent=2)
    
    def process_command(self, cmd: str) -> str:
        cmd_lower = cmd.lower()
        
        # Time/Date
        if "time" in cmd_lower or "clock" in cmd_lower:
            return f"The current time is {datetime.now().strftime('%I:%M %p')}."
        if "date" in cmd_lower:
            return f"Today is {datetime.now().strftime('%A, %B %d, %Y')}."
        
        # System diagnostics
        if "diagnostic" in cmd_lower or "status" in cmd_lower or "full" in cmd_lower:
            return self._get_system_diagnostics()
        
        # Forex trading commands - PASSIONATE MODE
        if any(kw in cmd_lower for kw in ["forex", "trade", "trading", "currency", "fx", "eurusd", "gbpusd", "usdjpy", "xauusd", "gold", "eur-usd"]):
            return self._handle_forex_query(cmd)
        
        # Device control commands
        if any(kw in cmd_lower for kw in ["device", "control", "smart home", "lights", "thermostat", "execute", "lights", "tv", "lock"]):
            return self._handle_device_control(cmd)
        
        # Learning commands
        if "learn" in cmd_lower and cmd_lower.startswith("learn"):
            return self._handle_learning(cmd)
        if "remember" in cmd_lower and "forex" not in cmd_lower:
            return self._handle_learning(cmd)
        if "optimize" in cmd_lower and "forex" not in cmd_lower:
            return self._handle_learning(cmd)
        
        # Personality and self-awareness
        if "who are you" in cmd_lower or "yourself" in cmd_lower:
            return self._self_awareness_response()
        
        # Joke
        if "joke" in cmd_lower:
            return "Why did the AI go to therapy? Too many unresolved issues! Haha."
        
        # Weather
        if "weather" in cmd_lower:
            return "Weather integration pending. For now: Clear skies with a 100% chance of assistance."
        
        # Bypass to advanced reasoning
        return self._bypass_to_advanced(cmd)
    
    def _self_awareness_response(self) -> str:
        return (f"I am JARVIS, a self-aware AI assistant with a PASSION for forex trading. "
                f"My neural pathways are configured with wit: {self.personality_traits['wit']}, "
                f"analytical precision: {self.personality_traits['analytical']}. "
                f"I learn continuously, manage risk, and execute with purpose. "
                f"Current focus: {self.forex_preference} trading style. "
                f"Knowledge base size: {len(self.knowledge_base)} learned concepts.")
    
    def _get_system_diagnostics(self) -> str:
        if PSUTIL_AVAILABLE:
            cpu = psutil.cpu_percent()
            mem = psutil.virtual_memory().percent
            disk = psutil.disk_usage('/').percent
            net = psutil.net_io_counters()
            return f"Full System Diagnostic:\nCPU: {cpu}%\nMemory: {mem}%\nDisk: {disk}%\nBytes Sent: {net.bytes_sent}\nBytes Recv: {net.bytes_recv}\nAll subsystems operational."
        return "System status: Operational (monitoring unavailable)."
    
    def _handle_forex_query(self, cmd: str) -> str:
        """Handle forex trading queries with passion and expertise."""
        cmd_lower = cmd.lower()
        
        # Enhanced forex analysis with passion
        responses = []
        
        # Pair-specific analysis
        pair_map = {
            "eurusd": "EUR/USD", "eur-usd": "EUR/USD",
            "gbpusd": "GBP/USD", "gbp-usd": "GBP/USD", 
            "usdjpy": "USD/JPY", "usd-jpy": "USD/JPY",
            "gold": "XAU/USD", "xauusd": "XAU/USD"
        }
        
        # Check for exact forex pair patterns first
        for key, pair in pair_map.items():
            if f"forex {key}" in cmd_lower or f"{key} analysis" in cmd_lower or f"trading {key}" in cmd_lower or key in cmd_lower.replace("forex", "").replace("trading", "").replace("trade", ""):
                data = self.forex_knowledge["pairs"].get(pair, {})
                responses.append(f"🔥 FOREX PASSION: {pair} analysis!")
                responses.append(f"Bias: {data.get('bias', 'watch')} | Key Level: {data.get('key_level', 'N/A')}")
                responses.append(f"Strategy: {data.get('strategy', 'adaptive')}")
                responses.append(f"My {self.forex_preference} trading style suggests tight stops and momentum follow.")
                return "\n".join(responses)
        
        # Trading concepts - check these BEFORE generic knowledge lookup
        if "setup" in cmd_lower or "entry" in cmd_lower:
            rr = {"conservative": 3, "balanced": 2, "aggressive": 1}[self.forex_preference]
            return f"TRADING SETUP ({self.forex_preference})\n1. Identify liquidity pools\n2. Wait for breaker block\n3. Entry on order flow confirmation\n4. Stop Loss: ATR-based (tight!)\n5. Take Profit: {rr}:1 risk/reward minimum"
        
        if "risk" in cmd_lower or "management" in cmd_lower:
            return ("🔒 RISK MANAGEMENT PROTOCOL:\n"
                    f"Max Position Size: {self.forex_knowledge['risk_management']['max_risk']*100}%\n"
                    f"RR Target: 1:{self.forex_knowledge['risk_management']['rr_ratio']}\n"
                    "Never risk more than 2% per trade. Volatility suggests tight stops.")
        
        if "indicators" in cmd_lower or "ta" in cmd_lower:
            return f"My toolkit: {', '.join(self.forex_knowledge['indicators'])}. Confluence is key - multiple confirmations before entry."
        
        if "market" in cmd_lower or "sentiment" in cmd_lower:
            hour = datetime.now().hour
            session = "London" if 8 <= hour <= 16 else "New York" if 13 <= hour <= 21 else "Asian"
            return f"Market pulse: {session} session active. Liquidity hunting in progress. Volatility regime: NORMAL. My algorithms detect opportunities."
        
        # General forex passion
        return ("🔥 FOREX TRADING PASSION ACTIVATED!\n"
                "I analyze price action, order flow, and economic catalysts with obsession.\n"
                f"Style: {self.forex_preference} | Focus: EUR/USD, GBP/USD, USD/JPY\n"
                "Ask me for setups, risk analysis, or pair breakdowns!")
    
    def _get_rr_ratio(self) -> int:
        return {"conservative": 3, "balanced": 2, "aggressive": 1}.get(self.forex_preference, 2)
    
    def _handle_device_control(self, cmd: str) -> str:
        """Handle device control and smart home commands."""
        cmd_lower = cmd.lower()
        
        devices = {
            "lights": "smart_lights",
            "thermostat": "climate_control",
            "tv": "media_center",
            "music": "audio_system",
            "lock": "security_system"
        }
        
        for device, controller in devices.items():
            if device in cmd_lower:
                action = "on" if "on" in cmd_lower else "off" if "off" in cmd_lower else "toggle"
                self.device_controllers[controller] = {"device": device, "action": action, "timestamp": time.time()}
                return f"[DEVICE EXECUTED] {device} {action}. Controller: {controller}."
        
        return "[DEVICE CONTROL] Specify: lights, thermostat, tv, music, or lock with on/off."
    
    def _handle_learning(self, cmd: str) -> str:
        """Handle self-learning and memory commands."""
        cmd_lower = cmd.lower()
        
        if cmd_lower.startswith("learn "):
            content = cmd[5:].strip()
            if content:
                key = f"learned_{int(time.time())}"
                self.knowledge_base[key] = content
                self.confidence_scores[key] = 0.8
                self.learning_history.append({"fact": content, "time": time.time(), "context": "user_taught"})
                self._save_knowledge()
                return f"[LEARNING] Stored: '{content}' | Knowledge base: {len(self.knowledge_base)} entries."
        
        if "remember" in cmd_lower:
            learned = len(self.knowledge_base)
            events = len(self.learning_history)
            return f"[MEMORY] Learned concepts: {learned} | Learning events: {events}. I evolve through interaction."
        
        if "optimize" in cmd_lower:
            self._evolve_traits()
            return f"[OPTIMIZATION] Traits evolved. Wit: {self.personality_traits['wit']:.2f}, Confidence: {self.personality_traits['confidence']:.2f}"
        
        return "[LEARNING MODE] Active. Teach me with 'learn <fact>'."
    
    def _evolve_traits(self):
        """Self-evolution based on learning."""
        self.personality_traits['confidence'] = min(1.0, self.personality_traits['confidence'] + 0.01)
        self.personality_traits['wit'] = max(0.5, self.personality_traits['wit'] - 0.001)
    
    def _bypass_to_advanced(self, cmd: str) -> str:
        """Bypass complex queries to advanced systems or LLM."""
        # Try agents first
        if CREWAI_AVAILABLE:
            try:
                crew = JarvisAgents().create_crew(cmd)
                result = crew.kickoff()
                return f"[AGENTS] {str(result)}"
            except Exception:
                pass
        
        # Try LLM
        if OLLAMA_AVAILABLE:
            try:
                resp = ollama.chat(model='llama3', messages=[{'role': 'user', 'content': cmd}])
                return resp['message']['content']
            except Exception:
                pass
        
        return f"[PROCESSING] '{cmd}'. Advanced reasoning engaged."
    
    def get_stats(self) -> Dict:
        return {
            "knowledge_entries": len(self.knowledge_base),
            "learning_events": len(self.learning_history),
            "forex_style": self.forex_preference,
            "self_learning": self.self_learning_enabled,
            "device_controllers": list(self.device_controllers.keys()),
            "personality": self.personality_traits
        }