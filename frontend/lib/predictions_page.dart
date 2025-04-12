import 'package:flutter/material.dart';
import 'prediction_row.dart'; // Importing the PredictionRow class

class PredictionsPage extends StatelessWidget {
  final List<PredictionRow> allRows;

  const PredictionsPage({required this.allRows, Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Predictions'),
      ),
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Table(
            border: TableBorder.all(color: Colors.grey.shade300),
            columnWidths: const {
              0: FlexColumnWidth(2),
              1: FlexColumnWidth(2),
              2: FlexColumnWidth(2),
            },
            children: [
              _buildHeaderRow(), // Table header
              for (final row in allRows) _buildDataRow(row), // Data rows
            ],
          ),
        ),
      ),
    );
  }

  // Table header row
  TableRow _buildHeaderRow() {
    return TableRow(
      decoration: const BoxDecoration(color: Colors.black87),
      children: ['Name', 'Prediction', 'Result'].map((text) {
        return Padding(
          padding: const EdgeInsets.all(8),
          child: Text(
            text,
            style: const TextStyle(
                color: Colors.white, fontWeight: FontWeight.bold),
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
      ),
      children: [
        _buildTextCell(row.name),
        _buildStatusCell(row.prediction),
        _buildStatusCell(row.result),
      ],
    );
  }

  // Text cell (for Name)
  Widget _buildTextCell(String text) {
    return Padding(
      padding: const EdgeInsets.all(8),
      child: Text(text),
    );
  }

  // Status cell (for Prediction/Result)
  Widget _buildStatusCell(String status) {
    bool isAccepted = status.toLowerCase() == 'accept';
    return Padding(
      padding: const EdgeInsets.all(8),
      child: Row(
        children: [
          Icon(
            isAccepted ? Icons.check : Icons.close,
            color: isAccepted ? Colors.green : Colors.red,
            size: 18,
          ),
          const SizedBox(width: 4),
          Text(status),
        ],
      ),
    );
  }
}
