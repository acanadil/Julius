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
import time

# Dependencies: requests PyPDF2 PIL pytesseract pillow pypandoc_binary redis

global r
r = redis.Redis(host='localhost', port=6379, db=0)

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


def _preprocess_image(image):
    """
    Preprocess the image to improve OCR accuracy.
    
    Args:
        image: PIL Image object
    Returns:
        Processed PIL Image object
    """
    image = image.convert('L')
    image = image.resize((image.width * 2, image.height * 2), Image.Resampling.LANCZOS)
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2.0)
    enhancer = ImageEnhance.Sharpness(image)
    image = enhancer.enhance(2.0)
    image = image.filter(ImageFilter.MedianFilter(size=3))
    image = image.point(lambda x: 0 if x < 128 else 255, '1')
    
    return image

def _data_extract_png(data):
    """
    Cast PNG data to JSON using OCR to extract text from the picture

    Args:
        data -> base 64 encoded string with PNG file contents
    Returns:
        structured extracted data -> JSON
    """

    image = _preprocess_image(Image.open(BytesIO(base64.b64decode(data))))
    
    text = pytesseract.image_to_string(image, config=r'--oem 3 --psm 6')
    text = re.sub(r'\n+', '\n', text).strip()
    lines = text.split('\n')

    passport_data = {}
    
    field_patterns = pattern_defines.PNG_PATTERN
    
    current_field = None
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        for field, pattern in field_patterns.items():
            match = re.search(pattern, line)
            if match:
                if field == "country":
                    passport_data[field] = match.group(1)
                elif field == "country_code":
                    passport_data[field] = match.group(1)
                elif field == "passport_num":
                    passport_data[field] = match.group(1)
                elif field == "name":
                    passport_data[field] = match.group(1)
                elif field == "birth_date":
                    passport_data[field] = match.group(1)
                elif field == "sex":
                    passport_data[field] = match.group(1)
                elif field == "issue_date":
                    passport_data[field] = match.group(1)
                elif field == "expiry_date":
                    passport_data[field] = match.group(1)
                else:
                    passport_data[field] = match.group(1)
                current_field = field
                break
        else:
            if current_field and current_field not in passport_data:
                passport_data[current_field] = line

    passport_data["extra_data"] = " ".join(lines[-3:]).strip().replace(" ", "")
    return passport_data

def _data_extract_docx(data):
    with open(f'tmp_f.docx', 'wb') as f:
        f.write(base64.b64decode(data))
    text = pypandoc.convert_file("tmp_f.docx", 'plain')
    
    client_data = pattern_defines.DOCX_CLIENT_DATA
    
    def clean_text(value):
        return value.strip().replace('\n', ' ').strip() if value else ''

    def is_checked(value):
        if value:
            return '☒' in value
        return False

    patterns = pattern_defines.DOCX_PATTERN

    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.DOTALL)
        if match:
            if key == 'name':
                client_data["Client Information"]["Last Name"] = clean_text(match.group(1))
                client_data["Client Information"]["First Name"] = clean_text(match.group(2))
            elif key == 'gender':
                if match.group(1) is not None and is_checked(match.group(1)):
                    client_data["Client Information"]["Gender"] = "Female"
                elif match.group(2) is not None and is_checked(match.group(2)):
                    client_data["Client Information"]["Gender"] = "Male"
            elif key == 'phone':
                client_data["Contact Info"]["Telephone"] = clean_text(match.group(1))
            elif key == 'email':
                client_data["Contact Info"]["Email"] = clean_text(match.group(1))
            elif key == 'pep':
                client_data["Personal Info"]["Politically Exposed Person"] = match.group(1) == "Yes"
            elif key == 'marital_status':
                client_data["Personal Info"]["Marital Status"] = clean_text(match.group(1))
            elif key == 'education':
                client_data["Personal Info"]["Highest Education"] = clean_text(match.group(1))
            elif key == 'education_history':
                client_data["Personal Info"]["Education History"] = clean_text(match.group(1))
            elif key == 'employment':
                client_data["Professional Background"]["Employment"]["Status"] = "Employee"
                client_data["Professional Background"]["Employment"]["Since"] = clean_text(match.group(1))
            elif key == 'employer':
                client_data["Professional Background"]["Employment"]["Employer"] = clean_text(match.group(1))
            elif key == 'position':
                client_data["Professional Background"]["Employment"]["Position"] = clean_text(match.group(1))
            elif key == 'wealth':
                client_data["Professional Background"]["Wealth"]["Total Estimated"] = clean_text(match.group(1))
            elif key == 'wealth_origin':
                client_data["Professional Background"]["Wealth"]["Inheritance Year"] = clean_text(match.group(1))
                client_data["Professional Background"]["Wealth"]["Inherited From"] = clean_text(match.group(2))
            elif key == 'assets':
                client_data["Professional Background"]["Wealth"]["Real Estate"] = int(match.group(1))
                client_data["Professional Background"]["Wealth"]["Business"] = int(match.group(2))
            elif key == 'income':
                client_data["Professional Background"]["Income"]["Total Estimated"] = clean_text(match.group(1))
            elif key == 'income_country':
                client_data["Professional Background"]["Income"]["Country"] = clean_text(match.group(1))
            elif key == 'commercial':
                client_data["Account Information"]["General"]["Commercial Account"] = match.group(1) == "Yes"
            elif key == 'risk_profile':
                client_data["Account Information"]["General"]["Risk Profile"] = clean_text(match.group(1))
            elif key == 'mandate':
                client_data["Account Information"]["General"]["Mandate Type"] = clean_text(match.group(1))
            elif key == 'experience':
                client_data["Account Information"]["General"]["Investment Experience"] = clean_text(match.group(1))
            elif key == 'horizon':
                client_data["Account Information"]["General"]["Investment Horizon"] = clean_text(match.group(1))
            elif key == 'markets':
                client_data["Account Information"]["General"]["Preferred Markets"] = clean_text(match.group(1))
            elif key == 'total_aum':
                client_data["Account Information"]["Assets"]["Total AUM"] = int(match.group(1))
            elif key == 'transfer_aum':
                client_data["Account Information"]["Assets"]["Transfer AUM"] = int(match.group(1))
            else:
                client_data["Client Information"][key.replace('_', ' ').title()] = clean_text(match.group(1))
    return client_data


def cast_files(data, outcome):
    global r

    """
    Extracts all the data from endpoint request to structured data

    Args:
        returned data from GET request -> JSON
        outcome -> String
    Returns:
        structured extracted data from all PDF file -> JSON
        structured extracted data from all TXT file -> JSON
        structured extracted data from all PNG file -> JSON
        structured extracted data from all DOCX file -> JSON
    """
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
        "outcome": outcome,
    }
    print(png_data)
    t = time.time()
    denei = png_data["passport_num"] if "passport_num" in png_data.keys() else pdf_data["passport_number"] if "passport_number" in pdf_data.keys() else f"PASSPORT_NUMBER_NOT_FOUND-{t}"
    resultao = "right" if outcome == "active" else "wrong"
    #r.set(f"true_{resultao}-{denei}", json.dumps(global_dict, ensure_ascii=False))
    return global_dict
    