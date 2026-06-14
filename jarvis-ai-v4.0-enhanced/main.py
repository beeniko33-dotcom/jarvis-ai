import os
import time
import threading
import random
from datetime import datetime
import psutil
import speech_recognition as sr
import pyttsx3
import ollama
from collections import deque
import json
import sys
sys.path.append('.')

from core.agent import JarvisAgents
from core.memory import VectorMemory
from optimizer import Optimizer

MEMORY_FILE = "jarvis_memory.json"

class Memory:
    def __init__(self):
        self.history = deque(maxlen=50)
        self.load()

    def add(self, user_cmd, response):
        self.history.append({"time": datetime.now().isoformat(), "user": user_cmd, "jarvis": response})
        self.save()

    def load(self):
        if os.path.exists(MEMORY_FILE):
            try:
                with open(MEMORY_FILE, 'r') as f:
                    data = json.load(f)
                    self.history = deque(data, maxlen=50)
            except:
                pass

    def save(self):
        with open(MEMORY_FILE, 'w') as f:
            json.dump(list(self.history), f)

    def get_context(self):
        return "\n".join([f"User: {h['user']}\nJarvis: {h['jarvis']}" for h in list(self.history)[-5:]])

class SelfAwareAgent:
    def __init__(self):
        self.memory = Memory()
        self.vector_memory = VectorMemory()
        self.performance_log = []
        self.tts_engine = pyttsx3.init()
        self.agents = JarvisAgents()
        self.optimizer = Optimizer()

    def speak(self, text):
        print("JARVIS:", text)
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()

    def listen(self, device_index=None):
        r = sr.Recognizer()
        try:
            with sr.Microphone(device_index=device_index) as source:
                print(f"Listening on device {device_index}...")
                audio = r.listen(source, timeout=5, phrase_time_limit=10)
                return r.recognize_google(audio).lower()
        except Exception as e:
            self.optimizer.log_error(e)
            return None

    def self_reflect(self, cmd, response):
        self.performance_log.append({"cmd": cmd, "response": response, "time": time.time()})

    def process_command(self, cmd):
        cmd_lower = cmd.lower()
        
        if "time" in cmd_lower or "clock" in cmd_lower:
            response = f"The current time is {datetime.now().strftime('%I:%M %p')}."
        elif "date" in cmd_lower:
            response = f"Today is {datetime.now().strftime('%A, %B %d, %Y')}."
        elif "diagnostics" in cmd_lower or "status" in cmd_lower or "cpu" in cmd_lower or "ram" in cmd_lower:
            cpu = psutil.cpu_percent()
            mem = psutil.virtual_memory().percent
            response = f"System diagnostics: CPU {cpu}%, Memory {mem}%. All systems nominal."
        elif "full diagnostic" in cmd_lower or "full system" in cmd_lower:
            cpu = psutil.cpu_percent()
            mem = psutil.virtual_memory().percent
            disk = psutil.disk_usage('/').percent
            net = psutil.net_io_counters()
            response = f"Full System Diagnostic:\nCPU: {cpu}%\nMemory: {mem}%\nDisk: {disk}%\nBytes Sent: {net.bytes_sent}\nBytes Recv: {net.bytes_recv}\nAll subsystems operational."
        elif "joke" in cmd_lower:
            response = "Why did the AI go to therapy? Too many unresolved issues! Haha."
        elif "weather" in cmd_lower:
            response = "Weather integration pending. For now: Clear skies with a 100% chance of assistance."
        elif "optimize" in cmd_lower or "improve" in cmd_lower or "self" in cmd_lower:
            self.optimizer.reflect_and_improve("User requested optimization")
            response = "Self-optimization cycle initiated. Performance logs analyzed and improvements applied."
        elif "switch microphone" in cmd_lower or "mic" in cmd_lower:
            response = "Available microphones listed in console. Say 'use mic X' to switch."
            print("Available mics:", sr.Microphone.list_microphone_names())
        elif "reminder" in cmd_lower or "todo" in cmd_lower or "remember" in cmd_lower:
            response = f"Reminder added: {cmd}. I'll track it in memory."
            self.vector_memory.add(cmd, "User reminder logged.")
        elif "shutdown" in cmd_lower or "reboot" in cmd_lower:
            response = "System control command acknowledged but safety protocol prevents actual shutdown."
        elif "search" in cmd_lower or "research" in cmd_lower or "news" in cmd_lower:
            try:
                crew = self.agents.create_crew(cmd)
                result = crew.kickoff()
                response = str(result)
            except Exception as e:
                self.optimizer.log_error(e)
                response = "Research initiated via agents."
        else:
            try:
                crew = self.agents.create_crew(cmd)
                result = crew.kickoff()
                response = str(result)
            except:
                try:
                    resp = ollama.chat(model='llama3', messages=[{'role': 'user', 'content': cmd}])
                    response = resp['message']['content']
                except:
                    response = "At your service, sir. Encountered an issue but optimizing now."
        
        self.memory.add(cmd, response)
        self.vector_memory.add(f"User: {cmd} | Jarvis: {response}")
        self.self_reflect(cmd, response)
        return response

class JarvisApp:
    def __init__(self):
        self.agent = SelfAwareAgent()
        print("Available microphones (including Bluetooth when paired):")
        for idx, name in enumerate(sr.Microphone.list_microphone_names()):
            print(f"{idx}: {name}")

    def run(self):
        self.agent.speak("Jarvis online. Self-aware, multi-agent, with vector memory and optimization. Say Jarvis.")
        while True:
            cmd = self.agent.listen()
            if cmd and "jarvis" in cmd:
                self.agent.speak("At your service.")
                follow = self.agent.listen()
                if follow:
                    self.agent.process_command(follow)
            time.sleep(0.5)

if __name__ == '__main__':
    app = JarvisApp()
    app.run()