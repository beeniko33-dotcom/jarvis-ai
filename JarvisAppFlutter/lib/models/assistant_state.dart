import 'package:flutter/foundation.dart';

@immutable
class AssistantState {
  final String status;
  final String response;
  final bool isLoading;
  final List<String> history;

  const AssistantState({
    required this.status,
    required this.response,
    required this.isLoading,
    required this.history,
  });

  factory AssistantState.initial() {
    return const AssistantState(
      status: 'Ready for Gemini/Gemma routing',
      response: '',
      isLoading: false,
      history: [],
    );
  }

  AssistantState copyWith({
    String? status,
    String? response,
    bool? isLoading,
    List<String>? history,
  }) {
    return AssistantState(
      status: status ?? this.status,
      response: response ?? this.response,
      isLoading: isLoading ?? this.isLoading,
      history: history ?? this.history,
    );
  }
}
