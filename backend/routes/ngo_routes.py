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

    # ✅ 1. CHECK FILE TYPE (ONLY IMAGE)
    if file.content_type not in ["image/jpeg", "image/png"]:
        return {"error": "Only JPG or PNG images are allowed"}

    # ✅ 2. CREATE UNIQUE FILE NAME
    file_extension = file.filename.split(".")[-1]
    unique_name = f"{uuid.uuid4()}.{file_extension}"
    file_path = f"uploads/{unique_name}"

    # ✅ 3. CREATE UPLOADS FOLDER IF NOT EXISTS
    if not os.path.exists("uploads"):
        os.makedirs("uploads")

    # ✅ 4. SAVE FILE SAFELY
    try:
        with open(file_path, "wb") as f:
            f.write(file.file.read())
    except Exception as e:
        return {"error": "File upload failed"}

    # ✅ 5. CREATE AGENT (NO NAME DUPLICATE CHECK NEEDED)
    agent = DeliveryAgent(
        name=name,
        lat=lat,
        lng=lng,
        capacity=capacity,
        profile_image=file_path,
        verified="pending"
    )

    # ✅ 6. SAVE TO DATABASE
    db.add(agent)
    db.commit()
    db.refresh(agent)   # get generated id

    # ✅ 7. RESPONSE
    return {
        "message": "Agent registered. Wait for admin approval",
        "agent_id": agent.id
    }