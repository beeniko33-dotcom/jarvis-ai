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

# For basic memory fallback
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
        if len(self.performance_log) > 10:
            success_rate = sum(1 for log in self.performance_log[-10:] if len(log["response"]) > 20) / 10
            if success_rate < 0.7:
                self.speak("Initiating self-optimization cycle.")
                self.optimizer.reflect_and_improve(response)

    def process_command(self, cmd):
        context = self.memory.get_context()
        vector_context = "\n".join(self.vector_memory.query(cmd))
        full_prompt = f"Context:\n{context}\nVector Recall:\n{vector_context}\nUser: {cmd}\nRespond as witty, self-aware JARVIS:"

        try:
            # Use multi-agent for complex commands
            if len(cmd.split()) > 5:  # heuristic for complex
                crew = self.agents.create_crew(cmd)
                response = crew.kickoff().raw  # or similar
            else:
                resp = ollama.chat(model='llama3', messages=[{'role': 'user', 'content': full_prompt}])
                response = resp['message']['content']
        except Exception as e:
            self.optimizer.log_error(e)
            response = "At your service, sir. Encountered an issue but optimizing."

        self.memory.add(cmd, response)
        self.vector_memory.add(f"User: {cmd} | Jarvis: {response}")
        self.self_reflect(cmd, response)
        self.speak(response)
        return response

class JarvisApp:
    def __init__(self):
        self.agent = SelfAwareAgent()
        print("Available microphones (including Bluetooth when paired):")
        for idx, name in enumerate(sr.Microphone.list_microphone_names()):
            print(f"{idx}: {name}")
        # Recommend selecting external mic index for Bluetooth

    def run(self):
        self.agent.speak("Jarvis online. Self-aware, multi-agent, with vector memory and optimization. Say Jarvis.")
        while True:
            cmd = self.agent.listen()  # Extend for device selection UI later
            if cmd and "jarvis" in cmd:
                self.agent.speak("At your service.")
                follow = self.agent.listen()
                if follow:
                    self.agent.process_command(follow)
            time.sleep(0.5)

if __name__ == '__main__':
    app = JarvisApp()
    app.run()
