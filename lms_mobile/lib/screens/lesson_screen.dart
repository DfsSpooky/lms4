import 'package:flutter/material.dart';

class LessonScreen extends StatelessWidget {
  final String title;
  final String? content;
  final String? videoUrl;

  const LessonScreen({
    Key? key, 
    required this.title, 
    this.content, 
    this.videoUrl
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0B1120), // Fondo oscuro estilo tu backend
      appBar: AppBar(
        title: Text(title, style: const TextStyle(color: Colors.white, fontSize: 16)),
        backgroundColor: Colors.transparent,
        iconTheme: const IconThemeData(color: Colors.white),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 1. Si hay video, mostramos un recuadro (placeholder por ahora)
            if (videoUrl != null && videoUrl!.isNotEmpty)
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
                      Text("Video URL:\n$videoUrl", 
                        textAlign: TextAlign.center,
                        style: const TextStyle(color: Colors.white70, fontSize: 10),
                      ),
                    ],
                  ),
                ),
              ),
            
            const SizedBox(height: 20),

            // 2. Título de la sección
            const Text(
              "Contenido de la lección:", 
              style: TextStyle(color: Colors.indigoAccent, fontWeight: FontWeight.bold, fontSize: 18)
            ),
            const Divider(color: Colors.grey),
            
            const SizedBox(height: 10),

            // 3. Contenido de texto
            Text(
              content ?? "Sin contenido disponible.",
              style: const TextStyle(color: Colors.white, fontSize: 16, height: 1.5),
            ),
          ],
        ),
      ),
    );
  }
}