# Enhanced JARVIS AI

## New Features
- Multi-Agent System with CrewAI (Planner, Researcher, Critic)
- Vector Memory with ChromaDB for long-term self-learning
- Auto-optimization and error logging
- WebSocket bridge for Electron/Three.js HUD
- Improved mic support (Bluetooth/external devices)

## Setup
pip install -r requirements.txt
ollama pull llama3
python -m api.bridge  # for WS
python main.py

Web HUD: cd web && npm start

Push changes to GitHub regularly!
