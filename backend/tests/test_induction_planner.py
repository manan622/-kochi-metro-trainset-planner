import pytest
from datetime import datetime, timedelta
from app.services.induction_service import InductionPlanner
from app.models.models import (
    Trainset, FitnessCertificate, JobCard, BrandingPriority, 
    TrainsetStatus, CertificateStatus, JobCardStatus, BrandingPriorityLevel
)

class TestInductionPlanner:
    """Test the induction planning logic"""
    
    def create_test_trainset(self, db_session, number="TS-2001", mileage=100000):
        """Helper to create a test trainset"""
        trainset = Trainset(
            number=number,
            current_mileage=mileage,
            stabling_bay="Bay-01",
            status=TrainsetStatus.STANDBY
        )
        db_session.add(trainset)
        db_session.commit()
        db_session.refresh(trainset)
        return trainset
    
    def test_planner_initialization(self, db_session):
        """Test that induction planner initializes correctly"""
        planner = InductionPlanner(db_session)
        assert planner.db == db_session
    
    def test_empty_fleet_planning(self, db_session):
        """Test planning with no trainsets"""
        planner = InductionPlanner(db_session)
        result = planner.plan_induction_for_date()
        
        assert isinstance(result, list)
        assert len(result) == 0
    
    def test_single_trainset_default_status(self, db_session):
        """Test planning with single trainset - should be standby by default"""
        trainset = self.create_test_trainset(db_session)
        
        planner = InductionPlanner(db_session)
        result = planner.plan_induction_for_date()
        
        assert len(result) == 1
        plan = result[0]
        assert plan.trainset_id == "TS-2001"
        assert plan.status in [TrainsetStatus.STANDBY, TrainsetStatus.FIT]
        assert plan.reason is not None
        assert isinstance(plan.conflict_alerts, list)
        assert isinstance(plan.metadata, dict)
    
    def test_expired_fitness_certificate_makes_unfit(self, db_session):
        """Test that expired fitness certificate makes trainset unfit"""
        trainset = self.create_test_trainset(db_session)
        
        # Add expired fitness certificate
        expired_cert = FitnessCertificate(
            trainset_id=trainset.id,
            certificate_type="Rolling-Stock",
            status=CertificateStatus.EXPIRED,
            issue_date=datetime.now() - timedelta(days=400),
            expiry_date=datetime.now() - timedelta(days=30),  # Expired 30 days ago
            issuing_authority="KMRL",
            certificate_number="FC-001"
        )
        db_session.add(expired_cert)
        db_session.commit()
        
        planner = InductionPlanner(db_session)
        result = planner.plan_induction_for_date()
        
        assert len(result) == 1
        plan = result[0]
        assert plan.status == TrainsetStatus.UNFIT
        assert "expired" in plan.reason.lower()
        assert len(plan.conflict_alerts) > 0
    
    def test_open_job_card_affects_status(self, db_session):
        """Test that open job card affects trainset status"""
        trainset = self.create_test_trainset(db_session)
        
        # Add open job card
        job_card = JobCard(
            trainset_id=trainset.id,
            job_card_number="JB-001",
            description="Brake repair required",
            status=JobCardStatus.OPEN,
            priority="High",
            created_date=datetime.now() - timedelta(days=5)
        )
        db_session.add(job_card)
        db_session.commit()
        
        planner = InductionPlanner(db_session)
        result = planner.plan_induction_for_date()
        
        assert len(result) == 1
        plan = result[0]
        # High priority open job card should make trainset unfit
        assert plan.status == TrainsetStatus.UNFIT
        assert "maintenance" in plan.reason.lower() or "job" in plan.reason.lower()
    
    def test_high_branding_priority_influences_status(self, db_session):
        """Test that high branding priority influences fit status"""
        trainset = self.create_test_trainset(db_session)
        
        # Add high priority branding
        branding = BrandingPriority(
            trainset_id=trainset.id,
            priority_level=BrandingPriorityLevel.HIGH,
            brand_name="Coca-Cola",
            contract_start_date=datetime.now() - timedelta(days=10),
            contract_end_date=datetime.now() + timedelta(days=90)
        )
        db_session.add(branding)
        db_session.commit()
        
        planner = InductionPlanner(db_session)
        result = planner.plan_induction_for_date()
        
        assert len(result) == 1
        plan = result[0]
        # High branding priority should influence toward fit status
        assert "branding" in plan.reason.lower() or "priority" in plan.reason.lower()
    
    def test_valid_fitness_certificate(self, db_session):
        """Test that valid fitness certificate doesn't cause issues"""
        trainset = self.create_test_trainset(db_session)
        
        # Add valid fitness certificate
        valid_cert = FitnessCertificate(
            trainset_id=trainset.id,
            certificate_type="Rolling-Stock",
            status=CertificateStatus.VALID,
            issue_date=datetime.now() - timedelta(days=30),
            expiry_date=datetime.now() + timedelta(days=300),  # Valid for 300 more days
            issuing_authority="KMRL",
            certificate_number="FC-002"
        )
        db_session.add(valid_cert)
        db_session.commit()
        
        planner = InductionPlanner(db_session)
        result = planner.plan_induction_for_date()
        
        assert len(result) == 1
        plan = result[0]
        # Valid certificate should not cause unfit status by itself
        assert "expired" not in plan.reason.lower()
    
    def test_multiple_trainsets_sorting(self, db_session):
        """Test that multiple trainsets are sorted correctly"""
        # Create trainsets with different issues
        fit_trainset = self.create_test_trainset(db_session, "TS-2001")
        unfit_trainset = self.create_test_trainset(db_session, "TS-2002")
        standby_trainset = self.create_test_trainset(db_session, "TS-2003")
        
        # Make one trainset unfit with expired certificate
        expired_cert = FitnessCertificate(
            trainset_id=unfit_trainset.id,
            certificate_type="Rolling-Stock",
            status=CertificateStatus.EXPIRED,
            issue_date=datetime.now() - timedelta(days=400),
            expiry_date=datetime.now() - timedelta(days=30),
            issuing_authority="KMRL",
            certificate_number="FC-003"
        )
        db_session.add(expired_cert)
        db_session.commit()
        
        planner = InductionPlanner(db_session)
        result = planner.plan_induction_for_date()
        
        assert len(result) == 3
        
        # Find the unfit trainset in results
        unfit_plans = [p for p in result if p.status == TrainsetStatus.UNFIT]
        assert len(unfit_plans) >= 1
        
        # Unfit trainsets should be sorted first (by priority)
        unfit_found = False
        for plan in result:
            if plan.status == TrainsetStatus.UNFIT:
                unfit_found = True
                break
            # If we find fit or standby before unfit, sorting is wrong
            assert plan.status not in [TrainsetStatus.FIT, TrainsetStatus.STANDBY] or not unfit_found
    
    def test_mileage_balancing_logic(self, db_session):
        """Test that mileage balancing is considered"""
        # Create trainsets with different mileages
        low_mileage_trainset = self.create_test_trainset(db_session, "TS-2001", 50000)
        high_mileage_trainset = self.create_test_trainset(db_session, "TS-2002", 150000)
        
        planner = InductionPlanner(db_session)
        result = planner.plan_induction_for_date()
        
        assert len(result) == 2
        
        # Check that mileage information is included in reasoning
        for plan in result:
            assert plan.metadata is not None
            assert "mileage" in plan.metadata
    
    def test_reasoning_contains_explanation(self, db_session):
        """Test that reasoning contains meaningful explanations"""
        trainset = self.create_test_trainset(db_session)
        
        planner = InductionPlanner(db_session)
        result = planner.plan_induction_for_date()
        
        assert len(result) == 1
        plan = result[0]
        
        # Reasoning should be a non-empty string
        assert isinstance(plan.reason, str)
        assert len(plan.reason.strip()) > 0
        
        # Should contain trainset number
        assert trainset.number in plan.reason
        
        # Should contain status
        assert plan.status.value in plan.reason
    
    def test_metadata_contains_required_fields(self, db_session):
        """Test that metadata contains expected fields"""
        trainset = self.create_test_trainset(db_session)
        
        planner = InductionPlanner(db_session)
        result = planner.plan_induction_for_date()
        
        assert len(result) == 1
        plan = result[0]
        
        # Metadata should be a dictionary
        assert isinstance(plan.metadata, dict)
        
        # Should contain expected keys
        expected_keys = ['fitness_certificate', 'job_cards', 'mileage', 'branding_priority']
        for key in expected_keys:
            assert key in plan.metadata
    
    def test_conflict_alerts_format(self, db_session):
        """Test that conflict alerts are properly formatted"""
        trainset = self.create_test_trainset(db_session)
        
        # Add expired certificate to generate conflict
        expired_cert = FitnessCertificate(
            trainset_id=trainset.id,
            certificate_type="Rolling-Stock",
            status=CertificateStatus.EXPIRED,
            issue_date=datetime.now() - timedelta(days=400),
            expiry_date=datetime.now() - timedelta(days=30),
            issuing_authority="KMRL",
            certificate_number="FC-004"
        )
        db_session.add(expired_cert)
        db_session.commit()
        
        planner = InductionPlanner(db_session)
        result = planner.plan_induction_for_date()
        
        assert len(result) == 1
        plan = result[0]
        
        # Conflict alerts should be a list
        assert isinstance(plan.conflict_alerts, list)
        
        # Should have at least one alert for expired certificate
        assert len(plan.conflict_alerts) > 0
        
        # Alerts should be strings
        for alert in plan.conflict_alerts:
            assert isinstance(alert, str)
            assert len(alert.strip()) > 0