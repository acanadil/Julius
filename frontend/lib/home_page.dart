import 'package:flutter/material.dart';
import 'prediction_row.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:async';

class HomePage extends StatefulWidget {
  final int maxRows;
  final Function(PredictionRow) onNewPrediction;
  final Function(int) onGameOver;
  final Function(int) updateScore;
  final int gameNumber;

  const HomePage({
    required this.maxRows,
    required this.onNewPrediction,
    required this.onGameOver,
    required this.updateScore,
    required this.gameNumber,
    Key? key,
  }) : super(key: key);

  @override
  _HomePageState createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  List<PredictionRow> _rows = [];
  Timer? _timer;
  int _score = 0;
  bool _isGameOver = false;
  final String apiUrl = 'http://localhost:5000/api/predictions';
  final ScrollController _scrollController = ScrollController();

  @override
  void initState() {
    super.initState();
    _startPolling();
  }

  void _startPolling() {
    _timer = Timer.periodic(const Duration(seconds: 3), (_) {
      if (!_isGameOver) {
        _fetchData();
      }
    });
  }

  Future<void> _fetchData() async {
    try {
      final response = await http.get(Uri.parse(apiUrl));

      if (response.statusCode == 200) {
        final Map<String, dynamic> newData = json.decode(response.body);

        final predictionMatch = newData['prediction'].toLowerCase() ==
            newData['result'].toLowerCase();

        setState(() {
          _rows.add(PredictionRow(
            newData['name'],
            newData['prediction'],
            newData['result'],
          ));

          if (predictionMatch) {
            _score++;
            widget.updateScore(_score);
          }

          if (!predictionMatch && !_isGameOver) {
            _isGameOver = true;
            widget.onGameOver(_score);

            Future.delayed(const Duration(seconds: 2), () {
              setState(() {
                _score = 0;
                _rows.clear();
                _isGameOver = false;
              });
            });
          }

          if (_rows.length > widget.maxRows) {
            _rows.removeAt(0);
          }

          widget.onNewPrediction(PredictionRow(
            newData['name'],
            newData['prediction'],
            newData['result'],
          ));
        });

        // Scroll automático al final
        WidgetsBinding.instance.addPostFrameCallback((_) {
          _scrollController.animateTo(
            _scrollController.position.maxScrollExtent,
            duration: const Duration(milliseconds: 300),
            curve: Curves.easeOut,
          );
        });
      } else {
        print('Error al cargar datos: ${response.statusCode}');
      }
    } catch (e) {
      print("Error fetching data: $e");
    }
  }

  @override
  void dispose() {
    _timer?.cancel();
    _scrollController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      controller: _scrollController,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            // Header Row: Game Number and Score
            _buildHeader(),

            // Table displaying predictions
            Card(
              elevation: 5,
              color: Colors.white,
              shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(15)),
              child: Padding(
                padding: const EdgeInsets.all(12.0),
                child: Table(
                  border: TableBorder.all(color: Colors.grey.shade300),
                  columnWidths: const {
                    0: FlexColumnWidth(2),
                    1: FlexColumnWidth(2),
                    2: FlexColumnWidth(2),
                  },
                  children: [
                    _buildHeaderRow(),
                    for (final row in _rows) _buildDataRow(row),
                    for (int i = _rows.length; i < widget.maxRows; i++)
                      _buildEmptyRow(),
                  ],
                ),
              ),
            ),

            // Game Over Message
            if (_isGameOver)
              Padding(
                padding: const EdgeInsets.all(16.0),
                child: ElevatedButton(
                  onPressed: () {
                    setState(() {
                      _isGameOver = false;
                      _rows.clear();
                      _score = 0;
                    });
                  },
                  style: ElevatedButton.styleFrom(
                    primary: Colors.red, // Red for Game Over
                    padding: const EdgeInsets.symmetric(
                        horizontal: 30, vertical: 15),
                  ),
                  child: const Text(
                    'Game Over!',
                    style: TextStyle(fontSize: 20),
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }

  // Header Row with Game Number and Score
  Widget _buildHeader() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Text('Game: ${widget.gameNumber}',
            style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
        const SizedBox(width: 32),
        Text('Score: $_score',
            style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
      ],
    );
  }

  // Header for the Table
  TableRow _buildHeaderRow() {
    return TableRow(
      decoration: BoxDecoration(
        color: Colors.blueAccent,
        borderRadius: BorderRadius.circular(10),
      ),
      children: ['Name', 'Prediction', 'Result'].map((text) {
        return Padding(
          padding: const EdgeInsets.all(8),
          child: Text(
            text,
            style: const TextStyle(
                color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16),
          ),
        );
      }).toList(),
    );
  }

  // Data row for each prediction
  TableRow _buildDataRow(PredictionRow row) {
    bool isMatch = row.prediction.toLowerCase() == row.result.toLowerCase();
    return TableRow(
      decoration: BoxDecoration(
        color: isMatch ? Colors.green[100] : Colors.red[100],
        borderRadius: BorderRadius.circular(8),
      ),
      children: [
        _buildTextCell(row.name),
        _buildStatusCell(row.prediction),
        _buildStatusCell(row.result),
      ],
    );
  }

  // Empty row when maxRows is not reached
  TableRow _buildEmptyRow() {
    return TableRow(
      children: List.generate(
        3,
        (index) => const Padding(
          padding: EdgeInsets.all(8),
          child: Text(''),
        ),
      ),
    );
  }

  // Helper to build text cells
  Widget _buildTextCell(String text) {
    return Padding(
      padding: const EdgeInsets.all(8),
      child: Text(text, style: const TextStyle(fontSize: 16)),
    );
  }

  // Helper to build status cells with icons
  Widget _buildStatusCell(String status) {
    bool isAccepted = status.toLowerCase() == 'accept';
    return Padding(
      padding: const EdgeInsets.all(8),
      child: Row(
        children: [
          Icon(
            isAccepted ? Icons.check : Icons.close,
            color: isAccepted ? Colors.green : Colors.red,
            size: 20,
          ),
          const SizedBox(width: 4),
          Text(status, style: const TextStyle(fontSize: 16)),
        ],
      ),
    );
  }
}
