import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../services/api_service.dart';
import 'course_detail_screen.dart';

class MyCoursesScreen extends StatefulWidget {
  @override
  _MyCoursesScreenState createState() => _MyCoursesScreenState();
}

class _MyCoursesScreenState extends State<MyCoursesScreen> {
  late Future<List<dynamic>> _myCoursesFuture;

  @override
  void initState() {
    super.initState();
    _myCoursesFuture = ApiService.getMyCourses();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Color(0xFF0B1120),
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        title: Text("Mis Cursos", style: GoogleFonts.poppins(color: Colors.white, fontWeight: FontWeight.bold)),
        automaticallyImplyLeading: false,
      ),
      body: FutureBuilder<List<dynamic>>(
        future: _myCoursesFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return Center(child: CircularProgressIndicator(color: Color(0xFF6366F1)));
          }
          if (snapshot.hasError) {
            return Center(child: Text("Error cargando cursos", style: TextStyle(color: Colors.white)));
          }

          final enrollments = snapshot.data ?? [];

          if (enrollments.isEmpty) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.school_outlined, size: 80, color: Colors.white24),
                  SizedBox(height: 20),
                  Text("Aún no te has inscrito en cursos", style: TextStyle(color: Colors.white54)),
                ],
              ),
            );
          }

          return ListView.builder(
            padding: EdgeInsets.all(20),
            itemCount: enrollments.length,
            itemBuilder: (context, index) {
              final enrollment = enrollments[index];
              final course = enrollment['course'];
              final progress = enrollment['progress_percent'] ?? 0;

              return Container(
                margin: EdgeInsets.only(bottom: 20),
                decoration: BoxDecoration(
                  color: Color(0xFF151E32),
                  borderRadius: BorderRadius.circular(15),
                ),
                child: Material(
                  color: Colors.transparent,
                  child: InkWell(
                    borderRadius: BorderRadius.circular(15),
                    onTap: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (context) => CourseDetailScreen(
                            courseId: course['id'],
                            title: course['title'],
                          ),
                        ),
                      ).then((_) {
                        // Refresh on back
                        setState(() {
                          _myCoursesFuture = ApiService.getMyCourses();
                        });
                      });
                    },
                    child: Padding(
                      padding: const EdgeInsets.all(12.0),
                      child: Row(
                        children: [
                          ClipRRect(
                            borderRadius: BorderRadius.circular(10),
                            child: SizedBox(
                              width: 80,
                              height: 80,
                              child: course['thumbnail'] != null
                                  ? CachedNetworkImage(imageUrl: course['thumbnail'], fit: BoxFit.cover)
                                  : Container(color: Colors.indigo),
                            ),
                          ),
                          SizedBox(width: 15),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  course['title'],
                                  style: GoogleFonts.poppins(color: Colors.white, fontWeight: FontWeight.w600),
                                  maxLines: 2,
                                  overflow: TextOverflow.ellipsis,
                                ),
                                SizedBox(height: 10),
                                LinearProgressIndicator(
                                  value: progress / 100,
                                  backgroundColor: Colors.white10,
                                  color: Colors.greenAccent,
                                  minHeight: 6,
                                  borderRadius: BorderRadius.circular(3),
                                ),
                                SizedBox(height: 5),
                                Text("$progress% Completado", style: TextStyle(color: Colors.white54, fontSize: 12)),
                              ],
                            ),
                          ),
                          Icon(Icons.arrow_forward_ios, color: Colors.white24, size: 16),
                        ],
                      ),
                    ),
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
