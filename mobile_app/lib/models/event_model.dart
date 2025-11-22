/// Event Model
/// Represents a security event

class EventModel {
  final int id;
  final int userId;
  final String eventType;
  final String? description;
  final String? imagePath;
  final double confidence;
  final DateTime timestamp;
  final bool isRead;
  final String? cameraId;
  final double? latitude;
  final double? longitude;
  
  EventModel({
    required this.id,
    required this.userId,
    required this.eventType,
    this.description,
    this.imagePath,
    required this.confidence,
    required this.timestamp,
    required this.isRead,
    this.cameraId,
    this.latitude,
    this.longitude,
  });
  
  /// Create EventModel from JSON
  factory EventModel.fromJson(Map<String, dynamic> json) {
    return EventModel(
      id: json['id'],
      userId: json['user_id'],
      eventType: json['event_type'],
      description: json['description'],
      imagePath: json['image_path'],
      confidence: (json['confidence'] as num).toDouble(),
      timestamp: DateTime.parse(json['timestamp']),
      isRead: json['is_read'],
      cameraId: json['camera_id'],
      latitude: json['latitude'] != null 
          ? (json['latitude'] as num).toDouble() 
          : null,
      longitude: json['longitude'] != null 
          ? (json['longitude'] as num).toDouble() 
          : null,
    );
  }
  
  /// Convert EventModel to JSON
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'user_id': userId,
      'event_type': eventType,
      'description': description,
      'image_path': imagePath,
      'confidence': confidence,
      'timestamp': timestamp.toIso8601String(),
      'is_read': isRead,
      'camera_id': cameraId,
      'latitude': latitude,
      'longitude': longitude,
    };
  }
  
  /// Get user-friendly event type name
  String get eventTypeName {
    switch (eventType) {
      case 'fast_movement':
        return 'Fast Movement';
      case 'loitering':
        return 'Loitering';
      case 'erratic_movement':
        return 'Erratic Movement';
      case 'theft':
        return 'Theft Alert';
      case 'suspicious_behavior':
        return 'Suspicious Behavior';
      default:
        return eventType.replaceAll('_', ' ').toUpperCase();
    }
  }
  
  /// Get event icon
  String get eventIcon {
    switch (eventType) {
      case 'fast_movement':
        return '🏃';
      case 'loitering':
        return '⏰';
      case 'erratic_movement':
        return '⚠️';
      case 'theft':
        return '🚨';
      case 'suspicious_behavior':
        return '👁️';
      default:
        return '📹';
    }
  }
  
  /// Get confidence percentage string
  String get confidencePercentage {
    return '${(confidence * 100).toStringAsFixed(1)}%';
  }
  
  /// Get formatted timestamp
  String get formattedTimestamp {
    final now = DateTime.now();
    final difference = now.difference(timestamp);
    
    if (difference.inMinutes < 1) {
      return 'Just now';
    } else if (difference.inHours < 1) {
      return '${difference.inMinutes} minutes ago';
    } else if (difference.inDays < 1) {
      return '${difference.inHours} hours ago';
    } else if (difference.inDays < 7) {
      return '${difference.inDays} days ago';
    } else {
      return '${timestamp.day}/${timestamp.month}/${timestamp.year}';
    }
  }
}
