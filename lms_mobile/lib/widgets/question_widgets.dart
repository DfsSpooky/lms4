import 'package:flutter/material.dart';

// --- Multiple Choice (Checkbox) ---
class MultipleChoiceQuestion extends StatefulWidget {
  final Map<String, dynamic> question;
  final List<int> selectedAnswers;
  final ValueChanged<List<int>> onChanged;

  const MultipleChoiceQuestion({
    super.key,
    required this.question,
    required this.selectedAnswers,
    required this.onChanged,
  });

  @override
  State<MultipleChoiceQuestion> createState() => _MultipleChoiceQuestionState();
}

class _MultipleChoiceQuestionState extends State<MultipleChoiceQuestion> {
  @override
  Widget build(BuildContext context) {
    final answers = widget.question['answers'] as List<dynamic>;
    return Column(
      children: answers.map((ans) {
        final id = ans['id'] as int;
        final isSelected = widget.selectedAnswers.contains(id);
        return CheckboxListTile(
          title: Text(ans['text'], style: const TextStyle(color: Colors.white70)),
          value: isSelected,
          activeColor: Colors.indigoAccent,
          checkColor: Colors.white,
          controlAffinity: ListTileControlAffinity.leading,
          onChanged: (bool? value) {
            final newSelection = List<int>.from(widget.selectedAnswers);
            if (value == true) {
              newSelection.add(id);
            } else {
              newSelection.remove(id);
            }
            widget.onChanged(newSelection);
          },
        );
      }).toList(),
    );
  }
}

// --- Short Answer (TextField) ---
class ShortAnswerQuestion extends StatelessWidget {
  final String currentAnswer;
  final ValueChanged<String> onChanged;

  const ShortAnswerQuestion({
    super.key,
    required this.currentAnswer,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
      child: TextField(
        controller: TextEditingController(text: currentAnswer)
          ..selection = TextSelection.fromPosition(
              TextPosition(offset: currentAnswer.length)), // Keep cursor at end
        style: const TextStyle(color: Colors.white),
        decoration: InputDecoration(
          hintText: "Escribe tu respuesta aquí...",
          hintStyle: TextStyle(color: Colors.grey[600]),
          enabledBorder: OutlineInputBorder(
            borderSide: BorderSide(color: Colors.white24),
            borderRadius: BorderRadius.circular(8),
          ),
          focusedBorder: OutlineInputBorder(
            borderSide: BorderSide(color: Colors.indigoAccent),
            borderRadius: BorderRadius.circular(8),
          ),
          filled: true,
          fillColor: Colors.black12,
        ),
        onChanged: onChanged,
      ),
    );
  }
}

// --- Ordering (Reorderable List) ---
class OrderingQuestion extends StatefulWidget {
  final Map<String, dynamic> question;
  final List<int> currentOrder; // IDs in order
  final ValueChanged<List<int>> onChanged;

  const OrderingQuestion({
    super.key,
    required this.question,
    required this.currentOrder,
    required this.onChanged,
  });

  @override
  State<OrderingQuestion> createState() => _OrderingQuestionState();
}

class _OrderingQuestionState extends State<OrderingQuestion> {
  late List<dynamic> _localList;

  @override
  void initState() {
    super.initState();
    _initializeList();
  }

  void _initializeList() {
    final originalAnswers = widget.question['answers'] as List<dynamic>;
    if (widget.currentOrder.isEmpty) {
      _localList = List.from(originalAnswers);
       WidgetsBinding.instance.addPostFrameCallback((_) {
         widget.onChanged(_localList.map((e) => e['id'] as int).toList());
       });
    } else {
      _localList = [];
      for (var id in widget.currentOrder) {
        final item = originalAnswers.firstWhere((element) => element['id'] == id, orElse: () => null);
        if (item != null) _localList.add(item);
      }
      for (var item in originalAnswers) {
        if (!widget.currentOrder.contains(item['id'])) {
          _localList.add(item);
        }
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return ReorderableListView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      itemCount: _localList.length,
      itemBuilder: (context, index) {
        final item = _localList[index];
        return Card(
          key: ValueKey(item['id']),
          color: Colors.white10,
          margin: const EdgeInsets.symmetric(vertical: 4),
          child: ListTile(
            leading: Icon(Icons.drag_handle, color: Colors.white54),
            title: Text(item['text'], style: const TextStyle(color: Colors.white)),
          ),
        );
      },
      onReorder: (oldIndex, newIndex) {
        setState(() {
          if (newIndex > oldIndex) newIndex -= 1;
          final item = _localList.removeAt(oldIndex);
          _localList.insert(newIndex, item);
        });
        widget.onChanged(_localList.map((e) => e['id'] as int).toList());
      },
    );
  }
}

// --- Matching (Dropdowns) ---
class MatchingQuestion extends StatefulWidget {
  final Map<String, dynamic> question;
  final Map<String, String> currentMatches; // { "answer_id": "selected_match_text" }
  final ValueChanged<Map<String, String>> onChanged;

  const MatchingQuestion({
    super.key,
    required this.question,
    required this.currentMatches,
    required this.onChanged,
  });

  @override
  State<MatchingQuestion> createState() => _MatchingQuestionState();
}

class _MatchingQuestionState extends State<MatchingQuestion> {
  late List<String> _options;

  @override
  void initState() {
    super.initState();
    final answers = widget.question['answers'] as List<dynamic>;
    // Extract match_text from answers to create the options for the dropdown
    _options = answers
        .map((a) => a['match_text'] as String?)
        .where((s) => s != null && s.isNotEmpty)
        .map((s) => s!)
        .toList();
    _options.shuffle(); // Shuffle options for the user
  }

  @override
  Widget build(BuildContext context) {
    final answers = widget.question['answers'] as List<dynamic>;

    return Column(
      children: answers.map((ans) {
        return Container(
          margin: const EdgeInsets.only(bottom: 10),
          padding: const EdgeInsets.all(10),
          decoration: BoxDecoration(
            border: Border.all(color: Colors.white24),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(ans['text'], style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
              const SizedBox(height: 5),
              DropdownButtonFormField<String>(
                dropdownColor: const Color(0xFF151E32),
                value: widget.currentMatches[ans['id'].toString()],
                items: _options.map((opt) {
                  return DropdownMenuItem(
                    value: opt,
                    child: Text(opt, style: const TextStyle(color: Colors.white)),
                  );
                }).toList(),
                onChanged: (val) {
                  if (val != null) {
                    final newMatches = Map<String, String>.from(widget.currentMatches);
                    newMatches[ans['id'].toString()] = val;
                    widget.onChanged(newMatches);
                  }
                },
                decoration: const InputDecoration(
                  enabledBorder: InputBorder.none,
                ),
                hint: const Text("Selecciona...", style: TextStyle(color: Colors.white54)),
              ),
            ],
          ),
        );
      }).toList(),
    );
  }
}
