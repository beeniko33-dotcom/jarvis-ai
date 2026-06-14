import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:permission_handler/permission_handler.dart';
import 'screens/home_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await _requestPermissions();
  runApp(const ProviderScope(child: JarvisApp()));
}

Future<void> _requestPermissions() async {
  await [Permission.microphone, Permission.speech].request();
}

class JarvisApp extends StatelessWidget {
  const JarvisApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'JARVIS Ultimate 2026',
      theme: ThemeData(
        brightness: Brightness.dark,
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.cyanAccent),
      ),
      home: const HomeScreen(),
      debugShowCheckedModeBanner: false,
    );
  }
}