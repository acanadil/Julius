import 'package:flutter/material.dart';
import 'prediction_row.dart'; // Asegúrate de importar esto
import 'games_page_details.dart';

class GamesPage extends StatelessWidget {
  final List<Map<String, int>> gameHistory;
  final List<PredictionRow> allPredictions;

  const GamesPage({
    required this.gameHistory,
    required this.allPredictions,
    Key? key,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: 16),
            Expanded(
              child: GridView.builder(
                gridDelegate: const SliverGridDelegateWithMaxCrossAxisExtent(
                  maxCrossAxisExtent: 200.0,
                  crossAxisSpacing: 8.0,
                  mainAxisSpacing: 8.0,
                  childAspectRatio: 0.8,
                ),
                itemCount: gameHistory.length,
                itemBuilder: (context, index) {
                  final gameInfo = gameHistory[index];
                  final gameNumber = gameInfo['game']!;

                  final gamePredictions = allPredictions
                      .where((p) => p.gameNumber == gameNumber)
                      .toList();

                  return InkWell(
                    onTap: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (context) => GameDetailPage(
                            gameNumber: gameNumber,
                            score: gameInfo['score']!,
                            predictions: gamePredictions,
                          ),
                        ),
                      );
                    },
                    child: Card(
                      elevation: 5,
                      color: Colors.white,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: Padding(
                        padding: const EdgeInsets.all(8.0),
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Text(
                              'Game $gameNumber',
                              style: const TextStyle(
                                fontSize: 24,
                                fontWeight: FontWeight.bold,
                                color: Colors.blueAccent,
                              ),
                            ),
                            const SizedBox(height: 8),
                            Text(
                              'Score: ${gameInfo['score']}',
                              style: const TextStyle(
                                fontSize: 14,
                                fontWeight: FontWeight.w500,
                                color: Colors.grey,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
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
