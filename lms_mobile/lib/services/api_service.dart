import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class ApiService {
  // IMPORTANTE: Asegúrate de que esta IP sea la de tu computadora actual.
  // Si cambia, actualízala aquí.
  static const String baseUrl = 'http://192.168.1.58:8000/api'; 

  // Método auxiliar para obtener los headers con el token (si existe)
  static Future<Map<String, String>> getHeaders() async {
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('token');
    return {
      'Content-Type': 'application/json',
      if (token != null) 'Authorization': 'Token $token',
    };
  }

  // 1. Iniciar Sesión
  static Future<Map<String, dynamic>> login(String username, String password) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/login/'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'username': username, 'password': password}),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Error de credenciales o conexión');
    }
  }

  // 2. Obtener lista de cursos (Para el Home)
  static Future<List<dynamic>> getCourses() async {
    final headers = await getHeaders();
    final response = await http.get(Uri.parse('$baseUrl/courses/'), headers: headers);

    if (response.statusCode == 200) {
      // Django devuelve una lista JSON
      return jsonDecode(response.body); 
    } else {
      throw Exception('Error al cargar cursos');
    }
  }

  // 3. Obtener detalle de un curso específico (Módulos y Lecciones)
  static Future<Map<String, dynamic>> getCourseDetail(int courseId) async {
    final headers = await getHeaders();
    final response = await http.get(
      Uri.parse('$baseUrl/courses/$courseId/'), 
      headers: headers
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Error al cargar el temario del curso');
    }
  }
}