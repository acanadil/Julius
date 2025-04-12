import 'package:flutter/material.dart';
import 'prediction_row.dart'; // Ensure PredictionRow has the field gameNumber

class PredictionsPage extends StatelessWidget {
  final List<PredictionRow> allRows;

  const PredictionsPage({required this.allRows, Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      //appBar: AppBar(
      //title: const Text('Predictions'),
      //backgroundColor:
      //    Theme.of(context).primaryColor, // Use theme's primary color
      //),
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Card(
            elevation: 4,
            color: Colors.white,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(16),
            ),
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                children: [
                  _buildHeaderRow(context),
                  const SizedBox(height: 16),
                  _buildTable(context),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  // Table Header Row with dynamic theme color
  Widget _buildHeaderRow(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Text(
          'Game Predictions',
          style: TextStyle(
            fontSize: 22,
            fontWeight: FontWeight.bold,
            color: Theme.of(context).primaryColor,
          ),
        ),
      ],
    );
  }

  // Table with rounded corners
  Widget _buildTable(BuildContext context) {
    return Table(
      border: TableBorder.all(
        color: Colors.grey.shade300,
        borderRadius: BorderRadius.circular(12),
      ),
      columnWidths: const {
        0: FlexColumnWidth(1), // Game
        1: FlexColumnWidth(2), // Name
        2: FlexColumnWidth(2), // Prediction
        3: FlexColumnWidth(2), // Result
      },
      children: [
        _buildTableHeader(context),
        for (final row in allRows) _buildDataRow(row, context),
      ],
    );
  }

  // Table Header with dynamic background color
  TableRow _buildTableHeader(BuildContext context) {
    return TableRow(
      decoration: BoxDecoration(
        color: Theme.of(context).primaryColor,
        borderRadius: BorderRadius.circular(12),
      ),
      children: ['Game', 'Name', 'Prediction', 'Result'].map((text) {
        return Padding(
          padding: const EdgeInsets.all(12),
          child: Text(
            text,
            style: TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.bold,
              fontSize: 16,
            ),
          ),
        );
      }).toList(),
    );
  }

  // Data Row with rounded corners and conditional styling based on result match
  TableRow _buildDataRow(PredictionRow row, BuildContext context) {
    bool isMatch = row.prediction.toLowerCase() == row.result.toLowerCase();
    return TableRow(
      decoration: BoxDecoration(
        color: isMatch ? Colors.green.shade100 : Colors.red.shade100,
        borderRadius: BorderRadius.circular(12),
      ),
      children: [
        _buildTextCell(row.gameNumber.toString(), context),
        _buildTextCell(row.name, context),
        _buildStatusCell(row.prediction, context),
        _buildStatusCell(row.result, context),
      ],
    );
  }

  // Generic text cell with padding and dynamic font size
  Widget _buildTextCell(String text, BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(12),
      child: Text(
        text,
        style: TextStyle(
          fontSize: 14,
          fontWeight: FontWeight.w500,
          color: Colors.black87,
        ),
      ),
    );
  }

  // Status cell with icons (check/cross) based on prediction status
  Widget _buildStatusCell(String status, BuildContext context) {
    bool isAccepted = status.toLowerCase() == 'accept';
    return Padding(
      padding: const EdgeInsets.all(12),
      child: Row(
        children: [
          Icon(
            isAccepted ? Icons.check : Icons.close,
            color: isAccepted ? Colors.green : Colors.red,
            size: 18,
          ),
          const SizedBox(width: 8),
          Text(
            status,
            style: TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.w500,
              color: isAccepted ? Colors.green : Colors.red,
            ),
          ),
        ],
      ),
    );
  }
}
