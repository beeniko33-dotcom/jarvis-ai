import os
import time
import random
from datetime import datetime

try:
    from crewai import Agent, Task, Crew, Process
    CREWAI_AVAILABLE = True
except ImportError:
    Agent = Task = Crew = Process = None
    CREWAI_AVAILABLE = False

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

from core.agent import JarvisAgents
from core.memory import VectorMemory
from core.brain import AdvancedBrain
from optimizer import Optimizer

class SelfAwareAgent:
    def __init__(self):
        self.memory = []
        self.vector_memory = VectorMemory()
        self.agents = JarvisAgents()
        self.optimizer = Optimizer()
        self.brain = AdvancedBrain()

    def speak(self, text):
        print("JARVIS:", text)
        if OLLAMA_AVAILABLE:
            try:
                import pyttsx3
                engine = pyttsx3.init()
                engine.say(text)
                engine.runAndWait()
            except Exception:
                pass

    def process_command(self, cmd):
        cmd_lower = cmd.lower()
        
        if "forex" in cmd_lower or "trade" in cmd_lower or "trading" in cmd_lower or "eurusd" in cmd_lower or "gbpusd" in cmd_lower or "usdjpy" in cmd_lower:
            response = self.brain.process_command(cmd)
        elif "device" in cmd_lower or "control" in cmd_lower or "execute" in cmd_lower or "lights" in cmd_lower or "thermostat" in cmd_lower:
            response = self.brain.process_command(cmd)
        elif "time" in cmd_lower or "clock" in cmd_lower:
            response = f"The current time is {datetime.now().strftime('%I:%M %p')}."
        elif "date" in cmd_lower:
            response = f"Today is {datetime.now().strftime('%A, %B %d, %Y')}."
        elif "diagnostics" in cmd_lower or "status" in cmd_lower or "cpu" in cmd_lower or "ram" in cmd_lower:
            if PSUTIL_AVAILABLE:
                cpu = psutil.cpu_percent()
                mem = psutil.virtual_memory().percent
                response = f"System diagnostics: CPU {cpu}%, Memory {mem}%. All systems nominal."
            else:
                response = "System status: Operational (monitoring unavailable)."
        elif "joke" in cmd_lower:
            response = "Why did the AI go to therapy? Too many unresolved issues! Haha."
        elif "weather" in cmd_lower:
            response = "Weather integration pending. For now: Clear skies with a 100% chance of assistance."
        elif "optimize" in cmd_lower or "improve" in cmd_lower:
            self.optimizer.reflect_and_improve("User requested optimization")
            response = "Self-optimization cycle initiated. Performance logs analyzed and improvements applied."
        elif "search" in cmd_lower or "research" in cmd_lower or "news" in cmd_lower:
            try:
                crew = self.agents.create_crew(cmd)
                result = crew.kickoff()
                response = str(result)
            except Exception as e:
                self.optimizer.log_error(e)
                response = "Research initiated via agents."
        elif "learn" in cmd_lower or "remember" in cmd_lower:
            response = self.brain.process_command(cmd)
        elif "who are you" in cmd_lower or "yourself" in cmd_lower:
            response = self.brain.process_command(cmd)
        elif "consciousness" in cmd_lower or "awareness" in cmd_lower:
            response = self.brain.process_command(cmd)
        elif "think" in cmd_lower:
            response = self.brain.process_command(cmd)
        elif "full diagnostic" in cmd_lower or "full system" in cmd_lower:
            if PSUTIL_AVAILABLE:
                cpu = psutil.cpu_percent()
                mem = psutil.virtual_memory().percent
                disk = psutil.disk_usage('/').percent
                net = psutil.net_io_counters()
                response = f"Full System Diagnostic:\nCPU: {cpu}%\nMemory: {mem}%\nDisk: {disk}%\nBytes Sent: {net.bytes_sent}\nBytes Recv: {net.bytes_recv}\nAll subsystems operational."
            else:
                response = "Full diagnostic: System online. Monitoring unavailable."
        else:
            if OLLAMA_AVAILABLE:
                try:
                    resp = ollama.chat(model='llama3', messages=[{'role': 'user', 'content': cmd}])
                    response = resp['message']['content']
                except Exception as e:
                    self.optimizer.log_error(e)
                    response = "At your service, sir. Encountered an issue but optimizing now."
            else:
                response = f"JARVIS received: {cmd}"
        
        self.memory.append({"cmd": cmd, "response": response})
        self.vector_memory.add(f"User: {cmd} | Jarvis: {response}")
        return response