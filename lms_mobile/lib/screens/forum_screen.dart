import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import '../providers/forum_provider.dart';
import '../widgets/skeletons.dart';
import 'forum_detail_screen.dart';
import 'create_topic_screen.dart';

class ForumScreen extends StatefulWidget {
  const ForumScreen({super.key});

  @override
  State<ForumScreen> createState() => _ForumScreenState();
}

class _ForumScreenState extends State<ForumScreen> {

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      Provider.of<ForumProvider>(context, listen: false).fetchTopics();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Color(0xFF0B1120),
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        title: Text("Comunidad", style: GoogleFonts.poppins(color: Colors.white, fontWeight: FontWeight.bold)),
        automaticallyImplyLeading: false,
      ),
      floatingActionButton: FloatingActionButton(
        backgroundColor: Color(0xFF6366F1),
        child: Icon(Icons.add, color: Colors.white),
        onPressed: () {
          Navigator.push(
            context,
            MaterialPageRoute(builder: (context) => CreateTopicScreen()),
          );
        },
      ),
      body: Consumer<ForumProvider>(
        builder: (context, provider, child) {
          if (provider.isLoading) {
            return ListView.builder(
              padding: EdgeInsets.all(20),
              itemCount: 5,
              itemBuilder: (_, __) => ForumTopicSkeleton(),
            );
          }
          if (provider.error != null) {
            return Center(child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text("Error cargando foro", style: TextStyle(color: Colors.white)),
                TextButton(
                  onPressed: () => provider.fetchTopics(),
                  child: Text("Reintentar")
                )
              ],
            ));
          }

          final topics = provider.topics;

          if (topics.isEmpty) {
            return Center(child: Text("No hay temas de discusión.", style: TextStyle(color: Colors.white54)));
          }

          return ListView.builder(
            padding: EdgeInsets.all(20),
            itemCount: topics.length,
            itemBuilder: (context, index) {
              final topic = topics[index];
              return Container(
                margin: EdgeInsets.only(bottom: 15),
                decoration: BoxDecoration(
                  color: Color(0xFF151E32),
                  borderRadius: BorderRadius.circular(15),
                ),
                child: Material(
                  color: Colors.transparent,
                  child: InkWell(
                    borderRadius: BorderRadius.circular(15),
                    onTap: () {
                       Navigator.push(
                        context,
                        MaterialPageRoute(builder: (context) => ForumDetailScreen(topic: topic)),
                      );
                    },
                    child: Padding(
                      padding: const EdgeInsets.all(15.0),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            topic['title'],
                            style: GoogleFonts.poppins(color: Colors.white, fontSize: 16, fontWeight: FontWeight.w600),
                          ),
                          SizedBox(height: 5),
                          Text(
                            topic['content'],
                            style: TextStyle(color: Colors.white70),
                            maxLines: 2,
                            overflow: TextOverflow.ellipsis,
                          ),
                          SizedBox(height: 10),
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Text(
                                "Por ${topic['user']['username'] ?? 'Usuario'}",
                                style: TextStyle(color: Colors.white38, fontSize: 12),
                              ),
                              Row(
                                children: [
                                  Icon(Icons.message, size: 14, color: Colors.white38),
                                  SizedBox(width: 4),
                                  Text("${topic['reply_count']}", style: TextStyle(color: Colors.white38, fontSize: 12)),
                                ],
                              )
                            ],
                          )
                        ],
                      ),
                    ),
                  ),
                ),
              );
            },
          );
        },
      ),
    );
  }
}
