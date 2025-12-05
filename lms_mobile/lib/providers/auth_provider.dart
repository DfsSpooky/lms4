import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../services/api_service.dart';

class AuthProvider with ChangeNotifier {
  bool _isAuthenticated = false;
  String? _token;

  bool get isAuthenticated => _isAuthenticated;

  Future<void> checkLoginStatus() async {
    final prefs = await SharedPreferences.getInstance();
    _token = prefs.getString('token');
    _isAuthenticated = _token != null;
    notifyListeners();
  }

  Future<bool> login(String username, String password) async {
    try {
      final data = await ApiService.login(username, password);
      final token = data['token']; // Según tu LoginAPIView en Django
      
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('token', token);
      
      _token = token;
      _isAuthenticated = true;
      notifyListeners();
      return true;
    } catch (e) {
      return false;
    }
  }

  Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('token');
    _isAuthenticated = false;
    notifyListeners();
  }
}