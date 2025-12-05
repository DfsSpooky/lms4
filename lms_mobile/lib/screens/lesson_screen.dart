import 'package:flutter/material.dart';
import '../services/api_service.dart';

class LessonScreen extends StatefulWidget {
  final int lessonId;
  final String title;
  final String? content;
  final String? videoUrl;

  const LessonScreen({
    super.key, 
    required this.lessonId,
    required this.title, 
    this.content, 
    this.videoUrl
  });

  @override
  @override
  State<LessonScreen> createState() => _LessonScreenState();
}

class _LessonScreenState extends State<LessonScreen> {
  bool _isLoading = false;

  void _markComplete() async {
    setState(() => _isLoading = true);
    try {
      await ApiService.markLessonComplete(widget.lessonId);
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text("Lección completada")));
      Navigator.pop(context);
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text("Error al marcar como completada")));
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0B1120),
      appBar: AppBar(
        title: Text(widget.title, style: const TextStyle(color: Colors.white, fontSize: 16)),
        backgroundColor: Colors.transparent,
        iconTheme: const IconThemeData(color: Colors.white),
      ),
      body: Column(
        children: [
          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  if (widget.videoUrl != null && widget.videoUrl!.isNotEmpty)
                    Container(
                      height: 200,
                      width: double.infinity,
                      decoration: BoxDecoration(
                        color: Colors.black,
                        border: Border.all(color: Colors.indigoAccent),
                        borderRadius: BorderRadius.circular(10)
                      ),
                      child: Center(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            const Icon(Icons.play_circle_fill, color: Colors.white, size: 50),
                            const SizedBox(height: 10),
                            Text("Video URL:\n${widget.videoUrl}",
                              textAlign: TextAlign.center,
                              style: const TextStyle(color: Colors.white70, fontSize: 10),
                            ),
                          ],
                        ),
                      ),
                    ),

                  const SizedBox(height: 20),

                  const Text(
                    "Contenido de la lección:",
                    style: TextStyle(color: Colors.indigoAccent, fontWeight: FontWeight.bold, fontSize: 18)
                  ),
                  const Divider(color: Colors.grey),

                  const SizedBox(height: 10),

                  Text(
                    widget.content ?? "Sin contenido disponible.",
                    style: const TextStyle(color: Colors.white, fontSize: 16, height: 1.5),
                  ),
                ],
              ),
            ),
          ),
          Container(
            padding: EdgeInsets.all(20),
            color: Color(0xFF151E32),
            child: SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                icon: Icon(Icons.check, color: Colors.white),
                label: Text("Marcar como Vista", style: TextStyle(color: Colors.white)),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.green,
                  padding: EdgeInsets.symmetric(vertical: 15),
                ),
                onPressed: _isLoading ? null : _markComplete,
              ),
            ),
          )
        ],
      ),
    );
  }
}
