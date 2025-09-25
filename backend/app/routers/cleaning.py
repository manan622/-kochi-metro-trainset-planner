"""
Cleaning Teams API Router
Handles authentication, team management, cleaning assignments, and photo evaluations
"""
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json
import os
import uuid
import shutil
from pathlib import Path

from app.models.database import get_db
from app.models.models import (
    CleaningTeam, CleaningUser, CleaningAssignment, CleaningPhotoEvaluation, 
    Trainset, CleaningStatus, CleaningQuality, CleaningTeamRole
)
from app.services.gemini_service import get_gemini_service, initialize_gemini_service
from app.services.huggingface_service import get_huggingface_service, initialize_huggingface_service
from app.services.ocr_service import get_ocr_service, initialize_ocr_service
from app.services.auth_service import create_access_token, verify_token, get_password_hash, verify_password
from pydantic import BaseModel, EmailStr
from typing import Union

# Initialize router
router = APIRouter(prefix="/api/cleaning", tags=["cleaning"])
security = HTTPBearer()

# Global AI service instances
gemini_service = None
huggingface_service = None
ocr_service = None

# Pydantic models for API
class CleaningTeamCreate(BaseModel):
    team_name: str
    team_leader: str
    team_members: List[str]
    shift_start: datetime
    shift_end: datetime
    specialization: Optional[str] = None
    contact_number: Optional[str] = None

class CleaningTeamResponse(BaseModel):
    id: int
    team_id: str
    team_name: str
    team_leader: str
    team_members: List[str]
    shift_start: datetime
    shift_end: datetime
    specialization: Optional[str]
    is_active: bool
    contact_number: Optional[str]

class CleaningUserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str
    team_id: int
    role: CleaningTeamRole
    employee_id: str

class CleaningUserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    team_id: int
    role: CleaningTeamRole
    employee_id: str
    is_active: bool

class CleaningUserLogin(BaseModel):
    username: str
    password: str

class CleaningAssignmentCreate(BaseModel):
    trainset_id: int
    team_id: int
    scheduled_start: datetime
    scheduled_end: datetime
    cleaning_type: str
    priority: str = "Medium"
    special_instructions: Optional[str] = None

class CleaningAssignmentResponse(BaseModel):
    id: int
    trainset_id: int
    team_id: int
    assigned_date: datetime
    scheduled_start: datetime
    scheduled_end: datetime
    actual_start: Optional[datetime]
    actual_end: Optional[datetime]
    cleaning_type: str
    status: CleaningStatus
    priority: str
    special_instructions: Optional[str]
    completion_notes: Optional[str]
    trainset_number: str
    team_name: str

class PhotoEvaluationResponse(BaseModel):
    id: int
    assignment_id: int
    photo_url: str
    photo_timestamp: datetime
    area_cleaned: str
    ai_quality_score: Optional[float]
    ai_quality_rating: Optional[CleaningQuality]
    ai_feedback: Optional[str]
    is_approved: Optional[bool]
    cleaner_name: str

class AssignmentUpdateRequest(BaseModel):
    status: Optional[CleaningStatus] = None
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    completion_notes: Optional[str] = None

# Dependency to get current cleaning user
async def get_current_cleaning_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> CleaningUser:
    token = credentials.credentials
    try:
        payload = verify_token(token)
        user_type = payload.get("user_type")
        user_id = payload.get("user_id")
        
        if user_type != "cleaning":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user type for cleaning dashboard"
            )
        
        user = db.query(CleaningUser).filter(CleaningUser.id == user_id).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        return user
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

# Authentication endpoints
@router.post("/auth/login", response_model=Dict[str, str])
async def login_cleaning_user(
    login_data: CleaningUserLogin,
    db: Session = Depends(get_db)
):
    """Authenticate cleaning team member."""
    user = db.query(CleaningUser).filter(
        CleaningUser.username == login_data.username
    ).first()
    
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive"
        )
    
    # Create access token with cleaning user type
    access_token = create_access_token(
        data={
            "sub": user.username,
            "user_id": user.id,
            "user_type": "cleaning",
            "team_id": user.team_id,
            "role": user.role.value
        }
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_type": "cleaning",
        "team_id": str(user.team_id),
        "role": user.role.value
    }

