import json
import re

def extract_json(text):
    """استخراج JSON صالح من النص باستخدام regex"""
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        return match.group(0)
    return None