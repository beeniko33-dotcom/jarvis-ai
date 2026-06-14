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

# For memory
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
        self.performance_log = []
        self.tts_engine = pyttsx3.init()  # Reuse engine

    def speak(self, text):
        print("JARVIS:", text)
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()

    def listen(self, device_index=None):
        r = sr.Recognizer()
        with sr.Microphone(device_index=device_index) as source:
            print("Listening...")
            audio = r.listen(source, timeout=5, phrase_time_limit=10)
            try:
                return r.recognize_google(audio).lower()
            except:
                return None

    def self_reflect(self, cmd, response):
        # Simple self-awareness
        self.performance_log.append({"cmd": cmd, "response": response, "time": time.time()})
        if len(self.performance_log) > 10:
            success_rate = sum(1 for log in self.performance_log[-10:] if len(log["response"]) > 10) / 10
            if success_rate < 0.7:
                self.speak("Self-optimizing response patterns.")
                # Could trigger prompt improvement here

    def process_command(self, cmd):
        context = self.memory.get_context()
        full_prompt = f"Context:\n{context}\nUser: {cmd}\nRespond as helpful, witty JARVIS:"
        
        try:
            resp = ollama.chat(model='llama3', messages=[{'role': 'user', 'content': full_prompt}])
            response = resp['message']['content']
        except:
            response = "At your service, sir. Command received."
        
        self.memory.add(cmd, response)
        self.self_reflect(cmd, response)
        self.speak(response)
        return response

class JarvisApp:
    def __init__(self):
        self.agent = SelfAwareAgent()
        # List available mics
        print("Available microphones:")
        for idx, name in enumerate(sr.Microphone.list_microphone_names()):
            print(f"{idx}: {name}")

    def run(self):
        self.agent.speak("Jarvis online with self-awareness. Say Jarvis to activate.")
        while True:
            cmd = self.agent.listen()  # Try default, can extend for Bluetooth
            if cmd and "jarvis" in cmd:
                self.agent.speak("At your service.")
                follow = self.agent.listen()
                if follow:
                    self.agent.process_command(follow)
            time.sleep(0.5)

if __name__ == '__main__':
    app = JarvisApp()
    app.run()
