from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from models import DeliveryAgent

import uuid
import os

router = APIRouter()


# 🔹 DATABASE CONNECTION
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 🔹 AGENT SIGNUP
@router.post("/signup")
def agent_signup(
    name: str,
    lat: float,
    lng: float,
    capacity: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    # 🔥 NEW: VALIDATE INPUTS
    if capacity <= 0:
        return {"error": "Capacity must be greater than 0"}

    # ✅ 1. CHECK FILE TYPE
    if file.content_type not in ["image/jpeg", "image/png"]:
        return {"error": "Only JPG or PNG images are allowed"}

    # 🔥 NEW: CREATE uploads folder
    if not os.path.exists("uploads"):
        os.makedirs("uploads")

    # ✅ 2. CREATE UNIQUE FILE NAME
    file_extension = file.filename.split(".")[-1]
    unique_name = f"{uuid.uuid4()}.{file_extension}"
    file_path = f"uploads/{unique_name}"

    # ✅ 3. SAVE FILE
    try:
        with open(file_path, "wb") as f:
            f.write(file.file.read())
    except Exception:
        return {"error": "File upload failed"}

    # 🔥 NEW: PREVENT DUPLICATE AGENTS (OPTIONAL)
    existing = db.query(DeliveryAgent).filter(
        DeliveryAgent.name == name,
        DeliveryAgent.lat == lat,
        DeliveryAgent.lng == lng
    ).first()

    if existing:
        return {"error": "Agent already registered at this location"}

    # ✅ 4. CREATE AGENT
    agent = DeliveryAgent(
        name=name,
        lat=lat,
        lng=lng,
        capacity=capacity,
        profile_image=file_path,
        verified="pending"
    )

    # ✅ 5. SAVE
    db.add(agent)
    db.commit()
    db.refresh(agent)

    # 🔥 NEW: RESPONSE IMPROVED
    return {
        "message": "Agent registered. Wait for admin approval",
        "agent_id": agent.id,
        "status": agent.verified
    }