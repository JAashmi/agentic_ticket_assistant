from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Assignment, Donation

from datetime import datetime

from utils.file_handler import FileHandler
from utils.constants import FILE_TYPES, ASSIGNMENT_STATUS

from agents.reassignment_agent import ReassignmentAgent
from agents.communication_agent import CommunicationAgent

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/accept")
def accept_assignment(assignment_id: int, db: Session = Depends(get_db)):

    assignment = db.get(Assignment, assignment_id)

    if not assignment:
        return {"error": "Not found"}

    if assignment.status != ASSIGNMENT_STATUS["ASSIGNED"]:
        return {"error": "Invalid state"}

    assignment.status = ASSIGNMENT_STATUS["ACCEPTED"]
    db.commit()

    return {"message": "Accepted"}


@router.post("/reject")
def reject_assignment(assignment_id: int, db: Session = Depends(get_db)):

    assignment = db.get(Assignment, assignment_id)

    if not assignment:
        return {"error": "Not found"}

    if assignment.status not in [
        ASSIGNMENT_STATUS["ASSIGNED"],
        ASSIGNMENT_STATUS["ACCEPTED"]
    ]:
        return {"error": "Invalid state"}

    assignment.status = ASSIGNMENT_STATUS["REJECTED"]
    db.commit()

    reassignment_agent = ReassignmentAgent(db)
    updated = reassignment_agent.run(assignment)

    if not updated:
        return {"message": "Rejected, no replacement"}

    return {
        "message": "Reassigned",
        "new_agent_id": updated.agent_id
    }


@router.post("/complete")
def complete_delivery(
    assignment_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    assignment = db.get(Assignment, assignment_id)

    if not assignment:
        return {"error": "Not found"}

    if assignment.status != ASSIGNMENT_STATUS["ACCEPTED"]:
        return {"error": "Invalid state"}

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

    assignment.status = ASSIGNMENT_STATUS["COMPLETED"]
    assignment.delivery_proof = file_path
    assignment.delivered_at = datetime.utcnow()

    db.commit()

    donation = db.get(Donation, assignment.donation_id)

    comm_agent = CommunicationAgent()
    report = comm_agent.generate_report(
        donation=donation,
        assignments=[assignment]
    )

    return {
        "message": "Completed",
        "proof": file_path,
        "report": report
    }