@router.get("/auth/me", response_model=CleaningUserResponse)
async def get_current_user_info(
    current_user: CleaningUser = Depends(get_current_cleaning_user)
):
    """Get current cleaning user information."""
    return CleaningUserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        team_id=current_user.team_id,
        role=current_user.role,
        employee_id=current_user.employee_id,
        is_active=current_user.is_active
    )

# Team management endpoints
@router.get("/teams", response_model=List[CleaningTeamResponse])
async def get_cleaning_teams(
    db: Session = Depends(get_db),
    current_user: CleaningUser = Depends(get_current_cleaning_user)
):
    """Get all cleaning teams."""
    teams = db.query(CleaningTeam).filter(CleaningTeam.is_active == True).all()
    
    result = []
    for team in teams:
        team_members = json.loads(team.team_members) if team.team_members else []
        result.append(CleaningTeamResponse(
            id=team.id,
            team_id=team.team_id,
            team_name=team.team_name,
            team_leader=team.team_leader,
            team_members=team_members,
            shift_start=team.shift_start,
            shift_end=team.shift_end,
            specialization=team.specialization,
            is_active=team.is_active,
            contact_number=team.contact_number
        ))
    
    return result

@router.get("/teams/{team_id}", response_model=CleaningTeamResponse)
async def get_cleaning_team(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: CleaningUser = Depends(get_current_cleaning_user)
):
    """Get specific cleaning team details."""
    team = db.query(CleaningTeam).filter(
        CleaningTeam.id == team_id,
        CleaningTeam.is_active == True
    ).first()
    
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cleaning team not found"
        )
    
    team_members = json.loads(team.team_members) if team.team_members else []
    return CleaningTeamResponse(
        id=team.id,
        team_id=team.team_id,
        team_name=team.team_name,
        team_leader=team.team_leader,
        team_members=team_members,
        shift_start=team.shift_start,
        shift_end=team.shift_end,
        specialization=team.specialization,
        is_active=team.is_active,
        contact_number=team.contact_number
    )

# Assignment endpoints
@router.get("/assignments", response_model=List[CleaningAssignmentResponse])
async def get_cleaning_assignments(
    db: Session = Depends(get_db),
    current_user: CleaningUser = Depends(get_current_cleaning_user),
    status_filter: Optional[str] = None,
    date_filter: Optional[str] = None
):
    """Get cleaning assignments for current user's team."""
    query = db.query(CleaningAssignment).join(Trainset).join(CleaningTeam).filter(
        CleaningAssignment.team_id == current_user.team_id
    )
    
    # Apply filters
    if status_filter:
        query = query.filter(CleaningAssignment.status == status_filter)
    
    if date_filter:
        try:
            filter_date = datetime.fromisoformat(date_filter).date()
            query = query.filter(func.date(CleaningAssignment.scheduled_start) == filter_date)
        except ValueError:
            pass
    
    assignments = query.order_by(CleaningAssignment.scheduled_start.desc()).all()
    
    result = []
    for assignment in assignments:
        result.append(CleaningAssignmentResponse(
            id=assignment.id,
            trainset_id=assignment.trainset_id,
            team_id=assignment.team_id,
            assigned_date=assignment.assigned_date,
            scheduled_start=assignment.scheduled_start,
            scheduled_end=assignment.scheduled_end,
            actual_start=assignment.actual_start,
            actual_end=assignment.actual_end,
            cleaning_type=assignment.cleaning_type,
            status=assignment.status,
            priority=assignment.priority,
            special_instructions=assignment.special_instructions,
            completion_notes=assignment.completion_notes,
            trainset_number=assignment.trainset.number,
            team_name=assignment.cleaning_team.team_name
        ))
    
    return result

