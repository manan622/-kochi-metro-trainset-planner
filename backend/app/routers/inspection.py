from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime, timedelta
import json

from app.models.database import get_db
from app.models.models import (
    Inspection, InspectionItem, Trainset, User,
    InspectionStatus, InspectionType, InspectionPriority
)
from app.services.auth_service import get_current_user, require_inspection, require_any_role
from app.schemas import (
    InspectionResponse, InspectionCreate, InspectionUpdate,
    InspectionItemResponse, InspectionItemUpdate, TrainsetAddRequest,
    TrainsetResponse
)

router = APIRouter()

def generate_inspection_number() -> str:
    """Generate a unique inspection number."""
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"INS-{timestamp}"

@router.get("/inspections/my", response_model=List[InspectionResponse])
async def get_my_inspections(
    status: Optional[InspectionStatus] = Query(None, description="Filter by status"),
    inspection_type: Optional[InspectionType] = Query(None, description="Filter by type"),
    limit: int = Query(50, description="Number of inspections to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_inspection)
):
    """Get inspections assigned to the current user."""
    try:
        query = db.query(Inspection).options(
            joinedload(Inspection.trainset),
            joinedload(Inspection.inspector),
            joinedload(Inspection.approver),
            joinedload(Inspection.inspection_items)
        ).filter(Inspection.inspector_id == current_user.id)
        
        if status:
            query = query.filter(Inspection.status == status)
        if inspection_type:
            query = query.filter(Inspection.inspection_type == inspection_type)
        
        inspections = query.order_by(Inspection.scheduled_date.desc()).limit(limit).all()
        
        # Format response with additional data
        result = []
        for inspection in inspections:
            inspection_dict = {
                "id": inspection.id,
                "trainset_id": inspection.trainset_id,
                "inspection_number": inspection.inspection_number,
                "inspector_id": inspection.inspector_id,
                "inspection_type": inspection.inspection_type,
                "status": inspection.status,
                "priority": inspection.priority,
                "scheduled_date": inspection.scheduled_date,
                "actual_start_time": inspection.actual_start_time,
                "actual_end_time": inspection.actual_end_time,
                "estimated_duration": inspection.estimated_duration,
                "actual_duration": inspection.actual_duration,
                "location": inspection.location,
                "description": inspection.description,
                "findings": inspection.findings,
                "recommendations": inspection.recommendations,
                "components_checked": inspection.components_checked,
                "defects_found": inspection.defects_found,
                "safety_compliance": inspection.safety_compliance,
                "approved_by": inspection.approved_by,
                "approved_at": inspection.approved_at,
                "completion_notes": inspection.completion_notes,
                "next_inspection_due": inspection.next_inspection_due,
                "created_at": inspection.created_at,
                "updated_at": inspection.updated_at,
                "trainset_number": inspection.trainset.number if inspection.trainset else None,
                "inspector_name": inspection.inspector.username if inspection.inspector else None,
                "approver_name": inspection.approver.username if inspection.approver else None,
                "inspection_items": [
                    {
                        "id": item.id,
                        "inspection_id": item.inspection_id,
                        "component_name": item.component_name,
                        "check_point": item.check_point,
                        "is_checked": item.is_checked,
                        "status": item.status,
                        "notes": item.notes,
                        "defect_severity": item.defect_severity,
                        "action_required": item.action_required,
                        "photo_url": item.photo_url,
                        "checked_at": item.checked_at,
                        "checked_by": item.checked_by,
                        "created_at": item.created_at,
                        "updated_at": item.updated_at
                    } for item in inspection.inspection_items
                ]
            }
            result.append(inspection_dict)
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching inspections: {str(e)}"
        )

