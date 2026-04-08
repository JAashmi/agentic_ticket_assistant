from groq import Groq
from config import GROQ_API_KEY

from services.map_service import generate_map_link, generate_navigation_link
from services.email_service import send_email


class CommunicationAgent:

    def __init__(self):
        self.client = Groq(api_key=GROQ_API_KEY)

    # 🔥 1. DELIVERY AGENT MESSAGE (SINGLE ASSIGNMENT)
    def notify_agent(self, agent, assignment, donation):

        pickup_link = generate_map_link(donation.lat, donation.lng)

        drop_link = generate_map_link(
            assignment.organization.lat,
            assignment.organization.lng
        )

        navigation_link = generate_navigation_link(
            donation.lat, donation.lng,
            assignment.organization.lat,
            assignment.organization.lng
        )

        prompt = f"""
You are a logistics assistant.

Create a clear instruction for a delivery agent.

Details:
- Pickup Location: {pickup_link}
- Drop Location: {drop_link}
- Navigation Link: {navigation_link}
- Food Type: {donation.food_type}
- Quantity: {assignment.quantity}
- Organization: {assignment.organization.name}

Instructions:
- Be simple
- Step-by-step
- Easy to understand
"""

        response = self.client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}]
        )

        message = response.choices[0].message.content

        # 🔥 SEND EMAIL TO AGENT
        if hasattr(agent, "email") and agent.email:
            send_email(
                to_email=agent.email,
                subject="New Delivery Assignment",
                body=message
            )

        return message

    # 🔥 2. DONOR FINAL REPORT (MULTIPLE ASSIGNMENTS)
    def notify_donor(self, donor, donation, assignments):

        details = ""

        for a in assignments:
            details += f"""
- {a.quantity} meals delivered to {a.organization.name}
  Delivered by Agent ID {a.agent_id}
  Proof Image: {a.delivery_proof}
"""

        prompt = f"""
Generate a friendly and professional report for a donor.

Donation Details:
- Total Food: {donation.quantity}

Distribution:
{details}

Include:
- Where food was delivered
- Which agent handled each delivery
- Mention proof images uploaded
- If multiple deliveries, explain clearly
- Keep tone positive and simple
"""

        response = self.client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}]
        )

        message = response.choices[0].message.content

        # 🔥 SEND EMAIL TO DONOR
        if hasattr(donor, "email") and donor.email:
            send_email(
                to_email=donor.email,
                subject="Your Donation Report",
                body=message
            )

        return message