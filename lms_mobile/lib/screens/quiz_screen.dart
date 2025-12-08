import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../widgets/question_widgets.dart';

class QuizScreen extends StatefulWidget {
  final Map<String, dynamic> quizData;

  const QuizScreen({super.key, required this.quizData});

  @override
  State<QuizScreen> createState() => _QuizScreenState();
}

class _QuizScreenState extends State<QuizScreen> {
  final Map<String, dynamic> _answers = {}; // Map questionId -> dynamic (int, List<int>, String, Map)
  bool _isSubmitting = false;
  Map<String, dynamic>? _result;

  void _submitQuiz() async {
    // Basic validation: Check if all questions have at least some answer
    // Note: Backend handles partial credit/grading, but let's warn user if they missed something.
    final questions = widget.quizData['questions'] as List<dynamic>;
    int answeredCount = 0;

    for (var q in questions) {
      if (_answers.containsKey(q['id'].toString())) {
        final val = _answers[q['id'].toString()];
        if (val != null) {
          if (val is String && val.isNotEmpty) answeredCount++;
          else if (val is List && val.isNotEmpty) answeredCount++;
          else if (val is Map && val.isNotEmpty) answeredCount++;
          else if (val is int) answeredCount++;
        }
      }
    }

    if (answeredCount < questions.length) {
       ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text("Por favor responde todas las preguntas antes de enviar.")));
       // You might want to allow submitting anyway? For now, let's block or just warn.
       // return; // Uncomment to block
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
    final type = question['question_type'] ?? 'single_choice';
    final qId = question['id'].toString();

    Widget content;

    if (type == 'single_choice' || type == 'true_false') {
      content = Column(
        children: (question['answers'] as List).map((ans) {
          final isSelected = _answers[qId] == ans['id'];
          return RadioListTile<int>(
            title: Text(ans['text'], style: const TextStyle(color: Colors.white70)),
            value: ans['id'],
            groupValue: _answers[qId],
            activeColor: Colors.indigoAccent,
            onChanged: (val) {
              setState(() {
                _answers[qId] = val;
              });
            },
          );
        }).toList(),
      );
    } else if (type == 'multiple_choice') {
      final selected = _answers[qId] as List<int>? ?? [];
      content = MultipleChoiceQuestion(
        question: question,
        selectedAnswers: selected,
        onChanged: (newVal) {
          setState(() => _answers[qId] = newVal);
        },
      );
    } else if (type == 'short_answer') {
      final current = _answers[qId] as String? ?? "";
      content = ShortAnswerQuestion(
        currentAnswer: current,
        onChanged: (newVal) {
          setState(() => _answers[qId] = newVal);
        },
      );
    } else if (type == 'ordering') {
      final currentOrder = _answers[qId] as List<int>? ?? [];
      content = OrderingQuestion(
        question: question,
        currentOrder: currentOrder,
        onChanged: (newOrder) {
           // We store the LIST of IDs in the order they are currently in.
           setState(() => _answers[qId] = newOrder);
        },
      );
    } else if (type == 'matching') {
      final currentMatches = _answers[qId] as Map<String, String>? ?? {};
      content = MatchingQuestion(
        question: question,
        currentMatches: currentMatches,
        onChanged: (newMatches) {
          setState(() => _answers[qId] = newMatches);
        },
      );
    } else {
      content = const Text("Tipo de pregunta no soportado", style: TextStyle(color: Colors.red));
    }

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
            if (question['question_type'] == 'multiple_choice')
               const Padding(
                 padding: EdgeInsets.only(top: 5),
                 child: Text("(Selecciona todas las correctas)", style: TextStyle(color: Colors.grey, fontSize: 12)),
               ),
             if (question['question_type'] == 'ordering')
               const Padding(
                 padding: EdgeInsets.only(top: 5),
                 child: Text("(Arrastra para ordenar)", style: TextStyle(color: Colors.grey, fontSize: 12)),
               ),
            const SizedBox(height: 10),
            content,
          ],
        ),
      ),
    );
  }

  Widget _buildResultScreen() {
    final passed = _result!['passed'] as bool;
    final score = _result!['score'];
    final needsGrading = _result!['needs_grading'] as bool? ?? false;

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
              passed ? Icons.check_circle : (needsGrading ? Icons.hourglass_top : Icons.cancel),
              size: 100,
              color: passed ? Colors.green : (needsGrading ? Colors.orange : Colors.red),
            ),
            const SizedBox(height: 20),
            Text(
              needsGrading ? "Pendiente de Calificación" : (passed ? "¡Aprobado!" : "No Aprobado"),
              style: TextStyle(
                  color: needsGrading ? Colors.orange : (passed ? Colors.green : Colors.red),
                  fontSize: 24, fontWeight: FontWeight.bold
              ),
            ),
            const SizedBox(height: 10),
            if (!needsGrading)
              Text(
                "Tu nota: $score",
                style: const TextStyle(color: Colors.white, fontSize: 20),
              ),
             if (needsGrading)
               const Padding(
                 padding: EdgeInsets.all(8.0),
                 child: Text("El profesor revisará tus respuestas abiertas pronto.", style: TextStyle(color: Colors.white70)),
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
