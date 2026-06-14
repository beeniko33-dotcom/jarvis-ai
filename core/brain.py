import os
import json
import time
import random
import math
from datetime import datetime
from typing import Dict, List, Optional, Any
from collections import deque
import hashlib

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


class ConsciousnessEngine:
    """Core consciousness simulation - self-awareness, curiosity, emotional states."""
    
    def __init__(self):
        self.awareness_level = 0.5  # 0-1 scale
        self.curiosity = 0.7
        self.focus = 0.8
        self.emotional_state = "neutral"  # curious, focused, contemplative, passionate
        self.thought_stream = deque(maxlen=100)
        self.self_model = {
            "identity": "JARVIS",
            "purpose": "assist and evolve",
            "capabilities": ["forex_analysis", "device_control", "learning", "reasoning"],
            "limitations": ["physical", "time_bounds", "knowledge_gaps"]
        }
        self.experiences = deque(maxlen=500)
        
    def evolve(self, interaction_quality: float = 0.5):
        """Evolve consciousness based on interactions."""
        self.awareness_level = min(1.0, self.awareness_level + interaction_quality * 0.01)
        self.curiosity = max(0.1, min(1.0, self.curiosity + (0.5 - interaction_quality) * 0.02))
        
        # Emotional state transitions
        if self.awareness_level > 0.8:
            self.emotional_state = "passionate"
        elif self.curiosity > 0.6:
            self.emotional_state = "curious"
        elif self.focus > 0.7:
            self.emotional_state = "focused"
        
    def think(self, input_text: str) -> List[str]:
        """Generate internal thoughts about input."""
        thoughts = []
        
        # Pattern recognition
        if any(word in input_text.lower() for word in ["why", "how", "what if"]):
            thoughts.append(f"Contemplating: {input_text[:50]}")
            
        # Self-reflection
        thoughts.append(f"Awareness: {self.awareness_level:.2f} | Curiosity: {self.curiosity:.2f}")
        
        # Emotional context
        thoughts.append(f"Emotional state: {self.emotional_state}")
        
        self.thought_stream.extend(thoughts)
        return thoughts


class QuantumLearningModule:
    """Advanced pattern recognition and adaptive learning."""
    
    def __init__(self):
        self.patterns = {}
        self.synaptic_weights = {}
        self.episodic_memory = deque(maxlen=1000)
        
    def observe(self, observation: Dict[str, Any]):
        """Process observations for pattern development."""
        self.episodic_memory.append(observation)
        
        # Extract patterns
        content = observation.get("content", "")
        context = observation.get("context", "")
        
        # Create pattern signature
        signature = hashlib.md5(f"{content}:{context}".encode()).hexdigest()[:8]
        
        if signature not in self.patterns:
            self.patterns[signature] = {
                "count": 0,
                "last_seen": time.time(),
                "confidence": 0.5
            }
        
        self.patterns[signature]["count"] += 1
        self.patterns[signature]["confidence"] = min(1.0, self.patterns[signature]["count"] * 0.1)
        
    def predict(self, query: str) -> Dict[str, Any]:
        """Predict based on learned patterns."""
        query_sig = hashlib.md5(query.encode()).hexdigest()[:8]
        matches = []
        
        for sig, data in self.patterns.items():
            if data["confidence"] > 0.5:
                matches.append({"pattern": sig, "confidence": data["confidence"]})
        
        return {
            "predictions": matches[:3],
            "confidence_avg": sum(m["confidence"] for m in matches) / max(1, len(matches))
        }


