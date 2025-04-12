import saving
import base64
import time
import json


code, data = saving.post_request()
current_time = int(time.time())

# Cast every file to JSON
outputs = []
outputs.append(saving.cast_files(data))

with open("output.json", "w") as f:
    json.dump(outputs, f, ensure_ascii=False)


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
        
    with open(f'data_files/output-{current_time}.{extension}', 'wb') as f:
        f.write(base64.b64decode(data["client_data"][document]))