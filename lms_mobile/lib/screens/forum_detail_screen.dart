import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import '../providers/forum_provider.dart';

class ForumDetailScreen extends StatefulWidget {
  final Map<String, dynamic> topic;

  const ForumDetailScreen({super.key, required this.topic});

  @override
  State<ForumDetailScreen> createState() => _ForumDetailScreenState();
}

class _ForumDetailScreenState extends State<ForumDetailScreen> {
  final _replyController = TextEditingController();
  bool _isSending = false;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      Provider.of<ForumProvider>(context, listen: false).fetchReplies(widget.topic['id']);
    });
  }

  void _sendReply() async {
    if (_replyController.text.isEmpty) return;
    setState(() => _isSending = true);
    
    final provider = Provider.of<ForumProvider>(context, listen: false);
    final success = await provider.postReply(widget.topic['id'], _replyController.text);
    
    if (!mounted) return;
    setState(() => _isSending = false);

    if (success) {
      _replyController.clear();
      FocusScope.of(context).unfocus();
    } else {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(provider.error ?? "Error al responder")));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Color(0xFF0B1120),
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        iconTheme: IconThemeData(color: Colors.white),
        title: Text("Discusión", style: TextStyle(color: Colors.white)),
      ),
      body: Column(
        children: [
          Expanded(
            child: SingleChildScrollView(
              padding: EdgeInsets.all(20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Topic Header
                  Text(widget.topic['title'], style: GoogleFonts.poppins(color: Colors.white, fontSize: 22, fontWeight: FontWeight.bold)),
                  SizedBox(height: 10),
                  Row(
                    children: [
                      CircleAvatar(backgroundColor: Colors.indigo, child: Text(widget.topic['user']['username'][0].toUpperCase())),
                      SizedBox(width: 10),
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(widget.topic['user']['username'], style: TextStyle(color: Colors.white)),
                          Text("Autor", style: TextStyle(color: Colors.white38, fontSize: 12)),
                        ],
                      )
                    ],
                  ),
                  SizedBox(height: 20),
                  Text(widget.topic['content'], style: TextStyle(color: Colors.white70, fontSize: 16)),
                  SizedBox(height: 30),
                  Divider(color: Colors.white10),
                  Text("Respuestas", style: GoogleFonts.poppins(color: Colors.white, fontWeight: FontWeight.bold)),
                  SizedBox(height: 20),

                  // Replies
                  Consumer<ForumProvider>(
                    builder: (context, provider, child) {
                      if (provider.isLoading && provider.replies.isEmpty) {
                        return Center(child: CircularProgressIndicator());
                      }
                      
                      final replies = provider.replies;
                      
                      if (replies.isEmpty) {
                         return Text("Sé el primero en responder.", style: TextStyle(color: Colors.grey));
                      }

                      return ListView.builder(
                        shrinkWrap: true,
                        physics: NeverScrollableScrollPhysics(),
                        itemCount: replies.length,
                        itemBuilder: (context, index) {
                          final reply = replies[index];
                          return Container(
                            margin: EdgeInsets.only(bottom: 15),
                            padding: EdgeInsets.all(15),
                            decoration: BoxDecoration(
                              color: Color(0xFF151E32),
                              borderRadius: BorderRadius.circular(10)
                            ),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Row(
                                  children: [
                                    Text(reply['user']['username'], style: TextStyle(color: Colors.indigoAccent, fontWeight: FontWeight.bold)),
                                    Spacer(),
                                    Text("Hace un momento", style: TextStyle(color: Colors.white38, fontSize: 10)),
                                  ],
                                ),
                                SizedBox(height: 8),
                                Text(reply['content'], style: TextStyle(color: Colors.white)),
                              ],
                            ),
                          );
                        },
                      );
                    },
                  )
                ],
              ),
            ),
          ),

          // Input
          Container(
            padding: EdgeInsets.all(10),
            color: Color(0xFF151E32),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _replyController,
                    style: TextStyle(color: Colors.white),
                    decoration: InputDecoration(
                      hintText: "Escribe una respuesta...",
                      hintStyle: TextStyle(color: Colors.white38),
                      border: InputBorder.none,
                    ),
                  ),
                ),
                IconButton(
                  icon: _isSending ? SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2)) : Icon(Icons.send, color: Colors.indigoAccent),
                  onPressed: _isSending ? null : _sendReply,
                )
              ],
            ),
          )
        ],
      ),
    );
  }
}
