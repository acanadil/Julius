import json
import redis
import google.generativeai as genai

# Conexión a Redis
r = redis.Redis(host='172.16.206.75', port=6379, decode_responses=True)

genai.configure(api_key="AIzaSyC4hlob4t5aNGJEaoNnEnaLuABJFU74EPU")

model = genai.GenerativeModel('gemini-2.0-flash-thinking-exp-01-21')

keys = r.keys('*')

raw_data = r.get(keys[2])
# print(raw_data)
parsed_data = json.loads(raw_data)

# Eliminar claves no deseadas
parsed_data.pop("passport", None)
parsed_data.pop("outcome", None)

prompt = f"""
You are a financial screening analyst at a bank. Your task is to evaluate whether the *description* of a client matches the factual data from the passport, profile, and account application form.

The input is a JSON object with the following sections:
- `profile`: structured client data (DOB, nationality, gender, assets, etc.)
- `account`: client account details
- `description`: a narrative background provided by the relationship manager

### Your Objective:
Compare the *description* with the structured data and determine whether the information is consistent and plausible. Focus on:
1. Name consistency
2. Date of birth accuracy
3. Gender mismatch
4. Employment history vs. claimed experience
5. Wealth claims vs. actual financials
6. Inheritance data (existence, year, source, value)
7. Residence and nationality consistency
8. General plausibility of timeline (e.g. age vs. employment years)

### Output format:
Respond ONLY with a JSON object in this format:

```json
{{
  "decision": "Accept" or "Reject",
  "reason": "Concise explanation of your decision"
}}
```

### Be strict:
- If there's any mismatch in critical identity or financial information, reject the application.
- Only accept if all key facts in the description are confirmed by the structured data.

Here is the input data:
```json
{json.dumps(parsed_data, indent=2)}
```
"""
# print(prompt)


response = model.generate_content(prompt)

print(response.text)

# try:
    
#     # Obtener todas las keys
#     keys = r.keys('*')

#     if keys:
#         print("Primeras 5 claves y sus valores:\n")
#         for key in keys[:5]:
#             value = r.get(key)
#             # print(f"{key}: {value}")
#             # print("\n\n")

#     # # Mostrar las keys
#     # if keys:
#     #     print("Claves almacenadas en Redis:")
#     #     for key in keys:
#     #         print(f"- {key}")
#     # else:
#     #     print("No hay claves almacenadas en Redis.")
# except redis.exceptions.ConnectionError as e:
#     print(f"Error de conexión: {e}")
