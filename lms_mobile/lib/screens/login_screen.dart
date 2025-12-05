import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../config/theme.dart';
import '../widgets/modern_widgets.dart';
import '../providers/auth_provider.dart';
import 'signup_screen.dart';
import 'forgot_password_screen.dart';
import 'package:google_fonts/google_fonts.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _userController = TextEditingController();
  final _passController = TextEditingController();
  bool _isLoading = false;

  void _submit() async {
    setState(() => _isLoading = true);
    final auth = Provider.of<AuthProvider>(context, listen: false);
    
    final success = await auth.login(_userController.text, _passController.text);
    
    if (!mounted) return;
    setState(() => _isLoading = false);
    
    if (!success) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Error al iniciar sesión'),
          backgroundColor: AppTheme.error,
          behavior: SnackBarBehavior.floating,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.background,
      body: Center(
        child: SingleChildScrollView(
          padding: EdgeInsets.all(24),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Container(
                padding: EdgeInsets.all(20),
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: AppTheme.surface,
                  boxShadow: [
                    BoxShadow(
                      color: AppTheme.primary.withOpacity(0.2),
                      blurRadius: 30,
                      spreadRadius: 10,
                    )
                  ],
                ),
                child: Icon(Icons.school_rounded, size: 64, color: AppTheme.primary),
              ),
              SizedBox(height: 32),
              GradientText(
                "LMS Academy",
                gradient: LinearGradient(
                  colors: [Colors.white, AppTheme.primary],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                style: GoogleFonts.outfit(fontSize: 36, fontWeight: FontWeight.bold),
              ),
              SizedBox(height: 8),
              Text(
                "Tu aprendizaje, sin límites",
                style: Theme.of(context).textTheme.bodyLarge,
              ),
              SizedBox(height: 48),

              ModernTextField(
                controller: _userController,
                label: 'Usuario',
                icon: Icons.person_outline,
              ),
              SizedBox(height: 20),
              ModernTextField(
                controller: _passController,
                label: 'Contraseña',
                icon: Icons.lock_outline,
                obscureText: true,
              ),

              SizedBox(height: 12),
              Align(
                alignment: Alignment.centerRight,
                child: TextButton(
                  onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => ForgotPasswordScreen())),
                  child: Text(
                    "¿Olvidaste tu contraseña?",
                    style: TextStyle(color: AppTheme.primary),
                  ),
                ),
              ),

              SizedBox(height: 32),

              ModernButton(
                text: "Iniciar Sesión",
                isLoading: _isLoading,
                onPressed: _submit,
              ),

              SizedBox(height: 32),
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text("¿No tienes cuenta?", style: TextStyle(color: Colors.white54)),
                  TextButton(
                    onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => SignupScreen())),
                    child: Text(
                      "Regístrate",
                      style: TextStyle(color: AppTheme.secondary, fontWeight: FontWeight.bold),
                    ),
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
