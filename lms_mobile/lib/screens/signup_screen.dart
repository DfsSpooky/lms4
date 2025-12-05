import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../services/api_service.dart';

class SignupScreen extends StatefulWidget {
  @override
  _SignupScreenState createState() => _SignupScreenState();
}

class _SignupScreenState extends State<SignupScreen> {
  final _formKey = GlobalKey<FormState>();
  final _usernameController = TextEditingController();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _isLoading = false;

  void _signup() async {
    if (_formKey.currentState!.validate()) {
      setState(() => _isLoading = true);
      try {
        await ApiService.signup(
          _usernameController.text,
          _emailController.text,
          _passwordController.text,
        );
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Cuenta creada exitosamente. Inicia sesión.')),
        );
        Navigator.pop(context);
      } catch (e) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(e.toString().replaceAll('Exception: ', ''))),
        );
      } finally {
        setState(() => _isLoading = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Color(0xFF0B1120),
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        iconTheme: IconThemeData(color: Colors.white),
      ),
      body: SingleChildScrollView(
        padding: EdgeInsets.all(20),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text("Crear Cuenta",
                style: GoogleFonts.poppins(fontSize: 32, fontWeight: FontWeight.bold, color: Colors.white)),
              SizedBox(height: 10),
              Text("Únete a nuestra comunidad de aprendizaje",
                style: GoogleFonts.poppins(color: Colors.white70)),
              SizedBox(height: 30),

              _buildTextField("Usuario", Icons.person, _usernameController),
              SizedBox(height: 20),
              _buildTextField("Email", Icons.email, _emailController),
              SizedBox(height: 20),
              _buildTextField("Contraseña", Icons.lock, _passwordController, obscureText: true),

              SizedBox(height: 40),

              SizedBox(
                width: double.infinity,
                height: 50,
                child: ElevatedButton(
                  onPressed: _isLoading ? null : _signup,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Color(0xFF6366F1),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  ),
                  child: _isLoading
                    ? CircularProgressIndicator(color: Colors.white)
                    : Text("Registrarse", style: GoogleFonts.poppins(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white)),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildTextField(String hint, IconData icon, TextEditingController controller, {bool obscureText = false}) {
    return Container(
      decoration: BoxDecoration(
        color: Color(0xFF151E32),
        borderRadius: BorderRadius.circular(12),
      ),
      child: TextFormField(
        controller: controller,
        obscureText: obscureText,
        style: TextStyle(color: Colors.white),
        validator: (value) => value!.isEmpty ? "Campo requerido" : null,
        decoration: InputDecoration(
          hintText: hint,
          hintStyle: TextStyle(color: Colors.white38),
          prefixIcon: Icon(icon, color: Colors.white38),
          border: InputBorder.none,
          contentPadding: EdgeInsets.symmetric(horizontal: 20, vertical: 15),
        ),
      ),
    );
  }
}
