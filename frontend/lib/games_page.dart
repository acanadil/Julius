import 'package:flutter/material.dart';

class GamesPage extends StatelessWidget {
  final List<Map<String, int>> gameHistory;

  const GamesPage({required this.gameHistory, Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text("Game History",
                style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
            const SizedBox(height: 16),
            Expanded(
              child: ListView.builder(
                itemCount: gameHistory.length,
                itemBuilder: (context, index) {
                  final gameInfo = gameHistory[index];
                  return ListTile(
                    title: Text(
                        "Game ${gameInfo['game']}: Score ${gameInfo['score']}"),
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}
