from sqlalchemy import Column, Integer, String, Float, ForeignKey
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)
    role = Column(String)  # donor, ngo, org, admin
    status = Column(String, default="pending")
class Donation(Base):
    __tablename__ = "donations"

    id = Column(Integer, primary_key=True)
    donor_id = Column(Integer, ForeignKey("users.id"))
    food_type = Column(String)
    quantity = Column(Integer)
    expiry_time = Column(String)
    lat = Column(Float)
    lng = Column(Float)
    status = Column(String, default="pending")
class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    required_quantity = Column(Integer)
    lat = Column(Float)
    lng = Column(Float)
    verified = Column(String, default="pending")
class NGO(Base):
    __tablename__ = "ngos"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    lat = Column(Float)
    lng = Column(Float)
    capacity = Column(Integer)
    verified = Column(String, default="pending")
class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True)
    donation_id = Column(Integer)
    ngo_id = Column(Integer)
    org_id = Column(Integer)
    quantity = Column(Integer)
    status = Column(String, default="assigned")