from agents.matching_agent import MatchingAgent
from agents.assignment_agent import AssignmentAgent
from agents.communication_agent import CommunicationAgent


class DonationPipeline:

    def __init__(self, db):
        self.db = db

        # 🔥 Initialize agents
        self.matching_agent = MatchingAgent(db)
        self.assignment_agent = AssignmentAgent(db)
        self.communication_agent = CommunicationAgent()

    def run(self, donation):

        try:
            print("🚀 Pipeline started for donation:", donation.id)

            # 🔹 STEP 1: MATCHING + SPLITTING
            match_results = self.matching_agent.run(donation)

            if not match_results:
                print("❌ No matches found")
                return []

            print(f"✅ Matching done: {len(match_results)} assignments possible")

            # 🔹 STEP 2: CREATE ASSIGNMENTS
            assignments = self.assignment_agent.run(donation, match_results)

            print(f"📦 Assignments created: {len(assignments)}")

            # 🔥 STEP 3: NOTIFY AGENTS (CORRECTED 🔥)
            for assignment in assignments:

                try:
                    message = self.communication_agent.notify_agent(
                        agent=assignment.agent,
                        assignment=assignment,
                        donation=assignment.donation
                    )

                    print(f"📩 Notification to Agent {assignment.agent.id}:")
                    print(message)

                except Exception as e:
                    print("⚠️ Notification failed:", str(e))

            # 🔹 STEP 4: UPDATE DONATION STATUS
            donation.status = "assigned"
            self.db.commit()

            print("🎉 Pipeline completed successfully")

            return assignments

        except Exception as e:
            self.db.rollback()
            print("🔥 Pipeline failed:", str(e))
            return []