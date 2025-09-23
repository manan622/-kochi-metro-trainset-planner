from typing import List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import json

from app.models.models import (
    Trainset, TrainsetStatus, FitnessCertificate, JobCard, 
    BrandingPriority, MileageRecord, CleaningSlot, StablingBay,
    CertificateStatus, JobCardStatus, BrandingPriorityLevel
)
from app.schemas import InductionPlanResponse

class InductionPlanner:
    """
    Rule-based trainset induction planner that determines which trainsets should:
    - Enter revenue service (Fit)
    - Remain on standby (Standby) 
    - Stay in Inspection Bay Line for maintenance (Unfit)
    """
    
    def __init__(self, db: Session):
        self.db = db
        
    def plan_induction_for_date(self, target_date: datetime = None) -> List[InductionPlanResponse]:
        """Generate induction plan for all trainsets."""
        if target_date is None:
            target_date = datetime.now()
            
        try:
            trainsets = self.db.query(Trainset).all()
            print(f"Found {len(trainsets)} trainsets in database")
        except Exception as e:
            print(f"Error querying trainsets: {str(e)}")
            # Return empty list if database query fails
            return []
            
        induction_plans = []
        
        for trainset in trainsets:
            try:
                plan = self._evaluate_trainset(trainset, target_date)
                induction_plans.append(plan)
            except Exception as e:
                print(f"Error evaluating trainset {trainset.number}: {str(e)}")
                # Create a basic plan for failed evaluations
                basic_plan = InductionPlanResponse(
                    trainset_id=trainset.number,
                    status=TrainsetStatus.STANDBY,
                    reason=f"Evaluation failed: {str(e)}",
                    conflict_alerts=["Evaluation Error"],
                    metadata={"error": str(e)}
                )
                induction_plans.append(basic_plan)
            
        # Sort by priority: Unfit first, then Fit, then Standby
        priority_order = {TrainsetStatus.UNFIT: 0, TrainsetStatus.FIT: 1, TrainsetStatus.STANDBY: 2}
        induction_plans.sort(key=lambda x: priority_order.get(x.status, 3))
        
        return induction_plans
    
    def _evaluate_trainset(self, trainset: Trainset, target_date: datetime) -> InductionPlanResponse:
        """Evaluate a single trainset and determine its status with reasoning."""
        
        # Initialize evaluation context
        reasons = []
        conflict_alerts = []
        metadata = {}
        
        try:
            # 1. Check Fitness Certificates
            fitness_issues = self._check_fitness_certificates(trainset, target_date)
            if fitness_issues:
                reasons.extend(fitness_issues["reasons"])
                conflict_alerts.extend(fitness_issues["alerts"])
                metadata["fitness_certificate"] = fitness_issues["summary"]
            else:
                metadata["fitness_certificate"] = "All certificates valid"
                
            # 2. Check Job Cards
            job_issues = self._check_job_cards(trainset)
            if job_issues:
                reasons.extend(job_issues["reasons"])
                conflict_alerts.extend(job_issues["alerts"])
                metadata["job_cards"] = job_issues["summary"]
            else:
                metadata["job_cards"] = "No pending maintenance"
                
            # 3. Basic information - skip complex evaluations for now
            metadata["branding_priority"] = "Not evaluated"
            metadata["mileage"] = f"{trainset.current_mileage:,.0f} km"
            metadata["cleaning_slot"] = "Not evaluated"
            metadata["stabling_bay"] = trainset.stabling_bay or "Not assigned"
            
            # Determine final status based on evaluation
            final_status = self._determine_final_status(conflict_alerts, reasons)
            
            # Create comprehensive reasoning
            comprehensive_reason = self._create_comprehensive_reasoning(
                trainset, final_status, reasons, conflict_alerts
            )
            
        except Exception as e:
            print(f"Error in _evaluate_trainset for {trainset.number}: {str(e)}")
            final_status = TrainsetStatus.STANDBY
            comprehensive_reason = f"Evaluation error: {str(e)}"
            conflict_alerts = ["Evaluation Error"]
            metadata = {"error": str(e)}
        
        return InductionPlanResponse(
            trainset_id=trainset.number,
            status=final_status,
            reason=comprehensive_reason,
            conflict_alerts=conflict_alerts,
            metadata=metadata
        )
    
    def _check_fitness_certificates(self, trainset: Trainset, target_date: datetime) -> Dict[str, Any]:
        """Check fitness certificate status."""
        try:
            certificates = trainset.fitness_certificates
        except Exception as e:
            print(f"Error accessing fitness certificates for {trainset.number}: {str(e)}")
            return {
                "reasons": ["Error accessing fitness certificates"],
                "alerts": ["Database Error"],
                "summary": "Cannot access fitness certificates"
            }
            
        issues = {"reasons": [], "alerts": [], "summary": ""}
        
        if not certificates:
            issues["reasons"].append("No fitness certificates found")
            issues["alerts"].append("Missing fitness certificates")
            issues["summary"] = "No fitness certificates on file"
            return issues
            
        expired_certs = []
        expiring_soon = []
        
        for cert in certificates:
            if cert.expiry_date <= target_date:
                expired_certs.append(f"{cert.certificate_type} (expired {cert.expiry_date.strftime('%Y-%m-%d')})")
                issues["alerts"].append(f"Expired {cert.certificate_type} Certificate")
            elif cert.expiry_date <= target_date + timedelta(days=7):
                expiring_soon.append(f"{cert.certificate_type} (expires {cert.expiry_date.strftime('%Y-%m-%d')})")
                
        if expired_certs:
            issues["reasons"].append(f"Fitness certificates expired: {', '.join(expired_certs)}")
            issues["summary"] = f"Expired certificates: {', '.join(expired_certs)}"
        elif expiring_soon:
            issues["reasons"].append(f"Fitness certificates expiring soon: {', '.join(expiring_soon)}")
            issues["summary"] = f"Expiring soon: {', '.join(expiring_soon)}"
        else:
            issues["summary"] = "All fitness certificates valid"
            
        return issues if issues["reasons"] or issues["alerts"] else None
    
    def _check_job_cards(self, trainset: Trainset) -> Dict[str, Any]:
        """Check open job cards."""
        try:
            job_cards = [jc for jc in trainset.job_cards if jc.status == JobCardStatus.OPEN]
        except Exception as e:
            print(f"Error accessing job cards for {trainset.number}: {str(e)}")
            return {
                "reasons": ["Error accessing job cards"],
                "alerts": ["Database Error"],
                "summary": "Cannot access job cards"
            }
        
        if not job_cards:
            return None
            
        issues = {"reasons": [], "alerts": [], "summary": ""}
        
        critical_jobs = []
        regular_jobs = []
        
        for job in job_cards:
            job_desc = f"{job.job_card_number} ({job.description})"
            if job.priority == "High":
                critical_jobs.append(job_desc)
                issues["alerts"].append(f"Critical maintenance: {job.job_card_number}")
            else:
                regular_jobs.append(job_desc)
                
        if critical_jobs:
            issues["reasons"].append(f"Critical maintenance pending: {', '.join(critical_jobs)}")
        if regular_jobs:
            issues["reasons"].append(f"Regular maintenance pending: {', '.join(regular_jobs)}")
            
        all_jobs = critical_jobs + regular_jobs
        issues["summary"] = f"Open jobs: {', '.join(all_jobs)}"
        
        return issues
    
    def _check_branding_priorities(self, trainset: Trainset, target_date: datetime) -> Dict[str, Any]:
        """Check branding priority commitments."""
        info = {"reasons": [], "summary": "Low"}
        
        active_priorities = [
            bp for bp in trainset.branding_priorities
            if bp.contract_start_date <= target_date <= bp.contract_end_date
        ]
        
        if not active_priorities:
            info["summary"] = "Low"
            return info
            
        highest_priority = max(active_priorities, key=lambda x: {
            BrandingPriorityLevel.HIGH: 3,
            BrandingPriorityLevel.MEDIUM: 2, 
            BrandingPriorityLevel.LOW: 1
        }.get(x.priority_level, 0))
        
        if highest_priority.priority_level == BrandingPriorityLevel.HIGH:
            info["reasons"].append(f"High priority branding commitment: {highest_priority.brand_name}")
            info["summary"] = f"High ({highest_priority.brand_name})"
        elif highest_priority.priority_level == BrandingPriorityLevel.MEDIUM:
            info["reasons"].append(f"Medium priority branding: {highest_priority.brand_name}")
            info["summary"] = f"Medium ({highest_priority.brand_name})"
        else:
            info["summary"] = f"Low ({highest_priority.brand_name})"
            
        return info
    
    def _check_mileage_balance(self, trainset: Trainset) -> Dict[str, Any]:
        """Check mileage balancing requirements."""
        info = {"reasons": [], "summary": f"{trainset.current_mileage:,.0f} km"}
        
        # Get average mileage across all trainsets
        avg_mileage = self.db.query(Trainset).with_entities(
            self.db.func.avg(Trainset.current_mileage)
        ).scalar() or 0
        
        mileage_diff = trainset.current_mileage - avg_mileage
        
        if mileage_diff > 5000:  # More than 5000km above average
            info["reasons"].append(f"High mileage trainset ({trainset.current_mileage:,.0f} km, {mileage_diff:+.0f} km from average)")
        elif mileage_diff < -5000:  # More than 5000km below average
            info["reasons"].append(f"Low mileage trainset preferred for service ({trainset.current_mileage:,.0f} km, {mileage_diff:+.0f} km from average)")
            
        return info
    
    def _check_cleaning_slots(self, trainset: Trainset, target_date: datetime) -> Dict[str, Any]:
        """Check cleaning slot availability."""
        info = {"reasons": [], "summary": "Available"}
        
        # Check for scheduled cleaning on target date
        scheduled_cleaning = [
            cs for cs in trainset.cleaning_slots
            if cs.slot_date.date() == target_date.date() and cs.status == "Scheduled"
        ]
        
        if scheduled_cleaning:
            slot = scheduled_cleaning[0]
            info["reasons"].append(f"Scheduled for cleaning: {slot.cleaning_type} in {slot.bay_number}")
            info["summary"] = f"Scheduled ({slot.cleaning_type})"
        else:
            info["summary"] = "Available"
            
        return info
    
    def _check_stabling_bay(self, trainset: Trainset) -> Dict[str, Any]:
        """Check stabling bay assignment."""
        info = {"reasons": [], "summary": trainset.stabling_bay or "Not assigned"}
        
        if trainset.stabling_bay:
            # Check bay availability
            bay = self.db.query(StablingBay).filter(
                StablingBay.bay_number == trainset.stabling_bay
            ).first()
            
            if bay:
                if not bay.is_available:
                    info["reasons"].append(f"Assigned bay {trainset.stabling_bay} unavailable")
                elif bay.maintenance_required:
                    info["reasons"].append(f"Assigned bay {trainset.stabling_bay} requires maintenance")
                else:
                    info["summary"] = f"{trainset.stabling_bay} (available)"
            else:
                info["reasons"].append(f"Assigned bay {trainset.stabling_bay} not found")
        else:
            info["reasons"].append("No stabling bay assigned")
            
        return info
    
    def _determine_final_status(self, conflict_alerts: List[str], reasons: List[str]) -> TrainsetStatus:
        """Determine final trainset status based on evaluation results."""
        
        # Critical issues that make trainset unfit
        critical_issues = [
            "Expired Fitness Certificate",
            "Missing fitness certificates", 
            "Critical maintenance"
        ]
        
        # Check for critical issues
        for alert in conflict_alerts:
            for critical in critical_issues:
                if critical.lower() in alert.lower():
                    return TrainsetStatus.UNFIT
                    
        # Check for pending maintenance
        pending_maintenance = any("maintenance pending" in reason.lower() for reason in reasons)
        if pending_maintenance:
            return TrainsetStatus.UNFIT
            
        # Check for high priority branding
        high_priority_branding = any("high priority branding" in reason.lower() for reason in reasons)
        if high_priority_branding:
            return TrainsetStatus.FIT
            
        # Default to standby if no clear indicators
        return TrainsetStatus.STANDBY
    
    def _create_comprehensive_reasoning(
        self, 
        trainset: Trainset, 
        status: TrainsetStatus, 
        reasons: List[str], 
        conflict_alerts: List[str]
    ) -> str:
        """Create comprehensive reasoning text."""
        
        base_text = f"Trainset {trainset.number} marked {status.value}"
        
        if conflict_alerts:
            alert_text = " and ".join(conflict_alerts)
            base_text += f" because {alert_text}"
        elif reasons:
            # Pick the most relevant reason
            primary_reason = reasons[0]
            base_text += f" because {primary_reason.lower()}"
        else:
            base_text += " based on standard operating parameters"
            
        # Add additional context if multiple issues
        if len(reasons) > 1:
            base_text += f". Additional considerations: {'; '.join(reasons[1:])}"
            
        return base_text