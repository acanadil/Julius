// lib/main.dart
import 'package:flutter/material.dart';
import 'home_page.dart';
import 'predictions_page.dart';
import 'games_page.dart';
import 'prediction_row.dart';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Flutter Navigation App',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: NavigationPage(),
    );
  }
}

class NavigationPage extends StatefulWidget {
  @override
  _NavigationPageState createState() => _NavigationPageState();
}

class _NavigationPageState extends State<NavigationPage> {
  List<Widget> _pages = [];
  List<PredictionRow> _allRows = [];
  int _gameScore = 0;
  int _gameNumber = 1;
  List<Map<String, int>> _gameHistory = [];

  @override
  void initState() {
    super.initState();
    _initializePages();
  }

  void _initializePages() {
    _pages = [
      HomePage(
        maxRows: 10,
        gameNumber: _gameNumber,
        onNewPrediction: (PredictionRow newRow) {
          setState(() {
            _allRows.add(newRow);
          });
        },
        onGameOver: (int finalScore) {
          setState(() {
            _gameHistory.add({'game': _gameNumber, 'score': finalScore});
            _gameNumber++;
            _gameScore = 0;
            _initializePages();
          });
        },
        updateScore: (int newScore) {
          setState(() {
            _gameScore = newScore;
          });
        },
      ),
      PredictionsPage(allRows: _allRows),
      GamesPage(gameHistory: _gameHistory),
    ];
  }

  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: 3,
      initialIndex: 0,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('QuackCoders'),
          bottom: TabBar(
            tabs: const [
              Tab(icon: Icon(Icons.home)),
              Tab(icon: Icon(Icons.analytics)),
              Tab(icon: Icon(Icons.history)),
            ],
          ),
        ),
        body: TabBarView(
          children: _pages,
        ),
      ),
    );
  }
}
