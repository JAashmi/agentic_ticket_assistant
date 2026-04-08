from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Assignment, Donation

from datetime import datetime
import uuid
import os

# 🔥 AGENTS
from agents.reassignment_agent import ReassignmentAgent
from agents.communication_agent import CommunicationAgent


router = APIRouter()


# 🔹 DATABASE CONNECTION
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 🔹 ACCEPT ASSIGNMENT
@router.post("/accept")
def accept_assignment(assignment_id: int, db: Session = Depends(get_db)):

    assignment = db.get(Assignment, assignment_id)

    if not assignment:
        return {"error": "Assignment not found"}

    # 🔥 Prevent invalid transitions
    if assignment.status != "assigned":
        return {"error": f"Cannot accept. Current status: {assignment.status}"}

    assignment.status = "accepted"
    db.commit()

    return {"message": "Assignment accepted"}
    

# 🔹 REJECT ASSIGNMENT (AUTO REASSIGN)



@router.post("/reject")
def reject_assignment(assignment_id: int, db: Session = Depends(get_db)):

    assignment = db.get(Assignment, assignment_id)

    if not assignment:
        return {"error": "Assignment not found"}

    # 🔥 VALID STATE CHECK
    if assignment.status not in ["assigned", "accepted"]:
        return {"error": f"Cannot reject. Current status: {assignment.status}"}

    # 🔥 MARK AS REJECTED FIRST
    assignment.status = "rejected"
    db.commit()

    # 🔥 REASSIGN SAME ASSIGNMENT
    reassignment_agent = ReassignmentAgent(db)
    updated_assignment = reassignment_agent.run(assignment)

    if not updated_assignment:
        return {
            "message": "Assignment rejected, but no alternative agent found"
        }

    return {
        "message": "Assignment reassigned successfully",
        "assignment_id": updated_assignment.id,
        "new_agent_id": updated_assignment.agent_id
    }


# 🔹 COMPLETE DELIVERY (UPLOAD PROOF + AI REPORT)
@router.post("/complete")
def complete_delivery(
    assignment_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    assignment = db.get(Assignment, assignment_id)

    if not assignment:
        return {"error": "Assignment not found"}

    # 🔥 Only accepted assignments can be completed
    if assignment.status != "accepted":
        return {"error": f"Cannot complete. Current status: {assignment.status}"}

    # 🔥 FILE TYPE CHECK
    if file.content_type not in ["image/jpeg", "image/png"]:
        return {"error": "Only JPG or PNG images allowed"}

    # 🔥 CREATE UPLOAD FOLDER
    if not os.path.exists("uploads"):
        os.makedirs("uploads")

    # 🔥 SAVE FILE
    file_path = f"uploads/{uuid.uuid4()}.jpg"

    try:
        with open(file_path, "wb") as f:
            f.write(file.file.read())
    except Exception:
        return {"error": "File upload failed"}

    # 🔥 UPDATE STATUS
    assignment.status = "completed"
    assignment.delivery_proof = file_path
    assignment.delivered_at = datetime.utcnow()

    db.commit()

    # 🔥 GENERATE AI REPORT
    donation = db.get(Donation, assignment.donation_id)

    comm_agent = CommunicationAgent()

    report = comm_agent.generate_report(
        donation=donation,
        assignments=[assignment]
    )

    return {
        "message": "Delivery completed successfully",
        "proof": file_path,
        "ai_report": report
    }


# 🔹 GET ALL ASSIGNMENTS (FOR DEBUG / FRONTEND)
@router.get("/list")
def get_assignments(db: Session = Depends(get_db)):

    assignments = db.query(Assignment).all()

    return assignments