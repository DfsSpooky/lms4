import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../services/api_service.dart';

class ProfileEditScreen extends StatefulWidget {
  final Map<String, dynamic> user;

  const ProfileEditScreen({super.key, required this.user});

  @override
  State<ProfileEditScreen> createState() => _ProfileEditScreenState();
}

class _ProfileEditScreenState extends State<ProfileEditScreen> {
  final _formKey = GlobalKey<FormState>();
  late TextEditingController _firstNameController;
  late TextEditingController _lastNameController;
  late TextEditingController _dniController;
  late TextEditingController _phoneController;
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    final user = widget.user;
    final profile = user['profile'] ?? {};
    _firstNameController = TextEditingController(text: user['first_name']);
    _lastNameController = TextEditingController(text: user['last_name']);
    _dniController = TextEditingController(text: profile['dni'] ?? '');
    _phoneController = TextEditingController(text: profile['phone_number'] ?? '');
  }

  void _save() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isLoading = true);

    final data = {
      'first_name': _firstNameController.text,
      'last_name': _lastNameController.text,
      'profile': {
        'dni': _dniController.text,
        'phone_number': _phoneController.text,
      }
    };

    try {
      await ApiService.updateUserProfile(data);
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text("Perfil actualizado")));
      Navigator.pop(context, true); // Return true to indicate update
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text("Error al guardar")));
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return PopScope(
      canPop: false, // Prevent back if mandatory? No, let's allow back but warn if incomplete?
      // Actually, if it's mandatory logic in MainScreen, MainScreen handles the block.
      // Here we just provide the form.
      child: Scaffold(
        backgroundColor: Color(0xFF0B1120),
        appBar: AppBar(
          title: Text("Completar Perfil", style: GoogleFonts.poppins()),
          backgroundColor: Color(0xFF151E32),
          automaticallyImplyLeading: false, // Hide back button if we want to force completion
          actions: [
            // If we are strictly forcing, we might show a logout button?
            // For now, let's assume this screen can be used for both "Force Update" and "Optional Edit".
            // If used from "Force Update", we shouldn't allow back.
          ],
        ),
        body: SingleChildScrollView(
          padding: EdgeInsets.all(20),
          child: Form(
            key: _formKey,
            child: Column(
              children: [
                Text(
                  "Es necesario que completes tu información personal para continuar.",
                  style: GoogleFonts.poppins(color: Colors.white70, fontSize: 14),
                  textAlign: TextAlign.center,
                ),
                SizedBox(height: 30),
                _buildField("Nombre", _firstNameController),
                _buildField("Apellido", _lastNameController),
                _buildField("DNI", _dniController, isNumber: true, validator: (v) => v!.length < 8 ? "DNI inválido" : null),
                _buildField("Celular", _phoneController, isNumber: true, validator: (v) => v!.isEmpty ? "Requerido" : null),
                SizedBox(height: 30),
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    onPressed: _isLoading ? null : _save,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Color(0xFF6366F1),
                      padding: EdgeInsets.symmetric(vertical: 15),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                    ),
                    child: _isLoading
                      ? CircularProgressIndicator(color: Colors.white)
                      : Text("Guardar y Continuar", style: GoogleFonts.poppins(fontWeight: FontWeight.bold)),
                  ),
                )
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildField(String label, TextEditingController controller, {bool isNumber = false, String? Function(String?)? validator}) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 15.0),
      child: TextFormField(
        controller: controller,
        keyboardType: isNumber ? TextInputType.number : TextInputType.text,
        style: TextStyle(color: Colors.white),
        validator: validator ?? (v) => v!.isEmpty ? "Requerido" : null,
        decoration: InputDecoration(
          labelText: label,
          labelStyle: TextStyle(color: Colors.white54),
          filled: true,
          fillColor: Color(0xFF151E32),
          border: OutlineInputBorder(borderRadius: BorderRadius.circular(10), borderSide: BorderSide.none),
        ),
      ),
    );
  }
}
