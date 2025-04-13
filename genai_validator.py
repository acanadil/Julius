from flask import Flask, request, jsonify
import json
import google.generativeai as genai
from datetime import datetime
genai.configure(api_key="AIzaSyC4hlob4t5aNGJEaoNnEnaLuABJFU74EPU")

model = genai.GenerativeModel('gemini-2.0-flash-thinking-exp-01-21')

app = Flask(__name__)

# Simula la respuesta del modelo
def evaluate_application(parsed_data):
    # parsed_data = json.loads(parsed_data)

    # # Eliminar claves no deseadas
    # parsed_data.pop("passport", None)
    # parsed_data.pop("outcome", None)

    prompt = f"""
You are a financial screening analyst at a bank. Today is '{datetime.now()}'. Your task is to evaluate whether the passport, profile, description, and account application form are consistent with each other.

The input is a JSON object with the following sections:
- `passport`: official identity information
- `profile`: structured client data (DOB, nationality, gender, assets, etc.)
- `account`: client account details
- `description`: a narrative background provided by the relationship manager

### Your Objective:
Carefully analyze ALL information across all documents before making any conclusions. Compare the *description* with the structured data to determine whether the information is consistent and plausible.
Have ZERO tolerance for name typos. Also, check syntax of known standards, such as phone number, email, etc.

Focus on:
1. Name consistency
2. Date of birth accuracy
3. Gender mismatch
4. Employment history vs. claimed experience
5. Wealth claims vs. actual financials
   - IMPORTANT: Look for explanations in the description that might clarify apparent financial inconsistencies (inheritances, family wealth, business sales, etc.)
6. Inheritance data
7. Residence and nationality consistency
8. General plausibility of timeline (e.g. age vs. employment years)
9. Other properties

### Analysis Requirements:
- Read the ENTIRE description before making judgments
- When identifying inconsistencies, CITE specific text from the relevant sections
- Avoid assumptions based on stereotypes or expectations
- Look for explanations of apparent inconsistencies in the narrative
- Remember that the profile contains self-reported information that may need verification against the description

### Output format:
Respond with a JSON object in this format (make always sure to verify that it follows this specific structure):

```
{{
  "decision": "Accept" or "Reject",
  "reason": "Brief explanation of your decision, citing specific evidence."
}}
```

Here is the input data:
```
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
