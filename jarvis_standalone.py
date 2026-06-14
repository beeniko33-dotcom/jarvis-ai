#!/usr/bin/env python3
"""
JARVIS AI - Standalone Executable Version
Single file build configuration for Windows EXE
"""

import os
import sys

# Ensure we can find modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import from core
from core.brain import AdvancedBrain
from core.agent import JarvisAgents
from core.memory import VectorMemory
from optimizer import Optimizer

# Voice support
try:
    import speech_recognition as sr
    import pyttsx3
    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False

def main():
    print("=" * 50)
    print("  JARVIS AI - Ultimate Assistant")
    print("=" * 50)
    
    brain = AdvancedBrain()
    
    print("\nVoice command enabled:", VOICE_AVAILABLE)
    print("Type 'exit' to quit\n")
    
    while True:
        try:
            cmd = input("You: ").strip()
            if cmd.lower() in ["exit", "quit", "shutdown"]:
                print("JARVIS: Shutting down. Goodbye!")
                break
            
            response = brain.process_command(cmd)
            print(f"JARVIS: {response}")
            
            if VOICE_AVAILABLE:
                try:
                    engine = pyttsx3.init()
                    engine.say(response)
                    engine.runAndWait()
                except:
                    pass
            
        except KeyboardInterrupt:
            print("\nJARVIS: Goodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()