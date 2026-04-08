from models import DeliveryAgent, Organization

from services.matching_services import (
    calculate_agent_score,
    sort_organizations_by_priority,
    filter_valid_agents
)


class MatchingAgent:

    def __init__(self, db):
        self.db = db

    def run(self, donation):
        """
        Main entry:
        1. Get valid organizations
        2. Sort by priority (distance + demand + ML)
        3. Split donation
        4. Assign best agents
        """

        # 🔹 STEP 1: GET VALID ORGANIZATIONS
        organizations = self.db.query(Organization).filter(
            Organization.verified == "approved"
        ).all()

        if not organizations:
            print("❌ No organizations available")
            return []

        # 🔥 STEP 2: SMART SORT (HYBRID)
        organizations = sort_organizations_by_priority(organizations, donation)

        remaining_quantity = donation.quantity
        results = []

        # 🔹 STEP 3: SPLIT DONATION
        for org in organizations:

            if remaining_quantity <= 0:
                break

            required = org.required_quantity or 0

            # ❌ Skip if no demand
            if required <= 0:
                continue

            assigned_qty = min(remaining_quantity, required)

            # 🔹 STEP 4: FIND BEST AGENT
            agent = self._find_best_agent(donation, assigned_qty)

            if not agent:
                print(f"⚠️ No agent available for org {org.id}")
                continue

            results.append({
                "agent": agent,
                "org": org,
                "quantity": assigned_qty
            })

            remaining_quantity -= assigned_qty

        return results

    def _find_best_agent(self, donation, quantity):
        """
        Find best delivery agent using hybrid scoring
        """

        agents = self.db.query(DeliveryAgent).filter(
            DeliveryAgent.verified == "approved"
        ).all()

        if not agents:
            return None

        # 🔥 FILTER VALID AGENTS
        valid_agents = filter_valid_agents(agents, quantity)

        if not valid_agents:
            return None

        best_agent = None
        best_score = float("inf")

        for agent in valid_agents:

            # 🔥 HYBRID SCORING (RULE + ML)
            score = calculate_agent_score(agent, donation, quantity)

            if score < best_score:
                best_score = score
                best_agent = agent

        return best_agent