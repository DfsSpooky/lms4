import 'package:flutter/material.dart';
import 'package:cached_network_image/cached_network_image.dart';
import 'package:google_fonts/google_fonts.dart';
import '../services/api_service.dart';
import 'lesson_screen.dart';

class CourseDetailScreen extends StatelessWidget {
  final int courseId;
  final String title;

  const CourseDetailScreen({Key? key, required this.courseId, required this.title}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Color(0xFF0B1120),
      body: FutureBuilder<Map<String, dynamic>>(
        future: ApiService.getCourseDetail(courseId),
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) 
            return Center(child: CircularProgressIndicator());
          
          if (snapshot.hasError) 
            return Center(child: Text("Error cargando curso", style: GoogleFonts.poppins(color: Colors.white)));

          final courseData = snapshot.data!;
          final modules = courseData['modules'] as List<dynamic>? ?? [];

          return CustomScrollView(
            slivers: [
              // 1. CABECERA FLEXIBLE (Efecto Parallax)
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
                    title,
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
                      // Gradiente oscuro abajo para que se lea el texto
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

              // 2. DESCRIPCIÓN Y CONTENIDO
              SliverToBoxAdapter(
                child: Padding(
                  padding: const EdgeInsets.all(20.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // Badges
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

              // 3. LISTA DE MÓDULOS (Optimizado con SliverList)
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
                            return ListTile(
                              contentPadding: EdgeInsets.only(left: 20, right: 20, bottom: 5),
                              leading: Container(
                                padding: EdgeInsets.all(8),
                                decoration: BoxDecoration(color: Colors.white10, shape: BoxShape.circle),
                                child: Icon(Icons.play_arrow, color: Colors.white, size: 16),
                              ),
                              title: Text(lesson['title'], style: GoogleFonts.poppins(color: Colors.grey[300], fontSize: 13)),
                              trailing: Icon(Icons.lock_open, color: Colors.grey, size: 14), // Icono de estado
                              onTap: () {
                                Navigator.push(
                                  context,
                                  MaterialPageRoute(
                                    builder: (context) => LessonScreen(
                                      title: lesson['title'],
                                      content: lesson['content'],
                                      videoUrl: lesson['video_url'],
                                    ),
                                  ),
                                );
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
              
              // Espacio extra al final
              SliverToBoxAdapter(child: SizedBox(height: 50)),
            ],
          );
        },
      ),
      // Botón flotante moderno para inscribirse (Decorativo por ahora)
      bottomNavigationBar: Container(
        padding: EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: Color(0xFF0B1120),
          border: Border(top: BorderSide(color: Colors.white10))
        ),
        child: ElevatedButton(
          onPressed: () {},
          style: ElevatedButton.styleFrom(
            backgroundColor: Color(0xFF6366F1),
            padding: EdgeInsets.symmetric(vertical: 15),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            elevation: 10,
            shadowColor: Color(0xFF6366F1).withOpacity(0.5)
          ),
          child: Text("Comenzar a aprender", 
            style: GoogleFonts.poppins(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
        ),
      ),
    );
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