from groq import Groq
from config import GROQ_API_KEY


class FraudAgent:

    def __init__(self):
        self.client = Groq(api_key=GROQ_API_KEY)

    def analyze_document(self, extracted_text, govt_id_number):
        """
        Analyze document authenticity using LLM
        """

        try:
            prompt = f"""
You are a fraud detection system.

Analyze the following document text and verify authenticity.

Details:
- Extracted Text: {extracted_text}
- Provided Govt ID: {govt_id_number}

Check:
1. Does the ID appear in the text?
2. Is the document consistent?
3. Any suspicious patterns?

Return result in JSON format:
{{
  "status": "valid / suspicious / fake",
  "confidence": 0.0 to 1.0,
  "reason": "short explanation"
}}
"""

            response = self.client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{"role": "user", "content": prompt}]
            )

            output = response.choices[0].message.content

            # ⚠️ Simple parsing (can improve later)
            if "fake" in output.lower():
                status = "fake"
                confidence = 0.3
            elif "suspicious" in output.lower():
                status = "suspicious"
                confidence = 0.6
            else:
                status = "valid"
                confidence = 0.9

            return {
                "status": status,
                "confidence": confidence,
                "raw_response": output
            }

        except Exception as e:
            print("🔥 Fraud detection failed:", str(e))

            return {
                "status": "error",
                "confidence": 0.0,
                "reason": "analysis failed"
            }

    # 🔥 BEHAVIOR ANALYSIS (ADVANCED)
    def detect_suspicious_activity(self, db, org):
        """
        Detect abnormal patterns
        """

        try:
            # Example checks

            # 🔹 Duplicate govt ID
            duplicates = db.query(type(org)).filter(
                type(org).govt_id_number == org.govt_id_number
            ).count()

            if duplicates > 1:
                return {
                    "status": "suspicious",
                    "reason": "Duplicate government ID"
                }

            # 🔹 Unrealistic demand
            if org.required_quantity and org.required_quantity > 10000:
                return {
                    "status": "suspicious",
                    "reason": "Unusually high demand"
                }

            return {
                "status": "valid"
            }

        except Exception as e:
            print("🔥 Behavior check failed:", str(e))
            return {"status": "error"}