from models import Assignment


class AssignmentAgent:

    def __init__(self, db):
        self.db = db

    def run(self, donation, match_results):
        """
        Creates assignment records based on matching results

        match_results format:
        [
            {"agent": agent_obj, "org": org_obj, "quantity": int},
            ...
        ]
        """

        created_assignments = []

        try:
            # 🔹 STEP 1: VALIDATION
            if not match_results:
                return []

            # 🔹 STEP 2: CREATE ASSIGNMENTS
            for item in match_results:

                agent = item["agent"]
                org = item["org"]
                quantity = item["quantity"]

                # ❌ Skip invalid entries
                if not agent or not org or quantity <= 0:
                    continue

                assignment = Assignment(
                    donation_id=donation.id,
                    agent_id=agent.id,
                    org_id=org.id,
                    quantity=quantity,
                    status="assigned"
                )

                self.db.add(assignment)
                created_assignments.append(assignment)

            # 🔹 STEP 3: UPDATE DONATION STATUS
            if created_assignments:
                donation.status = "assigned"

            # 🔹 STEP 4: COMMIT TRANSACTION
            self.db.commit()

            # 🔹 STEP 5: REFRESH OBJECTS (IMPORTANT)
            for a in created_assignments:
                self.db.refresh(a)

            return created_assignments

        except Exception as e:
            # 🔥 INDUSTRY PRACTICE: ROLLBACK
            self.db.rollback()
            print("🔥 Assignment creation failed:", str(e))
            return []