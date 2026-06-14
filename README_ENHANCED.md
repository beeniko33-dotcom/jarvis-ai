# Enhanced JARVIS AI

## New Features
- Multi-Agent System with CrewAI (Planner, Researcher, Critic)
- Vector Memory with ChromaDB for long-term self-learning
- Auto-optimization and error logging
- WebSocket bridge for Electron/Three.js HUD
- Improved mic support (Bluetooth/external devices)

## Setup
- Install Python 3.10 or newer (Python 3.11 / 3.12 recommended).
- Use the matching Python interpreter when installing dependencies.

pip install -r requirements.txt
ollama pull llama3
python -m api.bridge  # starts FastAPI bridge for Flutter/WebSocket
python main.py  # runs local voice assistant

Flutter frontend:
cd JarvisAppFlutter
flutter pub get
flutter run

Web HUD:
cd web && npm start

> Note: `crewai-tools` is optional and may not be available via pip. Install only if needed.

Push changes to GitHub regularly!
