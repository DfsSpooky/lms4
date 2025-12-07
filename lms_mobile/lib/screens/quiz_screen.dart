import 'package:flutter/material.dart';
import '../services/api_service.dart';

class QuizScreen extends StatefulWidget {
  final Map<String, dynamic> quizData;

  const QuizScreen({super.key, required this.quizData});

  @override
  State<QuizScreen> createState() => _QuizScreenState();
}

class _QuizScreenState extends State<QuizScreen> {
  final Map<String, dynamic> _answers = {}; // Map questionId -> answerId
  bool _isSubmitting = false;
  Map<String, dynamic>? _result;

  void _submitQuiz() async {
    // Validate if all questions are answered?
    // Backend allows partial submission, but UI should encourage full completion.
    if (_answers.length < (widget.quizData['questions'] as List).length) {
       ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text("Responde todas las preguntas")));
       return;
    }

    setState(() => _isSubmitting = true);
    try {
      final quizId = widget.quizData['id'];
      final result = await ApiService.submitQuiz(quizId, _answers);
      setState(() => _result = result);
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text("Error: $e")));
    } finally {
      if (mounted) setState(() => _isSubmitting = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_result != null) {
      return _buildResultScreen();
    }

    final questions = widget.quizData['questions'] as List<dynamic>;

    return Scaffold(
      backgroundColor: const Color(0xFF0B1120),
      appBar: AppBar(
        title: Text("Examen: ${widget.quizData['title']}", style: const TextStyle(color: Colors.white, fontSize: 16)),
        backgroundColor: Colors.transparent,
        iconTheme: const IconThemeData(color: Colors.white),
      ),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: questions.length,
              itemBuilder: (context, index) {
                final q = questions[index];
                return _buildQuestionCard(q, index + 1);
              },
            ),
          ),
          Container(
            padding: const EdgeInsets.all(20),
            color: const Color(0xFF151E32),
            width: double.infinity,
            child: ElevatedButton(
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.indigoAccent,
                padding: const EdgeInsets.symmetric(vertical: 15)
              ),
              onPressed: _isSubmitting ? null : _submitQuiz,
              child: _isSubmitting
                ? const CircularProgressIndicator(color: Colors.white)
                : const Text("Enviar Examen", style: TextStyle(color: Colors.white, fontSize: 16)),
            ),
          )
        ],
      ),
    );
  }

  Widget _buildQuestionCard(Map<String, dynamic> question, int index) {
    return Card(
      color: const Color(0xFF151E32),
      margin: const EdgeInsets.only(bottom: 20),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              "$index. ${question['text']}",
              style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16),
            ),
            const SizedBox(height: 10),
            ... (question['answers'] as List).map((ans) {
              final isSelected = _answers[question['id'].toString()] == ans['id'];
              return RadioListTile<int>(
                title: Text(ans['text'], style: const TextStyle(color: Colors.white70)),
                value: ans['id'],
                groupValue: _answers[question['id'].toString()],
                activeColor: Colors.indigoAccent,
                onChanged: (val) {
                  setState(() {
                    _answers[question['id'].toString()] = val;
                  });
                },
              );
            }).toList()
          ],
        ),
      ),
    );
  }

  Widget _buildResultScreen() {
    final passed = _result!['passed'] as bool;
    final score = _result!['score'];

    return Scaffold(
      backgroundColor: const Color(0xFF0B1120),
      appBar: AppBar(
        title: const Text("Resultados", style: TextStyle(color: Colors.white)),
        backgroundColor: Colors.transparent,
        automaticallyImplyLeading: false,
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              passed ? Icons.check_circle : Icons.cancel,
              size: 100,
              color: passed ? Colors.green : Colors.red,
            ),
            const SizedBox(height: 20),
            Text(
              passed ? "¡Aprobado!" : "No Aprobado",
              style: TextStyle(color: passed ? Colors.green : Colors.red, fontSize: 24, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 10),
            Text(
              "Tu nota: $score",
              style: const TextStyle(color: Colors.white, fontSize: 20),
            ),
            const SizedBox(height: 40),
            ElevatedButton(
              onPressed: () => Navigator.pop(context),
              child: const Text("Volver al Curso"),
            )
          ],
        ),
      ),
    );
  }
}
