import requests
from PyPDF2 import PdfReader
import base64
from io import BytesIO
import re
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import pypandoc
import pattern_defines
import redis
import json
from flask import Flask, request
import time
import google.generativeai as genai
import subprocess

# Dependencies: requests PyPDF2 PIL pytesseract pillow pypandoc_binary redis

global r
# r = redis.Redis(host='localhost', port=6379, db=0)

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'
genai.configure(api_key="AIzaSyC4hlob4t5aNGJEaoNnEnaLuABJFU74EPU")
model = genai.GenerativeModel('gemini-2.0-flash-thinking-exp-01-21')

def post_request():
    """
    POST request to create new game and get the first individual
    
    Args:
        none
    Returns:
        status code -> int
        data -> JSON
    """
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "X-API-Key": "BAh5a5BH_zic0UbuFm8pqlHRcc_ctl1DuYmcDl8-yok"
    }
    response = requests.post("https://hackathon-api.mlo.sehlat.io/game/start", headers=headers, json={"player_name": "QuackCoders"})
    return response.status_code, response.json()


def _data_extract_pdf(data):
    """
    Cast PDF data to JSON

    Args:
        data -> base 64 encoded string with PDF file contents
    Returns:
        structured extracted data -> JSON
    """
    try:
        pdf_stream = BytesIO(base64.b64decode(data))
        reader = PdfReader(pdf_stream)
        if "/AcroForm" not in reader.trailer["/Root"]:
            print("No form fields found in the PDF.")
            return {}
        form_fields = reader.get_fields()
        form_fields = {}
        acro_form = reader.trailer["/Root"]["/AcroForm"]
        if "/Fields" in acro_form:
            for field in acro_form["/Fields"]:
                field_dict = field.get_object()
                field_name = field_dict.get("/T")
                field_value = field_dict.get("/V")
                if field_name:
                    form_fields[field_name] = field_value if field_value else ""
        
        return form_fields
    
    except base64.binascii.Error:
        print("Invalid base64 encoding.")
        return {}
    except Exception as e:
        print(f"Error processing PDF: {str(e)}")
        return {}
    
def _data_extract_txt(data):
    """
    Cast TXT data to JSON

    Args:
        data -> base 64 encoded string with TXT file contents
    Returns:
        structured extracted data -> JSON
    """
    data = base64.b64decode(data).decode("UTF-8")
    result = {}
    
    lines = data.replace('\r\n', '\n').split('\n')
    current_key = None
    current_value = []
    key_pattern = re.compile(r'^(.*?):$')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        key_match = key_pattern.match(line)
        if key_match:
            if current_key is not None:
                result[current_key] = '\n'.join(current_value).strip()
                current_value = []
            
            current_key = key_match.group(1).strip()
        else:
            if current_key is not None:
                current_value.append(line)
    
    if current_key is not None and current_value:
        result[current_key] = '\n'.join(current_value).strip()
    return result

def _data_extract_png(data):

    image = Image.open(BytesIO(base64.b64decode(data))) 

    prompt = "Your objective is to structure into a JSON the information found on this passport, good luck."

    response = model.generate_content(
        [prompt, image],
        stream=False,
    )

    text = response.text.strip().removeprefix("```json").removesuffix("```").strip()

    print(text)

    return json.loads(text)

