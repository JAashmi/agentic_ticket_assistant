from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Donation

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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
    donation = Donation(
        donor_id=donor_id,
        food_type=food_type,
        quantity=quantity,
        expiry_time=expiry_time,
        lat=lat,
        lng=lng
    )

    db.add(donation)
    db.commit()

    return {"message": "Donation created"}