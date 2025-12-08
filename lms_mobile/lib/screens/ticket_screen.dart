import 'package:flutter/material.dart';
import 'package:qr_flutter/qr_flutter.dart';
import 'package:intl/intl.dart';
import '../services/api_service.dart';

class TicketScreen extends StatefulWidget {
  const TicketScreen({super.key});

  @override
  State<TicketScreen> createState() => _TicketScreenState();
}

class _TicketScreenState extends State<TicketScreen> {
  bool _isLoading = true;
  List<dynamic> _tickets = [];

  @override
  void initState() {
    super.initState();
    _loadTickets();
  }

  Future<void> _loadTickets() async {
    try {
      final tickets = await ApiService.getMyTickets();
      setState(() {
        _tickets = tickets;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text("Error cargando tickets: $e")));
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0B1120),
      appBar: AppBar(
        title: const Text("Mis Tickets", style: TextStyle(color: Colors.white)),
        backgroundColor: const Color(0xFF151E32),
        iconTheme: const IconThemeData(color: Colors.white),
      ),
      body: _isLoading
        ? const Center(child: CircularProgressIndicator())
        : _tickets.isEmpty
          ? const Center(child: Text("No tienes tickets aún", style: TextStyle(color: Colors.white)))
          : ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: _tickets.length,
              itemBuilder: (context, index) {
                final ticket = _tickets[index];
                final event = ticket['event'];
                final ticketId = ticket['id'];

                return Card(
                  color: const Color(0xFF151E32),
                  margin: const EdgeInsets.only(bottom: 20),
                  child: Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: Column(
                      children: [
                        Text(
                          event['title'],
                          style: const TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.bold),
                          textAlign: TextAlign.center,
                        ),
                        const SizedBox(height: 10),
                        Text(
                          DateFormat('dd MMMM yyyy - HH:mm').format(DateTime.parse(event['start_date'])),
                          style: const TextStyle(color: Colors.blueAccent),
                        ),
                        const SizedBox(height: 20),
                        Container(
                          padding: const EdgeInsets.all(10),
                          decoration: BoxDecoration(
                            color: Colors.white,
                            borderRadius: BorderRadius.circular(10)
                          ),
                          child: QrImageView(
                            data: ticketId,
                            version: QrVersions.auto,
                            size: 200.0,
                          ),
                        ),
                        const SizedBox(height: 20),
                        Text(
                          "ID: $ticketId",
                          style: const TextStyle(color: Colors.grey, fontSize: 12),
                        ),
                        const SizedBox(height: 5),
                        const Text(
                          "Presenta este código al ingresar",
                          style: TextStyle(color: Colors.white70),
                        )
                      ],
                    ),
                  ),
                );
              },
            ),
    );
  }
}
