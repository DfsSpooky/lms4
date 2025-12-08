import 'dart:io';
import 'package:flutter/material.dart';
import 'package:youtube_player_flutter/youtube_player_flutter.dart';
import 'package:file_picker/file_picker.dart';
import '../services/api_service.dart';

class LessonScreen extends StatefulWidget {
  final int lessonId;
  final String title;
  final String? content;
  final String? videoUrl;
  final String lessonType; // 'video', 'assignment', etc.

  const LessonScreen({
    super.key, 
    required this.lessonId,
    required this.title, 
    this.content, 
    this.videoUrl,
    this.lessonType = 'video'
  });

  @override
  State<LessonScreen> createState() => _LessonScreenState();
}

class _LessonScreenState extends State<LessonScreen> {
  bool _isLoading = false;
  YoutubePlayerController? _controller;
  bool _isPlayerReady = false;

  // Assignment fields
  final TextEditingController _assignmentTextController = TextEditingController();
  File? _selectedFile;

  @override
  void initState() {
    super.initState();
    if (widget.videoUrl != null && widget.videoUrl!.isNotEmpty && widget.lessonType == 'video') {
      final videoId = YoutubePlayer.convertUrlToId(widget.videoUrl!);
      if (videoId != null) {
        _controller = YoutubePlayerController(
          initialVideoId: videoId,
          flags: const YoutubePlayerFlags(
            autoPlay: false,
            mute: false,
          ),
        )..addListener(_listener);
      }
    }
  }

  void _listener() {
    if (_isPlayerReady && mounted && !_controller!.value.isFullScreen) {
      // Logic for when player state changes
    }
  }

  @override
  void deactivate() {
    _controller?.pause();
    super.deactivate();
  }

  @override
  void dispose() {
    _controller?.dispose();
    _assignmentTextController.dispose();
    super.dispose();
  }

  void _markComplete() async {
    setState(() => _isLoading = true);
    try {
      await ApiService.markLessonComplete(widget.lessonId);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text("Lección completada")));
        Navigator.pop(context);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text("Error al marcar como completada")));
      }
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  Future<void> _pickFile() async {
    FilePickerResult? result = await FilePicker.platform.pickFiles();

    if (result != null && result.files.single.path != null) {
      setState(() {
        _selectedFile = File(result.files.single.path!);
      });
    }
  }

  void _submitAssignment() async {
    if (_assignmentTextController.text.isEmpty && _selectedFile == null) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text("Debes agregar texto o un archivo")));
      return;
    }

    setState(() => _isLoading = true);
    try {
      await ApiService.submitAssignment(
        widget.lessonId,
        text: _assignmentTextController.text,
        file: _selectedFile
      );
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text("Tarea enviada correctamente")));
        Navigator.pop(context);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text("Error: $e")));
      }
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  Widget _buildAssignmentUI() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const SizedBox(height: 20),
        const Text("Entregar Tarea", style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold)),
        const SizedBox(height: 10),
        TextField(
          controller: _assignmentTextController,
          maxLines: 4,
          style: const TextStyle(color: Colors.white),
          decoration: const InputDecoration(
            hintText: "Escribe tu respuesta aquí...",
            hintStyle: TextStyle(color: Colors.grey),
            filled: true,
            fillColor: Color(0xFF151E32),
            border: OutlineInputBorder(),
          ),
        ),
        const SizedBox(height: 10),
        Row(
          children: [
            ElevatedButton.icon(
              onPressed: _pickFile,
              icon: const Icon(Icons.attach_file),
              label: const Text("Adjuntar Archivo"),
            ),
            const SizedBox(width: 10),
            if (_selectedFile != null)
              Expanded(
                child: Text(
                  _selectedFile!.path.split('/').last,
                  style: const TextStyle(color: Colors.white),
                  overflow: TextOverflow.ellipsis,
                ),
              )
          ],
        ),
        const SizedBox(height: 20),
        SizedBox(
          width: double.infinity,
          child: ElevatedButton(
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.indigoAccent,
              padding: const EdgeInsets.symmetric(vertical: 15),
            ),
            onPressed: _isLoading ? null : _submitAssignment,
            child: _isLoading
              ? const CircularProgressIndicator(color: Colors.white)
              : const Text("Enviar Tarea", style: TextStyle(color: Colors.white)),
          ),
        )
      ],
    );
  }

  Widget _buildContent(Widget? playerWidget) {
    return Scaffold(
      backgroundColor: const Color(0xFF0B1120),
      appBar: AppBar(
        title: Text(widget.title, style: const TextStyle(color: Colors.white, fontSize: 16)),
        backgroundColor: Colors.transparent,
        iconTheme: const IconThemeData(color: Colors.white),
      ),
      body: Column(
        children: [
          if (playerWidget != null)
            playerWidget
          else if (widget.lessonType == 'video' && widget.videoUrl != null && widget.videoUrl!.isNotEmpty)
            Container(
              height: 200,
              width: double.infinity,
              color: Colors.black,
              child: const Center(child: Text("URL de video inválida", style: TextStyle(color: Colors.white))),
            ),

          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    "Contenido de la lección:",
                    style: TextStyle(color: Colors.indigoAccent, fontWeight: FontWeight.bold, fontSize: 18)
                  ),
                  const Divider(color: Colors.grey),
                  const SizedBox(height: 10),
                  Text(
                    widget.content ?? "Sin contenido de texto.",
                    style: const TextStyle(color: Colors.white, fontSize: 16, height: 1.5),
                  ),

                  if (widget.lessonType == 'assignment')
                    _buildAssignmentUI(),
                ],
              ),
            ),
          ),

          if (widget.lessonType != 'assignment')
            Container(
              padding: const EdgeInsets.all(20),
              color: const Color(0xFF151E32),
              child: SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  icon: const Icon(Icons.check, color: Colors.white),
                  label: const Text("Marcar como Vista", style: TextStyle(color: Colors.white)),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.green,
                    padding: const EdgeInsets.symmetric(vertical: 15),
                  ),
                  onPressed: _isLoading ? null : _markComplete,
                ),
              ),
            )
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    if (_controller != null && widget.lessonType == 'video') {
      return YoutubePlayerBuilder(
        player: YoutubePlayer(
          controller: _controller!,
          showVideoProgressIndicator: true,
          progressIndicatorColor: Colors.amber,
          onReady: () {
            _isPlayerReady = true;
          },
        ),
        builder: (context, player) {
          return _buildContent(player);
        },
      );
    }
    return _buildContent(null);
  }
}
