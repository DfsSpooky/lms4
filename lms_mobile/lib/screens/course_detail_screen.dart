import 'package:flutter/material.dart';
import 'package:cached_network_image/cached_network_image.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:image_picker/image_picker.dart';
import 'dart:io';
import '../services/api_service.dart';
import 'lesson_screen.dart';

class CourseDetailScreen extends StatefulWidget {
  final int courseId;
  final String title;

  const CourseDetailScreen({Key? key, required this.courseId, required this.title}) : super(key: key);

  @override
  _CourseDetailScreenState createState() => _CourseDetailScreenState();
}

class _CourseDetailScreenState extends State<CourseDetailScreen> {
  late Future<Map<String, dynamic>> _courseFuture;
  final ImagePicker _picker = ImagePicker();

  @override
  void initState() {
    super.initState();
    _loadCourse();
  }

  void _loadCourse() {
    _courseFuture = ApiService.getCourseDetail(widget.courseId);
  }

  void _enroll() async {
    showModalBottomSheet(
      context: context,
      backgroundColor: Color(0xFF151E32),
      builder: (context) {
        return Container(
          padding: EdgeInsets.all(20),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text("Elige un plan", style: GoogleFonts.poppins(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold)),
              SizedBox(height: 20),
              ListTile(
                title: Text("Pago Completo", style: TextStyle(color: Colors.white)),
                leading: Icon(Icons.check_circle, color: Colors.greenAccent),
                onTap: () => _processEnrollment('full'),
              ),
              ListTile(
                title: Text("Pago Mensual", style: TextStyle(color: Colors.white)),
                leading: Icon(Icons.calendar_today, color: Colors.indigoAccent),
                onTap: () => _processEnrollment('monthly'),
              ),
            ],
          ),
        );
      }
    );
  }

  void _processEnrollment(String plan) async {
    Navigator.pop(context);
    try {
      await ApiService.enrollInCourse(widget.courseId, plan);
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text("Inscripción realizada. Ahora sube tu voucher.")));
      setState(() {
        _loadCourse();
      });
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text("Error al inscribirse")));
    }
  }

  void _uploadVoucher() async {
    final XFile? image = await _picker.pickImage(source: ImageSource.gallery);
    if (image == null) return;

    try {
      await ApiService.uploadCourseVoucher(widget.courseId, File(image.path));
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text("Voucher subido. Espera aprobación.")));
      setState(() {
        _loadCourse();
      });
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text("Error al subir voucher")));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Color(0xFF0B1120),
      body: FutureBuilder<Map<String, dynamic>>(
        future: _courseFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) 
            return Center(child: CircularProgressIndicator());
          
          if (snapshot.hasError) 
            return Center(child: Text("Error cargando curso", style: GoogleFonts.poppins(color: Colors.white)));

          final courseData = snapshot.data!;
          final modules = courseData['modules'] as List<dynamic>? ?? [];
          final isEnrolled = courseData['is_enrolled'] ?? false;
          final status = courseData['enrollment_status']; // 'pending', 'review', 'approved'

          // Logic to determine access
          final bool isApproved = status == 'approved';
          final bool isPending = status == 'pending';
          final bool isReview = status == 'review';

          return Column(
            children: [
              Expanded(
                child: CustomScrollView(
                  slivers: [
                    SliverAppBar(
                      expandedHeight: 250.0,
                      floating: false,
                      pinned: true,
                      backgroundColor: Color(0xFF0B1120),
                      leading: IconButton(
                        icon: Container(
                          padding: EdgeInsets.all(5),
                          decoration: BoxDecoration(color: Colors.black26, shape: BoxShape.circle),
                          child: Icon(Icons.arrow_back, color: Colors.white)
                        ),
                        onPressed: () => Navigator.pop(context),
                      ),
                      flexibleSpace: FlexibleSpaceBar(
                        title: Text(
                          widget.title,
                          style: GoogleFonts.poppins(
                            color: Colors.white,
                            fontSize: 12,
                            fontWeight: FontWeight.bold,
                            shadows: [Shadow(color: Colors.black, blurRadius: 10)]
                          ),
                        ),
                        background: Stack(
                          fit: StackFit.expand,
                          children: [
                            courseData['thumbnail'] != null
                              ? CachedNetworkImage(
                                  imageUrl: courseData['thumbnail'],
                                  fit: BoxFit.cover,
                                )
                              : Container(color: Colors.indigo),
                            Container(
                              decoration: BoxDecoration(
                                gradient: LinearGradient(
                                  begin: Alignment.topCenter,
                                  end: Alignment.bottomCenter,
                                  colors: [Colors.transparent, Color(0xFF0B1120)],
                                  stops: [0.6, 1.0]
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),

                    SliverToBoxAdapter(
                      child: Padding(
                        padding: const EdgeInsets.all(20.0),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            if (isPending)
                              Container(
                                margin: EdgeInsets.only(bottom: 20),
                                padding: EdgeInsets.all(15),
                                decoration: BoxDecoration(color: Colors.orange.withOpacity(0.2), borderRadius: BorderRadius.circular(10)),
                                child: Row(
                                  children: [
                                    Icon(Icons.warning_amber_rounded, color: Colors.orange),
                                    SizedBox(width: 10),
                                    Expanded(child: Text("Pago pendiente. Sube tu voucher para acceder.", style: TextStyle(color: Colors.orange)))
                                  ],
                                ),
                              ),
                            if (isReview)
                              Container(
                                margin: EdgeInsets.only(bottom: 20),
                                padding: EdgeInsets.all(15),
                                decoration: BoxDecoration(color: Colors.blue.withOpacity(0.2), borderRadius: BorderRadius.circular(10)),
                                child: Row(
                                  children: [
                                    Icon(Icons.access_time, color: Colors.blue),
                                    SizedBox(width: 10),
                                    Expanded(child: Text("Tu pago está en revisión. Te avisaremos pronto.", style: TextStyle(color: Colors.blue)))
                                  ],
                                ),
                              ),

                            Row(
                              children: [
                                _buildBadge(Icons.timer, "${courseData['duration_months'] ?? 1} Meses"),
                                SizedBox(width: 10),
                                _buildBadge(Icons.school, "Certificado"),
                              ],
                            ),
                            SizedBox(height: 20),
                            Text("Sobre este curso",
                              style: GoogleFonts.poppins(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold)),
                            SizedBox(height: 10),
                            Text(
                              courseData['description'] ?? "Sin descripción disponible.",
                              style: GoogleFonts.poppins(color: Colors.grey[400], fontSize: 14, height: 1.5),
                            ),
                            SizedBox(height: 30),
                            Text("Contenido del Curso",
                              style: GoogleFonts.poppins(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold)),
                          ],
                        ),
                      ),
                    ),

                    SliverList(
                      delegate: SliverChildBuilderDelegate(
                        (context, index) {
                          final module = modules[index];
                          final lessons = module['lessons'] as List<dynamic>? ?? [];

                          return Container(
                            margin: EdgeInsets.symmetric(horizontal: 15, vertical: 5),
                            decoration: BoxDecoration(
                              color: Color(0xFF151E32),
                              borderRadius: BorderRadius.circular(15),
                              border: Border.all(color: Colors.white10),
                            ),
                            child: Theme(
                              data: Theme.of(context).copyWith(dividerColor: Colors.transparent),
                              child: ExpansionTile(
                                iconColor: Colors.indigoAccent,
                                collapsedIconColor: Colors.white70,
                                title: Text(
                                  module['title'],
                                  style: GoogleFonts.poppins(color: Colors.white, fontWeight: FontWeight.w600)
                                ),
                                children: lessons.map((lesson) {
                                  final isCompleted = lesson['is_completed'] ?? false;
                                  return ListTile(
                                    contentPadding: EdgeInsets.only(left: 20, right: 20, bottom: 5),
                                    leading: Icon(
                                      isCompleted ? Icons.check_circle : Icons.play_circle_outline,
                                      color: isCompleted ? Colors.greenAccent : Colors.white,
                                    ),
                                    title: Text(lesson['title'], style: GoogleFonts.poppins(color: Colors.grey[300], fontSize: 13)),
                                    trailing: isApproved
                                      ? Icon(Icons.arrow_forward_ios, color: Colors.white24, size: 14)
                                      : Icon(Icons.lock, color: Colors.grey, size: 14),
                                    onTap: isApproved ? () {
                                      Navigator.push(
                                        context,
                                        MaterialPageRoute(
                                          builder: (context) => LessonScreen(
                                            lessonId: lesson['id'],
                                            title: lesson['title'],
                                            content: lesson['content'],
                                            videoUrl: lesson['video_url'],
                                          ),
                                        ),
                                      ).then((_) {
                                        setState(() { _loadCourse(); });
                                      });
                                    } : () {
                                      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text("Debes completar tu inscripción para ver las lecciones.")));
                                    },
                                  );
                                }).toList(),
                              ),
                            ),
                          );
                        },
                        childCount: modules.length,
                      ),
                    ),

                    SliverToBoxAdapter(child: SizedBox(height: 50)),
                  ],
                ),
              ),

              Container(
                padding: EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: Color(0xFF0B1120),
                  border: Border(top: BorderSide(color: Colors.white10))
                ),
                child: _buildBottomAction(isEnrolled, status),
              ),
            ],
          );
        },
      ),
    );
  }

  Widget _buildBottomAction(bool isEnrolled, String? status) {
    if (!isEnrolled) {
      return ElevatedButton(
        onPressed: _enroll,
        style: ElevatedButton.styleFrom(
          backgroundColor: Color(0xFF6366F1),
          padding: EdgeInsets.symmetric(vertical: 15),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          elevation: 10,
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text("Inscribirse ahora", style: GoogleFonts.poppins(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
          ],
        ),
      );
    }

    if (status == 'pending') {
       return ElevatedButton.icon(
        icon: Icon(Icons.upload_file, color: Colors.white),
        onPressed: _uploadVoucher,
        style: ElevatedButton.styleFrom(
          backgroundColor: Colors.orange,
          padding: EdgeInsets.symmetric(vertical: 15),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        ),
        label: Text("Subir Voucher de Pago", style: GoogleFonts.poppins(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
      );
    }

    if (status == 'review') {
       return Center(child: Text("Inscripción en revisión", style: TextStyle(color: Colors.blueAccent, fontWeight: FontWeight.bold)));
    }

    return Center(child: Text("Ya eres parte de este curso", style: TextStyle(color: Colors.greenAccent, fontWeight: FontWeight.bold)));
  }

  Widget _buildBadge(IconData icon, String text) {
    return Container(
      padding: EdgeInsets.symmetric(horizontal: 10, vertical: 5),
      decoration: BoxDecoration(
        color: Colors.white10,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: Colors.white12)
      ),
      child: Row(
        children: [
          Icon(icon, color: Colors.indigoAccent, size: 14),
          SizedBox(width: 5),
          Text(text, style: GoogleFonts.poppins(color: Colors.white70, fontSize: 12)),
        ],
      ),
    );
  }
}
