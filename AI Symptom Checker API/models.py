from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class SeverityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class RecommendationType(str, Enum):
    SELF_CARE = "self_care"
    CONSULT_DOCTOR = "consult_doctor"
    EMERGENCY = "emergency"
    LIFESTYLE = "lifestyle"
    MEDICATION = "medication"
    MONITORING = "monitoring"

class SymptomInput(BaseModel):
    """
    Flexible symptom input model that accepts various formats:
    - Single symptom as string
    - Multiple symptoms as list
    - Symptoms with additional context
    """
    symptoms: str = Field(
        ..., 
        description="Symptoms description - can be single symptom, multiple symptoms separated by commas, or detailed description",
        example="fever, headache, cough for 3 days"
    )
    age: Optional[int] = Field(None, description="Patient age", example=30)
    gender: Optional[str] = Field(None, description="Patient gender", example="male")
    additional_info: Optional[str] = Field(
        None, 
        description="Any additional relevant information about symptoms or medical history",
        example="Started 3 days ago, getting worse at night"
    )

class DetailedCondition(BaseModel):
    """Enhanced condition model with comprehensive information"""
    name: str = Field(..., description="Medical condition name")
    probability: float = Field(..., description="Match probability (0.0 to 1.0)")
    description: str = Field(..., description="Detailed condition description")
    severity: SeverityLevel = Field(..., description="Condition severity level")
    common_symptoms: List[str] = Field(..., description="Common symptoms associated with this condition")
    typical_duration: str = Field(..., description="Typical duration of the condition")
    when_to_see_doctor: str = Field(..., description="When to seek medical attention for this condition")
    self_care_tips: List[str] = Field(..., description="Self-care recommendations specific to this condition")

class DetailedRecommendation(BaseModel):
    """Enhanced recommendation model with comprehensive advice"""
    type: RecommendationType = Field(..., description="Type of recommendation")
    title: str = Field(..., description="Recommendation title")
    message: str = Field(..., description="Detailed recommendation message")
    urgency: SeverityLevel = Field(..., description="Urgency level")
    action_steps: List[str] = Field(..., description="Specific action steps to follow")
    timeframe: str = Field(..., description="Recommended timeframe for action")
    warning_signs: Optional[List[str]] = Field(None, description="Warning signs to watch for")

class SymptomAnalysis(BaseModel):
    """Detailed symptom analysis breakdown"""
    extracted_symptoms: List[str] = Field(..., description="Individual symptoms extracted from input")
    symptom_categories: Dict[str, List[str]] = Field(..., description="Symptoms grouped by body system/category")
    severity_assessment: SeverityLevel = Field(..., description="Overall severity assessment")
    risk_factors: List[str] = Field(..., description="Identified risk factors")

class ComprehensiveResponse(BaseModel):
    """Comprehensive response model with detailed analysis and recommendations"""
    input_text: str = Field(..., description="Original symptom input")
    symptom_analysis: SymptomAnalysis = Field(..., description="Detailed symptom breakdown")
    possible_conditions: List[DetailedCondition] = Field(..., description="Probable medical conditions with details")
    priority_recommendations: List[DetailedRecommendation] = Field(..., description="Priority recommendations based on analysis")
    general_advice: List[str] = Field(..., description="General health advice")
    red_flags: List[str] = Field(..., description="Warning signs that require immediate attention")
    follow_up_questions: List[str] = Field(..., description="Questions to help refine the diagnosis")
    confidence_score: float = Field(..., description="Overall confidence in the analysis (0.0 to 1.0)")
    disclaimer: str = Field(..., description="Medical disclaimer")

class HealthTip(BaseModel):
    """Health tip model (kept for potential future use)"""
    title: str
    description: str
    category: str