@router.post("/inspections", response_model=InspectionResponse)
async def create_inspection(
    inspection_data: InspectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_inspection)
):
    """Create a new inspection."""
    try:
        # Verify trainset exists
        trainset = db.query(Trainset).filter(Trainset.id == inspection_data.trainset_id).first()
        if not trainset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trainset not found"
            )
        
        # Create inspection
        inspection = Inspection(
            trainset_id=inspection_data.trainset_id,
            inspector_id=current_user.id,
            inspection_number=generate_inspection_number(),
            inspection_type=inspection_data.inspection_type,
            priority=inspection_data.priority,
            scheduled_date=inspection_data.scheduled_date,
            estimated_duration=inspection_data.estimated_duration,
            location=inspection_data.location,
            description=inspection_data.description,
            approval_required=inspection_data.approval_required
        )
        
        db.add(inspection)
        db.flush()  # Get the ID
        
        # Create inspection items if provided
        if inspection_data.inspection_items:
            for item_data in inspection_data.inspection_items:
                item = InspectionItem(
                    inspection_id=inspection.id,
                    component_name=item_data.component_name,
                    check_point=item_data.check_point,
                    is_checked=item_data.is_checked,
                    status=item_data.status,
                    notes=item_data.notes,
                    defect_severity=item_data.defect_severity,
                    action_required=item_data.action_required
                )
                db.add(item)
        
        db.commit()
        db.refresh(inspection)
        
        # Load with relationships for response
        inspection = db.query(Inspection).options(
            joinedload(Inspection.trainset),
            joinedload(Inspection.inspector),
            joinedload(Inspection.inspection_items)
        ).filter(Inspection.id == inspection.id).first()
        
        return {
            "id": inspection.id,
            "trainset_id": inspection.trainset_id,
            "inspection_number": inspection.inspection_number,
            "inspector_id": inspection.inspector_id,
            "inspection_type": inspection.inspection_type,
            "status": inspection.status,
            "priority": inspection.priority,
            "scheduled_date": inspection.scheduled_date,
            "actual_start_time": inspection.actual_start_time,
            "actual_end_time": inspection.actual_end_time,
            "estimated_duration": inspection.estimated_duration,
            "actual_duration": inspection.actual_duration,
            "location": inspection.location,
            "description": inspection.description,
            "findings": inspection.findings,
            "recommendations": inspection.recommendations,
            "components_checked": inspection.components_checked,
            "defects_found": inspection.defects_found,
            "safety_compliance": inspection.safety_compliance,
            "approved_by": inspection.approved_by,
            "approved_at": inspection.approved_at,
            "completion_notes": inspection.completion_notes,
            "next_inspection_due": inspection.next_inspection_due,
            "created_at": inspection.created_at,
            "updated_at": inspection.updated_at,
            "trainset_number": inspection.trainset.number,
            "inspector_name": inspection.inspector.username,
            "approver_name": None,
            "inspection_items": [
                {
                    "id": item.id,
                    "inspection_id": item.inspection_id,
                    "component_name": item.component_name,
                    "check_point": item.check_point,
                    "is_checked": item.is_checked,
                    "status": item.status,
                    "notes": item.notes,
                    "defect_severity": item.defect_severity,
                    "action_required": item.action_required,
                    "photo_url": item.photo_url,
                    "checked_at": item.checked_at,
                    "checked_by": item.checked_by,
                    "created_at": item.created_at,
                    "updated_at": item.updated_at
                } for item in inspection.inspection_items
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating inspection: {str(e)}"
        )

@router.get("/inspections/{inspection_id}", response_model=InspectionResponse)
async def get_inspection(
    inspection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_inspection)
):
    """Get inspection details."""
    try:
        inspection = db.query(Inspection).options(
            joinedload(Inspection.trainset),
            joinedload(Inspection.inspector),
            joinedload(Inspection.approver),
            joinedload(Inspection.inspection_items)
        ).filter(Inspection.id == inspection_id).first()
        
        if not inspection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Inspection not found"
            )
        
        # Check if user has access (inspector or management)
        if (current_user.role.value not in ['management'] and 
            inspection.inspector_id != current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this inspection"
            )
        
        return {
            "id": inspection.id,
            "trainset_id": inspection.trainset_id,
            "inspection_number": inspection.inspection_number,
            "inspector_id": inspection.inspector_id,
            "inspection_type": inspection.inspection_type,
            "status": inspection.status,
            "priority": inspection.priority,
            "scheduled_date": inspection.scheduled_date,
            "actual_start_time": inspection.actual_start_time,
            "actual_end_time": inspection.actual_end_time,
            "estimated_duration": inspection.estimated_duration,
            "actual_duration": inspection.actual_duration,
            "location": inspection.location,
            "description": inspection.description,
            "findings": inspection.findings,
            "recommendations": inspection.recommendations,
            "components_checked": inspection.components_checked,
            "defects_found": inspection.defects_found,
            "safety_compliance": inspection.safety_compliance,
            "approved_by": inspection.approved_by,
            "approved_at": inspection.approved_at,
            "completion_notes": inspection.completion_notes,
            "next_inspection_due": inspection.next_inspection_due,
            "created_at": inspection.created_at,
            "updated_at": inspection.updated_at,
            "trainset_number": inspection.trainset.number if inspection.trainset else None,
            "inspector_name": inspection.inspector.username if inspection.inspector else None,
            "approver_name": inspection.approver.username if inspection.approver else None,
            "inspection_items": [
                {
                    "id": item.id,
                    "inspection_id": item.inspection_id,
                    "component_name": item.component_name,
                    "check_point": item.check_point,
                    "is_checked": item.is_checked,
                    "status": item.status,
                    "notes": item.notes,
                    "defect_severity": item.defect_severity,
                    "action_required": item.action_required,
                    "photo_url": item.photo_url,
                    "checked_at": item.checked_at,
                    "checked_by": item.checked_by,
                    "created_at": item.created_at,
                    "updated_at": item.updated_at
                } for item in inspection.inspection_items
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching inspection: {str(e)}"
        )

@router.put("/inspections/{inspection_id}", response_model=InspectionResponse)
async def update_inspection(
    inspection_id: int,
    inspection_data: InspectionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_inspection)
):
    """Update an existing inspection."""
    try:
        inspection = db.query(Inspection).filter(Inspection.id == inspection_id).first()
        
        if not inspection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Inspection not found"
            )
        
        # Check if user has access (inspector or management)
        if (current_user.role.value not in ['management'] and 
            inspection.inspector_id != current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to modify this inspection"
            )
        
        # Update fields if provided
        update_data = inspection_data.dict(exclude_unset=True)
        
        # Special handling for timing updates
        if inspection_data.actual_start_time and not inspection.actual_start_time:
            update_data['status'] = InspectionStatus.IN_PROGRESS
        
        if inspection_data.actual_end_time and inspection_data.actual_start_time:
            # Calculate actual duration
            start = inspection_data.actual_start_time or inspection.actual_start_time
            end = inspection_data.actual_end_time
            if start and end:
                duration = int((end - start).total_seconds() / 60)  # minutes
                update_data['actual_duration'] = duration
            update_data['status'] = InspectionStatus.COMPLETED
        
        for field, value in update_data.items():
            setattr(inspection, field, value)
        
        db.commit()
        db.refresh(inspection)
        
        # Load with relationships for response
        inspection = db.query(Inspection).options(
            joinedload(Inspection.trainset),
            joinedload(Inspection.inspector),
            joinedload(Inspection.approver),
            joinedload(Inspection.inspection_items)
        ).filter(Inspection.id == inspection.id).first()
        
        return {
            "id": inspection.id,
            "trainset_id": inspection.trainset_id,
            "inspection_number": inspection.inspection_number,
            "inspector_id": inspection.inspector_id,
            "inspection_type": inspection.inspection_type,
            "status": inspection.status,
            "priority": inspection.priority,
            "scheduled_date": inspection.scheduled_date,
            "actual_start_time": inspection.actual_start_time,
            "actual_end_time": inspection.actual_end_time,
            "estimated_duration": inspection.estimated_duration,
            "actual_duration": inspection.actual_duration,
            "location": inspection.location,
            "description": inspection.description,
            "findings": inspection.findings,
            "recommendations": inspection.recommendations,
            "components_checked": inspection.components_checked,
            "defects_found": inspection.defects_found,
            "safety_compliance": inspection.safety_compliance,
            "approved_by": inspection.approved_by,
            "approved_at": inspection.approved_at,
            "completion_notes": inspection.completion_notes,
            "next_inspection_due": inspection.next_inspection_due,
            "created_at": inspection.created_at,
            "updated_at": inspection.updated_at,
            "trainset_number": inspection.trainset.number if inspection.trainset else None,
            "inspector_name": inspection.inspector.username if inspection.inspector else None,
            "approver_name": inspection.approver.username if inspection.approver else None,
            "inspection_items": [
                {
                    "id": item.id,
                    "inspection_id": item.inspection_id,
                    "component_name": item.component_name,
                    "check_point": item.check_point,
                    "is_checked": item.is_checked,
                    "status": item.status,
                    "notes": item.notes,
                    "defect_severity": item.defect_severity,
                    "action_required": item.action_required,
                    "photo_url": item.photo_url,
                    "checked_at": item.checked_at,
                    "checked_by": item.checked_by,
                    "created_at": item.created_at,
                    "updated_at": item.updated_at
                } for item in inspection.inspection_items
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating inspection: {str(e)}"
        )

@router.put("/inspections/{inspection_id}/items/{item_id}", response_model=InspectionItemResponse)
async def update_inspection_item(
    inspection_id: int,
    item_id: int,
    item_data: InspectionItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_inspection)
):
    """Update an inspection item."""
    try:
        # Verify inspection exists and user has access
        inspection = db.query(Inspection).filter(Inspection.id == inspection_id).first()
        if not inspection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Inspection not found"
            )
        
        if (current_user.role.value not in ['management'] and 
            inspection.inspector_id != current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to modify this inspection"
            )
        
        # Get inspection item
        item = db.query(InspectionItem).filter(
            InspectionItem.id == item_id,
            InspectionItem.inspection_id == inspection_id
        ).first()
        
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Inspection item not found"
            )
        
        # Update fields
        update_data = item_data.dict(exclude_unset=True)
        
        # Set checked timestamp if marking as checked
        if item_data.is_checked and not item.checked_at:
            update_data['checked_at'] = datetime.now()
            update_data['checked_by'] = current_user.id
        
        for field, value in update_data.items():
            setattr(item, field, value)
        
        db.commit()
        db.refresh(item)
        
        return item
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating inspection item: {str(e)}"
        )

