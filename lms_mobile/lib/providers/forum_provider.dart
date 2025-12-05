import 'package:flutter/material.dart';
import '../services/api_service.dart';

class ForumProvider with ChangeNotifier {
  List<dynamic> _topics = [];
  List<dynamic> _replies = [];
  bool _isLoading = false;
  String? _error;

  List<dynamic> get topics => _topics;
  List<dynamic> get replies => _replies;
  bool get isLoading => _isLoading;
  String? get error => _error;

  Future<void> fetchTopics() async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      _topics = await ApiService.getForumTopics();
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> fetchReplies(int topicId) async {
    _isLoading = true;
    _error = null;
    _replies = [];
    notifyListeners();

    try {
      _replies = await ApiService.getForumReplies(topicId);
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<bool> createTopic(String title, String content, int? courseId) async {
    _isLoading = true;
    notifyListeners();
    try {
      await ApiService.createForumTopic(title, content, courseId);
      await fetchTopics();
      return true;
    } catch (e) {
      _error = e.toString();
      return false;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<bool> postReply(int topicId, String content) async {
    // Note: We don't set global loading here to avoid full screen refresh, 
    // but for simplicity we can or handle it locally in UI. 
    // Let's keep it simple for now.
    try {
      await ApiService.postForumReply(topicId, content);
      await fetchReplies(topicId);
      return true;
    } catch (e) {
      _error = e.toString();
      return false;
    }
  }
}
