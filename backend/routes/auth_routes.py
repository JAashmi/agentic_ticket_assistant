from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User
from utils.hash import hash_password, verify_password

router = APIRouter()


# 🔹 DATABASE CONNECTION
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 🔹 SIGNUP
@router.post("/signup")
def signup(
    name: str,
    email: str,
    password: str,
    role: str,
    lat: float,
    lng: float,
    db: Session = Depends(get_db)
):

    # 🔥 NEW: CHECK DUPLICATE EMAIL
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        return {"error": "Email already registered"}

    # 🔥 NEW: BASIC VALIDATION
    if not name or not email or not password:
        return {"error": "All fields are required"}

    if role not in ["donor", "admin"]:
        return {"error": "Invalid role"}

    # ✅ CREATE USER
    user = User(
        name=name,
        email=email,
        password=hash_password(password),
        role=role,
        lat=lat,
        lng=lng,
        status="pending"
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "message": "User created. Wait for admin approval",
        "user_id": user.id
    }


# 🔹 LOGIN
@router.post("/login")
def login(email: str, password: str, db: Session = Depends(get_db)):

    # 🔥 NEW: USE MODERN METHOD
    user = db.query(User).filter(User.email == email).first()

    if not user:
        return {"error": "User not found"}

    # 🔥 PASSWORD CHECK
    if not verify_password(password, user.password):
        return {"error": "Invalid credentials"}

    # 🔥 APPROVAL CHECK
    if user.status != "approved":
        return {"error": "Waiting for admin approval"}

    # 🔥 OPTIONAL: ROLE CHECK SAFETY
    if user.role not in ["donor", "admin"]:
        return {"error": "Invalid role assigned"}

    return {
        "message": "Login success",
        "user_id": user.id,
        "role": user.role,
        "status": user.status
    }