from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from database import Base

from datetime import datetime


# 🔹 USER TABLE
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(String)
    status = Column(String, default="pending")

    # Location
    lat = Column(Float)
    lng = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)


# 🔹 DONATION TABLE
class Donation(Base):
    __tablename__ = "donations"

    id = Column(Integer, primary_key=True, index=True)
    donor_id = Column(Integer, ForeignKey("users.id"))
    food_type = Column(String)
    quantity = Column(Integer)
    expiry_time = Column(String)
    lat = Column(Float)
    lng = Column(Float)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)

# 🔹 ORGANIZATION TABLE
class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    required_quantity = Column(Integer)
    lat = Column(Float)
    lng = Column(Float)

    # Approval status
    verified = Column(String, default="pending")

    # Govt details
    govt_id_number = Column(String, unique=True)
    govt_proof = Column(String)   # file path

    # 🔥 AI VERIFICATION FIELDS (NEW)
    ai_verified = Column(String)      # valid / fake / error
    ai_confidence = Column(Float)     # 0.0 to 1.0
    created_at = Column(DateTime, default=datetime.utcnow)

# 🔹 NGO TABLE

class DeliveryAgent(Base):
    __tablename__ = "delivery_agents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    lat = Column(Float)
    lng = Column(Float)
    capacity = Column(Integer)

    # Approval status
    verified = Column(String, default="pending")

    # 🔥 ADD THIS
    emp_id = Column(String, unique=True)

    # Profile
    profile_image = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
# 🔹 ASSIGNMENT TABLE
class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, index=True)
    donation_id = Column(Integer, ForeignKey("donations.id"))
    ngo_id = Column(Integer, ForeignKey("ngos.id"))
    org_id = Column(Integer, ForeignKey("organizations.id"))

    quantity = Column(Integer)
    status = Column(String, default="assigned")
    created_at = Column(DateTime, default=datetime.utcnow)