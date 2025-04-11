import saving
import base64
import time

code, data = saving.post_request()
current_time = int(time.time())

# Cast every file to JSON
saving.cast_files(data)

# Save every file in its format
for document in data["client_data"].keys():
    match document:
        case "passport":
            extension = "png"
        case "profile":
            extension = "docx"
        case "account":
            extension = "pdf"
        case "description":
            extension = "txt"
        case _:
            raise Exception("Unsupported file has been received")
        
    with open(f'output-{current_time}.{extension}', 'wb') as f:
        f.write(base64.b64decode(data["client_data"][document]))