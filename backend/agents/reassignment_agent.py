from models import DeliveryAgent

from services.matching_services import (
    calculate_agent_score,
    filter_valid_agents
)


class ReassignmentAgent:

    def __init__(self, db):
        self.db = db

    def run(self, assignment):
        """
        Reassign a single assignment when agent rejects

        Steps:
        1. Get alternative agents
        2. Filter valid agents
        3. Select best using hybrid scoring
        4. Update same assignment
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

            # 🔥 STEP 2: FILTER VALID AGENTS
            valid_agents = filter_valid_agents(agents, assignment.quantity)

            if not valid_agents:
                print("❌ No agents with enough capacity")
                return None

            best_agent = None
            best_score = float("inf")

            # 🔥 STEP 3: HYBRID SCORING (SERVICE)
            for agent in valid_agents:

                score = calculate_agent_score(
                    agent,
                    assignment.donation,
                    assignment.quantity
                )

                if score < best_score:
                    best_score = score
                    best_agent = agent

            if not best_agent:
                print("❌ No suitable agent found")
                return None

            # 🔹 STEP 4: UPDATE EXISTING ASSIGNMENT
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