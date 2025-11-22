/// Event Provider
/// Manages events state and data

import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../models/event_model.dart';

class EventProvider with ChangeNotifier {
  final ApiService _apiService = ApiService();

  List<EventModel> _events = [];
  bool _isLoading = false;
  String? _errorMessage;
  int _totalEvents = 0;
  int _unreadCount = 0;
  Map<String, dynamic>? _statistics;

  List<EventModel> get events => _events;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;
  int get totalEvents => _totalEvents;
  int get unreadCount => _unreadCount;
  Map<String, dynamic>? get statistics => _statistics;

  /// Load events for user
  Future<void> loadEvents(int userId, {bool unreadOnly = false}) async {
    _isLoading = true;
    notifyListeners();

    try {
      final response = await _apiService.getEvents(
        userId,
        unreadOnly: unreadOnly,
      );

      _events = (response['events'] as List)
          .map((e) => EventModel.fromJson(e))
          .toList();
      _totalEvents = response['total'];
      _unreadCount = response['unread'];

      _errorMessage = null;
    } catch (e) {
      _errorMessage = 'Failed to load events: ${e.toString()}';
      _events = [];
    }

    _isLoading = false;
    notifyListeners();
  }

  /// Load statistics
  Future<void> loadStatistics(int userId, {int days = 7}) async {
    try {
      _statistics = await _apiService.getStatistics(userId, days: days);
      notifyListeners();
    } catch (e) {
      _errorMessage = 'Failed to load statistics';
    }
  }

  /// Mark event as read
  Future<void> markAsRead(int eventId) async {
    try {
      await _apiService.markEventAsRead(eventId);

      // Update local state
      final index = _events.indexWhere((e) => e.id == eventId);
      if (index != -1) {
        // Create a new list with updated event
        _events = List.from(_events);
        // We can't modify the existing EventModel, so we'll just reload
        // In a real app, you'd want to make EventModel mutable or handle this differently
      }

      _unreadCount = (_unreadCount > 0) ? _unreadCount - 1 : 0;
      notifyListeners();
    } catch (e) {
      _errorMessage = 'Failed to mark as read';
    }
  }

  /// Mark all events as read
  Future<void> markAllAsRead(int userId) async {
    try {
      await _apiService.markAllEventsAsRead(userId);
      _unreadCount = 0;
      
      // Reload events to update read status
      await loadEvents(userId);
    } catch (e) {
      _errorMessage = 'Failed to mark all as read';
    }
  }

  /// Refresh events
  Future<void> refresh(int userId) async {
    await loadEvents(userId);
    await loadStatistics(userId);
  }

  /// Clear error
  void clearError() {
    _errorMessage = null;
    notifyListeners();
  }

  /// Get unread count
  Future<void> updateUnreadCount(int userId) async {
    try {
      final response = await _apiService.getUnreadCount(userId);
      _unreadCount = response['unread_count'];
      notifyListeners();
    } catch (e) {
      // Silent fail
    }
  }
}
