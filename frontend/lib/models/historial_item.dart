import 'package:frontend/models/client_info.dart';

class HistorialItem {
  final ClientInfo? clientInfo;
  final String? decision;
  final String? status;

  HistorialItem({
    this.clientInfo,
    this.decision,
    this.status,
  });

  factory HistorialItem.fromJson(Map<String, dynamic> json) {
    return HistorialItem(
      clientInfo: json['client_info'] != null
          ? ClientInfo.fromJson(json['client_info'])
          : null,
      decision: json['decision'],
      status: json['status'],
    );
  }
}
