import re
from agents.fraud_agent import FraudAgent

fraud_agent = FraudAgent()


def validate_document(text, govt_id_input):
    """
    Hybrid verification:
    1. Rule-based scoring
    2. LLM fraud detection
    """

    # 🔹 STEP 1: RULE-BASED CHECK
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

    # 🔥 STEP 2: LLM FRAUD ANALYSIS
    ai_result = fraud_agent.analyze_document(text, govt_id_input)

    # 🔥 STEP 3: COMBINE RESULTS (VERY IMPORTANT)
    final_status = result["status"]
    final_confidence = (result["confidence"] + ai_result["confidence"]) / 2

    # Priority: fake > suspicious > valid
    if ai_result["status"] == "fake":
        final_status = "fake"
    elif ai_result["status"] == "suspicious":
        final_status = "suspicious"
    elif result["status"] == "valid":
        final_status = "valid"

    return {
        "status": final_status,
        "confidence": round(final_confidence, 2)
    }