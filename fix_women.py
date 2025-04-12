import redis
import time
import json

# Dependencies: requests PyPDF2 PIL pytesseract pillow pypandoc_binary redis

global r
r = redis.Redis(host='localhost', port=6379, db=0)

ghosted_women_counter = 0

for key in r.keys():
    if "true_" in str(key):
        continue
    temp = json.loads(r.get(key).decode())
    if b"Gender" in temp["profile"].keys():
        continue
    temp["profile"]["Gender"] = "Female"
    r.set(str(key), json.dumps(temp, ensure_ascii=False))
    ghosted_women_counter += 1

print(f"Congratulations! A total of {ghosted_women_counter} women where ghosted due to my incompetence :D")