import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:intl/intl.dart';
import '../services/api_service.dart';

class EventDetailScreen extends StatefulWidget {
  final int eventId;
  final String title;

  const EventDetailScreen({Key? key, required this.eventId, required this.title}) : super(key: key);

  @override
  _EventDetailScreenState createState() => _EventDetailScreenState();
}

class _EventDetailScreenState extends State<EventDetailScreen> {
  late Future<Map<String, dynamic>> _eventFuture;

  @override
  void initState() {
    super.initState();
    _loadEvent();
  }

  void _loadEvent() {
    _eventFuture = ApiService.getEventDetail(widget.eventId);
  }

  void _register() async {
    try {
      await ApiService.registerForEvent(widget.eventId);
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text("¡Registro exitoso!")));
      setState(() {
        _loadEvent();
      });
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.toString().replaceAll("Exception: ", ""))));
    }
  }

  String _formatTime(String isoDate) {
    try {
      final date = DateTime.parse(isoDate);
      return DateFormat('HH:mm').format(date);
    } catch (e) {
      return isoDate;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Color(0xFF0B1120),
      appBar: AppBar(
        title: Text(widget.title, style: GoogleFonts.poppins(fontSize: 16)),
        backgroundColor: Color(0xFF151E32),
      ),
      body: FutureBuilder<Map<String, dynamic>>(
        future: _eventFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting)
            return Center(child: CircularProgressIndicator());

          if (snapshot.hasError)
            return Center(child: Text("Error cargando detalles", style: TextStyle(color: Colors.white)));

          final event = snapshot.data!;
          final sessions = event['sessions'] as List<dynamic>? ?? [];
          final isRegistered = event['is_registered'] ?? false;
          final spotsLeft = event['spots_left'] ?? 0;

          return SingleChildScrollView(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (event['image'] != null)
                  Image.network(
                    event['image'],
                    width: double.infinity,
                    height: 200,
                    fit: BoxFit.cover,
                    errorBuilder: (context, error, stackTrace) => Container(height: 200, color: Colors.indigo),
                  ),

                Padding(
                  padding: EdgeInsets.all(20),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(event['title'], style: GoogleFonts.poppins(color: Colors.white, fontSize: 22, fontWeight: FontWeight.bold)),
                      SizedBox(height: 10),
                      Text(event['description'] ?? "", style: GoogleFonts.poppins(color: Colors.grey[400], height: 1.5)),

                      SizedBox(height: 20),
                      Row(
                        children: [
                          Icon(Icons.people, color: Colors.blueAccent),
                          SizedBox(width: 10),
                          Text("$spotsLeft lugares disponibles", style: TextStyle(color: Colors.white)),
                        ],
                      ),

                      SizedBox(height: 30),
                      Text("Agenda", style: GoogleFonts.poppins(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold)),
                      SizedBox(height: 10),

                      ...sessions.map((session) => Container(
                        margin: EdgeInsets.only(bottom: 10),
                        padding: EdgeInsets.all(15),
                        decoration: BoxDecoration(
                          color: Color(0xFF151E32),
                          borderRadius: BorderRadius.circular(10),
                          border: Border.all(color: Colors.white10)
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(session['title'], style: GoogleFonts.poppins(color: Colors.white, fontWeight: FontWeight.bold)),
                            SizedBox(height: 5),
                            Row(
                              children: [
                                Icon(Icons.access_time, size: 14, color: Colors.indigoAccent),
                                SizedBox(width: 5),
                                Text("${_formatTime(session['start_time'])} - ${_formatTime(session['end_time'])}", style: TextStyle(color: Colors.grey)),
                              ],
                            ),
                            if (session['speaker_name'] != null)
                               Padding(
                                 padding: const EdgeInsets.only(top: 5.0),
                                 child: Text("Speaker: ${session['speaker_name']}", style: TextStyle(color: Colors.blueGrey)),
                               ),
                          ],
                        ),
                      )).toList(),

                      SizedBox(height: 30),
                      SizedBox(
                        width: double.infinity,
                        child: isRegistered
                        ? ElevatedButton.icon(
                            icon: Icon(Icons.check_circle, color: Colors.white),
                            label: Text("Ya estás registrado"),
                            onPressed: null,
                            style: ElevatedButton.styleFrom(
                              backgroundColor: Colors.green,
                              disabledBackgroundColor: Colors.green.withOpacity(0.5),
                              padding: EdgeInsets.symmetric(vertical: 15),
                            ),
                          )
                        : ElevatedButton(
                            child: Text(spotsLeft > 0 ? "Registrarme" : "Agotado"),
                            onPressed: spotsLeft > 0 ? _register : null,
                            style: ElevatedButton.styleFrom(
                              backgroundColor: Color(0xFF6366F1),
                              padding: EdgeInsets.symmetric(vertical: 15),
                              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                            ),
                          ),
                      )
                    ],
                  ),
                )
              ],
            ),
          );
        },
      ),
    );
  }
}