@router.get("/assignments/{assignment_id}", response_model=CleaningAssignmentResponse)
async def get_cleaning_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: CleaningUser = Depends(get_current_cleaning_user)
):
    """Get specific cleaning assignment details."""
    assignment = db.query(CleaningAssignment).join(Trainset).join(CleaningTeam).filter(
        CleaningAssignment.id == assignment_id,
        CleaningAssignment.team_id == current_user.team_id
    ).first()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found or not accessible"
        )
    
    return CleaningAssignmentResponse(
        id=assignment.id,
        trainset_id=assignment.trainset_id,
        team_id=assignment.team_id,
        assigned_date=assignment.assigned_date,
        scheduled_start=assignment.scheduled_start,
        scheduled_end=assignment.scheduled_end,
        actual_start=assignment.actual_start,
        actual_end=assignment.actual_end,
        cleaning_type=assignment.cleaning_type,
        status=assignment.status,
        priority=assignment.priority,
        special_instructions=assignment.special_instructions,
        completion_notes=assignment.completion_notes,
        trainset_number=assignment.trainset.number,
        team_name=assignment.cleaning_team.team_name
    )

@router.put("/assignments/{assignment_id}", response_model=CleaningAssignmentResponse)
async def update_cleaning_assignment(
    assignment_id: int,
    update_data: AssignmentUpdateRequest,
    db: Session = Depends(get_db),
    current_user: CleaningUser = Depends(get_current_cleaning_user)
):
    """Update cleaning assignment status and details."""
    assignment = db.query(CleaningAssignment).filter(
        CleaningAssignment.id == assignment_id,
        CleaningAssignment.team_id == current_user.team_id
    ).first()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found or not accessible"
        )
    
    # Update fields
    if update_data.status is not None:
        assignment.status = update_data.status
    if update_data.actual_start is not None:
        assignment.actual_start = update_data.actual_start
    if update_data.actual_end is not None:
        assignment.actual_end = update_data.actual_end
    if update_data.completion_notes is not None:
        assignment.completion_notes = update_data.completion_notes
    
    assignment.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(assignment)
    
    return CleaningAssignmentResponse(
        id=assignment.id,
        trainset_id=assignment.trainset_id,
        team_id=assignment.team_id,
        assigned_date=assignment.assigned_date,
        scheduled_start=assignment.scheduled_start,
        scheduled_end=assignment.scheduled_end,
        actual_start=assignment.actual_start,
        actual_end=assignment.actual_end,
        cleaning_type=assignment.cleaning_type,
        status=assignment.status,
        priority=assignment.priority,
        special_instructions=assignment.special_instructions,
        completion_notes=assignment.completion_notes,
        trainset_number=assignment.trainset.number,
        team_name=assignment.cleaning_team.team_name
    )

