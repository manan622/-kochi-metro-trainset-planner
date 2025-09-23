import sys
import os
sys.path.append('c:/Users/Akhilesh/Desktop/Hackathon 2025/backend')

from app.models.database import SessionLocal
from app.services.induction_service import InductionPlanner
from datetime import datetime

def test_induction_planner():
    try:
        print("Creating database session...")
        db = SessionLocal()
        
        print("Creating InductionPlanner...")
        planner = InductionPlanner(db)
        
        print("Testing plan_induction_for_date...")
        target_date = datetime.now()
        
        # This is where the error likely occurs
        induction_plans = planner.plan_induction_for_date(target_date)
        
        print(f"Successfully generated {len(induction_plans)} induction plans")
        
        for plan in induction_plans[:3]:  # Show first 3
            print(f"Trainset {plan.trainset_id}: {plan.status.value}")
            
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    test_induction_planner()