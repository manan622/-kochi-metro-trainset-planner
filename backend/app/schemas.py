from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from app.models.models import (
    UserRole, TrainsetStatus, CertificateStatus, JobCardStatus, 
    BrandingPriorityLevel, InspectionStatus, InspectionType, InspectionPriority
)

# Auth Schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: UserRole
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Trainset Schemas
class TrainsetBase(BaseModel):
    number: str
    current_mileage: Optional[float] = 0.0
    stabling_bay: Optional[str] = None

class TrainsetCreate(TrainsetBase):
    pass

class TrainsetResponse(TrainsetBase):
    id: int
    status: TrainsetStatus
    reasoning: Optional[str] = None
    conflict_alerts: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Fitness Certificate Schemas
class FitnessCertificateBase(BaseModel):
    certificate_type: str
    status: CertificateStatus
    issue_date: datetime
    expiry_date: datetime
    issuing_authority: str
    certificate_number: str
    notes: Optional[str] = None

class FitnessCertificateResponse(FitnessCertificateBase):
    id: int
    trainset_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Job Card Schemas
class JobCardBase(BaseModel):
    job_card_number: str
    description: str
    status: JobCardStatus
    priority: Optional[str] = "Medium"
    created_date: datetime
    due_date: Optional[datetime] = None
    assigned_to: Optional[str] = None
    estimated_hours: Optional[float] = None

class JobCardResponse(JobCardBase):
    id: int
    trainset_id: int
    completed_date: Optional[datetime] = None
    actual_hours: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Branding Priority Schemas
class BrandingPriorityResponse(BaseModel):
    id: int
    trainset_id: int
    priority_level: BrandingPriorityLevel
    brand_name: str
    campaign_name: Optional[str] = None
    contract_start_date: datetime
    contract_end_date: datetime
    revenue_impact: Optional[float] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True

# Mileage Record Schemas
class MileageRecordResponse(BaseModel):
    id: int
    trainset_id: int
    date: datetime
    daily_mileage: float
    cumulative_mileage: float
    route: Optional[str] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True

# Cleaning Slot Schemas
class CleaningSlotResponse(BaseModel):
    id: int
    trainset_id: int
    slot_date: datetime
    slot_time_start: datetime
    slot_time_end: datetime
    cleaning_type: str
    bay_number: str
    assigned_crew: Optional[str] = None
    status: Optional[str] = "Scheduled"
    estimated_duration: Optional[int] = None
    actual_duration: Optional[int] = None

    class Config:
        from_attributes = True

# Stabling Bay Schemas
class StablingBayResponse(BaseModel):
    id: int
    bay_number: str
    capacity: int
    current_occupancy: int
    bay_type: str
    is_available: bool
    maintenance_required: bool
    location: Optional[str] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True

# Trainset Detail Response (with all related data)
class TrainsetDetailResponse(TrainsetResponse):
    fitness_certificates: List[FitnessCertificateResponse] = []
    job_cards: List[JobCardResponse] = []
    branding_priorities: List[BrandingPriorityResponse] = []
    mileage_records: List[MileageRecordResponse] = []
    cleaning_slots: List[CleaningSlotResponse] = []

# Induction Plan Response
class InductionPlanResponse(BaseModel):
    trainset_id: str
    status: TrainsetStatus
    reason: str
    conflict_alerts: List[str]
    metadata: dict

class InductionPlanRequest(BaseModel):
    date: Optional[datetime] = None
    force_recalculate: Optional[bool] = False

class FleetStatusResponse(BaseModel):
    trainsets: List[InductionPlanResponse]
    summary: dict
    generated_at: datetime

# Inspection Schemas
class InspectionItemBase(BaseModel):
    component_name: str
    check_point: str
    is_checked: Optional[bool] = False
    status: Optional[str] = "Pass"
    notes: Optional[str] = None
    defect_severity: Optional[str] = None
    action_required: Optional[str] = None

class InspectionItemCreate(InspectionItemBase):
    pass

class InspectionItemUpdate(BaseModel):
    is_checked: Optional[bool] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    defect_severity: Optional[str] = None
    action_required: Optional[str] = None
    photo_url: Optional[str] = None

class InspectionItemResponse(InspectionItemBase):
    id: int
    inspection_id: int
    photo_url: Optional[str] = None
    checked_at: Optional[datetime] = None
    checked_by: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class InspectionBase(BaseModel):
    trainset_id: int
    inspection_type: InspectionType
    priority: Optional[InspectionPriority] = InspectionPriority.MEDIUM
    scheduled_date: datetime
    estimated_duration: Optional[int] = None
    location: Optional[str] = None
    description: str
    approval_required: Optional[bool] = False

class InspectionCreate(InspectionBase):
    inspection_items: Optional[List[InspectionItemCreate]] = []

class InspectionUpdate(BaseModel):
    inspection_type: Optional[InspectionType] = None
    priority: Optional[InspectionPriority] = None
    scheduled_date: Optional[datetime] = None
    actual_start_time: Optional[datetime] = None
    actual_end_time: Optional[datetime] = None
    estimated_duration: Optional[int] = None
    location: Optional[str] = None
    description: Optional[str] = None
    findings: Optional[str] = None
    recommendations: Optional[str] = None
    safety_compliance: Optional[bool] = None
    completion_notes: Optional[str] = None
    next_inspection_due: Optional[datetime] = None
    status: Optional[InspectionStatus] = None

class InspectionResponse(InspectionBase):
    id: int
    inspection_number: str
    inspector_id: int
    status: InspectionStatus
    actual_start_time: Optional[datetime] = None
    actual_end_time: Optional[datetime] = None
    actual_duration: Optional[int] = None
    findings: Optional[str] = None
    recommendations: Optional[str] = None
    components_checked: Optional[str] = None
    defects_found: Optional[str] = None
    safety_compliance: Optional[bool] = True
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    completion_notes: Optional[str] = None
    next_inspection_due: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Related data
    trainset_number: Optional[str] = None
    inspector_name: Optional[str] = None
    approver_name: Optional[str] = None
    inspection_items: List[InspectionItemResponse] = []

    class Config:
        from_attributes = True

class TrainsetAddRequest(BaseModel):
    number: str
    current_mileage: Optional[float] = 0.0
    stabling_bay: Optional[str] = None
    description: Optional[str] = None