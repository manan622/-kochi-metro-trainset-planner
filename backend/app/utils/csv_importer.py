import pandas as pd
import os
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
import random

from app.models.database import SessionLocal
from app.models.models import (
    Trainset, FitnessCertificate, JobCard, BrandingPriority, 
    MileageRecord, CleaningSlot, StablingBay,
    TrainsetStatus, CertificateStatus, JobCardStatus, BrandingPriorityLevel
)

class CSVImporter:
    """Utility class for importing trainset data from CSV files."""
    
    def __init__(self, db: Session = None):
        self.db = db or SessionLocal()
        self._should_close_db = db is None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._should_close_db:
            self.db.close()
    
    def import_trainsets_from_csv(self, csv_file_path: str) -> Dict[str, Any]:
        """Import trainsets from CSV file."""
        if not os.path.exists(csv_file_path):
            raise FileNotFoundError(f"CSV file not found: {csv_file_path}")
        
        try:
            df = pd.read_csv(csv_file_path)
            results = {
                "imported": 0,
                "updated": 0,
                "errors": []
            }
            
            for _, row in df.iterrows():
                try:
                    self._import_trainset_row(row)
                    results["imported"] += 1
                except Exception as e:
                    results["errors"].append(f"Row {row.name}: {str(e)}")
            
            self.db.commit()
            return results
            
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Error importing CSV: {str(e)}")
    
    def _import_trainset_row(self, row: pd.Series):
        """Import a single trainset row from CSV."""
        # Check if trainset exists
        trainset = self.db.query(Trainset).filter(
            Trainset.number == row['trainset_number']
        ).first()
        
        if not trainset:
            # Create new trainset
            trainset = Trainset(
                number=row['trainset_number'],
                current_mileage=float(row.get('current_mileage', 0)),
                stabling_bay=row.get('stabling_bay'),
                status=TrainsetStatus.STANDBY
            )
            self.db.add(trainset)
            self.db.flush()  # Get the ID
        
        # Import related data if columns exist
        self._import_fitness_certificate(trainset, row)
        self._import_job_card(trainset, row)
        self._import_branding_priority(trainset, row)
        self._import_mileage_record(trainset, row)
        self._import_cleaning_slot(trainset, row)
    
    def _import_fitness_certificate(self, trainset: Trainset, row: pd.Series):
        """Import fitness certificate data."""
        if 'fc_type' in row and pd.notna(row['fc_type']):
            cert = FitnessCertificate(
                trainset_id=trainset.id,
                certificate_type=row['fc_type'],
                status=CertificateStatus(row.get('fc_status', 'Valid')),
                issue_date=pd.to_datetime(row.get('fc_issue_date', datetime.now())),
                expiry_date=pd.to_datetime(row.get('fc_expiry_date', datetime.now() + timedelta(days=365))),
                issuing_authority=row.get('fc_authority', 'KMRL'),
                certificate_number=row.get('fc_number', f"FC-{trainset.number}-{row['fc_type']}")
            )
            self.db.add(cert)
    
    def _import_job_card(self, trainset: Trainset, row: pd.Series):
        """Import job card data."""
        if 'job_card_number' in row and pd.notna(row['job_card_number']):
            job_card = JobCard(
                trainset_id=trainset.id,
                job_card_number=row['job_card_number'],
                description=row.get('job_description', 'Maintenance work'),
                status=JobCardStatus(row.get('job_status', 'Open')),
                priority=row.get('job_priority', 'Medium'),
                created_date=pd.to_datetime(row.get('job_created_date', datetime.now())),
                due_date=pd.to_datetime(row.get('job_due_date')) if pd.notna(row.get('job_due_date')) else None
            )
            self.db.add(job_card)
    
    def _import_branding_priority(self, trainset: Trainset, row: pd.Series):
        """Import branding priority data."""
        if 'brand_name' in row and pd.notna(row['brand_name']):
            # Handle optional fields with NaN values
            campaign_name = row.get('campaign_name')
            if pd.isna(campaign_name):
                campaign_name = None
            
            revenue_impact = row.get('revenue_impact')
            if pd.isna(revenue_impact):
                revenue_impact = None
            else:
                revenue_impact = float(revenue_impact)
            
            branding = BrandingPriority(
                trainset_id=trainset.id,
                priority_level=BrandingPriorityLevel(row.get('brand_priority', 'Low')),
                brand_name=row['brand_name'],
                campaign_name=campaign_name,
                contract_start_date=pd.to_datetime(row.get('brand_start_date', datetime.now())),
                contract_end_date=pd.to_datetime(row.get('brand_end_date', datetime.now() + timedelta(days=90))),
                revenue_impact=revenue_impact
            )
            self.db.add(branding)
    
    def _import_mileage_record(self, trainset: Trainset, row: pd.Series):
        """Import mileage record data."""
        if 'daily_mileage' in row and pd.notna(row['daily_mileage']):
            mileage = MileageRecord(
                trainset_id=trainset.id,
                date=pd.to_datetime(row.get('mileage_date', datetime.now())),
                daily_mileage=float(row['daily_mileage']),
                cumulative_mileage=float(row.get('cumulative_mileage', trainset.current_mileage)),
                route=row.get('route')
            )
            self.db.add(mileage)
    
    def _import_cleaning_slot(self, trainset: Trainset, row: pd.Series):
        """Import cleaning slot data."""
        if 'cleaning_type' in row and pd.notna(row['cleaning_type']):
            # Handle NaN values properly
            cleaning_date = row.get('cleaning_date')
            if pd.isna(cleaning_date):
                cleaning_date = datetime.now()
            else:
                cleaning_date = pd.to_datetime(cleaning_date)
            
            cleaning_bay = row.get('cleaning_bay')
            if pd.isna(cleaning_bay):
                cleaning_bay = 'Bay-01'
            
            cleaning_crew = row.get('cleaning_crew')
            if pd.isna(cleaning_crew):
                cleaning_crew = None
            
            cleaning_duration = row.get('cleaning_duration')
            if pd.isna(cleaning_duration):
                cleaning_duration = None
            else:
                cleaning_duration = int(cleaning_duration)
            
            cleaning = CleaningSlot(
                trainset_id=trainset.id,
                slot_date=cleaning_date,
                slot_time_start=cleaning_date.replace(hour=22, minute=0, second=0),
                slot_time_end=cleaning_date.replace(hour=4, minute=0, second=0) + timedelta(days=1),
                cleaning_type=row['cleaning_type'],
                bay_number=cleaning_bay,
                assigned_crew=cleaning_crew,
                estimated_duration=cleaning_duration
            )
            self.db.add(cleaning)

