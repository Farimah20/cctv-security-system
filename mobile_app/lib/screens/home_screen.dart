/// Home Screen
/// Main dashboard showing events and statistics

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/auth_provider.dart';
import '../providers/event_provider.dart';
import '../config/app_config.dart';
import '../models/event_model.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    final authProvider = Provider.of<AuthProvider>(context, listen: false);
    final eventProvider = Provider.of<EventProvider>(context, listen: false);
    
    if (authProvider.userId != null) {
      await eventProvider.loadEvents(authProvider.userId!);
      await eventProvider.loadStatistics(authProvider.userId!);
    }
  }

  Future<void> _refresh() async {
    final authProvider = Provider.of<AuthProvider>(context, listen: false);
    final eventProvider = Provider.of<EventProvider>(context, listen: false);
    
    if (authProvider.userId != null) {
      await eventProvider.refresh(authProvider.userId!);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('CCTV Monitor'),
        actions: [
          // Notifications Badge
          Consumer<EventProvider>(
            builder: (context, eventProvider, child) {
              return Stack(
                children: [
                  IconButton(
                    icon: const Icon(Icons.notifications),
                    onPressed: () {
                      // Navigate to events screen
                    },
                  ),
                  if (eventProvider.unreadCount > 0)
                    Positioned(
                      right: 8,
                      top: 8,
                      child: Container(
                        padding: const EdgeInsets.all(4),
                        decoration: BoxDecoration(
                          color: Colors.red,
                          shape: BoxShape.circle,
                        ),
                        constraints: const BoxConstraints(
                          minWidth: 16,
                          minHeight: 16,
                        ),
                        child: Text(
                          '${eventProvider.unreadCount}',
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 10,
                            fontWeight: FontWeight.bold,
                          ),
                          textAlign: TextAlign.center,
                        ),
                      ),
                    ),
                ],
              );
            },
          ),
          // Profile Menu
          PopupMenuButton<String>(
            onSelected: (value) async {
              if (value == 'profile') {
                // Navigate to profile
              } else if (value == 'logout') {
                final authProvider = Provider.of<AuthProvider>(
                  context,
                  listen: false,
                );
                await authProvider.logout();
              }
            },
            itemBuilder: (context) => [
              const PopupMenuItem(
                value: 'profile',
                child: Row(
                  children: [
                    Icon(Icons.person),
                    SizedBox(width: 8),
                    Text('Profile'),
                  ],
                ),
              ),
              const PopupMenuItem(
                value: 'logout',
                child: Row(
                  children: [
                    Icon(Icons.logout),
                    SizedBox(width: 8),
                    Text('Logout'),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _refresh,
        child: Consumer<EventProvider>(
          builder: (context, eventProvider, child) {
            if (eventProvider.isLoading && eventProvider.events.isEmpty) {
              return const Center(
                child: CircularProgressIndicator(),
              );
            }

            return SingleChildScrollView(
              physics: const AlwaysScrollableScrollPhysics(),
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Welcome Card
                  Consumer<AuthProvider>(
                    builder: (context, authProvider, child) {
                      return Card(
                        child: Padding(
                          padding: const EdgeInsets.all(16),
                          child: Row(
                            children: [
                              CircleAvatar(
                                radius: 30,
                                backgroundColor: Color(AppConfig.primaryColor),
                                child: Text(
                                  authProvider.username?[0].toUpperCase() ?? 'U',
                                  style: const TextStyle(
                                    fontSize: 24,
                                    color: Colors.white,
                                  ),
                                ),
                              ),
                              const SizedBox(width: 16),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      'Welcome back,',
                                      style: TextStyle(
                                        color: Colors.grey[600],
                                      ),
                                    ),
                                    Text(
                                      authProvider.username ?? 'User',
                                      style: const TextStyle(
                                        fontSize: 20,
                                        fontWeight: FontWeight.bold,
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                              Icon(
                                Icons.security,
                                size: 40,
                                color: Color(AppConfig.successColor),
                              ),
                            ],
                          ),
                        ),
                      );
                    },
                  ),
                  const SizedBox(height: 16),

                  // Statistics Cards
                  _buildStatisticsSection(eventProvider),
                  const SizedBox(height: 24),

                  // Recent Events Section
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text(
                        'Recent Events',
                        style: TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      TextButton(
                        onPressed: () {
                          // Navigate to all events
                        },
                        child: const Text('View All'),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),

                  // Events List
                  _buildEventsList(eventProvider),
                ],
              ),
            );
          },
        ),
      ),
    );
  }

  Widget _buildStatisticsSection(EventProvider eventProvider) {
    final stats = eventProvider.statistics;
    
    return Row(
      children: [
        Expanded(
          child: _buildStatCard(
            icon: Icons.event,
            title: 'Total Events',
            value: '${eventProvider.totalEvents}',
            color: Color(AppConfig.primaryColor),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _buildStatCard(
            icon: Icons.notifications_active,
            title: 'Unread',
            value: '${eventProvider.unreadCount}',
            color: Color(AppConfig.warningColor),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _buildStatCard(
            icon: Icons.trending_up,
            title: 'This Week',
            value: '${stats?['total_events'] ?? 0}',
            color: Color(AppConfig.successColor),
          ),
        ),
      ],
    );
  }

  Widget _buildStatCard({
    required IconData icon,
    required String title,
    required String value,
    required Color color,
  }) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Icon(icon, color: color, size: 32),
            const SizedBox(height: 8),
            Text(
              value,
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
            Text(
              title,
              style: TextStyle(
                fontSize: 12,
                color: Colors.grey[600],
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildEventsList(EventProvider eventProvider) {
    if (eventProvider.events.isEmpty) {
      return Card(
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(
            children: [
              Icon(
                Icons.check_circle_outline,
                size: 64,
                color: Colors.grey[400],
              ),
              const SizedBox(height: 16),
              Text(
                'No events detected',
                style: TextStyle(
                  fontSize: 16,
                  color: Colors.grey[600],
                ),
              ),
              const SizedBox(height: 8),
              Text(
                'Your security system is monitoring',
                style: TextStyle(
                  fontSize: 14,
                  color: Colors.grey[500],
                ),
              ),
            ],
          ),
        ),
      );
    }

    // Show first 5 events
    final recentEvents = eventProvider.events.take(5).toList();

    return Column(
      children: recentEvents.map((event) => _buildEventCard(event)).toList(),
    );
  }

  Widget _buildEventCard(EventModel event) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: event.isRead
              ? Colors.grey[300]
              : Color(AppConfig.dangerColor),
          child: Text(
            event.eventIcon,
            style: const TextStyle(fontSize: 20),
          ),
        ),
        title: Text(
          event.eventTypeName,
          style: TextStyle(
            fontWeight: event.isRead ? FontWeight.normal : FontWeight.bold,
          ),
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(event.description ?? 'No description'),
            const SizedBox(height: 4),
            Row(
              children: [
                Icon(Icons.access_time, size: 12, color: Colors.grey[600]),
                const SizedBox(width: 4),
                Text(
                  event.formattedTimestamp,
                  style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                ),
                const SizedBox(width: 12),
                Icon(Icons.speed, size: 12, color: Colors.grey[600]),
                const SizedBox(width: 4),
                Text(
                  event.confidencePercentage,
                  style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                ),
              ],
            ),
          ],
        ),
        trailing: Icon(
          event.isRead ? Icons.check : Icons.fiber_manual_record,
          color: event.isRead ? Colors.grey : Color(AppConfig.dangerColor),
          size: 12,
        ),
        onTap: () {
          // Navigate to event details
          _showEventDetails(event);
        },
      ),
    );
  }

  void _showEventDetails(EventModel event) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(event.eventTypeName),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Description: ${event.description ?? "N/A"}'),
            const SizedBox(height: 8),
            Text('Confidence: ${event.confidencePercentage}'),
            const SizedBox(height: 8),
            Text('Time: ${event.formattedTimestamp}'),
            if (event.cameraId != null) ...[
              const SizedBox(height: 8),
              Text('Camera: ${event.cameraId}'),
            ],
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Close'),
          ),
          if (!event.isRead)
            ElevatedButton(
              onPressed: () async {
                final eventProvider = Provider.of<EventProvider>(
                  context,
                  listen: false,
                );
                await eventProvider.markAsRead(event.id);
                if (mounted) Navigator.pop(context);
              },
              child: const Text('Mark as Read'),
            ),
        ],
      ),
    );
  }
}