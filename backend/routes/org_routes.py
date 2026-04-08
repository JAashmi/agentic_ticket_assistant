from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Organization

from utils.file_handler import FileHandler
from utils.constants import FILE_TYPES, STATUS

from utils.ocr import extract_text_from_pdf
from services.verification_service import validate_document

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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

    # 🔹 Duplicate check
    existing = db.query(Organization).filter(
        Organization.govt_id_number == govt_id_number
    ).first()

    if existing:
        return {"error": "Organization already exists"}

    if required_quantity <= 0:
        return {"error": "Invalid required quantity"}

    # 🔥 Use FileHandler
    try:
        file_path = FileHandler.save_file(
            file,
            folder="uploads/documents",
            allowed_types=[FILE_TYPES["PDF"]]
        )
    except Exception as e:
        return {"error": str(e)}

    # 🔹 OCR + AI verification
    try:
        extracted_text = extract_text_from_pdf(file_path)
        ai_result = validate_document(extracted_text, govt_id_number)
    except Exception:
        return {"error": "Document processing failed"}

    if ai_result["status"] == "fake":
        return {"error": "Document appears fake"}

    org = Organization(
        name=name,
        govt_id_number=govt_id_number,
        required_quantity=required_quantity,
        lat=lat,
        lng=lng,
        govt_proof=file_path,
        verified=STATUS["PENDING"],
        ai_verified=ai_result["status"],
        ai_confidence=ai_result["confidence"]
    )

    db.add(org)
    db.commit()
    db.refresh(org)

    return {
        "message": "Organization submitted",
        "org_id": org.id,
        "ai_status": ai_result
    }