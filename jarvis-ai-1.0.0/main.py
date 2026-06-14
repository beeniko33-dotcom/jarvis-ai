import speech_recognition as sr
import pyttsx3
import psutil
import pygame
import time
import threading
import ollama
from datetime import datetime
import random

engine = pyttsx3.init()
recognizer = sr.Recognizer()

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("JARVIS AI")

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

def run_full_diagnostics():
    speak("Running full system diagnostics.")
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    diag = f"Full Diagnostics - CPU: {cpu}%, Memory: {mem}%, Disk: {disk}%"
    speak(diag)
    print("Full system diagnostic completed.")
    speak("All systems nominal.")

def process_command(command):
    if "full diagnostic" in command or "full system" in command or "complete diagnostic" in command:
        run_full_diagnostics()
    elif "diagnostics" in command or "status" in command or "cpu" in command or "ram" in command:
        speak(get_system_diagnostics())
    elif "time" in command:
        speak(datetime.now().strftime("%I:%M %p"))
    elif "date" in command:
        speak(datetime.now().strftime("%A, %B %d, %Y"))
    elif "joke" in command:
        speak("Why did the AI go to therapy? Too many unresolved issues! Haha.")
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