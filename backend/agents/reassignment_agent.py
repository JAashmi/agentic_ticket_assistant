from models import DeliveryAgent
from services.matching_services import calculate_distance


class ReassignmentAgent:

    def __init__(self, db):
        self.db = db

    def run(self, assignment):
        """
        Reassign a single assignment when agent rejects

        Steps:
        1. Find new agent
        2. Update same assignment
        """

        try:
            # 🔹 STEP 1: GET AVAILABLE AGENTS (EXCLUDE CURRENT)
            agents = self.db.query(DeliveryAgent).filter(
                DeliveryAgent.verified == "approved",
                DeliveryAgent.id != assignment.agent_id
            ).all()

            if not agents:
                print("❌ No alternative agents available")
                return None

            best_agent = None
            best_score = float("inf")

            # 🔹 STEP 2: FIND BEST AGENT
            for agent in agents:

                # ❌ Skip if capacity not enough
                if agent.capacity < assignment.quantity:
                    continue

                distance = calculate_distance(
                    assignment.donation.lat,
                    assignment.donation.lng,
                    agent.lat,
                    agent.lng
                )

                # 🔥 SCORING FUNCTION
                capacity_ratio = assignment.quantity / agent.capacity

                score = (
                    distance * 0.7 +
                    capacity_ratio * 0.3
                )

                if score < best_score:
                    best_score = score
                    best_agent = agent

            if not best_agent:
                print("❌ No suitable agent found")
                return None

            # 🔹 STEP 3: UPDATE EXISTING ASSIGNMENT (IMPORTANT 🔥)
            old_agent_id = assignment.agent_id

            assignment.agent_id = best_agent.id
            assignment.status = "assigned"

            self.db.commit()
            self.db.refresh(assignment)

            print(f"🔁 Reassigned from Agent {old_agent_id} → {best_agent.id}")

            return assignment

        except Exception as e:
            self.db.rollback()
            print("🔥 Reassignment failed:", str(e))
            return None