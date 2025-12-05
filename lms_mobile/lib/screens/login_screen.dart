import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/auth_provider.dart';

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
    
    // Usamos las credenciales de tu script populate (admin / admin123)
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
      backgroundColor: Color(0xFF0B1120), // Tu color de fondo del backend
      body: Padding(
        padding: EdgeInsets.all(20),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text("LMS Academy", style: TextStyle(color: Colors.white, fontSize: 32, fontWeight: FontWeight.bold)),
            SizedBox(height: 40),
            TextField(
              controller: _userController,
              style: TextStyle(color: Colors.white),
              decoration: InputDecoration(
                filled: true,
                fillColor: Colors.white10,
                labelText: 'Usuario',
                labelStyle: TextStyle(color: Colors.grey),
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
              ),
            ),
            SizedBox(height: 20),
            TextField(
              controller: _passController,
              obscureText: true,
              style: TextStyle(color: Colors.white),
              decoration: InputDecoration(
                filled: true,
                fillColor: Colors.white10,
                labelText: 'Contraseña',
                labelStyle: TextStyle(color: Colors.grey),
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
              ),
            ),
            SizedBox(height: 40),
            _isLoading 
              ? CircularProgressIndicator()
              : ElevatedButton(
                  onPressed: _submit,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.indigo,
                    padding: EdgeInsets.symmetric(horizontal: 50, vertical: 15)
                  ),
                  child: Text("Entrar", style: TextStyle(color: Colors.white)),
                )
          ],
        ),
      ),
    );
  }
}