def generate_sample_csv(file_path: str, num_trainsets: int = 25):
    """Generate a sample CSV file with dummy trainset data."""
    
    # Generate sample data
    data = []
    for i in range(1, num_trainsets + 1):
        trainset_num = f"TS-{2000 + i:04d}"
        
        # Randomly determine if trainset has issues
        has_expired_cert = random.choice([True, False, False])  # 33% chance
        has_job_card = random.choice([True, False, False, False])  # 25% chance
        has_branding = random.choice([True, False, False])  # 33% chance
        
        row = {
            'trainset_number': trainset_num,
            'current_mileage': random.randint(80000, 150000),
            'stabling_bay': f"Bay-{random.randint(1, 10):02d}",
            
            # Fitness Certificate
            'fc_type': random.choice(['Rolling-Stock', 'Signalling', 'Telecom']),
            'fc_status': 'Expired' if has_expired_cert else 'Valid',
            'fc_issue_date': (datetime.now() - timedelta(days=random.randint(30, 400))).strftime('%Y-%m-%d'),
            'fc_expiry_date': (datetime.now() - timedelta(days=random.randint(1, 30)) if has_expired_cert 
                              else datetime.now() + timedelta(days=random.randint(30, 365))).strftime('%Y-%m-%d'),
            'fc_authority': 'KMRL',
            'fc_number': f"FC-{trainset_num}-001",
            
            # Job Card (only if has issues)
            'job_card_number': f"JB-{4000 + i}" if has_job_card else None,
            'job_description': random.choice([
                'Brake system repair', 'Door mechanism maintenance', 'Air conditioning service',
                'Wheel replacement', 'Electrical system check'
            ]) if has_job_card else None,
            'job_status': 'Open' if has_job_card else None,
            'job_priority': random.choice(['High', 'Medium', 'Low']) if has_job_card else None,
            'job_created_date': (datetime.now() - timedelta(days=random.randint(1, 15))).strftime('%Y-%m-%d') if has_job_card else None,
            'job_due_date': (datetime.now() + timedelta(days=random.randint(1, 7))).strftime('%Y-%m-%d') if has_job_card else None,
            
            # Branding (only some trainsets)
            'brand_name': random.choice([
                'Coca-Cola', 'Samsung', 'LG Electronics', 'Airtel', 'BSNL'
            ]) if has_branding else None,
            'campaign_name': f"Metro Campaign {random.randint(1, 50)}" if has_branding else None,
            'brand_priority': random.choice(['High', 'Medium', 'Low']) if has_branding else None,
            'brand_start_date': (datetime.now() - timedelta(days=random.randint(1, 60))).strftime('%Y-%m-%d') if has_branding else None,
            'brand_end_date': (datetime.now() + timedelta(days=random.randint(30, 180))).strftime('%Y-%m-%d') if has_branding else None,
            'revenue_impact': random.randint(50000, 500000) if has_branding else None,
            
            # Mileage Record
            'daily_mileage': random.randint(200, 800),
            'cumulative_mileage': random.randint(80000, 150000),
            'mileage_date': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
            'route': random.choice(['Blue Line', 'Green Line', 'Red Line']),
            
            # Cleaning Slot (some trainsets)
            'cleaning_type': random.choice(['Basic', 'Deep', 'Detailing']) if random.choice([True, False]) else None,
            'cleaning_date': datetime.now().strftime('%Y-%m-%d') if random.choice([True, False]) else None,
            'cleaning_bay': f"Bay-C{random.randint(1, 5)}" if random.choice([True, False]) else None,
            'cleaning_crew': f"Crew-{random.randint(1, 10)}" if random.choice([True, False]) else None,
            'cleaning_duration': random.choice([180, 240, 360]) if random.choice([True, False]) else None
        }
        
        data.append(row)
    
    # Create DataFrame and save to CSV
    df = pd.DataFrame(data)
    df.to_csv(file_path, index=False)
    print(f"Sample CSV generated: {file_path}")
    return file_path

