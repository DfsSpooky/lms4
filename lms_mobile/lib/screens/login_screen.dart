import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/auth_provider.dart';
import 'signup_screen.dart';
import 'forgot_password_screen.dart';
import 'package:google_fonts/google_fonts.dart';

class LoginScreen extends StatefulWidget {
  @override
  _LoginScreenState createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _userController = TextEditingController();
  final _passController = TextEditingController();
  bool _isLoading = false;

  void _submit() async {
    setState(() => _isLoading = true);
    final auth = Provider.of<AuthProvider>(context, listen: false);
    
    final success = await auth.login(_userController.text, _passController.text);
    
    setState(() => _isLoading = false);
    
    if (!success) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error al iniciar sesión')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Color(0xFF0B1120),
      body: Center(
        child: SingleChildScrollView(
          padding: EdgeInsets.all(20),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.school, size: 80, color: Color(0xFF6366F1)),
              SizedBox(height: 20),
              Text("LMS Academy", style: GoogleFonts.poppins(color: Colors.white, fontSize: 32, fontWeight: FontWeight.bold)),
              SizedBox(height: 10),
              Text("Tu aprendizaje, sin límites", style: GoogleFonts.poppins(color: Colors.white54)),
              SizedBox(height: 50),

              Container(
                decoration: BoxDecoration(
                  color: Color(0xFF151E32),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: TextField(
                  controller: _userController,
                  style: TextStyle(color: Colors.white),
                  decoration: InputDecoration(
                    prefixIcon: Icon(Icons.person, color: Colors.white38),
                    labelText: 'Usuario',
                    labelStyle: TextStyle(color: Colors.white38),
                    border: InputBorder.none,
                    contentPadding: EdgeInsets.symmetric(horizontal: 20, vertical: 15),
                  ),
                ),
              ),
              SizedBox(height: 20),
              Container(
                decoration: BoxDecoration(
                  color: Color(0xFF151E32),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: TextField(
                  controller: _passController,
                  obscureText: true,
                  style: TextStyle(color: Colors.white),
                  decoration: InputDecoration(
                    prefixIcon: Icon(Icons.lock, color: Colors.white38),
                    labelText: 'Contraseña',
                    labelStyle: TextStyle(color: Colors.white38),
                    border: InputBorder.none,
                    contentPadding: EdgeInsets.symmetric(horizontal: 20, vertical: 15),
                  ),
                ),
              ),

              SizedBox(height: 10),
              Align(
                alignment: Alignment.centerRight,
                child: TextButton(
                  onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => ForgotPasswordScreen())),
                  child: Text("¿Olvidaste tu contraseña?", style: TextStyle(color: Colors.white54)),
                ),
              ),

              SizedBox(height: 30),

              SizedBox(
                width: double.infinity,
                height: 50,
                child: ElevatedButton(
                  onPressed: _isLoading ? null : _submit,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Color(0xFF6366F1),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  ),
                  child: _isLoading
                    ? CircularProgressIndicator(color: Colors.white)
                    : Text("Iniciar Sesión", style: GoogleFonts.poppins(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white)),
                ),
              ),

              SizedBox(height: 20),
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text("¿No tienes cuenta?", style: TextStyle(color: Colors.white54)),
                  TextButton(
                    onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => SignupScreen())),
                    child: Text("Regístrate", style: TextStyle(color: Color(0xFF6366F1), fontWeight: FontWeight.bold)),
                  ),
                ],
              )
            ],
          ),
        ),
      ),
    );
  }
}
