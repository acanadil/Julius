// lib/main.dart

import 'package:flutter/material.dart';
import 'package:frontend/game_history_page.dart';
import 'home_page.dart';
import 'predictions_page.dart';
import 'games_page.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'QuackCoders',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: const NavigationPage(),
    );
  }
}

class NavigationPage extends StatelessWidget {
  const NavigationPage({super.key});

  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: 2, // Número de pestañas
      child: Scaffold(
        appBar: AppBar(
          title: const Text('QuackCoders'),
          bottom: const TabBar(
            tabs: [
              Tab(icon: Icon(Icons.home), text: 'Current Game'),
              Tab(icon: Icon(Icons.history), text: 'History'),
              // Tab(icon: Icon(Icons.sports_esports), text: 'Games'),
            ],
          ),
        ),
        body: const TabBarView(
          children: [
            HomePage(),
            GameHistoryPage(),
            // HomePage(),
            // PredictionsPage(),
            // GamesPage(),
          ],
        ),
      ),
    );
  }
}
