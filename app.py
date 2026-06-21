import json
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["AIPIPE_TOKEN"],
    base_url="https://aipipe.org/openai/v1"
)

def analyze_error_with_ai(code: str, tb: str):

    prompt = f"""
Analyze the Python code and traceback.

CODE:
{code}

TRACEBACK:
{tb}

Return JSON only:

{{
  "error_lines": [line_numbers]
}}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Return valid JSON only."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    content = response.choices[0].message.content

    try:
        data = json.loads(content)
        return data.get("error_lines", [])
    except Exception:
        return []
