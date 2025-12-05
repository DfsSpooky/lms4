import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../services/api_service.dart';

class NotificationsScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Color(0xFF0B1120),
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        iconTheme: IconThemeData(color: Colors.white),
        title: Text("Notificaciones", style: TextStyle(color: Colors.white)),
      ),
      body: FutureBuilder<List<dynamic>>(
        future: ApiService.getNotifications(),
        builder: (context, snapshot) {
          if (!snapshot.hasData) return Center(child: CircularProgressIndicator());
          final notifs = snapshot.data!;
          if (notifs.isEmpty) return Center(child: Text("Sin notificaciones", style: TextStyle(color: Colors.white54)));

          return ListView.builder(
            padding: EdgeInsets.all(20),
            itemCount: notifs.length,
            itemBuilder: (context, index) {
              final n = notifs[index];
              return ListTile(
                title: Text(n['message'], style: TextStyle(color: Colors.white)),
                subtitle: Text(n['created_at'], style: TextStyle(color: Colors.white38, fontSize: 10)),
                leading: Icon(Icons.notifications, color: n['is_read'] ? Colors.grey : Colors.amber),
                onTap: () async {
                  await ApiService.markNotificationRead(n['id']);
                  // Refresh?
                },
              );
            },
          );
        },
      ),
    );
  }
}
