from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Organization

# NEW IMPORTS
import uuid
from utils.ocr import extract_text_from_pdf
from services.verification_service import validate_document

router = APIRouter()


# 🔹 DATABASE CONNECTION
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 🔹 ORGANIZATION SIGNUP
@router.post("/signup")
def org_signup(
    name: str,
    govt_id_number: str,
    lat: float,
    lng: float,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # ✅ 1. CHECK DUPLICATE GOVT ID
    existing = db.query(Organization).filter(
        Organization.govt_id_number == govt_id_number
    ).first()

    if existing:
        return {"error": "Organization already exists with this Govt ID"}

    # ✅ 2. CHECK FILE TYPE
    if file.content_type != "application/pdf":
        return {"error": "Only PDF files are allowed"}

    # ✅ 3. CREATE UNIQUE FILE NAME
    unique_name = f"{uuid.uuid4()}.pdf"
    file_path = f"uploads/{unique_name}"

    # ✅ 4. SAVE FILE
    try:
        with open(file_path, "wb") as f:
            f.write(file.file.read())
    except Exception:
        return {"error": "File upload failed"}

    # ✅ 5. AI VERIFICATION
    try:
        extracted_text = extract_text_from_pdf(file_path)
        ai_result = validate_document(extracted_text, govt_id_number)
    except Exception:
        ai_result = {
            "status": "error",
            "confidence": 0.0
        }

    # 🔥 NEW: HANDLE OCR / AI FAILURE
    if ai_result["status"] == "error":
        return {"error": "Document processing failed"}

    # ✅ 6. SAVE TO DATABASE
    org = Organization(
        name=name,
        govt_id_number=govt_id_number,
        lat=lat,
        lng=lng,
        govt_proof=file_path,
        verified="pending",
        ai_verified=ai_result["status"],
        ai_confidence=ai_result["confidence"]
    )

    db.add(org)
    db.commit()

    # ✅ 7. RESPONSE
    return {
        "message": "Organization submitted for approval",
        "ai_status": ai_result
    }