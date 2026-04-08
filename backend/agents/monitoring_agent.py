from models import Assignment
from datetime import datetime, timedelta


class MonitoringAgent:

    def __init__(self, db):
        self.db = db

    # 🔹 TRACK ALL ACTIVE ASSIGNMENTS
    def track_active_assignments(self):
        """
        Get all assignments that are not completed
        """

        active = self.db.query(Assignment).filter(
            Assignment.status.in_(["assigned", "accepted"])
        ).all()

        return active

    # 🔹 DETECT STUCK ASSIGNMENTS
    def detect_stuck_assignments(self, minutes=30):
        """
        Detect assignments that are not progressing
        """

        threshold_time = datetime.utcnow() - timedelta(minutes=minutes)

        stuck = self.db.query(Assignment).filter(
            Assignment.status == "assigned",
            Assignment.created_at <= threshold_time
        ).all()

        return stuck

    # 🔹 DETECT LONG DELIVERY TIME
    def detect_delayed_deliveries(self, minutes=60):
        """
        Detect accepted but not completed deliveries
        """

        threshold_time = datetime.utcnow() - timedelta(minutes=minutes)

        delayed = self.db.query(Assignment).filter(
            Assignment.status == "accepted",
            Assignment.created_at <= threshold_time
        ).all()

        return delayed

    # 🔹 GENERATE SYSTEM STATUS REPORT
    def system_status(self):
        """
        Overall system health
        """

        total = self.db.query(Assignment).count()

        assigned = self.db.query(Assignment).filter(
            Assignment.status == "assigned"
        ).count()

        accepted = self.db.query(Assignment).filter(
            Assignment.status == "accepted"
        ).count()

        completed = self.db.query(Assignment).filter(
            Assignment.status == "completed"
        ).count()

        rejected = self.db.query(Assignment).filter(
            Assignment.status == "rejected"
        ).count()

        return {
            "total": total,
            "assigned": assigned,
            "accepted": accepted,
            "completed": completed,
            "rejected": rejected
        }

    # 🔹 AUTO HANDLE STUCK ASSIGNMENTS (OPTIONAL 🔥)
    def auto_reassign_stuck(self):
        """
        Automatically reassign stuck assignments
        """

        from agents.reassignment_agent import ReassignmentAgent

        stuck_assignments = self.detect_stuck_assignments()

        reassigned = []

        for assignment in stuck_assignments:

            print(f"⚠️ Reassigning stuck assignment {assignment.id}")

            reassignment_agent = ReassignmentAgent(self.db)

            updated = reassignment_agent.run(assignment)

            if updated:
                reassigned.append(updated.id)

        return reassigned