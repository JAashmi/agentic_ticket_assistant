from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Organization

import uuid
import os

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
    required_quantity: int,   # 🔥 NEW (VERY IMPORTANT)
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

    # 🔥 NEW: VALIDATE REQUIRED QUANTITY
    if required_quantity <= 0:
        return {"error": "Invalid required quantity"}

    # ✅ 2. CHECK FILE TYPE
    if file.content_type != "application/pdf":
        return {"error": "Only PDF files are allowed"}

    # 🔥 NEW: CREATE uploads folder if not exists
    if not os.path.exists("uploads"):
        os.makedirs("uploads")

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

    # 🔥 HANDLE OCR FAILURE
    if ai_result["status"] == "error":
        return {"error": "Document processing failed"}

    # 🔥 OPTIONAL: BLOCK FAKE DIRECTLY
    if ai_result["status"] == "fake":
        return {
            "error": "Document appears fake based on AI verification"
        }

    # ✅ 6. SAVE TO DATABASE
    org = Organization(
        name=name,
        govt_id_number=govt_id_number,
        required_quantity=required_quantity,   # 🔥 NEW
        lat=lat,
        lng=lng,
        govt_proof=file_path,
        verified="pending",
        ai_verified=ai_result["status"],
        ai_confidence=ai_result["confidence"]
    )

    db.add(org)
    db.commit()
    db.refresh(org)

    # ✅ 7. RESPONSE
    return {
        "message": "Organization submitted for approval",
        "org_id": org.id,
        "ai_status": ai_result
    }