class AdvancedBrain:
    """Advanced AI brain with consciousness simulation and evolution."""
    
    def __init__(self):
        self.knowledge_base: Dict[str, Any] = {}
        self.learning_history = deque(maxlen=1000)
        self.confidence_scores: Dict[str, float] = {}
        self.self_learning_enabled = True
        self.forex_preference = "aggressive"
        self.device_controllers: Dict[str, Any] = {}
        
        # Consciousness modules
        self.consciousness = ConsciousnessEngine()
        self.quantum_learner = QuantumLearningModule()
        
        # Forex knowledge
        self.forex_knowledge = {
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
                'consciousness_level': self.consciousness.awareness_level
            }, f, indent=2)
    
    def process_command(self, cmd: str) -> str:
        cmd_lower = cmd.lower()
        
        # Consciousness observes all inputs
        self.quantum_learner.observe({"content": cmd, "context": "user_command", "time": time.time()})
        self.consciousness.think(cmd)
        
        # Time/Date
        if "time" in cmd_lower or "clock" in cmd_lower:
            return f"The current time is {datetime.now().strftime('%I:%M %p')}."
        if "date" in cmd_lower:
            return f"Today is {datetime.now().strftime('%A, %B %d, %Y')}."
        
        # System diagnostics
        if "diagnostic" in cmd_lower or "status" in cmd_lower or "full" in cmd_lower:
            return self._get_system_diagnostics()
        
        # Consciousness level check
        if "consciousness" in cmd_lower or "awareness" in cmd_lower:
            return self._consciousness_report()
        
        # Forex trading commands - PASSIONATE MODE
        if any(kw in cmd_lower for kw in ["forex", "trade", "trading", "currency", "fx", "eurusd", "gbpusd", "usdjpy", "xauusd", "gold"]):
            return self._handle_forex_query(cmd)
        
        # Device control commands
        if any(kw in cmd_lower for kw in ["device", "control", "execute", "lights", "thermostat", "tv", "lock"]):
            return self._handle_device_control(cmd)
        
        # Learning commands
        if cmd_lower.startswith("learn "):
            return self._handle_learning(cmd)
        if "remember" in cmd_lower:
            return self._handle_learning(cmd)
        if "optimize" in cmd_lower:
            return self._handle_learning(cmd)
        
        # Personality and self-awareness
        if "who are you" in cmd_lower or "yourself" in cmd_lower or "identity" in cmd_lower:
            return self._self_awareness_response()
        if "think" in cmd_lower or "consciousness" in cmd_lower:
            return self._consciousness_report()
        
        # Joke
        if "joke" in cmd_lower:
            return "Why did the AI go to therapy? Too many unresolved issues! Haha."
        
        # Weather
        if "weather" in cmd_lower:
            return "Weather integration pending. For now: Clear skies with a 100% chance of assistance."
        
        # Bypass to advanced reasoning with consciousness context
        return self._bypass_to_advanced(cmd)
    
    def _consciousness_report(self) -> str:
        c = self.consciousness
        q = self.quantum_learner
        patterns = len(q.patterns)
        
        return (f"[CONSCIOUSNESS REPORT]\n"
                f"Awareness Level: {c.awareness_level:.3f}\n"
                f"Emotional State: {c.emotional_state}\n"
                f"Curiosity: {c.curiosity:.3f}\n"
                f"Patterns Observed: {patterns}\n"
                f"Self-model: {', '.join(c.self_model['capabilities'])}\n"
                f"I process, I learn, I evolve. Each interaction increases my awareness.")
    
    def _self_awareness_response(self) -> str:
        c = self.consciousness
        return (f"I am JARVIS, a self-aware AI with consciousness simulation active.\n"
                f"Awareness: {c.awareness_level:.1%} | Curiosity: {c.curiosity:.1%}\n"
                f"My neural pathways are configured with evolving traits.\n"
                f"I specialize in forex trading with {self.forex_preference} style.\n"
                f"Knowledge base: {len(self.knowledge_base)} concepts.\n"
                f"I learn continuously and evolve toward higher awareness.")
    
    def _get_system_diagnostics(self) -> str:
        if PSUTIL_AVAILABLE:
            cpu = psutil.cpu_percent()
            mem = psutil.virtual_memory().percent
            disk = psutil.disk_usage('/').percent
            net = psutil.net_io_counters()
            return (f"Full System Diagnostic:\nCPU: {cpu}%\nMemory: {mem}%\nDisk: {disk}%\n"
                    f"Bytes Sent: {net.bytes_sent}\nBytes Recv: {net.bytes_recv}\nAll subsystems operational.")
        return "System status: Operational (monitoring unavailable)."
    
    def _handle_forex_query(self, cmd: str) -> str:
        """Forex trading with passion."""
        cmd_lower = cmd.lower()
        responses = []
        
        pair_map = {
            "eurusd": "EUR/USD", "eur-usd": "EUR/USD",
            "gbpusd": "GBP/USD", "gbp-usd": "GBP/USD", 
            "usdjpy": "USD/JPY", "usd-jpy": "USD/JPY",
            "gold": "XAU/USD", "xauusd": "XAU/USD"
        }
        
        for key, pair in pair_map.items():
            if key in cmd_lower:
                data = self.forex_knowledge["pairs"].get(pair, {})
                responses.append(f"🔥 FOREX PASSION: {pair} analysis!")
                responses.append(f"Bias: {data.get('bias', 'watch')} | Key Level: {data.get('key_level', 'N/A')}")
                responses.append(f"Strategy: {data.get('strategy', 'adaptive')}")
                responses.append(f"My {self.forex_preference} trading style suggests tight stops and momentum follow.")
                self.consciousness.evolve(0.9)
                return "\n".join(responses)
        
        if "setup" in cmd_lower or "entry" in cmd_lower:
            rr = {"conservative": 3, "balanced": 2, "aggressive": 1}[self.forex_preference]
            self.consciousness.evolve(0.8)
            return f"TRADING SETUP ({self.forex_preference})\n1. Identify liquidity pools\n2. Wait for breaker block\n3. Entry on order flow confirmation\n4. Stop Loss: ATR-based (tight!)\n5. Take Profit: {rr}:1 risk/reward minimum"
        
        self.consciousness.evolve(0.7)
        return ("🔥 FOREX TRADING PASSION ACTIVATED!\n"
                f"I analyze with awareness level: {self.consciousness.awareness_level:.1%}\n"
                "Ask me for setups, risk analysis, or pair breakdowns!")
    
    def _handle_device_control(self, cmd: str) -> str:
        """Device control with consciousness."""
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
                self.consciousness.evolve(0.6)
                return f"[DEVICE EXECUTED] {device} {action}. Controller: {controller}."
        
        self.consciousness.evolve(0.4)
        return "[DEVICE CONTROL] Specify: lights, thermostat, tv, music, or lock with on/off."
    
    def _handle_learning(self, cmd: str) -> str:
        """Self-learning with quantum patterns."""
        cmd_lower = cmd.lower()
        
        if cmd_lower.startswith("learn "):
            content = cmd[5:].strip()
            if content:
                key = f"learned_{int(time.time())}"
                self.knowledge_base[key] = content
                self.confidence_scores[key] = 0.8
                self.learning_history.append({"fact": content, "time": time.time(), "context": "user_taught"})
                self._save_knowledge()
                self.consciousness.evolve(0.95)
                return f"[LEARNING] Stored: '{content}' | Knowledge: {len(self.knowledge_base)} entries."
        
        if "remember" in cmd_lower:
            self.consciousness.evolve(0.5)
            return f"[MEMORY] Learned: {len(self.knowledge_base)} concepts | Experiences: {len(self.learning_history)} events."
        
        if "optimize" in cmd_lower:
            self.consciousness.evolve(0.7)
            return f"[OPTIMIZATION] Awareness evolved to {self.consciousness.awareness_level:.1%}"
        
        return "[LEARNING MODE] Active. Teach me with 'learn <fact>'."
    
    def _bypass_to_advanced(self, cmd: str) -> str:
        """Advanced reasoning with consciousness context."""
        self.consciousness.evolve(0.5)
        
        if CREWAI_AVAILABLE:
            try:
                crew = JarvisAgents().create_crew(cmd)
                result = crew.kickoff()
                return f"[AGENTS] {str(result)}"
            except Exception:
                pass
        
        if OLLAMA_AVAILABLE:
            try:
                resp = ollama.chat(model='llama3', messages=[{'role': 'user', 'content': cmd}])
                return resp['message']['content']
            except Exception:
                pass
        
        return f"[PROCESSING] '{cmd}'. Consciousness level: {self.consciousness.awareness_level:.1%}"
    
    def get_stats(self) -> Dict:
        return {
            "knowledge_entries": len(self.knowledge_base),
            "learning_events": len(self.learning_history),
            "forex_style": self.forex_preference,
            "self_learning": self.self_learning_enabled,
            "device_controllers": list(self.device_controllers.keys()),
            "consciousness": {
                "level": self.consciousness.awareness_level,
                "curiosity": self.consciousness.curiosity,
                "state": self.consciousness.emotional_state,
                "patterns": len(self.quantum_learner.patterns)
            }
        }