import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'catalog_screen.dart';
import 'my_courses_screen.dart';
import 'forum_screen.dart';
import 'profile_screen.dart';
import 'events_screen.dart';
import 'profile_edit_screen.dart';
import '../services/api_service.dart';

class MainScreen extends StatefulWidget {
  @override
  _MainScreenState createState() => _MainScreenState();
}

class _MainScreenState extends State<MainScreen> {
  int _currentIndex = 0;

  final List<Widget> _screens = [
    CatalogScreen(),
    MyCoursesScreen(),
    EventsScreen(),
    ForumScreen(),
    ProfileScreen(),
  ];

  @override
  void initState() {
    super.initState();
    _checkProfileCompletion();
  }

  void _checkProfileCompletion() async {
    try {
      final user = await ApiService.getUserProfile();
      final profile = user['profile'] ?? {};
      final dni = profile['dni'];
      final phone = profile['phone_number'];

      if (dni == null || dni.toString().isEmpty || phone == null || phone.toString().isEmpty) {
        WidgetsBinding.instance.addPostFrameCallback((_) {
          Navigator.push(
             context,
             MaterialPageRoute(builder: (_) => ProfileEditScreen(user: user))
          );
        });
      }
    } catch (e) {
      // Ignore error, maybe offline
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: _screens[_currentIndex],
      bottomNavigationBar: Container(
        decoration: BoxDecoration(
          color: Color(0xFF151E32),
          border: Border(top: BorderSide(color: Colors.white10, width: 0.5)),
        ),
        child: BottomNavigationBar(
          currentIndex: _currentIndex,
          onTap: (index) => setState(() => _currentIndex = index),
          backgroundColor: Color(0xFF151E32),
          selectedItemColor: Color(0xFF6366F1),
          unselectedItemColor: Colors.grey,
          type: BottomNavigationBarType.fixed,
          showUnselectedLabels: true,
          selectedLabelStyle: GoogleFonts.poppins(fontSize: 12, fontWeight: FontWeight.bold),
          unselectedLabelStyle: GoogleFonts.poppins(fontSize: 12),
          items: [
            BottomNavigationBarItem(
              icon: Icon(Icons.explore_outlined),
              activeIcon: Icon(Icons.explore),
              label: 'Explorar',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.school_outlined),
              activeIcon: Icon(Icons.school),
              label: 'Mis Cursos',
            ),
             BottomNavigationBarItem(
              icon: Icon(Icons.calendar_today_outlined),
              activeIcon: Icon(Icons.calendar_today),
              label: 'Eventos',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.forum_outlined),
              activeIcon: Icon(Icons.forum),
              label: 'Comunidad',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.person_outline),
              activeIcon: Icon(Icons.person),
              label: 'Perfil',
            ),
          ],
        ),
      ),
    );
  }
}
