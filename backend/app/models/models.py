from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Float, Enum as SQLEnum
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
from app.models.database import Base

class UserRole(str, Enum):
    MANAGEMENT = "management"
    INSPECTION = "inspection" 
    WORKER = "worker"

class TrainsetStatus(str, Enum):
    FIT = "Fit"
    UNFIT = "Unfit"
    STANDBY = "Standby"

class CertificateStatus(str, Enum):
    VALID = "Valid"
    EXPIRED = "Expired"
    PENDING = "Pending"

class JobCardStatus(str, Enum):
    OPEN = "Open"
    CLOSED = "Closed"
    IN_PROGRESS = "In Progress"

class BrandingPriorityLevel(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Trainset(Base):
    __tablename__ = "trainsets"
    
    id = Column(Integer, primary_key=True, index=True)
    number = Column(String(20), unique=True, index=True, nullable=False)  # e.g., "TS-2003"
    status = Column(SQLEnum(TrainsetStatus), nullable=False, default=TrainsetStatus.STANDBY)
    current_mileage = Column(Float, default=0.0)
    stabling_bay = Column(String(20), nullable=True)  # e.g., "Bay-03"
    reasoning = Column(Text, nullable=True)  # Explainable reasoning for status
    conflict_alerts = Column(Text, nullable=True)  # JSON string of alerts
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    fitness_certificates = relationship("FitnessCertificate", back_populates="trainset")
    job_cards = relationship("JobCard", back_populates="trainset")
    branding_priorities = relationship("BrandingPriority", back_populates="trainset")
    mileage_records = relationship("MileageRecord", back_populates="trainset")
    cleaning_slots = relationship("CleaningSlot", back_populates="trainset")

class FitnessCertificate(Base):
    __tablename__ = "fitness_certificates"
    
    id = Column(Integer, primary_key=True, index=True)
    trainset_id = Column(Integer, ForeignKey("trainsets.id"), nullable=False)
    certificate_type = Column(String(50), nullable=False)  # "Rolling-Stock", "Signalling", "Telecom"
    status = Column(SQLEnum(CertificateStatus), nullable=False)
    issue_date = Column(DateTime(timezone=True), nullable=False)
    expiry_date = Column(DateTime(timezone=True), nullable=False)
    issuing_authority = Column(String(100), nullable=False)
    certificate_number = Column(String(50), nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    trainset = relationship("Trainset", back_populates="fitness_certificates")

class JobCard(Base):
    __tablename__ = "job_cards"
    
    id = Column(Integer, primary_key=True, index=True)
    trainset_id = Column(Integer, ForeignKey("trainsets.id"), nullable=False)
    job_card_number = Column(String(50), unique=True, nullable=False)  # e.g., "JB-4421"
    description = Column(Text, nullable=False)
    status = Column(SQLEnum(JobCardStatus), nullable=False, default=JobCardStatus.OPEN)
    priority = Column(String(20), default="Medium")  # High, Medium, Low
    created_date = Column(DateTime(timezone=True), nullable=False)
    due_date = Column(DateTime(timezone=True), nullable=True)
    completed_date = Column(DateTime(timezone=True), nullable=True)
    assigned_to = Column(String(100), nullable=True)
    estimated_hours = Column(Float, nullable=True)
    actual_hours = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    trainset = relationship("Trainset", back_populates="job_cards")

class BrandingPriority(Base):
    __tablename__ = "branding_priorities"
    
    id = Column(Integer, primary_key=True, index=True)
    trainset_id = Column(Integer, ForeignKey("trainsets.id"), nullable=False)
    priority_level = Column(SQLEnum(BrandingPriorityLevel), nullable=False)
    brand_name = Column(String(100), nullable=False)
    campaign_name = Column(String(100), nullable=True)
    contract_start_date = Column(DateTime(timezone=True), nullable=False)
    contract_end_date = Column(DateTime(timezone=True), nullable=False)
    revenue_impact = Column(Float, nullable=True)  # Financial impact in INR
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    trainset = relationship("Trainset", back_populates="branding_priorities")

class MileageRecord(Base):
    __tablename__ = "mileage_records"
    
    id = Column(Integer, primary_key=True, index=True)
    trainset_id = Column(Integer, ForeignKey("trainsets.id"), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    daily_mileage = Column(Float, nullable=False)
    cumulative_mileage = Column(Float, nullable=False)
    route = Column(String(100), nullable=True)
    fuel_consumption = Column(Float, nullable=True)  # If applicable
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    trainset = relationship("Trainset", back_populates="mileage_records")

class CleaningSlot(Base):
    __tablename__ = "cleaning_slots"
    
    id = Column(Integer, primary_key=True, index=True)
    trainset_id = Column(Integer, ForeignKey("trainsets.id"), nullable=False)
    slot_date = Column(DateTime(timezone=True), nullable=False)
    slot_time_start = Column(DateTime(timezone=True), nullable=False)
    slot_time_end = Column(DateTime(timezone=True), nullable=False)
    cleaning_type = Column(String(50), nullable=False)  # "Basic", "Deep", "Detailing"
    bay_number = Column(String(20), nullable=False)
    assigned_crew = Column(String(100), nullable=True)
    status = Column(String(20), default="Scheduled")  # Scheduled, In Progress, Completed, Cancelled
    estimated_duration = Column(Integer, nullable=True)  # in minutes
    actual_duration = Column(Integer, nullable=True)  # in minutes
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    trainset = relationship("Trainset", back_populates="cleaning_slots")

class StablingBay(Base):
    __tablename__ = "stabling_bays"
    
    id = Column(Integer, primary_key=True, index=True)
    bay_number = Column(String(20), unique=True, nullable=False)  # e.g., "Bay-01"
    capacity = Column(Integer, nullable=False, default=1)  # Number of trainsets it can hold
    current_occupancy = Column(Integer, default=0)
    bay_type = Column(String(50), nullable=False)  # "Maintenance", "Parking", "Inspection"
    is_available = Column(Boolean, default=True)
    maintenance_required = Column(Boolean, default=False)
    location = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())