from flask import Flask, request, jsonify
import json
import google.generativeai as genai

genai.configure(api_key="AIzaSyDwNrAUGPeQDQXBeyf9NVbxEifEGw6mtyE")

model = genai.GenerativeModel('gemini-2.0-flash-thinking-exp-01-21')

app = Flask(__name__)

# Simula la respuesta del modelo
def evaluate_application(parsed_data):
    # parsed_data = json.loads(parsed_data)

    # # Eliminar claves no deseadas
    # parsed_data.pop("passport", None)
    # parsed_data.pop("outcome", None)

    prompt = f"""
You are a financial screening analyst at a bank. Your task is to evaluate whether the passport, profile, description, and account application form are consistent with each other.

The input is a JSON object with the following sections:
- `passport`: official identity information
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
6. Inheritance data
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

Here is the input data:
```json
{json.dumps(parsed_data, indent=2)}
```
"""
    print(prompt)

    response = model.generate_content(prompt)

    text = response.text.strip().removeprefix("```json").removesuffix("```").strip()
    print(text)


    return text

@app.route('/evaluate', methods=['POST'])
def evaluate():
    try:
        parsed_data = request.get_json()
        result = evaluate_application(parsed_data)
        return json.loads(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
