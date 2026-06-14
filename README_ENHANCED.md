# Enhanced JARVIS AI

## Android Compatibility Enhancements
- Updated Flutter app for full device compatibility (mic, permissions, TTS)
- Added speech_to_text, permission_handler, flutter_tts
- Runtime permission requests in main.dart
- Target modern Android SDKs (build after pub get)

## New Features
- Multi-Agent System with CrewAI (Planner, Researcher, Critic)
- Vector Memory with ChromaDB for long-term self-learning
- Auto-optimization and error logging
- WebSocket bridge for Electron/Three.js HUD
- Improved mic support (Bluetooth/external devices)

## Setup

**Backend:**
- Python 3.11+
- `pip install -r requirements.txt`
- `ollama pull llama3`
- `python -m api.bridge`
- `python main.py`

**Flutter Android:**
```bash
cd JarvisAppFlutter
flutter pub get
flutter build apk --release --split-per-abi
```

Install the APK on your device. Grant microphone permissions.

**For specific device issues:** Share model/Android version for further tweaks.

Web HUD: `cd web && npm start`

> Note: Push changes regularly!