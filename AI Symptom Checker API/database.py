import sqlite3
import json
from typing import List, Optional
from models import SymptomInput, ComprehensiveResponse, HealthTip
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path: str = "symptom_checker.db"):
        self.db_path = db_path
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def initialize_database(self):
        """Initialize database with required tables and sample data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS symptom_analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                input_text TEXT NOT NULL,
                extracted_symptoms TEXT NOT NULL,
                age INTEGER,
                gender TEXT,
                additional_info TEXT,
                analysis_result TEXT NOT NULL,
                confidence_score REAL,
                severity_level TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conditions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT NOT NULL,
                symptoms TEXT NOT NULL,
                severity TEXT NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS health_tips (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS common_symptoms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                category TEXT NOT NULL
            )
        ''')
        
        # Insert sample data
        self._insert_sample_conditions(cursor)
        self._insert_sample_health_tips(cursor)
        self._insert_common_symptoms(cursor)
        
        conn.commit()
        conn.close()
    
    def _insert_sample_conditions(self, cursor):
        """Insert comprehensive sample medical conditions"""
        conditions = [
            ("Common Cold", "A viral infection of the upper respiratory tract causing mild to moderate symptoms", 
             "runny nose,sneezing,cough,sore throat,mild fever,congestion", "low"),
            ("Influenza (Flu)", "Influenza viral infection affecting respiratory system with systemic symptoms", 
             "fever,body aches,fatigue,cough,headache,chills,sore throat", "medium"),
            ("Migraine Headache", "Severe headache often with nausea, light sensitivity, and visual disturbances", 
             "severe headache,nausea,light sensitivity,visual disturbances,throbbing pain", "medium"),
            ("Food Poisoning", "Illness caused by consuming contaminated food or water", 
             "nausea,vomiting,diarrhea,stomach pain,fever,abdominal cramps", "medium"),
            ("Allergic Reaction", "Immune system response to allergens ranging from mild to severe", 
             "rash,itching,swelling,difficulty breathing,hives,runny nose", "high"),
            ("Dehydration", "Insufficient fluid levels in the body affecting normal function", 
             "thirst,dry mouth,fatigue,dizziness,dark urine,weakness", "medium"),
            ("Anxiety Disorder", "Mental health condition causing excessive worry and physical symptoms", 
             "restlessness,rapid heartbeat,sweating,difficulty concentrating,muscle tension", "low"),
            ("Gastritis", "Inflammation of the stomach lining causing digestive symptoms", 
             "stomach pain,nausea,bloating,loss of appetite,heartburn", "low"),
            ("Hypertension", "High blood pressure condition that may cause various symptoms", 
             "headache,dizziness,chest pain,shortness of breath,fatigue", "high"),
            ("Type 2 Diabetes", "Blood sugar regulation disorder with multiple systemic effects", 
             "excessive thirst,frequent urination,fatigue,blurred vision,slow healing", "high"),
            ("Bronchitis", "Inflammation of the bronchial tubes causing respiratory symptoms", 
             "persistent cough,mucus production,chest discomfort,fatigue,mild fever", "medium"),
            ("Sinusitis", "Inflammation of the sinus cavities causing facial pain and congestion", 
             "facial pain,nasal congestion,headache,thick nasal discharge,reduced smell", "low"),
            ("Urinary Tract Infection", "Bacterial infection of the urinary system", 
             "burning urination,frequent urination,pelvic pain,cloudy urine,strong urine odor", "medium"),
            ("Tension Headache", "Most common type of headache caused by muscle tension", 
             "dull headache,head pressure,neck stiffness,scalp tenderness", "low"),
            ("Viral Gastroenteritis", "Stomach flu causing gastrointestinal symptoms", 
             "nausea,vomiting,diarrhea,stomach cramps,low-grade fever,fatigue", "medium")
        ]
        
        cursor.executemany('''
            INSERT OR IGNORE INTO conditions (name, description, symptoms, severity)
            VALUES (?, ?, ?, ?)
        ''', conditions)
    
    def _insert_sample_health_tips(self, cursor):
        """Insert sample health tips"""
        tips = [
            ("Stay Hydrated", "Drink at least 8 glasses of water daily to maintain proper hydration", "general"),
            ("Regular Exercise", "Engage in at least 30 minutes of physical activity daily", "fitness"),
            ("Balanced Diet", "Eat a variety of fruits, vegetables, whole grains, and lean proteins", "nutrition"),
            ("Adequate Sleep", "Get 7-9 hours of quality sleep each night for optimal health", "sleep"),
            ("Stress Management", "Practice relaxation techniques like meditation or deep breathing", "mental_health"),
            ("Hand Hygiene", "Wash hands frequently with soap and water for at least 20 seconds", "hygiene"),
            ("Regular Checkups", "Schedule annual health checkups with your healthcare provider", "preventive"),
            ("Limit Alcohol", "Consume alcohol in moderation or avoid it completely", "lifestyle"),
            ("Don't Smoke", "Avoid smoking and exposure to secondhand smoke", "lifestyle"),
            ("Sun Protection", "Use sunscreen and protective clothing when outdoors", "skin_care")
        ]
        
        cursor.executemany('''
            INSERT OR IGNORE INTO health_tips (title, description, category)
            VALUES (?, ?, ?)
        ''', tips)
    
    def _insert_common_symptoms(self, cursor):
        """Insert comprehensive list of common symptoms"""
        symptoms = [
            ("fever", "general"),
            ("headache", "neurological"),
            ("cough", "respiratory"),
            ("sore throat", "respiratory"),
            ("runny nose", "respiratory"),
            ("nasal congestion", "respiratory"),
            ("shortness of breath", "respiratory"),
            ("chest pain", "cardiovascular"),
            ("nausea", "gastrointestinal"),
            ("vomiting", "gastrointestinal"),
            ("diarrhea", "gastrointestinal"),
            ("stomach pain", "gastrointestinal"),
            ("abdominal pain", "gastrointestinal"),
            ("loss of appetite", "gastrointestinal"),
            ("fatigue", "general"),
            ("weakness", "general"),
            ("dizziness", "neurological"),
            ("muscle aches", "musculoskeletal"),
            ("joint pain", "musculoskeletal"),
            ("back pain", "musculoskeletal"),
            ("rash", "dermatological"),
            ("itching", "dermatological"),
            ("swelling", "general"),
            ("difficulty sleeping", "sleep"),
            ("anxiety", "mental_health"),
            ("rapid heartbeat", "cardiovascular"),
            ("sweating", "general"),
            ("chills", "general"),
            ("body aches", "musculoskeletal"),
            ("sneezing", "respiratory")
        ]
        
        cursor.executemany('''
            INSERT OR IGNORE INTO common_symptoms (name, category)
            VALUES (?, ?)
        ''', symptoms)
    
    def store_symptom_analysis(self, symptom_input: SymptomInput, result: ComprehensiveResponse):
        """Store comprehensive symptom analysis in database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO symptom_analyses (
                    input_text, extracted_symptoms, age, gender, additional_info,
                    analysis_result, confidence_score, severity_level
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                symptom_input.symptoms,
                json.dumps(result.symptom_analysis.extracted_symptoms),
                symptom_input.age,
                symptom_input.gender,
                symptom_input.additional_info,
                result.json(),
                result.confidence_score,
                result.symptom_analysis.severity_assessment.value
            ))
            
            conn.commit()
        except Exception as e:
            print(f"Warning: Could not store symptom analysis: {e}")
        finally:
            conn.close()
    
    def get_health_tips(self, category: Optional[str] = None) -> List[HealthTip]:
        """Get health tips, optionally filtered by category"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if category:
            cursor.execute('SELECT title, description, category FROM health_tips WHERE category = ?', (category,))
        else:
            cursor.execute('SELECT title, description, category FROM health_tips')
        
        tips = [HealthTip(title=row[0], description=row[1], category=row[2]) for row in cursor.fetchall()]
        conn.close()
        return tips
    
    def get_common_symptoms(self) -> List[str]:
        """Get list of common symptoms"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT name FROM common_symptoms ORDER BY name')
        symptoms = [row[0] for row in cursor.fetchall()]
        conn.close()
        return symptoms
    
    def get_all_conditions(self) -> List[dict]:
        """Get all medical conditions"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT name, description, severity FROM conditions')
        conditions = [{"name": row[0], "description": row[1], "severity": row[2]} for row in cursor.fetchall()]
        conn.close()
        return conditions
    
    def get_conditions_by_symptoms(self, symptoms: List[str]) -> List[dict]:
        """Get conditions that match given symptoms with improved matching algorithm"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT name, description, symptoms, severity FROM conditions')
        all_conditions = cursor.fetchall()
        
        matching_conditions = []
        
        for condition in all_conditions:
            condition_symptoms = [s.strip().lower() for s in condition[2].split(',')]
            
            # Calculate match score using multiple methods
            exact_matches = 0
            partial_matches = 0
            
            for input_symptom in symptoms:
                input_symptom_lower = input_symptom.lower()
                
                # Check for exact matches
                for condition_symptom in condition_symptoms:
                    if condition_symptom in input_symptom_lower or input_symptom_lower in condition_symptom:
                        exact_matches += 1
                        break
                else:
                    # Check for partial matches (word overlap)
                    input_words = set(input_symptom_lower.split())
                    for condition_symptom in condition_symptoms:
                        condition_words = set(condition_symptom.split())
                        if input_words & condition_words:  # If there's any word overlap
                            partial_matches += 0.5
                            break
            
            total_score = exact_matches + partial_matches
            
            if total_score > 0:
                # Calculate probability based on matches and condition symptom count
                probability = min(total_score / len(condition_symptoms), 1.0)
                
                # Boost probability for exact matches
                if exact_matches > 0:
                    probability = min(probability * 1.3, 1.0)
                
                matching_conditions.append({
                    "name": condition[0],
                    "description": condition[1],
                    "symptoms": condition_symptoms,
                    "severity": condition[3],
                    "probability": probability,
                    "match_count": exact_matches,
                    "total_score": total_score
                })
        
        # Sort by probability, then by total score, then by exact matches
        matching_conditions.sort(
            key=lambda x: (x["probability"], x["total_score"], x["match_count"]), 
            reverse=True
        )
        
        conn.close()
        return matching_conditions
    
    def get_analysis_statistics(self) -> dict:
        """Get statistics about stored analyses (optional analytics)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT COUNT(*) FROM symptom_analyses')
            total_analyses = cursor.fetchone()[0]
            
            cursor.execute('''
                SELECT severity_level, COUNT(*) 
                FROM symptom_analyses 
                GROUP BY severity_level
            ''')
            severity_stats = dict(cursor.fetchall())
            
            cursor.execute('''
                SELECT AVG(confidence_score) 
                FROM symptom_analyses 
                WHERE confidence_score IS NOT NULL
            ''')
            avg_confidence = cursor.fetchone()[0] or 0
            
            return {
                "total_analyses": total_analyses,
                "severity_distribution": severity_stats,
                "average_confidence": round(avg_confidence, 2)
            }
        except Exception as e:
            print(f"Warning: Could not get statistics: {e}")
            return {"error": "Statistics unavailable"}
        finally:
            conn.close()

