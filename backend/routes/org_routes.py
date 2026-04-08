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
    required_quantity: int,
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

    # ✅ 2. VALIDATE REQUIRED QUANTITY
    if required_quantity <= 0:
        return {"error": "Invalid required quantity"}

    # ✅ 3. CHECK FILE TYPE
    if file.content_type != "application/pdf":
        return {"error": "Only PDF files are allowed"}

    # ✅ 4. CREATE UPLOAD FOLDER IF NOT EXISTS
    upload_dir = "uploads/documents"
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)

    # ✅ 5. CREATE UNIQUE FILE NAME
    unique_name = f"{uuid.uuid4()}.pdf"
    file_path = os.path.join(upload_dir, unique_name)

    # ✅ 6. SAVE FILE
    try:
        with open(file_path, "wb") as f:
            f.write(file.file.read())
    except Exception:
        return {"error": "File upload failed"}

    # ✅ 7. OCR + FRAUD VERIFICATION (HYBRID 🔥)
    try:
        extracted_text = extract_text_from_pdf(file_path)
        ai_result = validate_document(extracted_text, govt_id_number)
    except Exception:
        return {"error": "Document processing failed"}

    # 🔥 HANDLE FRAUD RESULTS

    if ai_result["status"] == "fake":
        return {
            "error": "Document appears fake based on AI verification"
        }

    if ai_result["status"] == "suspicious":
        print("⚠️ Suspicious organization detected:", name)

    # ✅ 8. SAVE TO DATABASE
    org = Organization(
        name=name,
        govt_id_number=govt_id_number,
        required_quantity=required_quantity,
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

    # ✅ 9. RESPONSE
    return {
        "message": "Organization submitted for approval",
        "org_id": org.id,
        "ai_status": ai_result
    }