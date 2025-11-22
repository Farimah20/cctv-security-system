/// Storage Service
/// Manages local data storage using SharedPreferences

import 'package:shared_preferences/shared_preferences.dart';
import '../config/app_config.dart';

class StorageService {
  /// Save authentication token
  Future<void> saveToken(String token) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(AppConfig.tokenKey, token);
  }
  
  /// Get authentication token
  Future<String?> getToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(AppConfig.tokenKey);
  }
  
  /// Save user ID
  Future<void> saveUserId(int userId) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setInt(AppConfig.userIdKey, userId);
  }
  
  /// Get user ID
  Future<int?> getUserId() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getInt(AppConfig.userIdKey);
  }
  
  /// Save username
  Future<void> saveUsername(String username) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(AppConfig.usernameKey, username);
  }
  
  /// Get username
  Future<String?> getUsername() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(AppConfig.usernameKey);
  }
  
  /// Save email
  Future<void> saveEmail(String email) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(AppConfig.emailKey, email);
  }
  
  /// Get email
  Future<String?> getEmail() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(AppConfig.emailKey);
  }
  
  /// Save user data (after login)
  Future<void> saveUserData({
    required String token,
    required int userId,
    required String username,
    required String email,
  }) async {
    await saveToken(token);
    await saveUserId(userId);
    await saveUsername(username);
    await saveEmail(email);
  }
  
  /// Check if user is logged in
  Future<bool> isLoggedIn() async {
    final token = await getToken();
    return token != null && token.isNotEmpty;
  }
  
  /// Clear all user data (logout)
  Future<void> clearUserData() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(AppConfig.tokenKey);
    await prefs.remove(AppConfig.userIdKey);
    await prefs.remove(AppConfig.usernameKey);
    await prefs.remove(AppConfig.emailKey);
  }
}