def _data_extract_docx(data):
    with open(f'tmp_f.docx', 'wb') as f:
        f.write(base64.b64decode(data))
    subprocess.run([
        'libreoffice',
        '--headless',
        '--convert-to', 'pdf',
        '--outdir', "./",
        "tmp_f.docx"
    ], check=True)

    uploaded_file = genai.upload_file("tmp_f.pdf") 

    prompt = """## Objective
Your task is to extract detailed client financial information from documents and structure it according to the specific JSON template provided below. You must capture all relevant client details while maintaining the required structure.
Be careful when picking values from checkboxes, a cross marks the selected option. Think twice. Or thrice.

## Required Output Structure
You must format the extracted data according to this JSON structure:
```json
{
  "Client Information": {
    "Address": "",
    "Country": "",
    "Dob": "",
    "Nationality": "",
    "Id Type": "",
    "Id Issue": "",
    "Id Expiry": "",
    "Gender": "",
    "Account Number": ""
  },
  "Contact Info": {},
  "Personal Info": {
    "Marital Status": ""
  },
  "Professional Background": {
    "Employment": "",
    "Employer": "",
    "Wealth": "",
    "Real Estate": "",
    "Business": "",
    "Income": ""
  },
  "Account Information": {
    "General": {},
    "Commercial Account": "",
    "Mandate Type": "",
    "Investment Experience": "",
    "Investment Horizon": "",
    "Preferred Markets": "",
    "Assets": ""
  }
}
```

## Information Mapping Guide
For each document, carefully search for and map the following information:

### Client Information Section
- **Address**: Complete street address, city, postal code (e.g., "ItÃ¤inen Teatterikuja 22, 45098 Sipoo")
- **Country**: Country of domicile (e.g., "Finland")
- **Dob**: Date of birth in YYYY-MM-DD format (e.g., "1998-03-23")
- **Nationality**: Client's nationality (e.g., "Finnish")
- **Id Type**: Type of identification document (e.g., "passport")
- **Id Issue**: ID issuance date in YYYY-MM-DD format (e.g., "2018-08-05")
- **Id Expiry**: ID expiration date in YYYY-MM-DD format (e.g., "2028-08-04")
- **Gender**: Client's gender (e.g., "Female")
- **Account Number**: Client's account number if available

### Contact Info Section
- Include all telephone numbers with country codes (e.g., "+358 044 459 20 38")
- Include all email addresses (e.g., "katriina.virtanen@elisa.fi")
- Add any additional communication methods as needed

### Personal Info Section
- **Marital Status**: Current marital status (Single, Married, Divorced, or Widowed)
- Add education information (e.g., highest education attained, institutions)
- Include political exposure status (PEP status)
- Add any other relevant personal details

### Professional Background Section
- **Employment**: Current employment status (e.g., "Employee", "Self-Employed")
- **Employer**: Name of current employer (e.g., "CapMan Oyj")
- **Wealth**: Total estimated wealth range (e.g., "EUR 1.5m-5m")
- **Real Estate**: Value of real estate holdings in EUR
- **Business**: Value of business holdings in EUR (e.g., "10000")
- **Income**: Annual income range (e.g., "< EUR 250,000")

### Account Information Section
- **General**: General account details (investment risk profile, etc.)
- **Commercial Account**: Whether it's a commercial account ("Yes" or "No")
- **Mandate Type**: Type of investment mandate (e.g., "Advisory", "Discretionary")
- **Investment Experience**: Level of investment experience (e.g., "Inexperienced", "Experienced", "Expert")
- **Investment Horizon**: Investment time horizon (e.g., "Short", "Medium", "Long-Term")
- **Preferred Markets**: Preferred investment markets (e.g., "Finland")
- **Assets**: Total assets under management in EUR (e.g., "2940000")

## Critical Rules
1. You **MUST** maintain all original field names exactly as shown in the template
2. You **MAY** add new fields within each section to include additional information 
3. You **MUST NOT** remove or modify any of the original field names
4. Use empty strings or null for missing information
5. Format all dates consistently as YYYY-MM-DD
6. Format currency values as numbers without currency symbols
7. Extract all information even if it appears in different sections of the document

## Analysis Process
1. Read the entire document thoroughly first
2. Identify all relevant client information from all sections
3. Map each piece of information to the appropriate field in the JSON structure
4. Verify that all required fields are populated when information is available
5. Ensure additional relevant information is included in appropriate sections

Provide the complete JSON structure with all extracted information properly formatted according to these instructions.
"""
    response = model.generate_content(
        [prompt, uploaded_file],
        stream=False,
    )

    text = response.text.strip().removeprefix("```json").removesuffix("```").strip()
    print(text)

    return json.loads(text)

def cast_files(data, outcome):
    global r
    with open("output.png", "wb") as f:
        f.write(base64.b64decode(data["client_data"]["passport"]))
    with open("output.docx", "wb") as f:
        f.write(base64.b64decode(data["client_data"]["profile"]))
    with open("output.pdf", "wb") as f:
        f.write(base64.b64decode(data["client_data"]["account"]))
    with open("output.txt", "wb") as f:
        f.write(base64.b64decode(data["client_data"]["description"]))

    pdf_data = _data_extract_pdf(data["client_data"]["account"])
    txt_data = _data_extract_txt(data["client_data"]["description"])
    png_data = _data_extract_png(data["client_data"]["passport"])
    docx_data = _data_extract_docx(data["client_data"]["profile"])
    global_dict = {
        "passport": png_data,
        "profile": docx_data,
        "account": pdf_data,
        "description": txt_data,
        # "outcome": outcome,
    }
    t = time.time()
    denei = png_data["passport_num"] if "passport_num" in png_data.keys() else pdf_data["passport_number"] if "passport_number" in pdf_data.keys() else f"PASSPORT_NUMBER_NOT_FOUND-{t}"
    resultao = "right" if outcome == "active" else "wrong"
    # r.set(f"true_{resultao}-{denei}", json.dumps(global_dict, ensure_ascii=False))
    return global_dict
    