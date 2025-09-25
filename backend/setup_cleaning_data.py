"""
Database setup script for cleaning teams and sample data.
Run this script to populate the database with cleaning teams, users, and assignments.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import json
from passlib.context import CryptContext

from app.models.database import SessionLocal, engine
from app.models.models import (
    Base, CleaningTeam, CleaningUser, CleaningAssignment, 
    CleaningPhotoEvaluation, Trainset, CleaningStatus, 
    CleaningQuality, CleaningTeamRole
)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def setup_cleaning_data():
    """Set up cleaning teams, users, and sample assignments."""
    db = SessionLocal()
    
    try:
        print("Setting up cleaning teams and data...")
        
        # Create cleaning teams
        teams_data = [
            {
                "team_id": "CT-001",
                "team_name": "Night Shift Alpha",
                "team_leader": "John Smith",
                "team_members": json.dumps(["John Smith", "Maria Garcia", "Ahmed Hassan", "Priya Patel"]),
                "shift_start": datetime.now().replace(hour=22, minute=0, second=0, microsecond=0),
                "shift_end": datetime.now().replace(hour=6, minute=0, second=0, microsecond=0) + timedelta(days=1),
                "specialization": "Interior Deep Cleaning",
                "contact_number": "+91-9876543210"
            },
            {
                "team_id": "CT-002", 
                "team_name": "Night Shift Beta",
                "team_leader": "Sarah Johnson",
                "team_members": json.dumps(["Sarah Johnson", "Rajesh Kumar", "Fatima Ali", "Chen Wei"]),
                "shift_start": datetime.now().replace(hour=23, minute=0, second=0, microsecond=0),
                "shift_end": datetime.now().replace(hour=7, minute=0, second=0, microsecond=0) + timedelta(days=1),
                "specialization": "Exterior & Maintenance",
                "contact_number": "+91-9876543211"
            },
            {
                "team_id": "CT-003",
                "team_name": "Rapid Response Team", 
                "team_leader": "David Wilson",
                "team_members": json.dumps(["David Wilson", "Lisa Chen", "Mohammed Shaikh"]),
                "shift_start": datetime.now().replace(hour=0, minute=0, second=0, microsecond=0),
                "shift_end": datetime.now().replace(hour=8, minute=0, second=0, microsecond=0),
                "specialization": "Emergency Cleaning",
                "contact_number": "+91-9876543212"
            }
        ]
        
        cleaning_teams = []
        for team_data in teams_data:
            team = CleaningTeam(**team_data)
            db.add(team)
            cleaning_teams.append(team)
        
        db.commit()
        
        # Refresh to get IDs
        for team in cleaning_teams:
            db.refresh(team)
        
        print(f"Created {len(cleaning_teams)} cleaning teams")
        
        # Create cleaning users
        users_data = [
            # Team Alpha (CT-001)
            {
                "username": "john.smith",
                "email": "john.smith@metro.com", 
                "hashed_password": hash_password("password123"),
                "full_name": "John Smith",
                "team_id": cleaning_teams[0].id,
                "role": CleaningTeamRole.TEAM_LEADER,
                "employee_id": "EMP-001"
            },
            {
                "username": "maria.garcia",
                "email": "maria.garcia@metro.com",
                "hashed_password": hash_password("password123"),
                "full_name": "Maria Garcia", 
                "team_id": cleaning_teams[0].id,
                "role": CleaningTeamRole.CLEANER,
                "employee_id": "EMP-002"
            },
            {
                "username": "ahmed.hassan",
                "email": "ahmed.hassan@metro.com",
                "hashed_password": hash_password("password123"),
                "full_name": "Ahmed Hassan",
                "team_id": cleaning_teams[0].id,
                "role": CleaningTeamRole.CLEANER,
                "employee_id": "EMP-003"
            },
            
            # Team Beta (CT-002)
            {
                "username": "sarah.johnson",
                "email": "sarah.johnson@metro.com",
                "hashed_password": hash_password("password123"),
                "full_name": "Sarah Johnson",
                "team_id": cleaning_teams[1].id,
                "role": CleaningTeamRole.TEAM_LEADER,
                "employee_id": "EMP-004"
            },
            {
                "username": "rajesh.kumar",
                "email": "rajesh.kumar@metro.com",
                "hashed_password": hash_password("password123"),
                "full_name": "Rajesh Kumar",
                "team_id": cleaning_teams[1].id,
                "role": CleaningTeamRole.CLEANER,
                "employee_id": "EMP-005"
            },
            
            # Rapid Response Team (CT-003)
            {
                "username": "david.wilson",
                "email": "david.wilson@metro.com",
                "hashed_password": hash_password("password123"),
                "full_name": "David Wilson",
                "team_id": cleaning_teams[2].id,
                "role": CleaningTeamRole.SUPERVISOR,
                "employee_id": "EMP-006"
            },
            
            # Demo users for easy testing
            {
                "username": "cleaner1",
                "email": "cleaner1@demo.com",
                "hashed_password": hash_password("password123"),
                "full_name": "Demo Cleaner 1",
                "team_id": cleaning_teams[0].id,
                "role": CleaningTeamRole.CLEANER,
                "employee_id": "DEMO-001"
            },
            {
                "username": "cleaner2",
                "email": "cleaner2@demo.com",
                "hashed_password": hash_password("password123"),
                "full_name": "Demo Cleaner 2",
                "team_id": cleaning_teams[1].id,
                "role": CleaningTeamRole.CLEANER,
                "employee_id": "DEMO-002"
            },
            {
                "username": "supervisor1",
                "email": "supervisor1@demo.com",
                "hashed_password": hash_password("password123"),
                "full_name": "Demo Supervisor",
                "team_id": cleaning_teams[2].id,
                "role": CleaningTeamRole.SUPERVISOR,
                "employee_id": "DEMO-003"
            }
        ]
        
        cleaning_users = []
        for user_data in users_data:
            user = CleaningUser(**user_data)
            db.add(user)
            cleaning_users.append(user)
        
        db.commit()
        
        # Refresh to get IDs
        for user in cleaning_users:
            db.refresh(user)
        
        print(f"Created {len(cleaning_users)} cleaning users")
        
        # Get some trainsets to create assignments for
        trainsets = db.query(Trainset).limit(10).all()
        
        if trainsets:
            # Create sample cleaning assignments
            assignments_data = []
            
            for i, trainset in enumerate(trainsets[:6]):
                team = cleaning_teams[i % len(cleaning_teams)]
                assignment_date = datetime.now() - timedelta(days=i)
                
                assignment = {
                    "trainset_id": trainset.id,
                    "team_id": team.id,
                    "assigned_date": assignment_date,
                    "scheduled_start": assignment_date.replace(hour=23, minute=0),
                    "scheduled_end": assignment_date.replace(hour=5, minute=0) + timedelta(days=1),
                    "cleaning_type": ["Interior", "Exterior", "Deep", "Maintenance"][i % 4],
                    "status": [CleaningStatus.COMPLETED, CleaningStatus.IN_PROGRESS, CleaningStatus.PENDING][i % 3],
                    "priority": ["High", "Medium", "Low"][i % 3],
                    "special_instructions": f"Focus on thorough cleaning of trainset {trainset.number}",
                }
                
                # Set actual times for completed assignments
                if assignment["status"] == CleaningStatus.COMPLETED:
                    assignment["actual_start"] = assignment["scheduled_start"]
                    assignment["actual_end"] = assignment["scheduled_start"] + timedelta(hours=4)
                    assignment["completion_notes"] = f"Cleaning completed successfully for {trainset.number}"
                
                assignments_data.append(assignment)
            
            cleaning_assignments = []
            for assignment_data in assignments_data:
                assignment = CleaningAssignment(**assignment_data)
                db.add(assignment)
                cleaning_assignments.append(assignment)
            
            db.commit()
            
            # Refresh to get IDs
            for assignment in cleaning_assignments:
                db.refresh(assignment)
            
            print(f"Created {len(cleaning_assignments)} cleaning assignments")
            
            # Create sample photo evaluations for completed assignments
            completed_assignments = [a for a in cleaning_assignments if a.status == CleaningStatus.COMPLETED]
            
            photo_evaluations = []
            for assignment in completed_assignments:
                # Get users from the assigned team
                team_users = [u for u in cleaning_users if u.team_id == assignment.team_id]
                
                if team_users:
                    areas = ["Interior", "Exterior", "Seats", "Floor", "Windows"]
                    for j, area in enumerate(areas[:3]):  # 3 photos per assignment
                        
                        # Simulate AI evaluation results
                        quality_scores = [95, 87, 78, 92, 73]
                        quality_ratings = [CleaningQuality.EXCELLENT, CleaningQuality.GOOD, 
                                         CleaningQuality.SATISFACTORY, CleaningQuality.EXCELLENT, 
                                         CleaningQuality.SATISFACTORY]
                        
                        score = quality_scores[j % len(quality_scores)]
                        rating = quality_ratings[j % len(quality_ratings)]
                        
                        photo_eval = CleaningPhotoEvaluation(
                            assignment_id=assignment.id,
                            cleaner_id=team_users[j % len(team_users)].id,
                            photo_url=f"/uploads/cleaning_photos/sample_{assignment.id}_{j}.jpg",
                            photo_timestamp=assignment.actual_end - timedelta(minutes=30-j*10),
                            area_cleaned=area,
                            ai_evaluation_result=json.dumps({
                                "quality_score": score,
                                "quality_rating": rating.value,
                                "confidence": 0.9,
                                "feedback": f"Good cleaning quality detected in {area.lower()} area. Minor improvements possible.",
                                "areas_of_concern": [],
                                "recommendations": ["Maintain current cleaning standards"]
                            }),
                            ai_quality_score=score,
                            ai_quality_rating=rating,
                            ai_feedback=f"AI Assessment: {rating.value} quality cleaning of {area.lower()} area with {score}% confidence",
                            is_approved=score >= 75
                        )
                        
                        db.add(photo_eval)
                        photo_evaluations.append(photo_eval)
            
            db.commit()
            print(f"Created {len(photo_evaluations)} sample photo evaluations")
        
        print("✅ Cleaning data setup completed successfully!")
        print("\nDemo Login Credentials:")
        print("- cleaner1 / password123 (Team Alpha - Cleaner)")
        print("- cleaner2 / password123 (Team Beta - Cleaner)")  
        print("- supervisor1 / password123 (Rapid Response - Supervisor)")
        print("\nAccess cleaning dashboard at: /cleaning/login")
        
    except Exception as e:
        print(f"Error setting up cleaning data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Setup cleaning data
    setup_cleaning_data()