def create_stabling_bays(db: Session):
    """Create sample stabling bay data."""
    bay_types = ['Maintenance', 'Parking', 'Inspection']
    
    for i in range(1, 11):
        bay = StablingBay(
            bay_number=f"Bay-{i:02d}",
            capacity=1,
            current_occupancy=random.choice([0, 1]),
            bay_type=random.choice(bay_types),
            is_available=random.choice([True, True, True, False]),  # 75% available
            maintenance_required=random.choice([False, False, False, True]),  # 25% need maintenance
            location=f"Section {chr(65 + i//3)}" # Section A, B, C, D
        )
        db.add(bay)
    
    db.commit()

# CLI utility functions
def import_csv_command(csv_file_path: str):
    """Command line utility to import CSV data."""
    try:
        with CSVImporter() as importer:
            results = importer.import_trainsets_from_csv(csv_file_path)
            print(f"Import completed:")
            print(f"- Imported: {results['imported']} trainsets")
            print(f"- Updated: {results['updated']} trainsets")
            if results['errors']:
                print(f"- Errors: {len(results['errors'])}")
                for error in results['errors']:
                    print(f"  {error}")
    except Exception as e:
        print(f"Import failed: {e}")

def generate_sample_data_command(file_path: str = "sample_trainsets.csv", num_trainsets: int = 25):
    """Command line utility to generate sample data."""
    try:
        generate_sample_csv(file_path, num_trainsets)
        print(f"Sample data generated: {file_path}")
        
        # Also create stabling bays
        from app.models.database import SessionLocal
        db = SessionLocal()
        create_stabling_bays(db)
        db.close()
        print("Sample stabling bays created")
        
    except Exception as e:
        print(f"Sample data generation failed: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python csv_importer.py generate [file_path] [num_trainsets]")
        print("  python csv_importer.py import <csv_file_path>")
    elif sys.argv[1] == "generate":
        file_path = sys.argv[2] if len(sys.argv) > 2 else "sample_trainsets.csv"
        num_trainsets = int(sys.argv[3]) if len(sys.argv) > 3 else 25
        generate_sample_data_command(file_path, num_trainsets)
    elif sys.argv[1] == "import":
        if len(sys.argv) < 3:
            print("Error: CSV file path required")
        else:
            import_csv_command(sys.argv[2])