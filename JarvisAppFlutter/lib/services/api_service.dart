import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  ApiService();

  static const String _defaultUrl = 'http://10.0.2.2:8000';
  static String _baseUrl = _defaultUrl;

  static void setBaseUrl(String url) {
    _baseUrl = url;
  }

  static String get baseUrl => _baseUrl;

  Future<String> sendCommand(String command) async {
    final uri = Uri.parse('$_baseUrl/command');
    final response = await http.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'command': command}),
    );

    if (response.statusCode == 200) {
      final body = jsonDecode(response.body) as Map<String, dynamic>;
      return body['response']?.toString() ?? 'No response from JARVIS.';
    }

    throw Exception('Backend request failed (${response.statusCode}): ${response.body}');
  }
}