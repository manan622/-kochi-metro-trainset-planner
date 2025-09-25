from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.models.database import get_db
from app.models.models import (
    Trainset, User, CleaningAssignment, CleaningTeam, 
    CleaningPhotoEvaluation, CleaningUser
)
from app.services.auth_service import get_current_user, require_any_role, require_management
from app.services.induction_service import InductionPlanner
from app.utils.csv_importer import generate_sample_csv, CSVImporter, create_stabling_bays
from app.schemas import (
    TrainsetResponse, 
    TrainsetDetailResponse, 
    InductionPlanResponse,
    InductionPlanRequest,
    FleetStatusResponse
)

router = APIRouter()

@router.post("/induction/plan", response_model=FleetStatusResponse)
async def generate_induction_plan(
    request: Optional[InductionPlanRequest] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_any_role)
):
    """
    Generate nightly trainset induction plan.
    
    Returns a ranked list of trainsets with their status (Fit, Unfit, Standby)
    and explainable reasoning for each decision.
    
    Access: All authenticated users (management, inspection, worker)
    """
    try:
        planner = InductionPlanner(db)
        
        target_date = request.date if request and request.date else datetime.now()
        induction_plans = planner.plan_induction_for_date(target_date)
        
        # Generate summary statistics
        summary = {
            "total_trainsets": len(induction_plans),
            "fit": len([p for p in induction_plans if p.status.value == "Fit"]),
            "unfit": len([p for p in induction_plans if p.status.value == "Unfit"]),
            "standby": len([p for p in induction_plans if p.status.value == "Standby"]),
            "total_alerts": sum(len(p.conflict_alerts) for p in induction_plans),
            "planning_date": target_date.isoformat()
        }
        
        return FleetStatusResponse(
            trainsets=induction_plans,
            summary=summary,
            generated_at=datetime.now()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating induction plan: {str(e)}"
        )

@router.get("/trainsets", response_model=List[TrainsetResponse])
async def get_all_trainsets(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_any_role)
):
    """Get list of all trainsets with basic information."""
    try:
        trainsets = db.query(Trainset).all()
        print(f"Successfully loaded {len(trainsets)} trainsets")
        return trainsets
    except Exception as e:
        print(f"Error loading trainsets: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error loading trainsets: {str(e)}"
        )

@router.get("/trainsets/{trainset_id}", response_model=TrainsetDetailResponse)
async def get_trainset_detail(
    trainset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_any_role)
):
    """Get detailed information for a specific trainset including all related data."""
    try:
        trainset = db.query(Trainset).filter(Trainset.id == trainset_id).first()
        
        if not trainset:
            print(f"Trainset with ID {trainset_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Trainset with ID {trainset_id} not found"
            )
        
        print(f"Successfully loaded trainset {trainset.number} (ID: {trainset_id})")
        return trainset
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error loading trainset {trainset_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error loading trainset: {str(e)}"
        )

@router.get("/trainsets/number/{trainset_number}", response_model=TrainsetDetailResponse)
async def get_trainset_by_number(
    trainset_number: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_any_role)
):
    """Get detailed information for a specific trainset by its number (e.g., TS-2003)."""
    try:
        trainset = db.query(Trainset).filter(Trainset.number == trainset_number).first()
        
        if not trainset:
            print(f"Trainset {trainset_number} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Trainset {trainset_number} not found"
            )
        
        print(f"Successfully loaded trainset {trainset_number} (ID: {trainset.id})")
        return trainset
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error loading trainset {trainset_number}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error loading trainset {trainset_number}: {str(e)}"
        )

@router.get("/fleet/status", response_model=FleetStatusResponse)
async def get_fleet_status(
    date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_any_role)
):
    """Get current fleet status with induction recommendations."""
    try:
        target_date = datetime.fromisoformat(date) if date else datetime.now()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD format."
        )
    
    planner = InductionPlanner(db)
    induction_plans = planner.plan_induction_for_date(target_date)
    
    summary = {
        "total_trainsets": len(induction_plans),
        "fit": len([p for p in induction_plans if p.status.value == "Fit"]),
        "unfit": len([p for p in induction_plans if p.status.value == "Unfit"]),
        "standby": len([p for p in induction_plans if p.status.value == "Standby"]),
        "total_alerts": sum(len(p.conflict_alerts) for p in induction_plans),
        "planning_date": target_date.isoformat()
    }
    
    return FleetStatusResponse(
        trainsets=induction_plans,
        summary=summary,
        generated_at=datetime.now()
    )

