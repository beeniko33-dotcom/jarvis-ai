import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/assistant_state.dart';
import '../services/api_service.dart';

final assistantProvider = StateNotifierProvider<AssistantNotifier, AssistantState>(
  (ref) => AssistantNotifier(),
);

class AssistantNotifier extends StateNotifier<AssistantState> {
  AssistantNotifier() : super(AssistantState.initial());

  final ApiService _apiService = ApiService();

  Future<void> sendCommand(String command) async {
    if (command.isEmpty) return;
    final routedModel = _routeModel(command);
    state = state.copyWith(
      status: 'Routing to $routedModel…',
      isLoading: true,
      history: [...state.history, 'You: $command'],
    );

    try {
      final response = await _apiService.sendCommand(command);
      state = state.copyWith(
        response: response,
        status: 'Response received from $routedModel',
        isLoading: false,
        history: [...state.history, 'Jarvis: $response'],
      );
    } catch (error) {
      state = state.copyWith(
        response: error.toString(),
        status: 'Backend request failed',
        isLoading: false,
      );
    }
  }

  String _routeModel(String command) {
    final normalized = command.toLowerCase();
    if (normalized.contains('research') || normalized.contains('analysis') || command.split(' ').length > 5) {
      return 'Gemini';
    }
    return 'Gemma';
  }
}
