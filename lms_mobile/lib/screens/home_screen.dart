import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:cached_network_image/cached_network_image.dart';
import 'package:google_fonts/google_fonts.dart';
import '../services/api_service.dart';
import '../providers/auth_provider.dart';
import 'course_detail_screen.dart';

class HomeScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    // Definimos colores modernos aquí para reusar
    final bgDark = Color(0xFF0B1120);
    final cardColor = Color(0xFF151E32);
    final accentColor = Color(0xFF6366F1); // Indigo vibrante

    return Scaffold(
      backgroundColor: bgDark,
      body: SafeArea(
        child: Column(
          children: [
            // 1. CABECERA PERSONALIZADA
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 20.0),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text("Bienvenido de nuevo,", 
                        style: GoogleFonts.poppins(color: Colors.white70, fontSize: 14)),
                      Text("Estudiante", 
                        style: GoogleFonts.poppins(color: Colors.white, fontSize: 24, fontWeight: FontWeight.bold)),
                    ],
                  ),
                  Container(
                    decoration: BoxDecoration(
                      color: accentColor.withOpacity(0.2),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: IconButton(
                      icon: Icon(Icons.logout, color: accentColor),
                      onPressed: () => Provider.of<AuthProvider>(context, listen: false).logout(),
                    ),
                  )
                ],
              ),
            ),

            // 2. BUSCADOR VISUAL
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 20.0),
              child: Container(
                padding: EdgeInsets.symmetric(horizontal: 15),
                height: 50,
                decoration: BoxDecoration(
                  color: cardColor,
                  borderRadius: BorderRadius.circular(15),
                  border: Border.all(color: Colors.white10),
                ),
                child: Row(
                  children: [
                    Icon(Icons.search, color: Colors.grey),
                    SizedBox(width: 10),
                    Text("Busca un curso...", style: GoogleFonts.poppins(color: Colors.grey)),
                  ],
                ),
              ),
            ),

            SizedBox(height: 25),

            // 3. LISTA DE CURSOS CON DISEÑO PRO
            Expanded(
              child: FutureBuilder<List<dynamic>>(
                future: ApiService.getCourses(),
                builder: (context, snapshot) {
                  if (snapshot.connectionState == ConnectionState.waiting) 
                    return Center(child: CircularProgressIndicator(color: accentColor));
                  
                  if (snapshot.hasError) 
                    return Center(child: Text("Error de conexión", style: TextStyle(color: Colors.white)));

                  final courses = snapshot.data ?? [];

                  if (courses.isEmpty)
                    return Center(child: Text("No hay cursos aún", style: TextStyle(color: Colors.white)));

                  return ListView.builder(
                    padding: EdgeInsets.symmetric(horizontal: 20),
                    itemCount: courses.length,
                    itemBuilder: (context, index) {
                      final course = courses[index];
                      return Container(
                        margin: EdgeInsets.only(bottom: 20),
                        decoration: BoxDecoration(
                          color: cardColor,
                          borderRadius: BorderRadius.circular(20),
                          boxShadow: [
                            BoxShadow(color: Colors.black26, blurRadius: 10, offset: Offset(0, 5))
                          ],
                        ),
                        child: Material(
                          color: Colors.transparent,
                          child: InkWell(
                            borderRadius: BorderRadius.circular(20),
                            onTap: () {
                               Navigator.push(
                                context,
                                MaterialPageRoute(
                                  builder: (context) => CourseDetailScreen(
                                    courseId: course['id'],
                                    title: course['title'],
                                  ),
                                ),
                              );
                            },
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                // Imagen Grande con Etiqueta
                                Stack(
                                  children: [
                                    ClipRRect(
                                      borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
                                      child: SizedBox(
                                        height: 160,
                                        width: double.infinity,
                                        child: course['thumbnail'] != null
                                          ? CachedNetworkImage(
                                              imageUrl: course['thumbnail'],
                                              fit: BoxFit.cover,
                                              placeholder: (context, url) => Container(color: Colors.grey[900]),
                                            )
                                          : Container(color: Colors.indigo),
                                      ),
                                    ),
                                    Positioned(
                                      top: 10, right: 10,
                                      child: Container(
                                        padding: EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                                        decoration: BoxDecoration(
                                          color: Colors.black54,
                                          borderRadius: BorderRadius.circular(10),
                                          // AQUÍ ESTABA EL ERROR: Se eliminó la línea 'backdropFilter'
                                        ),
                                        child: Row(
                                          children: [
                                            Icon(Icons.star, color: Colors.amber, size: 14),
                                            SizedBox(width: 4),
                                            Text(
                                              "${course['average_rating'] ?? '5.0'}", 
                                              style: GoogleFonts.poppins(color: Colors.white, fontSize: 12, fontWeight: FontWeight.bold)
                                            ),
                                          ],
                                        ),
                                      ),
                                    )
                                  ],
                                ),
                                
                                // Información del Curso
                                Padding(
                                  padding: const EdgeInsets.all(15.0),
                                  child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      Text(
                                        course['category_name'] ?? "General",
                                        style: GoogleFonts.poppins(color: accentColor, fontSize: 10, fontWeight: FontWeight.bold),
                                      ),
                                      SizedBox(height: 5),
                                      Text(
                                        course['title'],
                                        style: GoogleFonts.poppins(color: Colors.white, fontSize: 16, fontWeight: FontWeight.w600),
                                        maxLines: 2,
                                        overflow: TextOverflow.ellipsis,
                                      ),
                                      SizedBox(height: 10),
                                      Row(
                                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                        children: [
                                          Row(
                                            children: [
                                              Icon(Icons.person_outline, color: Colors.grey, size: 16),
                                              SizedBox(width: 5),
                                              Text(
                                                course['instructor_name'] ?? "Instructor",
                                                style: GoogleFonts.poppins(color: Colors.grey, fontSize: 12),
                                              ),
                                            ],
                                          ),
                                          Text(
                                            "S/ ${course['price']}",
                                            style: GoogleFonts.poppins(color: Colors.greenAccent, fontSize: 16, fontWeight: FontWeight.bold),
                                          ),
                                        ],
                                      )
                                    ],
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                      );
                    },
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}