@router.post("/inspection/trainsets", response_model=TrainsetResponse)
async def add_trainset_for_inspection(
    trainset_data: TrainsetAddRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_inspection)
):
    """Add a new trainset to the database for mid-day check or emergency inspection."""
    try:
        # Check if trainset already exists
        existing = db.query(Trainset).filter(Trainset.number == trainset_data.number).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Trainset {trainset_data.number} already exists"
            )
        
        # Create new trainset
        trainset = Trainset(
            number=trainset_data.number,
            current_mileage=trainset_data.current_mileage,
            stabling_bay=trainset_data.stabling_bay,
            reasoning=trainset_data.description or f"Added for inspection by {current_user.username}"
        )
        
        db.add(trainset)
        db.commit()
        db.refresh(trainset)
        
        return trainset
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding trainset: {str(e)}"
        )

@router.get("/inspection/trainsets/available", response_model=List[TrainsetResponse])
async def get_available_trainsets(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_inspection)
):
    """Get list of trainsets available for inspection."""
    try:
        trainsets = db.query(Trainset).order_by(Trainset.number).all()
        return trainsets
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching trainsets: {str(e)}"
        )

@router.post("/inspections/{inspection_id}/start")
async def start_inspection(
    inspection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_inspection)
):
    """Start an inspection (mark as in progress)."""
    try:
        inspection = db.query(Inspection).filter(Inspection.id == inspection_id).first()
        
        if not inspection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Inspection not found"
            )
        
        if inspection.inspector_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to start this inspection"
            )
        
        if inspection.status != InspectionStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot start inspection with status: {inspection.status}"
            )
        
        inspection.status = InspectionStatus.IN_PROGRESS
        inspection.actual_start_time = datetime.now()
        
        db.commit()
        
        return {"message": "Inspection started successfully", "started_at": inspection.actual_start_time}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error starting inspection: {str(e)}"
        )

