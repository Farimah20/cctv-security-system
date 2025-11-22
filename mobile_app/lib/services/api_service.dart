/// API Service
/// Handles all HTTP requests to the backend server

import 'dart:convert';
import 'package:http/http.dart' as http;
import '../config/app_config.dart';
import 'storage_service.dart';

class ApiService {
  final StorageService _storage = StorageService();
  
  /// Get headers with authentication token
  Future<Map<String, String>> _getHeaders({bool includeAuth = false}) async {
    Map<String, String> headers = {
      'Content-Type': 'application/json',
    };
    
    if (includeAuth) {
      String? token = await _storage.getToken();
      if (token != null) {
        headers['Authorization'] = 'Bearer $token';
      }
    }
    
    return headers;
  }
  
  /// Handle API response
  dynamic _handleResponse(http.Response response) {
    if (response.statusCode >= 200 && response.statusCode < 300) {
      if (response.body.isEmpty) {
        return null;
      }
      return json.decode(response.body);
    } else {
      throw Exception('API Error: ${response.statusCode} - ${response.body}');
    }
  }
  
  /// Login user
  Future<Map<String, dynamic>> login(String username, String password) async {
    final url = Uri.parse('${AppConfig.baseUrl}${AppConfig.loginEndpoint}');
    
    final response = await http.post(
      url,
      headers: await _getHeaders(),
      body: json.encode({
        'username': username,
        'password': password,
      }),
    );
    
    return _handleResponse(response);
  }
  
  /// Register new user
  Future<Map<String, dynamic>> register(
    String username,
    String email,
    String password,
  ) async {
    final url = Uri.parse('${AppConfig.baseUrl}${AppConfig.registerEndpoint}');
    
    final response = await http.post(
      url,
      headers: await _getHeaders(),
      body: json.encode({
        'username': username,
        'email': email,
        'password': password,
      }),
    );
    
    return _handleResponse(response);
  }
  
  /// Get user profile
  Future<Map<String, dynamic>> getProfile() async {
    final url = Uri.parse('${AppConfig.baseUrl}${AppConfig.profileEndpoint}');
    
    final response = await http.get(
      url,
      headers: await _getHeaders(includeAuth: true),
    );
    
    return _handleResponse(response);
  }
  
  /// Get user events
  Future<Map<String, dynamic>> getEvents(
    int userId, {
    int page = 1,
    int pageSize = 20,
    bool unreadOnly = false,
  }) async {
    final queryParams = {
      'page': page.toString(),
      'page_size': pageSize.toString(),
      'unread_only': unreadOnly.toString(),
    };
    
    final url = Uri.parse(
      '${AppConfig.baseUrl}${AppConfig.eventsEndpoint}/$userId',
    ).replace(queryParameters: queryParams);
    
    final response = await http.get(
      url,
      headers: await _getHeaders(includeAuth: true),
    );
    
    return _handleResponse(response);
  }
  
  /// Get event by ID
  Future<Map<String, dynamic>> getEvent(int eventId) async {
    final url = Uri.parse('${AppConfig.baseUrl}/events/$eventId');
    
    final response = await http.get(
      url,
      headers: await _getHeaders(includeAuth: true),
    );
    
    return _handleResponse(response);
  }
  
  /// Mark event as read
  Future<Map<String, dynamic>> markEventAsRead(int eventId) async {
    final url = Uri.parse('${AppConfig.baseUrl}/events/$eventId/read');
    
    final response = await http.patch(
      url,
      headers: await _getHeaders(includeAuth: true),
    );
    
    return _handleResponse(response);
  }
  
  /// Mark all events as read
  Future<Map<String, dynamic>> markAllEventsAsRead(int userId) async {
    final url = Uri.parse(
      '${AppConfig.baseUrl}/events/user/$userId/mark-all-read',
    );
    
    final response = await http.post(
      url,
      headers: await _getHeaders(includeAuth: true),
    );
    
    return _handleResponse(response);
  }
  
  /// Get event statistics
  Future<Map<String, dynamic>> getStatistics(int userId, {int days = 7}) async {
    final url = Uri.parse(
      '${AppConfig.baseUrl}${AppConfig.statisticsEndpoint}/$userId/statistics?days=$days',
    );
    
    final response = await http.get(
      url,
      headers: await _getHeaders(includeAuth: true),
    );
    
    return _handleResponse(response);
  }
  
  /// Get unread count
  Future<Map<String, dynamic>> getUnreadCount(int userId) async {
    final url = Uri.parse(
      '${AppConfig.baseUrl}/events/user/$userId/unread-count',
    );
    
    final response = await http.get(
      url,
      headers: await _getHeaders(includeAuth: true),
    );
    
    return _handleResponse(response);
  }
  
  /// Update user profile
  Future<Map<String, dynamic>> updateProfile({
    String? email,
    String? username,
    String? password,
  }) async {
    final url = Uri.parse('${AppConfig.baseUrl}${AppConfig.profileEndpoint}');
    
    Map<String, dynamic> body = {};
    if (email != null) body['email'] = email;
    if (username != null) body['username'] = username;
    if (password != null) body['password'] = password;
    
    final response = await http.put(
      url,
      headers: await _getHeaders(includeAuth: true),
      body: json.encode(body),
    );
    
    return _handleResponse(response);
  }
  
  /// Request password reset
  Future<Map<String, dynamic>> requestPasswordReset(String email) async {
    final url = Uri.parse(
      '${AppConfig.baseUrl}/auth/password-reset/request',
    );
    
    final response = await http.post(
      url,
      headers: await _getHeaders(),
      body: json.encode({'email': email}),
    );
    
    return _handleResponse(response);
  }
  
  /// Confirm password reset
  Future<Map<String, dynamic>> confirmPasswordReset(
    String token,
    String newPassword,
  ) async {
    final url = Uri.parse(
      '${AppConfig.baseUrl}/auth/password-reset/confirm',
    );
    
    final response = await http.post(
      url,
      headers: await _getHeaders(),
      body: json.encode({
        'token': token,
        'new_password': newPassword,
      }),
    );
    
    return _handleResponse(response);
  }
  
  /// Get event image URL
  String getEventImageUrl(int eventId) {
    return '${AppConfig.baseUrl}/files/event/$eventId/image';
  }
}
