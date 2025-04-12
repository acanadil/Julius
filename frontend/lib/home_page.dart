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

        final newRow = PredictionRow(
          newData['name'],
          newData['prediction'],
          newData['result'],
          widget.gameNumber,
        );

        setState(() {
          _rows.add(newRow);

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

          widget.onNewPrediction(newRow);
        });

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
            // Title below AppBar
            _buildTitle(context),

            // Card containing all content including the table
            Card(
              elevation: 5,
              color: Colors.white,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(15),
              ),
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _buildHeader(),
                    const SizedBox(height: 16),
                    _buildTable(),
                    if (_isGameOver) _buildGameOverButton(),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  // Title under AppBar
  Widget _buildTitle(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16.0),
      child: Text(
        'Predictor',
        style: TextStyle(
          fontSize: 24,
          fontWeight: FontWeight.bold,
          color: Theme.of(context).primaryColor,
        ),
      ),
    );
  }

  // Header for score and game number
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

  // Table content
  Widget _buildTable() {
    return Table(
      border: TableBorder.all(color: Colors.grey.shade300),
      columnWidths: const {
        0: FlexColumnWidth(2), // Name
        1: FlexColumnWidth(2), // Prediction
        2: FlexColumnWidth(2), // Result
      },
      children: [
        _buildHeaderRow(),
        // Only add data rows that have information
        for (final row in _rows)
          if (row.name.isNotEmpty &&
              row.prediction.isNotEmpty &&
              row.result.isNotEmpty)
            _buildDataRow(row),
        // Add empty rows only if there are blank spaces needed (do not mark rows as empty if no data)
        for (int i = _rows.length; i < widget.maxRows; i++) _buildEmptyRow(),
      ],
    );
  }

  // Game over button
  Widget _buildGameOverButton() {
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Center(
        // Centered the "Game Over!" button
        child: ElevatedButton(
          onPressed: () {
            setState(() {
              _isGameOver = false;
              _rows.clear();
              _score = 0;
            });
          },
          style: ElevatedButton.styleFrom(
            primary: Colors.red,
            padding: const EdgeInsets.symmetric(horizontal: 30, vertical: 15),
          ),
          child: const Text(
            'Game Over!',
            style: TextStyle(fontSize: 20),
          ),
        ),
      ),
    );
  }

  // Table header row
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

  // Data row
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

  // Empty row for filling up the table if needed
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

  // Text cell for displaying data
  Widget _buildTextCell(String text) {
    return Padding(
      padding: const EdgeInsets.all(8),
      child: Text(text, style: const TextStyle(fontSize: 16)),
    );
  }

  // Status cell with icons (check/cross) based on prediction status
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
