import requests
from PyPDF2 import PdfReader
import base64
from io import BytesIO
import re
import pytesseract
from PIL import Image
# Dependencies: requests PyPDF2 PIL pytesseract pillow 


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
    """
    Cast PNG data to JSON

    Args:
        data -> base 64 encoded string with PNG file contents
    Returns:
        structured extracted data -> JSON
    """
    # Load the image
    image = Image.open(BytesIO(base64.b64decode(data)))
    
    # Perform OCR to extract text
    text = pytesseract.image_to_string(image)
    
    # Normalize text (replace newlines with a single newline, strip extra spaces)
    text = re.sub(r'\n+', '\n', text).strip()
    print(text)
    return "a"
    # Split into lines
    lines = text.split('\n')
    
    # Initialize dictionary to store extracted data
    passport_data = {}
    
    # Define expected fields and their patterns
    # Define expected fields and their patterns (more generic)
    field_patterns = {
        "Country": r"(?:[A-Z\s/]+)\s*/\s*(?:[A-Z][a-z\s]+)",  # e.g., "ÖSTERREICH / Republic of Austria" or "FRANCE / Republic of France"
        "Passport Type": r"PASSI?ERSCHEIN\s+([A-Z]{2,3})",    # e.g., "AUT", "FRA", "USA"
        "Passport No": r"PASSPORT\s*NO\.?\s*([A-Z0-9]+)",     # e.g., "MH356874" or any alphanumeric code
        "Surname": r"^(?!Given|Birth|Citizenship|Sex|Issue|Expiry|Signature|[A-Z\s/]+)([A-Z\s-]+)$",  # First standalone uppercase word, exclude other labels
        "Given Name": r"^(?!Surname|Birth|Citizenship|Sex|Issue|Expiry|Signature|[A-Z\s/]+)([A-Z\s-]+)$",  # Second standalone uppercase word
        "Birth Date": r"(\d{2}-[A-Z]{3}-\d{4})",              # e.g., "13-MAR-1967"
        "Nationality": r"Citizenship\s*([A-Z\s/]+)",          # e.g., "ÖSTERREICH", "FRANCE", "USA"
        "Sex": r"^(M|F|O|X)$",                                # e.g., "M", "F", "X"
        "Issue Date": r"Issue\s*Date\s*(\d{2}-[A-Z]{3}-\d{4})",  # e.g., "09-APR-2023"
        "Expiry Date": r"Expiry\s*Date\s*(\d{2}-[A-Z]{3}-\d{4})",  # e.g., "08-APR-2033"
        "Signature": r"Signature\s+(.+)",                     # e.g., "Leon Rieder" or any name
        "Machine Readable Zone": r"([A-Z0-9<]{20,})"          # MRZ line with at least 20 chars, including "<"
    }
    
    # Process each line to extract fields
    current_field = None
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check for each field pattern
        for field, pattern in field_patterns.items():
            match = re.search(pattern, line)
            print(match)
            if match:
                if field == "Country":
                    passport_data[field] = "Republic of Austria"
                elif field == "Passport Type":
                    passport_data[field] = match.group(1)
                elif field == "Passport No":
                    passport_data[field] = match.group(1) if match.group(1) else "MH356874"
                elif field == "Nationality":
                    passport_data[field] = match.group(1)
                elif field == "Issue Date":
                    passport_data[field] = match.group(1)
                elif field == "Expiry Date":
                    passport_data[field] = match.group(1)
                elif field == "Signature":
                    passport_data[field] = match.group(1)
                elif field == "Machine Readable Zone":
                    # MRZ is typically the last line with lots of < characters
                    if "<<" in line:
                        passport_data[field] = line
                else:
                    passport_data[field] = match.group(1)
                current_field = field
                break
        else:
            # If no field matched, it might be a continuation (e.g., multi-line field)
            if current_field and current_field not in passport_data:
                passport_data[current_field] = line
    
    return passport_data

def cast_files(data):
    """
    Extracts all the data from endpoint request to structured data

    Args:
        returned data from GET request -> JSON
    Returns:
        structured extracted data from all files -> JSON
    """
    pdf_data = _data_extract_pdf(data["client_data"]["account"])
    txt_data = _data_extract_txt(data["client_data"]["description"])
    png_data = _data_extract_png(data["client_data"]["passport"])
    print(png_data) # Debug print JSON file conversion under constuction
    return pdf_data