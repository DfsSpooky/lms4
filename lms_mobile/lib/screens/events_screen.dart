import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';
import '../providers/event_provider.dart';
import '../widgets/skeletons.dart';
import 'event_detail_screen.dart';

class EventsScreen extends StatefulWidget {
  const EventsScreen({super.key});

  @override
  State<EventsScreen> createState() => _EventsScreenState();
}

class _EventsScreenState extends State<EventsScreen> {

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      Provider.of<EventProvider>(context, listen: false).fetchEvents();
    });
  }

  String _formatDate(String isoDate) {
    try {
      final date = DateTime.parse(isoDate);
      return DateFormat('dd/MM/yyyy HH:mm').format(date);
    } catch (e) {
      return isoDate;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Color(0xFF0B1120),
      appBar: AppBar(
        title: Text("Eventos", style: GoogleFonts.poppins(fontWeight: FontWeight.bold, fontSize: 18)),
        backgroundColor: Color(0xFF151E32),
        elevation: 0,
        automaticallyImplyLeading: false,
      ),
      body: Consumer<EventProvider>(
        builder: (context, provider, child) {
          if (provider.isLoading) {
            return ListView.builder(
              padding: EdgeInsets.all(20),
              itemCount: 3,
              itemBuilder: (_, __) => EventSkeleton(),
            );
          }

          if (provider.error != null) {
            return Center(child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text("Error al cargar eventos", style: GoogleFonts.poppins(color: Colors.white)),
                TextButton(
                  onPressed: () => provider.fetchEvents(),
                  child: Text("Reintentar")
                )
              ],
            ));
          }

          final events = provider.events;

          if (events.isEmpty) {
            return Center(child: Text("No hay eventos disponibles", style: GoogleFonts.poppins(color: Colors.grey)));
          }

          return ListView.builder(
            padding: EdgeInsets.all(20),
            itemCount: events.length,
            itemBuilder: (context, index) {
              final event = events[index];
              return GestureDetector(
                onTap: () {
                   Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (context) => EventDetailScreen(
                        eventId: event['id'],
                        title: event['title'],
                      )
                    )
                  );
                },
                child: Container(
                  margin: EdgeInsets.only(bottom: 20),
                  decoration: BoxDecoration(
                    color: Color(0xFF151E32),
                    borderRadius: BorderRadius.circular(15),
                    boxShadow: [BoxShadow(color: Colors.black26, blurRadius: 10, offset: Offset(0, 5))]
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      ClipRRect(
                        borderRadius: BorderRadius.vertical(top: Radius.circular(15)),
                        child: event['image'] != null
                          ? Image.network(
                              event['image'],
                              height: 150,
                              width: double.infinity,
                              fit: BoxFit.cover,
                              errorBuilder: (context, error, stackTrace) => Container(height: 150, color: Colors.indigo, child: Icon(Icons.event, size: 50, color: Colors.white)),
                            )
                          : Container(height: 150, color: Colors.indigo, child: Icon(Icons.event, size: 50, color: Colors.white)),
                      ),
                      Padding(
                        padding: EdgeInsets.all(15),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              event['title'],
                              style: GoogleFonts.poppins(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16),
                            ),
                            SizedBox(height: 5),
                            Row(
                              children: [
                                Icon(Icons.calendar_today, color: Colors.indigoAccent, size: 14),
                                SizedBox(width: 5),
                                Text(_formatDate(event['start_date']), style: GoogleFonts.poppins(color: Colors.grey[400], fontSize: 12)),
                              ],
                            ),
                            SizedBox(height: 5),
                             Row(
                              children: [
                                Icon(Icons.location_on, color: Colors.redAccent, size: 14),
                                SizedBox(width: 5),
                                Text(event['location'], style: GoogleFonts.poppins(color: Colors.grey[400], fontSize: 12)),
                              ],
                            ),
                          ],
                        ),
                      )
                    ],
                  ),
                ),
              );
            },
          );
        },
      ),
    );
  }
}
