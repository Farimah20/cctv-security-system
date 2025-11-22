/// Authentication Provider
/// Manages user authentication state

import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../services/storage_service.dart';

class AuthProvider with ChangeNotifier {
  final ApiService _apiService = ApiService();
  final StorageService _storage = StorageService();

  bool _isAuthenticated = false;
  bool _isLoading = false;
  String? _username;
  String? _email;
  int? _userId;
  String? _errorMessage;

  bool get isAuthenticated => _isAuthenticated;
  bool get isLoading => _isLoading;
  String? get username => _username;
  String? get email => _email;
  int? get userId => _userId;
  String? get errorMessage => _errorMessage;

  /// Check if user is logged in on app start
  Future<void> checkLoginStatus() async {
    _isLoading = true;
    notifyListeners();

    try {
      final isLoggedIn = await _storage.isLoggedIn();

      if (isLoggedIn) {
        _username = await _storage.getUsername();
        _email = await _storage.getEmail();
        _userId = await _storage.getUserId();
        _isAuthenticated = true;
      }
    } catch (e) {
      _errorMessage = 'Failed to check login status';
    }

    _isLoading = false;
    notifyListeners();
  }

  /// Login user
  Future<bool> login(String username, String password) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final response = await _apiService.login(username, password);
      final token = response['access_token'];

      // Get user profile
      await _storage.saveToken(token);
      final profile = await _apiService.getProfile();

      // Save user data
      await _storage.saveUserData(
        token: token,
        userId: profile['id'],
        username: profile['username'],
        email: profile['email'],
      );

      _username = profile['username'];
      _email = profile['email'];
      _userId = profile['id'];
      _isAuthenticated = true;
      _isLoading = false;
      notifyListeners();

      return true;
    } catch (e) {
      _errorMessage = 'Login failed: ${e.toString()}';
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  /// Register new user
  Future<bool> register(
    String username,
    String email,
    String password,
  ) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      await _apiService.register(username, email, password);
      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _errorMessage = 'Registration failed: ${e.toString()}';
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  /// Logout user
  Future<void> logout() async {
    await _storage.clearUserData();
    _isAuthenticated = false;
    _username = null;
    _email = null;
    _userId = null;
    notifyListeners();
  }

  /// Update profile
  Future<bool> updateProfile({
    String? newEmail,
    String? newUsername,
    String? newPassword,
  }) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final response = await _apiService.updateProfile(
        email: newEmail,
        username: newUsername,
        password: newPassword,
      );

      if (newEmail != null) {
        _email = response['email'];
        await _storage.saveEmail(_email!);
      }

      if (newUsername != null) {
        _username = response['username'];
        await _storage.saveUsername(_username!);
      }

      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _errorMessage = 'Update failed: ${e.toString()}';
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  /// Clear error message
  void clearError() {
    _errorMessage = null;
    notifyListeners();
  }
}
