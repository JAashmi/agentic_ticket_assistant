from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from models import DeliveryAgent

from utils.file_handler import FileHandler
from utils.constants import FILE_TYPES, STATUS

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/signup")
def agent_signup(
    name: str,
    lat: float,
    lng: float,
    capacity: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    if capacity <= 0:
        return {"error": "Invalid capacity"}

    # 🔥 Use FileHandler
    try:
        file_path = FileHandler.save_file(
            file,
            folder="uploads/images",
            allowed_types=[
                FILE_TYPES["IMAGE_JPG"],
                FILE_TYPES["IMAGE_PNG"]
            ]
        )
    except Exception as e:
        return {"error": str(e)}

    # 🔹 Duplicate check
    existing = db.query(DeliveryAgent).filter(
        DeliveryAgent.name == name,
        DeliveryAgent.lat == lat,
        DeliveryAgent.lng == lng
    ).first()

    if existing:
        return {"error": "Agent already exists"}

    agent = DeliveryAgent(
        name=name,
        lat=lat,
        lng=lng,
        capacity=capacity,
        profile_image=file_path,
        verified=STATUS["PENDING"]
    )

    db.add(agent)
    db.commit()
    db.refresh(agent)

    return {
        "message": "Agent registered",
        "agent_id": agent.id,
        "status": agent.verified
    }