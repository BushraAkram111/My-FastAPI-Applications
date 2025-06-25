import requests
import json
import time
from typing import Dict, Any

class APITester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def test_root_endpoint(self) -> bool:
        """Test the root endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/")
            print(f"✓ Root endpoint: {response.status_code}")
            print(f"  Response: {response.json()}")
            return response.status_code == 200
        except Exception as e:
            print(f"✗ Root endpoint failed: {e}")
            return False
    
    def test_health_check(self) -> bool:
        """Test the health check endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            print(f"✓ Health check: {response.status_code}")
            print(f"  Response: {response.json()}")
            return response.status_code == 200
        except Exception as e:
            print(f"✗ Health check failed: {e}")
            return False
    
    def test_symptom_check(self) -> bool:
        """Test the symptom check endpoint"""
        try:
            # Test data
            test_symptoms = {
                "symptoms": ["fever", "headache", "cough"],
                "age": 30,
                "gender": "male",
                "duration": "2 days"
            }
            
            response = self.session.post(
                f"{self.base_url}/check-symptoms",
                json=test_symptoms
            )
            print(f"✓ Symptom check: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"  Input symptoms: {result['input_symptoms']}")
                print(f"  Possible conditions: {len(result['possible_conditions'])}")
                print(f"  Recommendations: {len(result['recommendations'])}")
                
                # Print first condition if available
                if result['possible_conditions']:
                    condition = result['possible_conditions'][0]
                    print(f"  Top condition: {condition['name']} (probability: {condition['probability']:.2f})")
                
                return True
            return False
        except Exception as e:
            print(f"✗ Symptom check failed: {e}")
            return False
    
    def test_health_tips(self) -> bool:
        """Test the health tips endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/health-tips")
            print(f"✓ Health tips: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"  Number of tips: {len(result['tips'])}")
                if result['tips']:
                    print(f"  First tip: {result['tips'][0]['title']}")
                return True
            return False
        except Exception as e:
            print(f"✗ Health tips failed: {e}")
            return False
    
    def test_common_symptoms(self) -> bool:
        """Test the common symptoms endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/symptoms")
            print(f"✓ Common symptoms: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"  Number of symptoms: {len(result['common_symptoms'])}")
                if result['common_symptoms']:
                    print(f"  First few symptoms: {result['common_symptoms'][:5]}")
                return True
            return False
        except Exception as e:
            print(f"✗ Common symptoms failed: {e}")
            return False
    
    def test_conditions(self) -> bool:
        """Test the conditions endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/conditions")
            print(f"✓ Conditions: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"  Number of conditions: {len(result['conditions'])}")
                if result['conditions']:
                    print(f"  First condition: {result['conditions'][0]['name']}")
                return True
            return False
        except Exception as e:
            print(f"✗ Conditions failed: {e}")
            return False
    
    def test_error_handling(self) -> bool:
        """Test error handling with invalid input"""
        try:
            # Test with empty symptoms
            response = self.session.post(
                f"{self.base_url}/check-symptoms",
                json={"symptoms": []}
            )
            print(f"✓ Error handling (empty symptoms): {response.status_code}")
            return response.status_code == 400
        except Exception as e:
            print(f"✗ Error handling failed: {e}")
            return False
    
    def run_all_tests(self) -> Dict[str, bool]:
        """Run all tests and return results"""
        print("=" * 50)
        print("AI Symptom Checker API - Test Suite")
        print("=" * 50)
        
        tests = {
            "Root Endpoint": self.test_root_endpoint,
            "Health Check": self.test_health_check,
            "Symptom Check": self.test_symptom_check,
            "Health Tips": self.test_health_tips,
            "Common Symptoms": self.test_common_symptoms,
            "Conditions": self.test_conditions,
            "Error Handling": self.test_error_handling
        }
        
        results = {}
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests.items():
            print(f"\n--- Testing {test_name} ---")
            result = test_func()
            results[test_name] = result
            if result:
                passed += 1
        
        print("\n" + "=" * 50)
        print(f"Test Results: {passed}/{total} tests passed")
        print("=" * 50)
        
        return results

def main():
    """Main function to run tests"""
    print("Starting API tests...")
    print("Make sure the API server is running on http://localhost:8000")
    print("You can start it with: python3 main.py")
    
    # Wait a moment for user to start server if needed
    input("Press Enter when the server is running...")
    
    tester = APITester()
    results = tester.run_all_tests()
    
    # Summary
    if all(results.values()):
        print("\n🎉 All tests passed! The API is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
        failed_tests = [name for name, result in results.items() if not result]
        print(f"Failed tests: {', '.join(failed_tests)}")

if __name__ == "__main__":
    main()

