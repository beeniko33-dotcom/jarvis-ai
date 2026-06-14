# JARVIS AI - Mobile Build Instructions

## Prerequisites
- Flutter SDK installed (https://docs.flutter.dev/get-started/install)
- For Android: Android SDK with ADB
- For iOS: Xcode on macOS
- For backend: Python 3.11+, ollama

## Quick Setup

### Backend (Python)
```bash
pip install -r requirements.txt
ollama pull llama3
python -m api.bridge  # Runs FastAPI backend on port 8000
```

### Mobile App (Flutter)

#### Android
```bash
cd JarvisAppFlutter
flutter pub get
flutter build apk --release --split-per-abi
```
Install: `adb install build/app/outputs/flutter-apk/app-arm64-v8a-release.apk`

#### iOS (macOS only)
```bash
cd JarvisAppFlutter
flutter pub get
flutter build ipa --release
```
Then deploy via Xcode or Transporter.

## Backend URL Configuration
- Android emulator: Uses `10.0.2.2:8000` (default)
- For physical device: Change WiFi IP in `lib/services/api_service.dart`
- For iOS simulator: Uses `127.0.0.1:8000`

## Mobile Features
- Voice input via speech_to_text
- Text-to-speech via flutter_tts
- Runtime permission handling
- Animated particle orb UI
- Multi-agent AI routing

## Permissions Required
- Microphone (for voice commands)
- Internet (for backend communication)

> Note: This environment lacks Flutter/Android SDKs. Run builds on your local machine with proper SDK installation.