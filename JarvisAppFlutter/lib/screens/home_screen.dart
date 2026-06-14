import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_tts/flutter_tts.dart';
import 'package:speech_to_text/speech_to_text.dart';
import '../providers/assistant_provider.dart';
import '../widgets/particle_orb.dart';

class HomeScreen extends ConsumerStatefulWidget {
  const HomeScreen({super.key});

  @override
  ConsumerState<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends ConsumerState<HomeScreen> {
  final TextEditingController _commandController = TextEditingController();
  final FlutterTts _flutterTts = FlutterTts();
  final SpeechToText _speech = SpeechToText();
  bool _isListening = false;
  bool _speechAvailable = false;

  @override
  void initState() {
    super.initState();
    _initSpeech();
  }

  Future<void> _initSpeech() async {
    _speechAvailable = await _speech.initialize();
    setState(() {});
  }

  Future<void> _initTts() async {
    await _flutterTts.setLanguage("en-US");
    await _flutterTts.setSpeechRate(0.9);
  }

  Future<void> _startListening() async {
    if (!_speechAvailable) return;
    setState(() => _isListening = true);
    await _speech.listen(onResult: (result) {
      if (result.recognizedWords.isNotEmpty) {
        _commandController.text = result.recognizedWords;
      }
    });
  }

  Future<void> _stopListening() async {
    setState(() => _isListening = false);
    await _speech.stopListening();
  }

  Future<void> _sendCommand() async {
    final command = _commandController.text.trim();
    if (command.isEmpty) return;
    await ref.read(assistantProvider.notifier).sendCommand(command);
    _commandController.clear();
    if (state.response.isNotEmpty) {
      await _flutterTts.speak(state.response);
    }
  }

  @override
  void dispose() {
    _commandController.dispose();
    _flutterTts.stop();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(assistantProvider);
    return Scaffold(
      appBar: AppBar(
        title: const Text('JARVIS Ultimate 2026'),
        elevation: 0,
        backgroundColor: Colors.black,
      ),
      backgroundColor: Colors.black,
      body: SafeArea(
        child: Column(
          children: [
            Expanded(
              child: Stack(
                children: [
                  const ParticleOrb(),
                  Positioned(
                    left: 20,
                    right: 20,
                    top: 20,
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'Gemini AI + Gemma Fallback',
                          style: TextStyle(color: Colors.cyanAccent, fontSize: 16),
                        ),
                        const SizedBox(height: 10),
                        Container(
                          padding: const EdgeInsets.all(16),
                          decoration: BoxDecoration(
                            color: Colors.white12,
                            borderRadius: BorderRadius.circular(18),
                          ),
                          child: Text(
                            state.status,
                            style: const TextStyle(color: Colors.white70),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            Container(
              decoration: BoxDecoration(
                color: Colors.white12,
                borderRadius: const BorderRadius.only(
                  topLeft: Radius.circular(24),
                  topRight: Radius.circular(24),
                ),
              ),
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  TextField(
                    controller: _commandController,
                    style: const TextStyle(color: Colors.white),
                    decoration: InputDecoration(
                      hintText: 'Say something to JARVIS...',
                      hintStyle: TextStyle(color: Colors.white54),
                      prefixIcon: const Icon(Icons.mic, color: Colors.cyanAccent),
                      filled: true,
                      fillColor: Colors.white10,
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(18),
                        borderSide: BorderSide.none,
                      ),
                    ),
                    textInputAction: TextInputAction.send,
                    onSubmitted: (_) => _sendCommand(),
                  ),
                  const SizedBox(height: 16),
                  Row(
                    children: [
                      Expanded(
                        flex: 2,
                        child: ElevatedButton.icon(
                          icon: Icon(_isListening ? Icons.mic : Icons.mic_none),
                          label: Text(_isListening ? 'Listening...' : 'Voice Input'),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: _isListening ? Colors.red : Colors.cyanAccent,
                            foregroundColor: Colors.black,
                            padding: const EdgeInsets.symmetric(vertical: 16),
                          ),
                          onPressed: state.isLoading
                              ? null
                              : () {
                                  if (_isListening) {
                                    _stopListening();
                                  } else {
                                    _startListening();
                                  }
                                },
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        flex: 3,
                        child: ElevatedButton.icon(
                          icon: const Icon(Icons.send),
                          label: const Text('Send Command'),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.cyanAccent,
                            foregroundColor: Colors.black,
                            padding: const EdgeInsets.symmetric(vertical: 16),
                          ),
                          onPressed: state.isLoading ? null : _sendCommand,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  if (state.isLoading)
                    const LinearProgressIndicator(color: Colors.cyanAccent),
                  const SizedBox(height: 16),
                  Align(
                    alignment: Alignment.centerLeft,
                    child: Text(
                      'Latest response',
                      style: TextStyle(color: Colors.white.withOpacity(0.7)),
                    ),
                  ),
                  const SizedBox(height: 8),
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: Colors.white10,
                      borderRadius: BorderRadius.circular(16),
                    ),
                    child: Text(
                      state.response.isEmpty ? 'Awaiting command...' : state.response,
                      style: const TextStyle(color: Colors.white),
                    ),
                  ),
                  const SizedBox(height: 16),
                  Align(
                    alignment: Alignment.centerLeft,
                    child: Text(
                      'Session log',
                      style: TextStyle(color: Colors.white.withOpacity(0.7)),
                    ),
                  ),
                  const SizedBox(height: 8),
                  SizedBox(
                    height: 120,
                    child: ListView.builder(
                      itemCount: state.history.length,
                      itemBuilder: (context, index) {
                        return Text(
                          state.history[index],
                          style: const TextStyle(color: Colors.white70, fontSize: 13),
                        );
                      },
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}