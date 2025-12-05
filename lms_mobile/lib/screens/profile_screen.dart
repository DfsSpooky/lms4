import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:google_fonts/google_fonts.dart';
import '../services/api_service.dart';
import '../providers/auth_provider.dart';
import 'notifications_screen.dart';
import 'installments_screen.dart';
import 'profile_edit_screen.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});

  @override
  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  Map<String, dynamic>? _profile;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadProfile();
  }

  void _loadProfile() async {
    try {
      final data = await ApiService.getUserProfile();
      setState(() {
        _profile = data;
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) return Center(child: CircularProgressIndicator());

    final user = _profile ?? {};
    final profile = user['profile'] ?? {};

    return Scaffold(
      backgroundColor: Color(0xFF0B1120),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: EdgeInsets.all(20),
          child: Column(
            children: [
              SizedBox(height: 20),
              CircleAvatar(
                radius: 50,
                backgroundColor: Colors.indigo,
                backgroundImage: profile['avatar'] != null ? NetworkImage(profile['avatar']) : null,
                child: profile['avatar'] == null ? Icon(Icons.person, size: 50, color: Colors.white) : null,
              ),
              SizedBox(height: 15),
              Text(
                "${user['first_name']} ${user['last_name']}",
                style: GoogleFonts.poppins(color: Colors.white, fontSize: 22, fontWeight: FontWeight.bold),
              ),
              Text(
                user['email'] ?? "",
                style: GoogleFonts.poppins(color: Colors.white54),
              ),
              SizedBox(height: 30),

              _buildMenuOption(
                icon: Icons.notifications_outlined,
                title: "Notificaciones",
                onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => NotificationsScreen())),
              ),
              _buildMenuOption(
                icon: Icons.payment_outlined,
                title: "Mis Pagos",
                onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => InstallmentsScreen())),
              ),
              _buildMenuOption(
                icon: Icons.edit_outlined,
                title: "Editar Perfil",
                onTap: () async {
                  final result = await Navigator.push(
                    context,
                    MaterialPageRoute(builder: (_) => ProfileEditScreen(user: _profile!))
                  );
                  if (result == true) _loadProfile();
                },
              ),
              SizedBox(height: 20),
              _buildMenuOption(
                icon: Icons.logout,
                title: "Cerrar Sesión",
                color: Colors.redAccent,
                onTap: () => Provider.of<AuthProvider>(context, listen: false).logout(),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildMenuOption({required IconData icon, required String title, required VoidCallback onTap, Color color = Colors.white}) {
    return Container(
      margin: EdgeInsets.only(bottom: 15),
      decoration: BoxDecoration(
        color: Color(0xFF151E32),
        borderRadius: BorderRadius.circular(15),
      ),
      child: ListTile(
        leading: Container(
          padding: EdgeInsets.all(10),
          decoration: BoxDecoration(
            color: color.withValues(alpha: 0.1),
            shape: BoxShape.circle,
          ),
          child: Icon(icon, color: color),
        ),
        title: Text(title, style: GoogleFonts.poppins(color: Colors.white, fontWeight: FontWeight.w500)),
        trailing: Icon(Icons.arrow_forward_ios, color: Colors.white24, size: 16),
        onTap: onTap,
      ),
    );
  }
}
