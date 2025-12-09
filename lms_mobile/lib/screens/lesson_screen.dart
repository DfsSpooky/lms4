import 'package:flutter/material.dart';
import 'package:youtube_player_flutter/youtube_player_flutter.dart';
import 'package:file_picker/file_picker.dart';
import 'dart:io';
import '../services/api_service.dart';

class LessonScreen extends StatefulWidget {
  final int lessonId;
  final String title;
  final String? content;
  final String? videoUrl;
  final String? lessonType;
  final String? fileUrl;
  final Map<String, dynamic>? userAssignment;

  const LessonScreen({
    super.key, 
    required this.lessonId,
    required this.title, 
    this.content, 
    this.videoUrl,
    this.lessonType,
    this.fileUrl,
    this.userAssignment,
  });

  @override
  State<LessonScreen> createState() => _LessonScreenState();
}

class _LessonScreenState extends State<LessonScreen> {
  bool _isLoading = false;
  YoutubePlayerController? _controller;
  bool _isPlayerReady = false;
  String? _uploadedFileUrl;
  String? _feedback;
  String? _score;

  @override
  void initState() {
    super.initState();
    if (widget.userAssignment != null) {
      _uploadedFileUrl = widget.userAssignment!['file'];
      _feedback = widget.userAssignment!['feedback'];
      _score = widget.userAssignment!['score']?.toString();
    }

    if (widget.videoUrl != null && widget.videoUrl!.isNotEmpty) {
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
      // Logic for when player state changes (optional)
    }
  }

  @override
  void deactivate() {
    // Pauses video while navigating to next page.
    _controller?.pause();
    super.deactivate();
  }

  @override
  void dispose() {
    _controller?.dispose();
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

  void _uploadAssignment() async {
    FilePickerResult? result = await FilePicker.platform.pickFiles();
    if (result != null) {
      File file = File(result.files.single.path!);
      setState(() => _isLoading = true);
      try {
        await ApiService.uploadAssignment(widget.lessonId, file);
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text("Tarea enviada con éxito")));
          // Normally we would reload the data, but for now we mark as uploaded
          setState(() {
            _uploadedFileUrl = "uploaded"; // Placeholder to update UI
          });
        }
      } catch (e) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text("Error al subir tarea")));
        }
      } finally {
        if (mounted) setState(() => _isLoading = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return YoutubePlayerBuilder(
      onExitFullScreen: () {
        // The player forces portraitUp after exiting fullscreen. This overrides the behaviour.
        // SystemChrome.setPreferredOrientations(DeviceOrientation.values);
      },
      player: YoutubePlayer(
        controller: _controller!,
        showVideoProgressIndicator: true,
        progressIndicatorColor: Colors.amber,
        onReady: () {
          _isPlayerReady = true;
        },
        bottomActions: [
          CurrentPosition(),
          ProgressBar(isExpanded: true),
          FullScreenButton(),
        ],
      ),
      builder: (context, player) {
        return Scaffold(
          backgroundColor: const Color(0xFF0B1120),
          appBar: AppBar(
            title: Text(widget.title, style: const TextStyle(color: Colors.white, fontSize: 16)),
            backgroundColor: Colors.transparent,
            iconTheme: const IconThemeData(color: Colors.white),
          ),
          body: Column(
            children: [
              if (_controller != null)
                player
              else if (widget.videoUrl != null && widget.videoUrl!.isNotEmpty)
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

                      const SizedBox(height: 30),

                      if (widget.lessonType == 'assignment') ...[
                         const Divider(color: Colors.white24),
                         const Text(
                          "Tarea / Asignación:",
                          style: TextStyle(color: Colors.orangeAccent, fontWeight: FontWeight.bold, fontSize: 18)
                        ),
                        const SizedBox(height: 10),

                        if (_uploadedFileUrl != null)
                          Container(
                            padding: const EdgeInsets.all(15),
                            decoration: BoxDecoration(
                              color: Colors.green.withValues(alpha: 0.2),
                              borderRadius: BorderRadius.circular(10),
                              border: Border.all(color: Colors.green)
                            ),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Row(
                                  children: [
                                    const Icon(Icons.check_circle, color: Colors.green),
                                    const SizedBox(width: 10),
                                    const Expanded(child: Text("Tarea enviada", style: TextStyle(color: Colors.green, fontWeight: FontWeight.bold))),
                                  ],
                                ),
                                if (_score != null) ...[
                                  const SizedBox(height: 10),
                                  Text("Nota: $_score", style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                                ],
                                if (_feedback != null && _feedback!.isNotEmpty) ...[
                                  const SizedBox(height: 5),
                                  Text("Feedback: $_feedback", style: const TextStyle(color: Colors.white70)),
                                ]
                              ],
                            ),
                          )
                        else
                          Container(
                            padding: const EdgeInsets.all(20),
                            decoration: BoxDecoration(
                              color: const Color(0xFF151E32),
                              borderRadius: BorderRadius.circular(10)
                            ),
                            child: Column(
                              children: [
                                const Icon(Icons.cloud_upload_outlined, color: Colors.white54, size: 50),
                                const SizedBox(height: 10),
                                const Text("Sube tu archivo aquí (PDF, Word, Imagen)", style: TextStyle(color: Colors.white70)),
                                const SizedBox(height: 20),
                                SizedBox(
                                  width: double.infinity,
                                  child: ElevatedButton.icon(
                                    icon: const Icon(Icons.upload_file, color: Colors.white),
                                    label: const Text("Seleccionar Archivo", style: TextStyle(color: Colors.white)),
                                    style: ElevatedButton.styleFrom(
                                      backgroundColor: Colors.indigo,
                                      padding: const EdgeInsets.symmetric(vertical: 15),
                                    ),
                                    onPressed: _isLoading ? null : _uploadAssignment,
                                  ),
                                )
                              ],
                            ),
                          ),
                      ]
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
      },
    );
  }
}
