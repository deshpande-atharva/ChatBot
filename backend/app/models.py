from sqlalchemy import Column, String, Boolean, Integer, Float, DateTime, Text, ForeignKey, Enum, JSON
from .database import Base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum


class SessionStatus(enum.Enum):
    active = "active"
    completed = "completed"

class MessageSender(enum.Enum):
    user = "user"
    bot = "bot"

class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(String(36), primary_key=True)  # UUID length
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(Enum(SessionStatus), default=SessionStatus.active)
    current_step = Column(String(50), default="zip_code")
    data = Column(JSON, default=dict)  # MySQL JSON type
    
    # Relationships
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")
    vehicles = relationship("Vehicle", back_populates="session", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(String(36), primary_key=True)  # UUID length
    session_id = Column(String(36), ForeignKey("sessions.id"))
    sender = Column(Enum(MessageSender), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    session = relationship("Session", back_populates="messages")

class Vehicle(Base):
    __tablename__ = "vehicles"
    
    id = Column(String(36), primary_key=True)  # UUID length
    session_id = Column(String(36), ForeignKey("sessions.id"))
    
    # Vehicle identification (either VIN or Year/Make/Body)
    vin = Column(String(17), nullable=True)
    year = Column(Integer, nullable=True)
    make = Column(String(50), nullable=True)
    body_type = Column(String(50), nullable=True)
    
    # Vehicle use information
    vehicle_use = Column(String(20), nullable=False)  # commuting, commercial, farming, business
    blind_spot_warning = Column(Boolean, nullable=False)
    
    # Commuting details (if vehicle_use == 'commuting')
    commute_days_per_week = Column(Integer, nullable=True)
    commute_one_way_miles = Column(Float, nullable=True)
    
    # Commercial/Farming/Business details
    annual_mileage = Column(Integer, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    session = relationship("Session", back_populates="vehicles")