from models import DeliveryAgent, Organization
from services.matching_services import calculate_distance


class MatchingAgent:

    def __init__(self, db):
        self.db = db

    def run(self, donation):
        """
        Main entry:
        1. Get valid organizations
        2. Sort by distance
        3. Split donation
        4. Assign best agents
        """

        # 🔹 STEP 1: GET VALID ORGANIZATIONS
        organizations = self.db.query(Organization).filter(
            Organization.verified == "approved"
        ).all()

        if not organizations:
            return []

        # 🔹 STEP 2: SORT BY DISTANCE
        organizations.sort(
            key=lambda org: calculate_distance(
                donation.lat,
                donation.lng,
                org.lat,
                org.lng
            )
        )

        remaining_quantity = donation.quantity
        results = []

        # 🔹 STEP 3: SPLIT DONATION
        for org in organizations:

            if remaining_quantity <= 0:
                break

            required = org.required_quantity or 0

            # Skip if org doesn't need food
            if required <= 0:
                continue

            assigned_qty = min(remaining_quantity, required)

            # 🔹 STEP 4: FIND BEST AGENT
            agent = self._find_best_agent(
                donation,
                assigned_qty
            )

            if not agent:
                continue  # skip if no agent available

            results.append({
                "agent": agent,
                "org": org,
                "quantity": assigned_qty
            })

            remaining_quantity -= assigned_qty

        return results

    def _find_best_agent(self, donation, quantity):
        """
        Find best delivery agent using scoring
        """

        agents = self.db.query(DeliveryAgent).filter(
            DeliveryAgent.verified == "approved"
        ).all()

        best_agent = None
        best_score = float("inf")

        for agent in agents:

            # ❌ Skip if capacity not enough
            if agent.capacity < quantity:
                continue

            # 🔹 Calculate distance
            distance = calculate_distance(
                donation.lat,
                donation.lng,
                agent.lat,
                agent.lng
            )

            # 🔹 SCORING FUNCTION (VERY IMPORTANT 🔥)
            capacity_ratio = quantity / agent.capacity

            score = (
                distance * 0.7 +         # distance weight
                capacity_ratio * 0.3     # load efficiency
            )

            # 🔹 Select best
            if score < best_score:
                best_score = score
                best_agent = agent

        return best_agent