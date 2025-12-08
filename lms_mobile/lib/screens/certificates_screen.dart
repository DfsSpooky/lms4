import 'package:flutter/material.dart';
import '../services/api_service.dart';

class CertificatesScreen extends StatefulWidget {
  const CertificatesScreen({super.key});

  @override
  State<CertificatesScreen> createState() => _CertificatesScreenState();
}

class _CertificatesScreenState extends State<CertificatesScreen> {
  bool _isLoading = true;
  List<dynamic> _completedCourses = [];

  @override
  void initState() {
    super.initState();
    _loadCertificates();
  }

  Future<void> _loadCertificates() async {
    try {
      final courses = await ApiService.getMyCourses();
      // Filter for completed courses (progress == 100)
      final completed = courses.where((c) => c['progress_percent'] == 100).toList();

      setState(() {
        _completedCourses = completed;
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text("Error cargando certificados: $e")));
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0B1120),
      appBar: AppBar(
        title: const Text("Mis Certificados", style: TextStyle(color: Colors.white)),
        backgroundColor: const Color(0xFF151E32),
        iconTheme: const IconThemeData(color: Colors.white),
      ),
      body: _isLoading
        ? const Center(child: CircularProgressIndicator())
        : _completedCourses.isEmpty
          ? const Center(child: Text("No tienes certificados aún.\nCompleta un curso al 100%.", textAlign: TextAlign.center, style: TextStyle(color: Colors.white)))
          : ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: _completedCourses.length,
              itemBuilder: (context, index) {
                final enrollment = _completedCourses[index];
                final course = enrollment['course'];

                return Card(
                  color: const Color(0xFF151E32),
                  margin: const EdgeInsets.only(bottom: 20),
                  child: Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: Column(
                      children: [
                        const Icon(Icons.workspace_premium, color: Colors.amber, size: 50),
                        const SizedBox(height: 10),
                        Text(
                          course['title'],
                          style: const TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold),
                          textAlign: TextAlign.center,
                        ),
                        const SizedBox(height: 5),
                        const Text(
                          "Completado con éxito",
                          style: TextStyle(color: Colors.green),
                        ),
                        const SizedBox(height: 20),
                        ElevatedButton.icon(
                          onPressed: () {
                             ScaffoldMessenger.of(context).showSnackBar(
                               const SnackBar(content: Text("Descarga disponible próximamente en web"))
                             );
                          },
                          icon: const Icon(Icons.download),
                          label: const Text("Descargar Certificado"),
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