@router.get("/trainsets/{trainset_id}/evaluation")
async def get_trainset_evaluation(
    trainset_id: int,
    date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_any_role)
):
    """Get detailed evaluation for a specific trainset."""
    try:
        trainset = db.query(Trainset).filter(Trainset.id == trainset_id).first()
        
        if not trainset:
            print(f"Trainset with ID {trainset_id} not found for evaluation")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Trainset with ID {trainset_id} not found"
            )
        
        try:
            target_date = datetime.fromisoformat(date) if date else datetime.now()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Use YYYY-MM-DD format."
            )
        
        planner = InductionPlanner(db)
        evaluation = planner._evaluate_trainset(trainset, target_date)
        
        print(f"Successfully evaluated trainset {trainset.number} (ID: {trainset_id})")
        return evaluation
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error evaluating trainset {trainset_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error evaluating trainset: {str(e)}"
        )

@router.post("/data/load-sample")
async def load_sample_data(
    num_trainsets: int = Query(25, description="Number of sample trainsets to generate"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_management)
):
    """Load sample trainset data for testing and demonstration.
    
    Access: Management only
    """
    try:
        import os
        import tempfile
        
        # Create temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
            csv_path = temp_file.name
        
        # Generate sample CSV data
        generate_sample_csv(csv_path, num_trainsets)
        
        # Import the data
        with CSVImporter(db) as importer:
            results = importer.import_trainsets_from_csv(csv_path)
        
        # Create stabling bays
        create_stabling_bays(db)
        
        # Clean up temporary file
        os.unlink(csv_path)
        
        return {
            "message": "Sample data loaded successfully",
            "imported_trainsets": results["imported"],
            "updated_trainsets": results["updated"],
            "errors": results["errors"],
            "stabling_bays_created": True
        }
        
    except Exception as e:
        print(f"Error loading sample data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error loading sample data: {str(e)}"
        )

@router.delete("/data/clear")
async def clear_all_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_management)
):
    """Clear all trainset data from the database.
    
    Access: Management only
    """
    try:
        from app.models.models import (
            CleaningSlot, MileageRecord, BrandingPriority, 
            JobCard, FitnessCertificate, Trainset, StablingBay
        )
        
        # Delete in order to respect foreign key constraints
        db.query(CleaningSlot).delete()
        db.query(MileageRecord).delete()
        db.query(BrandingPriority).delete()
        db.query(JobCard).delete()
        db.query(FitnessCertificate).delete()
        db.query(Trainset).delete()
        db.query(StablingBay).delete()
        
        db.commit()
        
        return {
            "message": "All trainset data cleared successfully"
        }
        
    except Exception as e:
        db.rollback()
        print(f"Error clearing data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error clearing data: {str(e)}"
        )

# Management endpoints for viewing cleaning data
@router.get("/trainsets/{trainset_id}/cleaning")
async def get_trainset_cleaning_info(
    trainset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_any_role)
):
    """Get cleaning information for a specific trainset."""
    try:
        trainset = db.query(Trainset).filter(Trainset.id == trainset_id).first()
        
        if not trainset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Trainset with ID {trainset_id} not found"
            )
        
        # Get recent cleaning assignments
        cleaning_assignments = db.query(CleaningAssignment).filter(
            CleaningAssignment.trainset_id == trainset_id
        ).order_by(CleaningAssignment.assigned_date.desc()).limit(5).all()
        
        # Get photos for recent assignments
        assignment_ids = [a.id for a in cleaning_assignments]
        photos = db.query(CleaningPhotoEvaluation).filter(
            CleaningPhotoEvaluation.assignment_id.in_(assignment_ids)
        ).order_by(CleaningPhotoEvaluation.photo_timestamp.desc()).all() if assignment_ids else []
        
        # Calculate average quality score
        avg_score = (
            sum(p.ai_quality_score for p in photos if p.ai_quality_score) / len(photos)
            if photos and any(p.ai_quality_score for p in photos)
            else 0
        )
        
        return {
            "trainset_number": trainset.number,
            "recent_assignments": [
                {
                    "id": assignment.id,
                    "team_name": assignment.cleaning_team.team_name,
                    "cleaning_type": assignment.cleaning_type,
                    "status": assignment.status.value,
                    "assigned_date": assignment.assigned_date,
                    "completed_date": assignment.actual_end,
                    "completion_notes": assignment.completion_notes
                }
                for assignment in cleaning_assignments
            ],
            "recent_photos": [
                {
                    "id": photo.id,
                    "assignment_id": photo.assignment_id,
                    "area_cleaned": photo.area_cleaned,
                    "ai_quality_score": photo.ai_quality_score,
                    "ai_quality_rating": photo.ai_quality_rating.value if photo.ai_quality_rating else None,
                    "photo_timestamp": photo.photo_timestamp,
                    "cleaner_name": photo.cleaner.full_name,
                    "team_name": photo.assignment.cleaning_team.team_name,
                    "is_approved": photo.is_approved
                }
                for photo in photos
            ],
            "quality_summary": {
                "average_score": round(avg_score, 1),
                "total_photos": len(photos),
                "approved_photos": len([p for p in photos if p.is_approved]),
                "recent_assignments": len(cleaning_assignments)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error loading cleaning info for trainset {trainset_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error loading cleaning information: {str(e)}"
        )