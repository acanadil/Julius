PNG_PATTERN = {
    "country": r"(?:[A-Z\s/]+)\s*/\s*([A-Z][a-z\s]+)",
    "country_code": r"( [A-Z]{3} )",
    "passport_num": r"([A-Z]{2}\d{7})",
    "name": r"^([A-Z]+ [A-Z]+ [A-Z]+)$",
    "birth_date": r"(\d{2}-[A-Za-z]{3}-\d{4} )",
    "issue_date": r"( \d{2}-[A-Za-z]{3}-\d{4})",
    "sex": r"(M |F )",
    "expiry_date": r"^(\d{2}-[A-Za-z]{3}-\d{4})$"
}

DOCX_PATTERN = {
    'name': r'Last Name\s+([^\n]+?)\s*First/ Middle Name\s+([^\n]+?)\s*Address',
    'address': r'Address\s+([^\n]+?)\s*Country of Domicile',
    'country': r'Country of Domicile\s+([^\n]+?)\s*Date of birth',
    'dob': r'Date of birth\s+(\d{4}-\d{2}-\d{2})',
    'nationality': r'Nationality\s+([^\n]+?)\s*Passport No',
    'passport': r'Passport No/ Unique ID\s+([^\n]+?)\s*ID Type',
    'id_type': r'ID Type\s+([^\n]+?)\s*ID Issue Date',
    'id_issue': r'ID Issue Date\s+(\d{4}-\d{2}-\d{2})',
    'id_expiry': r'ID Expiry Date\s+(\d{4}-\d{2}-\d{2})',
    'gender': r'Gender\s+.*?☐ Female\s*(☒?) Male',
    'phone': r'Communication Medium\s+Telephone\s+([^\n]+?)\s*E-Mail',
    'email': r'E-Mail\s+([^\n]+?)\s*Account Holder',
    'pep': r'Is the client or associated person a Politically Exposed Person.*?☒?\s*(No|Yes)',
    'marital_status': r'Marital Status\s+.*?☒?\s*(Divorced|Married|Single|Widowed)',
    'education': r'Highest education attained\s+([^\n]+?)\s*Education History',
    'education_history': r'Education History\s+([^\n]+?)\s*Account Holder',
    'employment': r'Current employment and function\s+.*?☒?\s*Employee Since\s+(\d{4})',
    'employer': r'Name Employer\s+([^\n]+?)\s*Position',
    'position': r'Position\s+([^\n]+?)\s*☐ Self-Employed',
    'wealth': r'Total wealth estimated\s+.*?☒?\s*EUR\s+([\d.m-]+)',
    'wealth_origin': r'Origin of wealth\s+.*?☒?\s*Employment\s*.*?☒?\s*Inheritance\s*.*?father,(\d{4}),([^\n]+)',
    'assets': r'Estimated Assets\s+.*?☒?\s*Real Estate EUR\s+([\d]+)\s*.*?☒?\s*Business EUR\s+([\d]+)',
    'income': r'Estimated Total income p.a.\s+.*?☒?\s*<\s*EUR\s+([\d,]+)',
    'income_country': r'Country of main source of income\s+([^\n]+)',
    'account_number': r'Account Number\s+([^\n]+)',
    'commercial': r'Commercial Account\s+.*?☒?\s*(Yes|No)',
    'risk_profile': r'Investment Risk Profile\s+.*?☒?\s*(Low|Moderate|Considerable|High)',
    'mandate': r'Type of Mandate\s+.*?☒?\s*(Advisory|Discretionary)',
    'experience': r'Investment Experience\s+.*?☒?\s*(Inexperienced|Experienced|Expert)',
    'horizon': r'Investment Horizon\s+.*?☒?\s*(Short|Medium|Long-Term)',
    'markets': r'Preferred Markets\s+([^\n]+)',
    'total_aum': r'Total Asset Under Management\s+([\d]+)',
    'transfer_aum': r'Asset Under Management to transfer to BJB\s+([\d]+)'
}

DOCX_CLIENT_DATA = {
    "Client Information": {},
    "Contact Info": {},
    "Personal Info": {},
    "Professional Background": {
        "Employment": {},
        "Wealth": {},
        "Income": {}
    },
    "Account Information": {
        "General": {},
        "Assets": {}
    }
}