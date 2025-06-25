from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import SymptomInput, ComprehensiveResponse
from symptom_checker import EnhancedSymptomAnalyzer
from database import DatabaseManager
import uvicorn

# Initialize FastAPI app
app = FastAPI(
    title="AI Symptom Checker API",
    description="An advanced AI-powered symptom checker that provides comprehensive analysis and detailed recommendations",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
db_manager = DatabaseManager()
symptom_analyzer = EnhancedSymptomAnalyzer()

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    db_manager.initialize_database()

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to AI Symptom Checker API v2.0",
        "description": "Advanced AI-powered symptom analysis with comprehensive recommendations",
        "version": "2.0.0",
        "features": [
            "Flexible symptom input (single or multiple symptoms)",
            "Comprehensive condition analysis",
            "Detailed recommendations with action steps",
            "Risk assessment and severity evaluation",
            "Follow-up questions for better diagnosis",
            "Emergency warning system"
        ],
        "main_endpoint": "/analyze-symptoms",
        "documentation": "/docs",
        "health_check": "/health"
    }

@app.post("/analyze-symptoms", response_model=ComprehensiveResponse)
async def analyze_symptoms(symptom_input: SymptomInput):
    """
    Comprehensive symptom analysis endpoint
    
    This endpoint accepts flexible symptom input and provides:
    - Detailed symptom analysis and categorization
    - Probable medical conditions with comprehensive information
    - Prioritized recommendations with specific action steps
    - Risk assessment and severity evaluation
    - Warning signs and red flags
    - Follow-up questions for better diagnosis
    
    Input examples:
    - Single symptom: "headache"
    - Multiple symptoms: "fever, cough, sore throat"
    - Descriptive input: "I have been feeling tired and have a runny nose for 3 days"
    """
    try:
        # Validate input
        if not symptom_input.symptoms or not symptom_input.symptoms.strip():
            raise HTTPException(
                status_code=400, 
                detail="Symptom description is required. Please describe your symptoms."
            )
        
        # Perform comprehensive analysis
        result = symptom_analyzer.analyze_symptoms(symptom_input)
        
        # Store analysis for learning (optional - can be disabled for privacy)
        try:
            db_manager.store_symptom_analysis(symptom_input, result)
        except Exception as e:
            # Don't fail the request if storage fails
            print(f"Warning: Could not store analysis: {e}")
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error analyzing symptoms: {str(e)}"
        )

@app.get("/health")
async def health_check():
    """
    API health check endpoint
    """
    try:
        # Test database connection
        db_manager.get_connection().close()
        
        return {
            "status": "healthy",
            "service": "AI Symptom Checker API",
            "version": "2.0.0",
            "database": "connected",
            "ai_analyzer": "ready"
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Service unhealthy: {str(e)}"
        )


if __name__ == "__main__":
   
    uvicorn.run("main:app",host="0.0.0.0", port=8000, reload=True  )

