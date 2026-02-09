import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

import '../config/app_config.dart';

class ApiService {
  // IMPORTANTE: Asegúrate de que esta IP sea la de tu computadora actual.
  static const String baseUrl = AppConfig.apiBaseUrl; 

  // Método auxiliar para obtener los headers con el token
  static Future<Map<String, String>> getHeaders() async {
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('token');
    return {
      'Content-Type': 'application/json',
      if (token != null) 'Authorization': 'Token $token',
    };
  }

  // --- AUTH ---

  static Future<Map<String, dynamic>> login(String username, String password) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/login/'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'username': username, 'password': password}),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Error de credenciales');
    }
  }

  static Future<Map<String, dynamic>> signup(String username, String email, String password) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/signup/'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'username': username,
        'email': email,
        'password': password
      }),
    );

    if (response.statusCode == 201) {
      return jsonDecode(response.body);
    } else {
      final body = jsonDecode(response.body);
      throw Exception(body['error'] ?? 'Error al registrarse');
    }
  }

  static Future<void> resetPassword(String email) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/password-reset/'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'email': email}),
    );

    if (response.statusCode != 200) {
       throw Exception('Error al solicitar recuperación');
    }
  }

  // --- USER ---

  static Future<Map<String, dynamic>> getUserProfile() async {
    final headers = await getHeaders();
    final response = await http.get(Uri.parse('$baseUrl/me/'), headers: headers);

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Error cargando perfil');
    }
  }

  static Future<Map<String, dynamic>> updateUserProfile(Map<String, dynamic> data) async {
    final headers = await getHeaders();
    final response = await http.patch(
      Uri.parse('$baseUrl/me/'),
      headers: headers,
      body: jsonEncode(data)
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Error actualizando perfil');
    }
  }

  // --- COURSES ---

  static Future<List<dynamic>> getCourses() async {
    final headers = await getHeaders();
    final response = await http.get(Uri.parse('$baseUrl/courses/'), headers: headers);

    if (response.statusCode == 200) {
      return jsonDecode(response.body); 
    } else {
      throw Exception('Error al cargar cursos');
    }
  }

  static Future<Map<String, dynamic>> getCourseDetail(int courseId) async {
    final headers = await getHeaders();
    final response = await http.get(
      Uri.parse('$baseUrl/courses/$courseId/'), 
      headers: headers
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Error al cargar curso');
    }
  }

  static Future<List<dynamic>> getMyCourses() async {
    final headers = await getHeaders();
    final response = await http.get(Uri.parse('$baseUrl/my-courses/'), headers: headers);

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Error al cargar mis cursos');
    }
  }

  static Future<void> enrollInCourse(int courseId, String plan) async {
    final headers = await getHeaders();
    final response = await http.post(
      Uri.parse('$baseUrl/courses/$courseId/enroll/'),
      headers: headers,
      body: jsonEncode({'payment_plan': plan})
    );

    if (response.statusCode != 200) {
      throw Exception('Error al inscribirse');
    }
  }

  static Future<void> uploadCourseVoucher(int courseId, File file) async {
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('token');

    var request = http.MultipartRequest('POST', Uri.parse('$baseUrl/courses/$courseId/upload_voucher/'));
    if (token != null) request.headers['Authorization'] = 'Token $token';

    request.files.add(await http.MultipartFile.fromPath('voucher', file.path));

    var response = await request.send();
    if (response.statusCode != 200) {
      throw Exception('Error al subir voucher');
    }
  }

  // --- PROGRESS ---

  static Future<void> markLessonComplete(int lessonId) async {
    final headers = await getHeaders();
    final response = await http.post(
      Uri.parse('$baseUrl/progress/lesson/$lessonId/complete/'),
      headers: headers,
    );
    if (response.statusCode != 200) {
      throw Exception('Error al marcar lección');
    }
  }

  static Future<void> uploadAssignment(int lessonId, File file) async {
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('token');

    var request = http.MultipartRequest('POST', Uri.parse('$baseUrl/progress/lesson/$lessonId/upload_assignment/'));
    if (token != null) request.headers['Authorization'] = 'Token $token';

    request.files.add(await http.MultipartFile.fromPath('file', file.path));

    var response = await request.send();
    if (response.statusCode != 200) {
      throw Exception('Error al subir tarea');
    }
  }

  static Future<Map<String, dynamic>> submitQuiz(int quizId, Map<String, dynamic> answers) async {
    final headers = await getHeaders();
    final response = await http.post(
      Uri.parse('$baseUrl/progress/quiz/$quizId/submit/'),
      headers: headers,
      body: jsonEncode({'answers': answers}),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Error al enviar examen');
    }
  }

  // --- FORUM ---

  static Future<List<dynamic>> getForumTopics() async {
    final headers = await getHeaders();
    final response = await http.get(Uri.parse('$baseUrl/forum/'), headers: headers);
    if (response.statusCode == 200) return jsonDecode(response.body);
    throw Exception('Error cargando foro');
  }

  static Future<void> createForumTopic(String title, String content, int? courseId) async {
    final headers = await getHeaders();
    final body = {
      'title': title,
      'content': content,
      if (courseId != null) 'course': courseId
    };
    final response = await http.post(
      Uri.parse('$baseUrl/forum/'),
      headers: headers,
      body: jsonEncode(body)
    );
    if (response.statusCode != 201) throw Exception('Error creando tema');
  }

  static Future<List<dynamic>> getForumReplies(int topicId) async {
    final headers = await getHeaders();
    final response = await http.get(Uri.parse('$baseUrl/forum/$topicId/replies/'), headers: headers);
    if (response.statusCode == 200) return jsonDecode(response.body);
    throw Exception('Error cargando respuestas');
  }

  static Future<void> postForumReply(int topicId, String content) async {
    final headers = await getHeaders();
    final response = await http.post(
      Uri.parse('$baseUrl/forum/$topicId/reply/'),
      headers: headers,
      body: jsonEncode({'content': content})
    );
    if (response.statusCode != 201) throw Exception('Error publicando respuesta');
  }

  // --- UTILS ---

  static Future<List<dynamic>> getNotifications() async {
    final headers = await getHeaders();
    final response = await http.get(Uri.parse('$baseUrl/notifications/'), headers: headers);
    if (response.statusCode == 200) return jsonDecode(response.body);
    throw Exception('Error cargando notificaciones');
  }

  static Future<void> markNotificationRead(int id) async {
    final headers = await getHeaders();
    await http.post(Uri.parse('$baseUrl/notifications/$id/mark_read/'), headers: headers);
  }

  static Future<List<dynamic>> getInstallments() async {
    final headers = await getHeaders();
    final response = await http.get(Uri.parse('$baseUrl/installments/'), headers: headers);
    if (response.statusCode == 200) return jsonDecode(response.body);
    throw Exception('Error cargando pagos');
  }

  // --- EVENTS ---

  static Future<List<dynamic>> getEvents() async {
    final headers = await getHeaders();
    final response = await http.get(Uri.parse('$baseUrl/events/'), headers: headers);
    if (response.statusCode == 200) return jsonDecode(response.body);
    throw Exception('Error cargando eventos');
  }

  static Future<Map<String, dynamic>> getEventDetail(int eventId) async {
    final headers = await getHeaders();
    final response = await http.get(Uri.parse('$baseUrl/events/$eventId/'), headers: headers);
    if (response.statusCode == 200) return jsonDecode(response.body);
    throw Exception('Error cargando evento');
  }

  static Future<void> registerForEvent(int eventId) async {
    final headers = await getHeaders();
    final response = await http.post(
      Uri.parse('$baseUrl/events/$eventId/register/'),
      headers: headers,
    );
    if (response.statusCode != 201) {
      final body = jsonDecode(response.body);
      throw Exception(body['error'] ?? 'Error registrándose al evento');
    }
  }

  static Future<List<dynamic>> getMyTickets() async {
    final headers = await getHeaders();
    final response = await http.get(Uri.parse('$baseUrl/events/my_tickets/'), headers: headers);
    if (response.statusCode == 200) return jsonDecode(response.body);
    throw Exception('Error cargando mis tickets');
  }
}