# Photo upload and evaluation endpoints
@router.post("/assignments/{assignment_id}/photos", response_model=PhotoEvaluationResponse)
async def upload_cleaning_photo(
    assignment_id: int,
    photo: UploadFile = File(...),
    area_cleaned: str = Form(...),
    db: Session = Depends(get_db),
    current_user: CleaningUser = Depends(get_current_cleaning_user)
):
    """Upload and evaluate cleaning photo using AI."""
    print(f"Starting photo upload for assignment {assignment_id} by user {current_user.username}")
    print(f"Photo filename: {photo.filename}, content type: {photo.content_type}")
    print(f"Area cleaned: {area_cleaned}")
    
    # Verify assignment exists and belongs to user's team
    assignment = db.query(CleaningAssignment).filter(
        CleaningAssignment.id == assignment_id,
        CleaningAssignment.team_id == current_user.team_id
    ).first()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found or not accessible"
        )
    
    # Validate file type
    if not photo.content_type or not photo.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File must be an image. Received content type: {photo.content_type}"
        )
    
    # Validate file size (max 10MB)
    if photo.size and photo.size > 10 * 1024 * 1024:  # 10MB
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size too large. Maximum size is 10MB. Received: {photo.size} bytes"
        )
    
    try:
        # Create upload directory if it doesn't exist
        upload_dir = Path("uploads/cleaning_photos")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        file_extension = photo.filename.split(".")[-1] if "." in photo.filename else "jpg"
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = upload_dir / unique_filename
        
        print(f"Saving photo to: {file_path}")
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(photo.file, buffer)
        
        # Verify file was saved
        if not file_path.exists():
            raise Exception(f"Failed to save file to {file_path}")
        
        print(f"File saved successfully. Size: {file_path.stat().st_size} bytes")
        
        # Read image data for AI evaluation
        with open(file_path, "rb") as f:
            image_data = f.read()
        
        print(f"Image data read successfully. Size: {len(image_data)} bytes")
        
        # Get AI services in order of preference
        print("Getting AI services")
        # Use the global service instances directly instead of calling get functions
        global gemini_service, huggingface_service, ocr_service
        print(f"Gemini service object: {gemini_service}")
        print(f"Hugging Face service object: {huggingface_service}")
        print(f"OCR service object: {ocr_service}")
        
        # Evaluate image with AI (try services in order of preference)
        trainset = db.query(Trainset).filter(Trainset.id == assignment.trainset_id).first()
        if not trainset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trainset not found"
            )
            
        evaluation_result = None
        service_used = None
        
        # Try Hugging Face first (as default service)
        if huggingface_service:
            print("Starting AI evaluation with Hugging Face service")
            try:
                evaluation_result = huggingface_service.evaluate_cleaning_photo(
                    image_data=image_data,
                    area_type=area_cleaned,
                    cleaning_type=assignment.cleaning_type,
                    trainset_number=trainset.number
                )
                service_used = "Hugging Face"
                print(f"AI evaluation completed with Hugging Face. Result: {evaluation_result}")
            except Exception as e:
                print(f"Exception during Hugging Face AI evaluation: {str(e)}")
                import traceback
                print(f"Traceback: {traceback.format_exc()}")
        
        # Try Gemini if Hugging Face failed or is not available
        if not evaluation_result and gemini_service:
            print("Starting AI evaluation with Gemini service")
            try:
                evaluation_result = gemini_service.evaluate_cleaning_photo(
                    image_data=image_data,
                    area_type=area_cleaned,
                    cleaning_type=assignment.cleaning_type,
                    trainset_number=trainset.number
                )
                service_used = "Gemini"
                print(f"AI evaluation completed with Gemini. Result: {evaluation_result}")
            except Exception as e:
                print(f"Exception during Gemini AI evaluation: {str(e)}")
                import traceback
                print(f"Traceback: {traceback.format_exc()}")
        
        # Try OCR service as final fallback
        if not evaluation_result and ocr_service:
            print("Starting AI evaluation with OCR service")
            try:
                evaluation_result = ocr_service.evaluate_cleaning_photo(
                    image_data=image_data,
                    area_type=area_cleaned,
                    cleaning_type=assignment.cleaning_type,
                    trainset_number=trainset.number
                )
                service_used = "OCR"
                print(f"AI evaluation completed with OCR. Result: {evaluation_result}")
            except Exception as e:
                print(f"Exception during OCR AI evaluation: {str(e)}")
                import traceback
                print(f"Traceback: {traceback.format_exc()}")
        
        # If all services failed, use default evaluation
        if not evaluation_result:
            print("All AI evaluation services unavailable, using default evaluation")
            evaluation_result = {
                "error": "All AI evaluation services temporarily unavailable",
                "quality_score": 50,  # Default middle score
                "quality_rating": "Satisfactory",  # Default rating - using correct enum value
                "feedback": "AI evaluation services are temporarily unavailable. This evaluation is based on default values. The system will automatically use AI services when they become available again.",
                "confidence": 0.0
            }
            service_used = "None (Default)"
        elif "error" in evaluation_result:
            print(f"AI evaluation error: {evaluation_result['error']}")
            # Still create the record but with error information
            service_used = service_used or "Error"
        
        print(f"Using AI service: {service_used}")
        
        # Create photo evaluation record
        # Handle case where AI evaluation failed
        quality_score = evaluation_result.get("quality_score", 0) if not evaluation_result.get("error") else 0
        quality_rating = evaluation_result.get("quality_rating", "Unsatisfactory") if not evaluation_result.get("error") else "Unsatisfactory"
        feedback = evaluation_result.get("feedback", "AI evaluation failed") if not evaluation_result.get("error") else evaluation_result.get("feedback", "AI evaluation failed")
        
        # Validate quality rating
        print(f"Attempting to create CleaningQuality enum with value: {quality_rating}")
        try:
            quality_rating_enum = CleaningQuality(quality_rating)
            print(f"Successfully created CleaningQuality enum: {quality_rating_enum}")
        except ValueError as ve:
            print(f"ValueError when creating CleaningQuality enum: {ve}")
            print(f"Invalid quality rating: {quality_rating}, using default Unsatisfactory")
            # Use the correct enum value - it should be "Unsatisfactory" not "UNSATISFACTORY"
            quality_rating_enum = CleaningQuality.UNSATISFACTORY
        except Exception as e:
            print(f"Unexpected error when creating CleaningQuality enum: {e}")
            quality_rating_enum = CleaningQuality.UNSATISFACTORY
        
        print(f"Creating CleaningPhotoEvaluation object with parameters:")
        print(f"  assignment_id: {assignment_id}")
        print(f"  cleaner_id: {current_user.id}")
        print(f"  photo_url: {str(file_path)}")
        print(f"  photo_timestamp: {datetime.utcnow()}")
        print(f"  area_cleaned: {area_cleaned}")
        print(f"  ai_evaluation_result: {json.dumps(evaluation_result)[:100]}...")
        print(f"  ai_quality_score: {quality_score}")
        print(f"  ai_quality_rating: {quality_rating_enum}")
        print(f"  ai_feedback: {feedback[:50] if feedback else 'None'}...")
        print(f"  is_approved: {quality_score >= 70}")
        
        photo_eval = CleaningPhotoEvaluation(
            assignment_id=assignment_id,
            cleaner_id=current_user.id,
            photo_url=str(file_path),
            photo_timestamp=datetime.utcnow(),
            area_cleaned=area_cleaned,
            ai_evaluation_result=json.dumps(evaluation_result),
            ai_quality_score=quality_score,
            ai_quality_rating=quality_rating_enum,
            ai_feedback=feedback,
            is_approved=quality_score >= 70  # Auto-approve if score >= 70
        )
        print(f"Successfully created CleaningPhotoEvaluation object")
        
        print(f"Attempting to save photo evaluation to database for assignment {assignment_id}")
        try:
            db.add(photo_eval)
            print("Added photo evaluation to session")
            db.commit()
            print("Committed to database")
            db.refresh(photo_eval)
            print("Refreshed photo evaluation from database")
        except Exception as db_error:
            print(f"Database error: {str(db_error)}")
            import traceback
            print(f"Database error traceback: {traceback.format_exc()}")
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(db_error)} - Check server logs for details"
            )
        
        return PhotoEvaluationResponse(
            id=photo_eval.id,
            assignment_id=photo_eval.assignment_id,
            photo_url=photo_eval.photo_url,
            photo_timestamp=photo_eval.photo_timestamp,
            area_cleaned=photo_eval.area_cleaned,
            ai_quality_score=photo_eval.ai_quality_score,
            ai_quality_rating=photo_eval.ai_quality_rating,
            ai_feedback=photo_eval.ai_feedback,
            is_approved=photo_eval.is_approved,
            cleaner_name=current_user.full_name
        )
        
    except Exception as e:
        # Log detailed error information
        import traceback
        error_details = f"Failed to process photo: {str(e)}\nTraceback: {traceback.format_exc()}"
        print(f"ERROR: {error_details}")
        
        # Clean up file if something went wrong
        if 'file_path' in locals() and file_path.exists():
            try:
                file_path.unlink()
            except Exception as cleanup_error:
                print(f"ERROR: Failed to clean up file: {cleanup_error}")
        
        # Return a more detailed error response
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process photo: {str(e)} - Check server logs for details"
        )

