from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Donation, User

from orchestrator.pipeline import DonationPipeline

router = APIRouter()


# 🔹 DATABASE CONNECTION
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 🔹 CREATE DONATION
@router.post("/donate")
def create_donation(
    donor_id: int,
    food_type: str,
    quantity: int,
    expiry_time: str,
    lat: float,
    lng: float,
    db: Session = Depends(get_db)
):

    # 🔥 USE MODERN METHOD
    user = db.get(User, donor_id)

    # ✅ VALIDATIONS
    if not user or user.role != "donor":
        return {"error": "Only donors allowed"}

    if user.status != "approved":
        return {"error": "Donor not approved"}

    if quantity <= 0:
        return {"error": "Invalid quantity"}

    if not food_type:
        return {"error": "Food type required"}

    # ✅ CREATE DONATION
    donation = Donation(
        donor_id=donor_id,
        food_type=food_type,
        quantity=quantity,
        expiry_time=expiry_time,
        lat=lat,
        lng=lng,
        status="pending"
    )

    db.add(donation)
    db.commit()
    db.refresh(donation)

    # 🔥 TRIGGER AI PIPELINE (CORE)
    pipeline = DonationPipeline(db)
    assignments = pipeline.run(donation)

    return {
        "message": "Donation created and processed",
        "donation_id": donation.id,
        "assignments_created": len(assignments) if assignments else 0
    }