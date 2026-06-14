import speech_recognition as sr # pyright: ignore[reportMissingImports]
import pyttsx3 # type: ignore
import psutil
import pygame
import time
import threading
import requests
import ollama
from datetime import datetime
import random

# Initialize
engine = pyttsx3.init()
recognizer = sr.Recognizer()

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("JARVIS AI")

# Particle simulation for orb
class Particle:
    def __init__(self, x=400, y=300, speed=4):
        self.x = x
        self.y = y
        self.vx = (random.random() - 0.5) * speed
        self.vy = (random.random() - 0.5) * speed
        self.life = random.randint(80, 120)

    def reset(self):
        self.__init__()

particles = [Particle() for _ in range(200)]

def speak(text):
    print("JARVIS:", text)
    engine.say(text)
    engine.runAndWait()

def listen():
    with sr.Microphone() as source:
        print("Listening...")
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            text = recognizer.recognize_google(audio).lower()
            print("You:", text)
            return text
        except sr.WaitTimeoutError:
            print("Timeout: No voice detected.")
            return "timeout"
        except sr.UnknownValueError:
            print("Could not understand audio.")
            return "error"
        except sr.RequestError as e:
            print(f"Google Speech API error: {e}")
            return "api_error"

def get_system_diagnostics():
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory().percent
    return f"CPU: {cpu}%, Memory: {mem}%"

def run_diagnostics():
    speak("Running full system diagnostics.")
    diag = get_system_diagnostics()
    speak(diag)
    for i in range(10, 101, 20):
        print(f"Diagnostics: {i}%")
        time.sleep(0.5)
    speak("All systems nominal.")

def process_command(command):
    if "diagnostics" in command:
        run_diagnostics()
    elif "time" in command:
        speak(datetime.now().strftime("%I:%M %p"))
    elif "exit" in command or "quit" in command:
        global running
        running = False
        speak("Shutting down. Goodbye!")
    else:
        try:
            response = ollama.chat(model='llama3', messages=[{'role': 'user', 'content': command}])
            speak(response['message']['content'])
        except Exception as e:
            print(f"Ollama error: {e}")
            speak("Sorry, I can't process this command right now.")

def main_loop():
    speak("Jarvis online. How can I assist you today?")
    while running:
        command = listen()
        if command not in ["timeout", "error", "api_error"]:
            process_command(command)
        time.sleep(1)

if __name__ == "__main__":
    threading.Thread(target=main_loop, daemon=True).start()
    running = True
    clock = pygame.time.Clock()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                speak("Shutting down. Goodbye!")
        screen.fill((0, 0, 0))
        for p in particles:
            p.x += p.vx
            p.y += p.vy
            p.life -= 1
            if p.life <= 0:
                p.reset()
            pygame.draw.circle(screen, (0, 255, 255), (int(p.x), int(p.y)), 3)
        pygame.display.flip()
        clock.tick(30)
    pygame.quit()