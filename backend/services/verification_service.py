import re

def validate_document(text, govt_id_input):
    result = {
        "status": "fake",
        "confidence": 0.0
    }

    if govt_id_input in text:
        result["confidence"] += 0.4

    pattern = r"[A-Z]{2}-\d{8}"
    if re.search(pattern, text):
        result["confidence"] += 0.3

    keywords = ["Government", "India", "Certificate", "ID"]
    matches = sum(1 for k in keywords if k.lower() in text.lower())
    result["confidence"] += matches * 0.1

    if result["confidence"] >= 0.5:
        result["status"] = "valid"

    return result