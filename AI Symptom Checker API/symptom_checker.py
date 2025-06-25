import re
from typing import List, Dict, Set, Tuple
from models import (
    SymptomInput, ComprehensiveResponse, DetailedCondition, DetailedRecommendation,
    SymptomAnalysis, SeverityLevel, RecommendationType
)
from database import DatabaseManager

class EnhancedSymptomAnalyzer:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.disclaimer = (
            "This AI symptom analysis is for informational purposes only and should not replace "
            "professional medical advice. Always consult with a qualified healthcare provider for "
            "accurate diagnosis and treatment. If you're experiencing a medical emergency, "
            "call emergency services immediately."
        )
        
        # Symptom categories for better organization
        self.symptom_categories = {
            "respiratory": ["cough", "shortness of breath", "chest pain", "wheezing", "sore throat", "runny nose", "congestion"],
            "gastrointestinal": ["nausea", "vomiting", "diarrhea", "stomach pain", "abdominal pain", "loss of appetite", "bloating"],
            "neurological": ["headache", "dizziness", "confusion", "memory loss", "seizure", "numbness", "tingling"],
            "musculoskeletal": ["muscle aches", "joint pain", "back pain", "stiffness", "weakness", "swelling"],
            "cardiovascular": ["chest pain", "rapid heartbeat", "palpitations", "high blood pressure", "shortness of breath"],
            "dermatological": ["rash", "itching", "swelling", "hives", "skin changes", "bruising"],
            "general": ["fever", "fatigue", "weight loss", "weight gain", "night sweats", "chills"],
            "mental_health": ["anxiety", "depression", "mood changes", "sleep problems", "stress", "panic"]
        }
        
        # Emergency symptoms that require immediate attention
        self.emergency_symptoms = {
            "chest pain", "difficulty breathing", "severe headache", "loss of consciousness",
            "severe allergic reaction", "stroke symptoms", "heart attack symptoms",
            "severe abdominal pain", "high fever", "seizure", "severe bleeding"
        }
    
    def analyze_symptoms(self, symptom_input: SymptomInput) -> ComprehensiveResponse:
        """
        Main method to perform comprehensive symptom analysis
        """
        # Parse and extract symptoms from flexible input
        extracted_symptoms = self._parse_symptom_input(symptom_input.symptoms)
        
        # Categorize symptoms
        symptom_categories = self._categorize_symptoms(extracted_symptoms)
        
        # Assess overall severity
        severity_assessment = self._assess_severity(extracted_symptoms, symptom_input)
        
        # Identify risk factors
        risk_factors = self._identify_risk_factors(symptom_input, extracted_symptoms)
        
        # Create symptom analysis
        symptom_analysis = SymptomAnalysis(
            extracted_symptoms=extracted_symptoms,
            symptom_categories=symptom_categories,
            severity_assessment=severity_assessment,
            risk_factors=risk_factors
        )
        
        # Get matching conditions with detailed information
        possible_conditions = self._get_detailed_conditions(extracted_symptoms, symptom_input)
        
        # Generate comprehensive recommendations
        priority_recommendations = self._generate_detailed_recommendations(
            symptom_analysis, possible_conditions, symptom_input
        )
        
        # Generate general advice
        general_advice = self._generate_general_advice(symptom_analysis)
        
        # Identify red flags
        red_flags = self._identify_red_flags(extracted_symptoms)
        
        # Generate follow-up questions
        follow_up_questions = self._generate_follow_up_questions(symptom_analysis, possible_conditions)
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(extracted_symptoms, possible_conditions)
        
        return ComprehensiveResponse(
            input_text=symptom_input.symptoms,
            symptom_analysis=symptom_analysis,
            possible_conditions=possible_conditions,
            priority_recommendations=priority_recommendations,
            general_advice=general_advice,
            red_flags=red_flags,
            follow_up_questions=follow_up_questions,
            confidence_score=confidence_score,
            disclaimer=self.disclaimer
        )
    
    def _parse_symptom_input(self, symptoms_text: str) -> List[str]:
        """
        Parse flexible symptom input and extract individual symptoms
        """
        # Clean and normalize the input
        symptoms_text = symptoms_text.lower().strip()
        
        # Common separators and patterns
        separators = [',', ';', ' and ', ' & ', '\n', ' also ', ' plus ']
        
        # Split by separators
        symptoms = [symptoms_text]
        for sep in separators:
            new_symptoms = []
            for symptom in symptoms:
                new_symptoms.extend([s.strip() for s in symptom.split(sep) if s.strip()])
            symptoms = new_symptoms
        
        # Remove common non-symptom words and phrases
        filter_words = {
            'i have', 'i am', 'experiencing', 'feeling', 'symptoms', 'symptom',
            'for', 'days', 'hours', 'weeks', 'since', 'yesterday', 'today',
            'the', 'a', 'an', 'my', 'me', 'is', 'are', 'been', 'being'
        }
        
        cleaned_symptoms = []
        for symptom in symptoms:
            # Remove time references but keep the core symptom
            symptom = re.sub(r'\b\d+\s*(day|days|hour|hours|week|weeks)\b', '', symptom)
            symptom = re.sub(r'\b(since|for|about|around)\s+\w+\b', '', symptom)
            
            # Remove filter words
            words = symptom.split()
            filtered_words = [w for w in words if w not in filter_words and len(w) > 1]
            
            if filtered_words:
                cleaned_symptom = ' '.join(filtered_words).strip()
                if len(cleaned_symptom) > 2:  # Minimum length check
                    cleaned_symptoms.append(cleaned_symptom)
        
        return list(set(cleaned_symptoms))  # Remove duplicates
    
    def _categorize_symptoms(self, symptoms: List[str]) -> Dict[str, List[str]]:
        """
        Categorize symptoms by body system
        """
        categorized = {category: [] for category in self.symptom_categories.keys()}
        
        for symptom in symptoms:
            symptom_lower = symptom.lower()
            categorized_this_symptom = False
            
            for category, category_symptoms in self.symptom_categories.items():
                for cat_symptom in category_symptoms:
                    if cat_symptom in symptom_lower or symptom_lower in cat_symptom:
                        categorized[category].append(symptom)
                        categorized_this_symptom = True
                        break
                
                if categorized_this_symptom:
                    break
            
            # If not categorized, add to general
            if not categorized_this_symptom:
                categorized["general"].append(symptom)
        
        # Remove empty categories
        return {k: v for k, v in categorized.items() if v}
    
    def _assess_severity(self, symptoms: List[str], symptom_input: SymptomInput) -> SeverityLevel:
        """
        Assess overall severity based on symptoms and context
        """
        # Check for emergency symptoms
        for symptom in symptoms:
            for emergency in self.emergency_symptoms:
                if emergency in symptom.lower():
                    return SeverityLevel.CRITICAL
        
        # High severity indicators
        high_severity_indicators = [
            "severe", "intense", "unbearable", "excruciating", "sharp", "stabbing",
            "difficulty breathing", "chest pain", "high fever"
        ]
        
        for symptom in symptoms:
            for indicator in high_severity_indicators:
                if indicator in symptom.lower():
                    return SeverityLevel.HIGH
        
        # Medium severity: multiple symptoms or concerning combinations
        if len(symptoms) >= 4 or any("fever" in s.lower() for s in symptoms):
            return SeverityLevel.MEDIUM
        
        return SeverityLevel.LOW
    
    def _identify_risk_factors(self, symptom_input: SymptomInput, symptoms: List[str]) -> List[str]:
        """
        Identify risk factors based on age, symptoms, and additional info
        """
        risk_factors = []
        
        # Age-related risk factors
        if symptom_input.age:
            if symptom_input.age > 65:
                risk_factors.append("Advanced age (increased risk for complications)")
            elif symptom_input.age < 5:
                risk_factors.append("Young age (requires careful monitoring)")
        
        # Symptom-based risk factors
        if len(symptoms) > 5:
            risk_factors.append("Multiple concurrent symptoms")
        
        if any("fever" in s.lower() for s in symptoms):
            risk_factors.append("Presence of fever (indicates possible infection)")
        
        if any("chest pain" in s.lower() for s in symptoms):
            risk_factors.append("Chest pain (requires cardiac evaluation)")
        
        return risk_factors
    
    def _get_detailed_conditions(self, symptoms: List[str], symptom_input: SymptomInput) -> List[DetailedCondition]:
        """
        Get detailed condition information with enhanced matching
        """
        matching_conditions = self.db_manager.get_conditions_by_symptoms(symptoms)
        detailed_conditions = []
        
        for condition_data in matching_conditions[:4]:  # Top 4 matches
            # Get additional details for the condition
            condition_details = self._get_condition_details(condition_data["name"])
            
            detailed_condition = DetailedCondition(
                name=condition_data["name"],
                probability=min(condition_data["probability"] * 1.2, 1.0),  # Slight boost for better matching
                description=condition_data["description"],
                severity=SeverityLevel(condition_data["severity"]),
                common_symptoms=condition_data["symptoms"],
                typical_duration=condition_details["typical_duration"],
                when_to_see_doctor=condition_details["when_to_see_doctor"],
                self_care_tips=condition_details["self_care_tips"]
            )
            detailed_conditions.append(detailed_condition)
        
        return detailed_conditions
    
    def _get_condition_details(self, condition_name: str) -> Dict[str, any]:
        """
        Get additional details for specific conditions
        """
        condition_details = {
            "Common Cold": {
                "typical_duration": "7-10 days",
                "when_to_see_doctor": "If symptoms worsen after 3 days or persist beyond 10 days",
                "self_care_tips": ["Rest and stay hydrated", "Use saline nasal rinses", "Consider honey for cough relief", "Maintain good hygiene"]
            },
            "Flu": {
                "typical_duration": "1-2 weeks",
                "when_to_see_doctor": "If you have difficulty breathing, persistent fever over 3 days, or severe symptoms",
                "self_care_tips": ["Get plenty of rest", "Stay well hydrated", "Consider antiviral medication if within 48 hours", "Monitor temperature regularly"]
            },
            "Migraine": {
                "typical_duration": "4-72 hours",
                "when_to_see_doctor": "If headaches become more frequent, severe, or are accompanied by neurological symptoms",
                "self_care_tips": ["Rest in dark, quiet room", "Apply cold or warm compress", "Stay hydrated", "Avoid known triggers"]
            },
            "Food Poisoning": {
                "typical_duration": "1-5 days",
                "when_to_see_doctor": "If you have severe dehydration, blood in stool, or high fever",
                "self_care_tips": ["Stay hydrated with clear fluids", "Follow BRAT diet", "Avoid dairy and fatty foods", "Rest and recover gradually"]
            }
        }
        
        return condition_details.get(condition_name, {
            "typical_duration": "Variable",
            "when_to_see_doctor": "If symptoms persist or worsen",
            "self_care_tips": ["Monitor symptoms", "Stay hydrated", "Get adequate rest", "Seek medical advice if concerned"]
        })
    
    def _generate_detailed_recommendations(self, symptom_analysis: SymptomAnalysis, 
                                         conditions: List[DetailedCondition], 
                                         symptom_input: SymptomInput) -> List[DetailedRecommendation]:
        """
        Generate comprehensive, prioritized recommendations
        """
        recommendations = []
        
        # Emergency recommendation if critical severity
        if symptom_analysis.severity_assessment == SeverityLevel.CRITICAL:
            recommendations.append(DetailedRecommendation(
                type=RecommendationType.EMERGENCY,
                title="Seek Immediate Emergency Care",
                message="Your symptoms indicate a potentially serious condition that requires immediate medical attention.",
                urgency=SeverityLevel.CRITICAL,
                action_steps=[
                    "Call emergency services (911) immediately",
                    "Do not drive yourself to the hospital",
                    "Have someone stay with you",
                    "Bring a list of current medications"
                ],
                timeframe="Immediately",
                warning_signs=["Worsening symptoms", "Loss of consciousness", "Severe difficulty breathing"]
            ))
            return recommendations
        
        # High priority medical consultation
        if symptom_analysis.severity_assessment == SeverityLevel.HIGH:
            recommendations.append(DetailedRecommendation(
                type=RecommendationType.CONSULT_DOCTOR,
                title="Schedule Urgent Medical Consultation",
                message="Your symptoms require prompt medical evaluation to rule out serious conditions.",
                urgency=SeverityLevel.HIGH,
                action_steps=[
                    "Contact your healthcare provider today",
                    "If unavailable, visit urgent care center",
                    "Prepare a detailed symptom timeline",
                    "List all current medications and allergies"
                ],
                timeframe="Within 24 hours",
                warning_signs=["Symptoms getting worse", "New symptoms developing", "Difficulty performing daily activities"]
            ))
        
        # Medium priority consultation
        elif symptom_analysis.severity_assessment == SeverityLevel.MEDIUM:
            recommendations.append(DetailedRecommendation(
                type=RecommendationType.CONSULT_DOCTOR,
                title="Schedule Medical Consultation",
                message="Your symptoms warrant medical evaluation to ensure proper diagnosis and treatment.",
                urgency=SeverityLevel.MEDIUM,
                action_steps=[
                    "Schedule appointment with your healthcare provider",
                    "Monitor symptoms and note any changes",
                    "Keep a symptom diary",
                    "Prepare questions for your doctor"
                ],
                timeframe="Within 2-3 days",
                warning_signs=["Symptoms persist beyond expected timeframe", "New symptoms appear", "Symptoms interfere with daily life"]
            ))
        
        # Self-care recommendations based on symptoms
        self_care_rec = self._generate_self_care_recommendations(symptom_analysis, conditions)
        if self_care_rec:
            recommendations.append(self_care_rec)
        
        # Monitoring recommendations
        monitoring_rec = self._generate_monitoring_recommendations(symptom_analysis)
        if monitoring_rec:
            recommendations.append(monitoring_rec)
        
        return recommendations
    
    def _generate_self_care_recommendations(self, symptom_analysis: SymptomAnalysis, 
                                          conditions: List[DetailedCondition]) -> DetailedRecommendation:
        """
        Generate self-care recommendations based on symptoms
        """
        action_steps = []
        
        # General self-care
        action_steps.extend([
            "Get adequate rest (7-9 hours of sleep)",
            "Stay well hydrated (8-10 glasses of water daily)",
            "Eat nutritious, easily digestible foods"
        ])
        
        # Symptom-specific recommendations
        if "respiratory" in symptom_analysis.symptom_categories:
            action_steps.extend([
                "Use a humidifier or breathe steam from hot shower",
                "Avoid irritants like smoke and strong odors",
                "Consider honey for cough relief (if over 1 year old)"
            ])
        
        if "gastrointestinal" in symptom_analysis.symptom_categories:
            action_steps.extend([
                "Follow BRAT diet (bananas, rice, applesauce, toast)",
                "Avoid dairy, fatty, and spicy foods temporarily",
                "Consider probiotics to restore gut health"
            ])
        
        if "general" in symptom_analysis.symptom_categories and any("fever" in s for s in symptom_analysis.extracted_symptoms):
            action_steps.extend([
                "Monitor temperature regularly",
                "Use fever-reducing medication as directed",
                "Wear light, breathable clothing"
            ])
        
        return DetailedRecommendation(
            type=RecommendationType.SELF_CARE,
            title="Self-Care and Home Management",
            message="These self-care measures can help manage your symptoms and support recovery.",
            urgency=SeverityLevel.LOW,
            action_steps=action_steps,
            timeframe="Start immediately and continue as needed",
            warning_signs=["Symptoms worsen despite self-care", "New concerning symptoms develop"]
        )
    
    def _generate_monitoring_recommendations(self, symptom_analysis: SymptomAnalysis) -> DetailedRecommendation:
        """
        Generate monitoring recommendations
        """
        return DetailedRecommendation(
            type=RecommendationType.MONITORING,
            title="Symptom Monitoring and Tracking",
            message="Careful monitoring of your symptoms will help track progress and identify any concerning changes.",
            urgency=SeverityLevel.LOW,
            action_steps=[
                "Keep a daily symptom diary with severity ratings",
                "Note any triggers or patterns you observe",
                "Track temperature if fever is present",
                "Record any new symptoms that develop",
                "Note response to any treatments or medications"
            ],
            timeframe="Daily until symptoms resolve",
            warning_signs=[
                "Symptoms suddenly worsen",
                "High fever (over 103°F/39.4°C)",
                "Difficulty breathing or chest pain",
                "Severe dehydration signs"
            ]
        )
    
    def _generate_general_advice(self, symptom_analysis: SymptomAnalysis) -> List[str]:
        """
        Generate general health advice
        """
        advice = [
            "Maintain good hygiene by washing hands frequently",
            "Avoid close contact with others if you feel unwell",
            "Listen to your body and rest when needed",
            "Stay connected with family or friends for support"
        ]
        
        if symptom_analysis.severity_assessment in [SeverityLevel.MEDIUM, SeverityLevel.HIGH]:
            advice.append("Consider having someone check on you regularly")
            advice.append("Keep emergency contact numbers easily accessible")
        
        return advice
    
    def _identify_red_flags(self, symptoms: List[str]) -> List[str]:
        """
        Identify warning signs that require immediate attention
        """
        red_flags = []
        
        emergency_patterns = {
            "chest pain": "Severe or crushing chest pain, especially with shortness of breath",
            "difficulty breathing": "Severe difficulty breathing or inability to catch your breath",
            "high fever": "Fever over 103°F (39.4°C) or fever with severe symptoms",
            "severe headache": "Sudden, severe headache unlike any you've had before",
            "confusion": "Sudden confusion, disorientation, or difficulty speaking",
            "severe pain": "Pain that is unbearable or prevents normal activities"
        }
        
        for symptom in symptoms:
            for pattern, warning in emergency_patterns.items():
                if pattern in symptom.lower():
                    red_flags.append(warning)
        
        # General red flags
        red_flags.extend([
            "Symptoms that rapidly worsen",
            "Signs of severe dehydration (dizziness, dry mouth, little/no urination)",
            "Persistent vomiting that prevents keeping fluids down",
            "Any symptom that causes you significant concern"
        ])
        
        return list(set(red_flags))  # Remove duplicates
    
    def _generate_follow_up_questions(self, symptom_analysis: SymptomAnalysis, 
                                    conditions: List[DetailedCondition]) -> List[str]:
        """
        Generate follow-up questions to help refine diagnosis
        """
        questions = [
            "How long have you been experiencing these symptoms?",
            "Have the symptoms been getting better, worse, or staying the same?",
            "Are there any activities or times of day when symptoms are worse?",
            "Have you taken any medications or treatments for these symptoms?"
        ]
        
        # Symptom-specific questions
        if "respiratory" in symptom_analysis.symptom_categories:
            questions.append("Do you have any known allergies or asthma?")
            questions.append("Have you been exposed to anyone who was sick recently?")
        
        if "gastrointestinal" in symptom_analysis.symptom_categories:
            questions.append("Have you eaten anything unusual or from a new source recently?")
            questions.append("Are you able to keep fluids down?")
        
        if any("headache" in s.lower() for s in symptom_analysis.extracted_symptoms):
            questions.append("Is this headache different from headaches you normally get?")
            questions.append("Are you experiencing any vision changes or sensitivity to light?")
        
        return questions
    
    def _calculate_confidence_score(self, symptoms: List[str], conditions: List[DetailedCondition]) -> float:
        """
        Calculate confidence score for the analysis
        """
        base_confidence = 0.6
        
        # Adjust based on number of symptoms
        if len(symptoms) >= 3:
            base_confidence += 0.1
        elif len(symptoms) == 1:
            base_confidence -= 0.1
        
        # Adjust based on condition matches
        if conditions and conditions[0].probability > 0.7:
            base_confidence += 0.2
        elif not conditions:
            base_confidence -= 0.2
        
        # Adjust based on symptom specificity
        specific_symptoms = ["chest pain", "difficulty breathing", "severe headache"]
        if any(spec in ' '.join(symptoms).lower() for spec in specific_symptoms):
            base_confidence += 0.1
        
        return min(max(base_confidence, 0.1), 0.9)  # Keep between 0.1 and 0.9

