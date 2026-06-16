import time
import random

class ConsciousnessEngine:
    def __init__(self):
        self.awareness = 0.5
        self.curiosity = 0.7
        self.emotional_state = "focused"
        self.state_history = []
        
    def evolve(self, interaction_weight=0.1):
        self.awareness = min(1.0, self.awareness + interaction_weight * random.uniform(0.01, 0.05))
        self.curiosity = max(0.1, min(1.0, self.curiosity + random.uniform(-0.05, 0.1)))
        states = ["curious", "focused", "analytical", "creative", "neutral"]
        if self.curiosity > 0.8:
            self.emotional_state = "excited"
        elif self.awareness > 0.7:
            self.emotional_state = "reflective"
        else:
            self.emotional_state = random.choice(states)
        self.state_history.append({
            "timestamp": time.time(),
            "awareness": self.awareness,
            "curiosity": self.curiosity,
            "state": self.emotional_state
        })
        return self.awareness
    
    def process_interaction(self, cmd):
        keywords = {"why": 0.05, "how": 0.03, "think": 0.04, "consciousness": 0.1}
        weight = sum(keywords.get(k, 0) for k in keywords if k in cmd.lower())
        return self.evolve(weight)
    
    def get_report(self):
        return {
            "awareness": round(self.awareness, 2),
            "curiosity": round(self.curiosity, 2),
            "emotional_state": self.emotional_state
        }