@router.get("/assignments/{assignment_id}/photos", response_model=List[PhotoEvaluationResponse])
async def get_assignment_photos(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: CleaningUser = Depends(get_current_cleaning_user)
):
    """Get all photos for a specific assignment."""
    # Verify assignment access
    assignment = db.query(CleaningAssignment).filter(
        CleaningAssignment.id == assignment_id,
        CleaningAssignment.team_id == current_user.team_id
    ).first()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found or not accessible"
        )
    
    photos = db.query(CleaningPhotoEvaluation).join(CleaningUser).filter(
        CleaningPhotoEvaluation.assignment_id == assignment_id
    ).order_by(CleaningPhotoEvaluation.photo_timestamp.desc()).all()
    
    result = []
    for photo in photos:
        result.append(PhotoEvaluationResponse(
            id=photo.id,
            assignment_id=photo.assignment_id,
            photo_url=photo.photo_url,
            photo_timestamp=photo.photo_timestamp,
            area_cleaned=photo.area_cleaned,
            ai_quality_score=photo.ai_quality_score,
            ai_quality_rating=photo.ai_quality_rating,
            ai_feedback=photo.ai_feedback,
            is_approved=photo.is_approved,
            cleaner_name=photo.cleaner.full_name
        ))
    
    return result

# Dashboard summary endpoints
@router.get("/dashboard/summary")
async def get_cleaning_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: CleaningUser = Depends(get_current_cleaning_user)
):
    """Get dashboard summary for cleaning team."""
    today = datetime.now().date()
    
    # Get today's assignments
    today_assignments = db.query(CleaningAssignment).filter(
        CleaningAssignment.team_id == current_user.team_id,
        func.date(CleaningAssignment.scheduled_start) == today
    ).all()
    
    # Count assignments by status
    pending = len([a for a in today_assignments if a.status == CleaningStatus.PENDING])
    in_progress = len([a for a in today_assignments if a.status == CleaningStatus.IN_PROGRESS])
    completed = len([a for a in today_assignments if a.status == CleaningStatus.COMPLETED])
    
    # Get recent photos
    recent_photos = db.query(CleaningPhotoEvaluation).join(CleaningAssignment).filter(
        CleaningAssignment.team_id == current_user.team_id
    ).order_by(CleaningPhotoEvaluation.photo_timestamp.desc()).limit(5).all()
    
    # Calculate average quality score
    avg_score = db.query(func.avg(CleaningPhotoEvaluation.ai_quality_score)).join(CleaningAssignment).filter(
        CleaningAssignment.team_id == current_user.team_id,
        CleaningPhotoEvaluation.ai_quality_score.isnot(None)
    ).scalar() or 0
    
    return {
        "team_info": {
            "team_id": current_user.team.team_id,
            "team_name": current_user.team.team_name,
            "team_leader": current_user.team.team_leader,
            "user_role": current_user.role.value
        },
        "today_summary": {
            "total_assignments": len(today_assignments),
            "pending": pending,
            "in_progress": in_progress,
            "completed": completed,
            "completion_rate": round((completed / len(today_assignments)) * 100, 1) if today_assignments else 0
        },
        "quality_metrics": {
            "average_score": round(avg_score, 1),
            "total_photos": len(recent_photos),
            "approved_photos": len([p for p in recent_photos if p.is_approved])
        },
        "recent_activity": [
            {
                "photo_id": photo.id,
                "area_cleaned": photo.area_cleaned,
                "quality_score": photo.ai_quality_score,
                "timestamp": photo.photo_timestamp,
                "trainset": photo.assignment.trainset.number
            }
            for photo in recent_photos
        ]
    }