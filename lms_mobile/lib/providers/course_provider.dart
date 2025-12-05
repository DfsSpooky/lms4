import 'dart:io';
import 'package:flutter/material.dart';
import '../services/api_service.dart';

class CourseProvider with ChangeNotifier {
  List<dynamic> _courses = [];
  List<dynamic> _myCourses = [];
  Map<String, dynamic>? _selectedCourse;
  bool _isLoading = false;
  String? _error;

  List<dynamic> get courses => _courses;
  List<dynamic> get myCourses => _myCourses;
  Map<String, dynamic>? get selectedCourse => _selectedCourse;
  bool get isLoading => _isLoading;
  String? get error => _error;

  Future<void> fetchCourses() async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      _courses = await ApiService.getCourses();
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> fetchMyCourses() async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      _myCourses = await ApiService.getMyCourses();
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> fetchCourseDetail(int courseId) async {
    _isLoading = true;
    _error = null;
    _selectedCourse = null; // Clear previous selection
    notifyListeners();

    try {
      _selectedCourse = await ApiService.getCourseDetail(courseId);
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<bool> enrollInCourse(int courseId, String plan) async {
    _isLoading = true;
    notifyListeners();
    try {
      await ApiService.enrollInCourse(courseId, plan);
      await fetchCourseDetail(courseId); // Refresh detail
      await fetchMyCourses(); // Refresh my courses list
      return true;
    } catch (e) {
      _error = e.toString();
      return false;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<bool> uploadVoucher(int courseId, File file) async {
    _isLoading = true;
    notifyListeners();
    try {
      await ApiService.uploadCourseVoucher(courseId, file);
      await fetchCourseDetail(courseId);
      return true;
    } catch (e) {
      _error = e.toString();
      return false;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
}
