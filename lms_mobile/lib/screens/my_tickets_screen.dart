import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:qr_flutter/qr_flutter.dart';
import '../services/api_service.dart';
import '../widgets/skeletons.dart';
import 'package:intl/intl.dart';

class MyTicketsScreen extends StatefulWidget {
  const MyTicketsScreen({super.key});

  @override
  State<MyTicketsScreen> createState() => _MyTicketsScreenState();
}

class _MyTicketsScreenState extends State<MyTicketsScreen> {
  bool _isLoading = true;
  List<dynamic> _tickets = [];
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadTickets();
  }

  void _loadTickets() async {
    try {
      final tickets = await ApiService.getMyTickets();
      setState(() {
        _tickets = tickets;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = "Error al cargar tickets";
        _isLoading = false;
      });
    }
  }

  String _formatDate(String? isoDate) {
    if (isoDate == null) return "";
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
      backgroundColor: const Color(0xFF0B1120),
      appBar: AppBar(
        title: Text("Mis Tickets", style: GoogleFonts.poppins(fontWeight: FontWeight.bold, fontSize: 18)),
        backgroundColor: const Color(0xFF151E32),
        elevation: 0,
        iconTheme: const IconThemeData(color: Colors.white),
      ),
      body: _isLoading
        ? ListView.builder(itemCount: 3, padding: const EdgeInsets.all(20), itemBuilder: (_,__) => const EventSkeleton())
        : _error != null
          ? Center(child: Text(_error!, style: GoogleFonts.poppins(color: Colors.redAccent)))
          : _tickets.isEmpty
            ? Center(child: Text("No tienes tickets comprados", style: GoogleFonts.poppins(color: Colors.white54)))
            : ListView.builder(
                padding: const EdgeInsets.all(20),
                itemCount: _tickets.length,
                itemBuilder: (context, index) {
                  final ticket = _tickets[index];
                  final event = ticket['event'] ?? {};

                  return Container(
                    margin: const EdgeInsets.only(bottom: 20),
                    decoration: BoxDecoration(
                      color: const Color(0xFF151E32),
                      borderRadius: BorderRadius.circular(15),
                      border: Border.all(color: Colors.white10)
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        // Header con Evento
                        Container(
                          padding: const EdgeInsets.all(15),
                          decoration: BoxDecoration(
                            color: Colors.indigo.withValues(alpha: 0.1),
                            borderRadius: const BorderRadius.vertical(top: Radius.circular(15))
                          ),
                          child: Row(
                            children: [
                              const Icon(Icons.confirmation_number, color: Colors.indigoAccent),
                              const SizedBox(width: 10),
                              Expanded(
                                child: Text(
                                  event['title'] ?? "Evento",
                                  style: GoogleFonts.poppins(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16),
                                  overflow: TextOverflow.ellipsis,
                                ),
                              )
                            ],
                          ),
                        ),

                        Padding(
                          padding: const EdgeInsets.all(20),
                          child: Column(
                            children: [
                              Row(
                                children: [
                                  Expanded(
                                    child: Column(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [
                                        _infoRow(Icons.calendar_today, _formatDate(event['start_date'])),
                                        const SizedBox(height: 10),
                                        _infoRow(Icons.location_on, event['location'] ?? "Virtual"),
                                        const SizedBox(height: 10),
                                        _infoRow(Icons.person, "Asistente: Yo"),
                                      ],
                                    ),
                                  ),
                                  // QR Code
                                  Container(
                                    decoration: BoxDecoration(
                                      color: Colors.white,
                                      borderRadius: BorderRadius.circular(10)
                                    ),
                                    padding: const EdgeInsets.all(5),
                                    child: QrImageView(
                                      data: ticket['id']?.toString() ?? "unknown",
                                      version: QrVersions.auto,
                                      size: 100.0,
                                      backgroundColor: Colors.white,
                                    ),
                                  ),
                                ],
                              ),
                              const SizedBox(height: 15),
                              const Divider(color: Colors.white10),
                              const SizedBox(height: 10),
                              Text(
                                "ID: ${ticket['id']}",
                                style: GoogleFonts.mono(color: Colors.grey, fontSize: 10),
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

  Widget _infoRow(IconData icon, String text) {
    return Row(
      children: [
        Icon(icon, color: Colors.grey, size: 14),
        const SizedBox(width: 8),
        Expanded(child: Text(text, style: GoogleFonts.poppins(color: Colors.white70, fontSize: 13))),
      ],
    );
  }
}
