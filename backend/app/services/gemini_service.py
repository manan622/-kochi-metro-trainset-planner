"""
Gemini AI Service for cleaning photo evaluation and analysis.
Provides AI-powered assessment of cleaning quality from photos.
"""
import google.generativeai as genai
import json
import base64
from typing import Dict, Any, Optional, List
from PIL import Image
import io
import os
from datetime import datetime

class GeminiCleaningEvaluator:
    """Service for evaluating cleaning quality using Google Gemini AI."""
    
    def __init__(self, api_key: str):
        """Initialize Gemini AI service with API key."""
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
    def evaluate_cleaning_photo(
        self, 
        image_data: bytes, 
        area_type: str, 
        cleaning_type: str,
        trainset_number: str
    ) -> Dict[str, Any]:
        """
        Evaluate cleaning quality from a photo using Gemini AI.
        
        Args:
            image_data: Raw image bytes
            area_type: Type of area cleaned (Interior, Exterior, Seats, Floor, etc.)
            cleaning_type: Type of cleaning performed (Basic, Deep, Maintenance)
            trainset_number: Train identification number
            
        Returns:
            Dictionary containing evaluation results
        """
        try:
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_data))
            
            # Create evaluation prompt
            prompt = self._create_evaluation_prompt(area_type, cleaning_type, trainset_number)
            
            # Generate AI response
            response = self.model.generate_content([prompt, image])
            
            # Parse AI response
            evaluation_result = self._parse_ai_response(response.text)
            
            # Add metadata
            evaluation_result.update({
                "area_type": area_type,
                "cleaning_type": cleaning_type,
                "trainset_number": trainset_number,
                "evaluation_timestamp": datetime.utcnow().isoformat(),
                "ai_model": "gemini-1.5-flash"
            })
            
            return evaluation_result
            
        except Exception as e:
            return {
                "error": f"AI evaluation failed: {str(e)}",
                "quality_score": 0,
                "quality_rating": "UNSATISFACTORY",
                "feedback": "Unable to evaluate image due to technical error",
                "confidence": 0.0
            }
    
    def batch_evaluate_photos(
        self, 
        photos_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Evaluate multiple cleaning photos in batch.
        
        Args:
            photos_data: List of photo data dictionaries
            
        Returns:
            List of evaluation results
        """
        results = []
        for photo_data in photos_data:
            result = self.evaluate_cleaning_photo(
                image_data=photo_data['image_data'],
                area_type=photo_data['area_type'],
                cleaning_type=photo_data['cleaning_type'],
                trainset_number=photo_data['trainset_number']
            )
            results.append(result)
        return results
    
    def _create_evaluation_prompt(
        self, 
        area_type: str, 
        cleaning_type: str, 
        trainset_number: str
    ) -> str:
        """Create detailed prompt for AI evaluation."""
        
        base_prompt = f"""
You are an expert metro train cleaning quality inspector. Analyze this photo of a cleaned {area_type.lower()} area from trainset {trainset_number} after {cleaning_type.lower()} cleaning.

Evaluate the cleaning quality based on these criteria:

1. **Cleanliness Standards for {area_type}:**
   - No visible dirt, dust, or debris
   - No stains or marks on surfaces
   - Proper sanitization evidence
   - Surface shine and finish quality

2. **Specific {cleaning_type} Cleaning Requirements:**
   {self._get_cleaning_type_requirements(cleaning_type)}

3. **Safety and Compliance:**
   - No cleaning residue left behind
   - All safety protocols followed
   - Equipment properly stored

**Provide your evaluation in this exact JSON format:**
```json
{{
    "quality_score": [0-100 numerical score],
    "quality_rating": "[EXCELLENT|GOOD|SATISFACTORY|NEEDS_IMPROVEMENT|UNSATISFACTORY]",
    "confidence": [0.0-1.0 confidence level],
    "feedback": "Detailed feedback explaining the rating",
    "areas_of_concern": ["list", "of", "specific", "issues"],
    "recommendations": ["list", "of", "improvement", "suggestions"],
    "compliance_status": "[COMPLIANT|NON_COMPLIANT|PARTIAL]",
    "detected_issues": {{
        "dirt_residue": [true/false],
        "incomplete_cleaning": [true/false],
        "safety_hazards": [true/false],
        "damage_visible": [true/false]
    }}
}}
```

Be thorough, objective, and provide constructive feedback for improvement.
"""
        return base_prompt
    
    def _get_cleaning_type_requirements(self, cleaning_type: str) -> str:
        """Get specific requirements based on cleaning type."""
        requirements = {
            "Basic": """
   - General dusting and wiping
   - Floor sweeping and mopping
   - Window cleaning
   - Basic sanitization
""",
            "Deep": """
   - Thorough scrubbing of all surfaces
   - Deep sanitization and disinfection
   - Removal of stubborn stains
   - Detailed cleaning of hard-to-reach areas
""",
            "Maintenance": """
   - Technical equipment cleaning
   - Preventive maintenance cleaning
   - Specialized cleaning agents
   - Component-specific cleaning protocols
""",
            "Interior": """
   - Seat cleaning and sanitization
   - Floor deep cleaning
   - Handrail and pole cleaning
   - Air vent and lighting cleaning
""",
            "Exterior": """
   - Body washing and polishing
   - Window and door cleaning
   - Undercarriage cleaning
   - Paint and surface protection
"""
        }
        return requirements.get(cleaning_type, "Standard cleaning protocols")
    
    def _parse_ai_response(self, ai_response: str) -> Dict[str, Any]:
        """Parse AI response and extract evaluation data."""
        try:
            # Extract JSON from response
            start_idx = ai_response.find('{')
            end_idx = ai_response.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                raise ValueError("No JSON found in AI response")
            
            json_str = ai_response[start_idx:end_idx]
            evaluation_data = json.loads(json_str)
            
            # Validate required fields
            required_fields = ['quality_score', 'quality_rating', 'confidence', 'feedback']
            for field in required_fields:
                if field not in evaluation_data:
                    evaluation_data[field] = self._get_default_value(field)
            
            # Ensure score is within valid range
            evaluation_data['quality_score'] = max(0, min(100, evaluation_data['quality_score']))
            
            # Ensure confidence is within valid range
            evaluation_data['confidence'] = max(0.0, min(1.0, evaluation_data['confidence']))
            
            return evaluation_data
            
        except Exception as e:
            # Return default values if parsing fails
            return {
                "quality_score": 50,
                "quality_rating": "SATISFACTORY",
                "confidence": 0.5,
                "feedback": f"AI response parsing error: {str(e)}",
                "areas_of_concern": [],
                "recommendations": ["Manual review recommended"],
                "compliance_status": "PARTIAL",
                "detected_issues": {
                    "dirt_residue": False,
                    "incomplete_cleaning": False,
                    "safety_hazards": False,
                    "damage_visible": False
                }
            }
    
    def _get_default_value(self, field: str) -> Any:
        """Get default value for missing fields."""
        defaults = {
            'quality_score': 50,
            'quality_rating': 'SATISFACTORY',
            'confidence': 0.5,
            'feedback': 'Evaluation completed with default values',
            'areas_of_concern': [],
            'recommendations': [],
            'compliance_status': 'PARTIAL',
            'detected_issues': {}
        }
        return defaults.get(field, None)
    
    def get_overall_cleaning_assessment(
        self, 
        photo_evaluations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate overall cleaning assessment from multiple photo evaluations.
        
        Args:
            photo_evaluations: List of individual photo evaluation results
            
        Returns:
            Overall assessment summary
        """
        if not photo_evaluations:
            return {
                "overall_score": 0,
                "overall_rating": "UNSATISFACTORY",
                "total_photos": 0,
                "summary": "No photos available for evaluation"
            }
        
        # Calculate average score
        scores = [eval_result.get('quality_score', 0) for eval_result in photo_evaluations]
        avg_score = sum(scores) / len(scores)
        
        # Determine overall rating
        if avg_score >= 90:
            overall_rating = "EXCELLENT"
        elif avg_score >= 80:
            overall_rating = "GOOD"
        elif avg_score >= 70:
            overall_rating = "SATISFACTORY"
        elif avg_score >= 50:
            overall_rating = "NEEDS_IMPROVEMENT"
        else:
            overall_rating = "UNSATISFACTORY"
        
        # Collect all issues and recommendations
        all_issues = []
        all_recommendations = []
        
        for eval_result in photo_evaluations:
            all_issues.extend(eval_result.get('areas_of_concern', []))
            all_recommendations.extend(eval_result.get('recommendations', []))
        
        # Remove duplicates
        unique_issues = list(set(all_issues))
        unique_recommendations = list(set(all_recommendations))
        
        return {
            "overall_score": round(avg_score, 2),
            "overall_rating": overall_rating,
            "total_photos": len(photo_evaluations),
            "average_confidence": round(sum(e.get('confidence', 0) for e in photo_evaluations) / len(photo_evaluations), 2),
            "score_range": {
                "min": min(scores),
                "max": max(scores)
            },
            "common_issues": unique_issues[:5],  # Top 5 issues
            "key_recommendations": unique_recommendations[:5],  # Top 5 recommendations
            "summary": f"Cleaning assessment completed for {len(photo_evaluations)} photos with average score of {avg_score:.1f}%"
        }


# Service instance (will be initialized in router)
gemini_evaluator: Optional[GeminiCleaningEvaluator] = None

def initialize_gemini_service(api_key: str) -> GeminiCleaningEvaluator:
    """Initialize the global Gemini service instance."""
    global gemini_evaluator
    gemini_evaluator = GeminiCleaningEvaluator(api_key)
    return gemini_evaluator

def get_gemini_service() -> Optional[GeminiCleaningEvaluator]:
    """Get the initialized Gemini service instance."""
    return gemini_evaluator