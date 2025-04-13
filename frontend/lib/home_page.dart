// lib/home_page.dart

import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:frontend/models/historial_item.dart';
import 'package:http/http.dart' as http;
import 'models/historial_response.dart';

class HomePage extends StatefulWidget {
  const HomePage({Key? key}) : super(key: key);

  @override
  _HomePageState createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  final String _endpointUrl = 'http://172.16.206.124:5000/historial';
  Timer? _timer;
  HistorialResponse? _historialResponse;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _fetchData();
    // Actualización cada 1 segundo
    _timer = Timer.periodic(const Duration(seconds: 1), (_) {
      _fetchData();
    });
  }

  Future<void> _fetchData() async {
    try {
      final response = await http.get(Uri.parse(_endpointUrl));
      if (response.statusCode == 200) {
        final Map<String, dynamic> decodedJson = json.decode(response.body);
        setState(() {
          _historialResponse = HistorialResponse.fromJson(decodedJson);
          _isLoading = false;
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
    super.dispose();
  }

  Widget _buildDataTable(List<HistorialItem> items) {
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: DataTable(
        columns: const [
          DataColumn(label: Text('Nombre')),
          DataColumn(label: Text('Decision')),
          DataColumn(label: Text('Status')),
        ],
        rows: items.map((item) {
          final String nombre = item.clientInfo != null
              ? '${item.clientInfo!.givenNames ?? ""} ${item.clientInfo!.surname ?? ""}'
              : 'N/A';
          final bool accepted = item.decision?.toLowerCase() == 'accept';
          return DataRow(cells: [
            DataCell(Text(nombre)),
            DataCell(Row(
              children: [
                Icon(
                  accepted ? Icons.check : Icons.close,
                  color: accepted ? Colors.green : Colors.red,
                  size: 18,
                ),
                const SizedBox(width: 4),
                Text(item.decision ?? '')
              ],
            )),
            DataCell(Text(item.status ?? '')),
          ]);
        }).toList(),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Historial'),
      ),
      body: _isLoading || _historialResponse == null
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Sección para "historial_partida_actual"
                  Text(
                    'Historial Partida Actual',
                    style: Theme.of(context).textTheme.headlineMedium,
                  ),
                  const SizedBox(height: 8),
                  _buildDataTable(_historialResponse!.historialPartidaActual),
                  const SizedBox(height: 24),
                  // Sección para "historial_partidas"
                  Text(
                    'Historial Partidas',
                    style: Theme.of(context).textTheme.headlineMedium,
                  ),
                  const SizedBox(height: 8),
                  // Puede haber varias partidas, se iteran
                  ..._historialResponse!.historialPartidas.map((partida) {
                    return Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        _buildDataTable(partida),
                        const Divider(height: 32),
                      ],
                    );
                  }).toList(),
                ],
              ),
            ),
    );
  }
}
