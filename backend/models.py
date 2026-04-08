from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


# 🔹 USER TABLE
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)

    role = Column(String)  # donor / admin
    status = Column(String, default="pending")

    # Location
    lat = Column(Float)
    lng = Column(Float)

    created_at = Column(DateTime, default=datetime.utcnow)

    # 🔥 RELATION
    donations = relationship("Donation", back_populates="donor")


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
    email = Column(String)

    status = Column(String, default="pending")

    created_at = Column(DateTime, default=datetime.utcnow)

    # 🔥 RELATIONS
    donor = relationship("User", back_populates="donations")
    assignments = relationship("Assignment", back_populates="donation")


# 🔹 ORGANIZATION TABLE
class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String)

    required_quantity = Column(Integer)

    lat = Column(Float)
    lng = Column(Float)

    verified = Column(String, default="pending")

    govt_id_number = Column(String, unique=True)
    govt_proof = Column(String)

    ai_verified = Column(String)
    ai_confidence = Column(Float)

    created_at = Column(DateTime, default=datetime.utcnow)

    # 🔥 RELATION
    assignments = relationship("Assignment", back_populates="organization")


# 🔹 DELIVERY AGENT TABLE
class DeliveryAgent(Base):
    __tablename__ = "delivery_agents"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String)

    lat = Column(Float)
    lng = Column(Float)

    capacity = Column(Integer)

    verified = Column(String, default="pending")

    emp_id = Column(String, unique=True)

    profile_image = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow)

    # 🔥 RELATION
    assignments = relationship("Assignment", back_populates="agent")


# 🔹 ASSIGNMENT TABLE (CORE 🔥)
class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, index=True)

    donation_id = Column(Integer, ForeignKey("donations.id"))
    agent_id = Column(Integer, ForeignKey("delivery_agents.id"))
    org_id = Column(Integer, ForeignKey("organizations.id"))

    quantity = Column(Integer)

    status = Column(String, default="assigned")

    delivery_proof = Column(String)
    delivered_at = Column(DateTime)

    created_at = Column(DateTime, default=datetime.utcnow)

    # 🔥 RELATIONSHIPS (VERY IMPORTANT 🔥)
    donation = relationship("Donation", back_populates="assignments")
    agent = relationship("DeliveryAgent", back_populates="assignments")
    organization = relationship("Organization", back_populates="assignments")