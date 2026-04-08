from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User, DeliveryAgent, Organization

router = APIRouter()


# 🔹 DATABASE CONNECTION
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 🔹 APPROVE USER
@router.post("/approve_user")
def approve_user(user_id: int, db: Session = Depends(get_db)):

    user = db.get(User, user_id)

    # ✅ CHECK EXISTS
    if not user:
        return {"error": "User not found"}

    # 🔥 NEW: PREVENT RE-APPROVAL
    if user.status == "approved":
        return {"error": "User already approved"}

    user.status = "approved"
    db.commit()

    return {"message": "User approved"}


# 🔹 APPROVE DELIVERY AGENT
@router.post("/approve_agent")
def approve_agent(agent_id: int, emp_id: str, db: Session = Depends(get_db)):

    agent = db.get(DeliveryAgent, agent_id)

    if not agent:
        return {"error": "Delivery agent not found"}

    # 🔥 NEW: PREVENT RE-APPROVAL
    if agent.verified == "approved":
        return {"error": "Agent already approved"}

    # 🔥 CHECK DUPLICATE EMP ID
    existing = db.query(DeliveryAgent).filter(
        DeliveryAgent.emp_id == emp_id
    ).first()

    if existing and existing.id != agent_id:
        return {"error": "EMP ID already assigned"}

    agent.emp_id = emp_id
    agent.verified = "approved"

    db.commit()

    return {
        "message": "Delivery agent approved with EMP ID",
        "emp_id": emp_id
    }


# 🔹 REJECT DELIVERY AGENT
@router.post("/reject_agent")
def reject_agent(agent_id: int, db: Session = Depends(get_db)):

    agent = db.get(DeliveryAgent, agent_id)

    if not agent:
        return {"error": "Delivery agent not found"}

    # 🔥 NEW: PREVENT DOUBLE REJECTION
    if agent.verified == "rejected":
        return {"error": "Agent already rejected"}

    agent.verified = "rejected"
    db.commit()

    return {"message": "Delivery agent rejected"}


# 🔹 APPROVE ORGANIZATION
@router.post("/approve_org")
def approve_org(org_id: int, db: Session = Depends(get_db)):

    org = db.get(Organization, org_id)

    if not org:
        return {"error": "Organization not found"}

    # 🔥 NEW: PREVENT RE-APPROVAL
    if org.verified == "approved":
        return {"error": "Organization already approved"}

    # 🔥 AI VALIDATION CHECK
    if org.ai_verified == "fake":
        return {
            "error": "AI marked this document as fake. Cannot approve."
        }

    org.verified = "approved"
    db.commit()

    return {
        "message": "Organization approved",
        "ai_status": org.ai_verified,
        "confidence": org.ai_confidence
    }


# 🔹 REJECT ORGANIZATION
@router.post("/reject_org")
def reject_org(org_id: int, db: Session = Depends(get_db)):

    org = db.get(Organization, org_id)

    if not org:
        return {"error": "Organization not found"}

    # 🔥 NEW: PREVENT DOUBLE REJECTION
    if org.verified == "rejected":
        return {"error": "Organization already rejected"}

    org.verified = "rejected"
    db.commit()

    return {"message": "Organization rejected"}