@router.post("/inspections/{inspection_id}/complete")
async def complete_inspection(
    inspection_id: int,
    completion_notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_inspection)
):
    """Complete an inspection."""
    try:
        inspection = db.query(Inspection).filter(Inspection.id == inspection_id).first()
        
        if not inspection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Inspection not found"
            )
        
        if inspection.inspector_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to complete this inspection"
            )
        
        if inspection.status != InspectionStatus.IN_PROGRESS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot complete inspection with status: {inspection.status}"
            )
        
        now = datetime.now()
        inspection.status = InspectionStatus.COMPLETED
        inspection.actual_end_time = now
        
        if completion_notes:
            inspection.completion_notes = completion_notes
        
        # Calculate actual duration
        if inspection.actual_start_time:
            duration = int((now - inspection.actual_start_time).total_seconds() / 60)
            inspection.actual_duration = duration
        
        # Set next inspection due date (30 days from now as default)
        if not inspection.next_inspection_due:
            inspection.next_inspection_due = now + timedelta(days=30)
        
        db.commit()
        
        return {
            "message": "Inspection completed successfully",
            "completed_at": inspection.actual_end_time,
            "duration_minutes": inspection.actual_duration,
            "next_due": inspection.next_inspection_due
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error completing inspection: {str(e)}"
        )