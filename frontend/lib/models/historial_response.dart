import 'package:frontend/models/historial_item.dart';

class HistorialResponse {
  final List<HistorialItem> historialPartidaActual;
  final List<List<HistorialItem>> historialPartidas;

  HistorialResponse({
    required this.historialPartidaActual,
    required this.historialPartidas,
  });

  factory HistorialResponse.fromJson(Map<String, dynamic> json) {
    return HistorialResponse(
      historialPartidaActual: (json['historial_partida_actual'] as List)
          .map((e) => HistorialItem.fromJson(e))
          .toList(),
      historialPartidas: (json['historial_partidas'] as List)
          .map<List<HistorialItem>>((innerList) => innerList
              .map<HistorialItem>((e) => HistorialItem.fromJson(e))
              .toList())
          .toList(),
    );
  }
}
