class ClientInfo {
  final String? birthDate;
  final String? citizenship;
  final String? code;
  final String? country;
  final String? countryCode;
  final String? documentType;
  final String? expiryDate;
  final String? givenNames;
  final String? issueDate;
  final String? passportNumber;
  final String? sex;
  final String? signature;
  final String? surname;
  // final String? machineReadableZone;
  final String? mrz;
  final String? type;
  final String? passportType;
  final String? issuingCountry;
  final Map<String, dynamic>? document;

  ClientInfo({
    this.birthDate,
    this.citizenship,
    this.code,
    this.country,
    this.countryCode,
    this.documentType,
    this.expiryDate,
    this.givenNames,
    this.issueDate,
    this.passportNumber,
    this.sex,
    this.signature,
    this.surname,
    // this.machineReadableZone,
    this.mrz,
    this.type,
    this.passportType,
    this.issuingCountry,
    this.document,
  });

  factory ClientInfo.fromJson(Map<String, dynamic> json) {
    return ClientInfo(
      birthDate: json['birth_date'],
      citizenship: json['citizenship'],
      code: json['code'],
      country: json['country'],
      countryCode: json['country_code'],
      documentType: json['document_type'],
      expiryDate: json['expiry_date'],
      givenNames: json['given_names'],
      issueDate: json['issue_date'],
      passportNumber: json['passport_number'],
      sex: json['sex'],
      signature: json['signature'],
      surname: json['surname'],
      // machineReadableZone: json['machine_readable_zone'],
      mrz: json['mrz'],
      type: json['type'],
      passportType: json['passport_type'],
      issuingCountry: json['issuing_country'],
      document: json['document'],
    );
  }
}
