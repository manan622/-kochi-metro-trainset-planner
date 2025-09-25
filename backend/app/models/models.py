from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Float, Enum as SQLEnum
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

class InspectionStatus(str, Enum):
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    APPROVED = "Approved"
    REJECTED = "Rejected"

class InspectionType(str, Enum):
    SCHEDULED = "Scheduled"
    MID_DAY_CHECK = "Mid Day Check"
    EMERGENCY = "Emergency"
    MAINTENANCE = "Maintenance"
    SAFETY_CHECK = "Safety Check"

class InspectionPriority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"

class CleaningStatus(str, Enum):
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    VERIFIED = "Verified"
    REJECTED = "Rejected"

class CleaningQuality(str, Enum):
    EXCELLENT = "Excellent"
    GOOD = "Good"
    SATISFACTORY = "Satisfactory"
    NEEDS_IMPROVEMENT = "Needs Improvement"
    UNSATISFACTORY = "Unsatisfactory"

class CleaningTeamRole(str, Enum):
    TEAM_LEADER = "Team Leader"
    CLEANER = "Cleaner"
    SUPERVISOR = "Supervisor"

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
    cleaning_assignments = relationship("CleaningAssignment", back_populates="trainset")
    inspections = relationship("Inspection", back_populates="trainset")

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

class CleaningTeam(Base):
    __tablename__ = "cleaning_teams"
    
    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(String(20), unique=True, nullable=False)  # e.g., "CT-001"
    team_name = Column(String(100), nullable=False)
    team_leader = Column(String(100), nullable=False)
    team_members = Column(Text, nullable=True)  # JSON string of member names
    shift_start = Column(DateTime(timezone=True), nullable=False)
    shift_end = Column(DateTime(timezone=True), nullable=False)
    specialization = Column(String(100), nullable=True)  # "Interior", "Exterior", "Deep Cleaning"
    is_active = Column(Boolean, default=True)
    contact_number = Column(String(20), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    cleaning_assignments = relationship("CleaningAssignment", back_populates="cleaning_team")

class CleaningUser(Base):
    __tablename__ = "cleaning_users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    team_id = Column(Integer, ForeignKey("cleaning_teams.id"), nullable=False)
    role = Column(SQLEnum(CleaningTeamRole), nullable=False)
    employee_id = Column(String(20), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    team = relationship("CleaningTeam")
    photo_evaluations = relationship("CleaningPhotoEvaluation", back_populates="cleaner")

class CleaningAssignment(Base):
    __tablename__ = "cleaning_assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    trainset_id = Column(Integer, ForeignKey("trainsets.id"), nullable=False)
    team_id = Column(Integer, ForeignKey("cleaning_teams.id"), nullable=False)
    assigned_date = Column(DateTime(timezone=True), nullable=False)
    scheduled_start = Column(DateTime(timezone=True), nullable=False)
    scheduled_end = Column(DateTime(timezone=True), nullable=False)
    actual_start = Column(DateTime(timezone=True), nullable=True)
    actual_end = Column(DateTime(timezone=True), nullable=True)
    cleaning_type = Column(String(50), nullable=False)  # "Interior", "Exterior", "Deep", "Maintenance"
    status = Column(SQLEnum(CleaningStatus), default=CleaningStatus.PENDING)
    priority = Column(String(20), default="Medium")  # High, Medium, Low
    special_instructions = Column(Text, nullable=True)
    completion_notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    trainset = relationship("Trainset")
    cleaning_team = relationship("CleaningTeam", back_populates="cleaning_assignments")
    photo_evaluations = relationship("CleaningPhotoEvaluation", back_populates="assignment")

class CleaningPhotoEvaluation(Base):
    __tablename__ = "cleaning_photo_evaluations"
    
    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("cleaning_assignments.id"), nullable=False)
    cleaner_id = Column(Integer, ForeignKey("cleaning_users.id"), nullable=False)
    photo_url = Column(String(500), nullable=False)  # Path to stored image
    photo_timestamp = Column(DateTime(timezone=True), nullable=False)
    area_cleaned = Column(String(100), nullable=False)  # "Interior", "Exterior", "Seats", "Floor", etc.
    ai_evaluation_result = Column(Text, nullable=True)  # JSON string with AI analysis
    ai_quality_score = Column(Float, nullable=True)  # 0-100 score from AI
    ai_quality_rating = Column(SQLEnum(CleaningQuality), nullable=True)
    ai_feedback = Column(Text, nullable=True)  # AI generated feedback
    manual_override = Column(Boolean, default=False)
    manual_rating = Column(SQLEnum(CleaningQuality), nullable=True)
    manual_feedback = Column(Text, nullable=True)
    is_approved = Column(Boolean, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    assignment = relationship("CleaningAssignment", back_populates="photo_evaluations")
    cleaner = relationship("CleaningUser", back_populates="photo_evaluations")

class Inspection(Base):
    __tablename__ = "inspections"
    
    id = Column(Integer, primary_key=True, index=True)
    trainset_id = Column(Integer, ForeignKey("trainsets.id"), nullable=False)
    inspector_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    inspection_number = Column(String(50), unique=True, nullable=False)  # e.g., "INS-2024-001"
    inspection_type = Column(SQLEnum(InspectionType), nullable=False)
    status = Column(SQLEnum(InspectionStatus), default=InspectionStatus.PENDING)
    priority = Column(SQLEnum(InspectionPriority), default=InspectionPriority.MEDIUM)
    scheduled_date = Column(DateTime(timezone=True), nullable=False)
    actual_start_time = Column(DateTime(timezone=True), nullable=True)
    actual_end_time = Column(DateTime(timezone=True), nullable=True)
    estimated_duration = Column(Integer, nullable=True)  # in minutes
    actual_duration = Column(Integer, nullable=True)  # in minutes
    location = Column(String(100), nullable=True)  # Bay number or location
    description = Column(Text, nullable=False)
    findings = Column(Text, nullable=True)  # Inspection findings
    recommendations = Column(Text, nullable=True)  # Inspector recommendations
    components_checked = Column(Text, nullable=True)  # JSON string of checked components
    defects_found = Column(Text, nullable=True)  # JSON string of defects
    safety_compliance = Column(Boolean, default=True)
    approval_required = Column(Boolean, default=False)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    completion_notes = Column(Text, nullable=True)
    next_inspection_due = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    trainset = relationship("Trainset", back_populates="inspections")
    inspector = relationship("User", foreign_keys=[inspector_id])
    approver = relationship("User", foreign_keys=[approved_by])
    inspection_items = relationship("InspectionItem", back_populates="inspection")

class InspectionItem(Base):
    __tablename__ = "inspection_items"
    
    id = Column(Integer, primary_key=True, index=True)
    inspection_id = Column(Integer, ForeignKey("inspections.id"), nullable=False)
    component_name = Column(String(100), nullable=False)  # e.g., "Brakes", "Doors", "Lighting"
    check_point = Column(String(200), nullable=False)  # Specific check point
    is_checked = Column(Boolean, default=False)
    status = Column(String(20), default="Pass")  # Pass, Fail, Warning
    notes = Column(Text, nullable=True)
    defect_severity = Column(String(20), nullable=True)  # Minor, Major, Critical
    action_required = Column(Text, nullable=True)
    photo_url = Column(String(500), nullable=True)  # Path to inspection photo
    checked_at = Column(DateTime(timezone=True), nullable=True)
    checked_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    inspection = relationship("Inspection", back_populates="inspection_items")
    checker = relationship("User")