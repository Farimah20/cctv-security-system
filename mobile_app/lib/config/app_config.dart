/// Application Configuration
/// Contains API URLs and app constants

class AppConfig {
  // API Base URL
  // For Android Emulator: use 10.0.2.2
  // For iOS Simulator: use localhost
  // For Real Device: use your computer's IP address
  //static const String baseUrl = 'http://10.0.2.2:8000';برای android
  static const String baseUrl = 'http://localhost:8000';  // برای Linux Desktop
  
  // API Endpoints
  static const String loginEndpoint = '/auth/login';
  static const String registerEndpoint = '/auth/register';
  static const String profileEndpoint = '/users/me';
  static const String eventsEndpoint = '/events/user';
  static const String statisticsEndpoint = '/events/user';
  
  // App Info
  static const String appName = 'CCTV Security Monitor';
  static const String appVersion = '1.0.0';
  
  // Storage Keys
  static const String tokenKey = 'auth_token';
  static const String userIdKey = 'user_id';
  static const String usernameKey = 'username';
  static const String emailKey = 'email';
  
  // Theme Colors
  static const int primaryColor = 0xFF2196F3; // Blue
  static const int accentColor = 0xFFFF5722;  // Deep Orange
  static const int successColor = 0xFF4CAF50; // Green
  static const int warningColor = 0xFFFFC107; // Amber
  static const int dangerColor = 0xFFF44336;  // Red
  
  // Pagination
  static const int pageSize = 20;
  
  // Timeouts
  static const Duration connectTimeout = Duration(seconds: 10);
  static const Duration receiveTimeout = Duration(seconds: 10);
}
