import 'package:flutter/material.dart';
import 'prediction_row.dart';

class GameDetailPage extends StatelessWidget {
  final int gameNumber;
  final int score;
  final List<PredictionRow> predictions;

  const GameDetailPage({
    required this.gameNumber,
    required this.score,
    required this.predictions,
    Key? key,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Game $gameNumber'),
        backgroundColor: Colors.blueAccent,
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Score: $score',
                style:
                    const TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
            // const SizedBox(height: 16),
            // const Text('Prediction History:',
            //     style: TextStyle(fontSize: 20, fontWeight: FontWeight.w600)),
            const SizedBox(height: 8),
            Expanded(
              child: ListView.builder(
                itemCount: predictions.length,
                itemBuilder: (context, index) {
                  final prediction = predictions[index];
                  final match = prediction.prediction.toLowerCase() ==
                      prediction.result.toLowerCase();
                  return Card(
                    color: match ? Colors.green[100] : Colors.red[100],
                    child: ListTile(
                      title: Text(prediction.name),
                      subtitle: Text(
                          'Prediction: ${prediction.prediction} | Result: ${prediction.result}'),
                      trailing: Icon(
                        match ? Icons.check : Icons.close,
                        color: match ? Colors.green : Colors.red,
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
