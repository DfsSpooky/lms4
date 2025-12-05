import 'package:flutter/material.dart';
import '../services/api_service.dart';

class EventProvider with ChangeNotifier {
  List<dynamic> _events = [];
  List<dynamic> _myTickets = [];
  Map<String, dynamic>? _selectedEvent;
  bool _isLoading = false;
  String? _error;

  List<dynamic> get events => _events;
  List<dynamic> get myTickets => _myTickets;
  Map<String, dynamic>? get selectedEvent => _selectedEvent;
  bool get isLoading => _isLoading;
  String? get error => _error;

  Future<void> fetchEvents() async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      _events = await ApiService.getEvents();
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> fetchEventDetail(int eventId) async {
    _isLoading = true;
    _error = null;
    _selectedEvent = null;
    notifyListeners();

    try {
      _selectedEvent = await ApiService.getEventDetail(eventId);
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<bool> registerForEvent(int eventId) async {
    _isLoading = true;
    notifyListeners();
    try {
      await ApiService.registerForEvent(eventId);
      await fetchEventDetail(eventId); // Refresh detail
      return true;
    } catch (e) {
      _error = e.toString();
      return false;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> fetchMyTickets() async {
    _isLoading = true;
    _error = null;
    notifyListeners();
    try {
      _myTickets = await ApiService.getMyTickets();
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
}
