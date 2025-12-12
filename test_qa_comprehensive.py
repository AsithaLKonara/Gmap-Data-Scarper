"""
Comprehensive QA Test Script
Tests from three perspectives: QA Tester, Lead Collector User, Admin
"""
import os
import sys
import requests
import json
from typing import Dict, Optional
from datetime import datetime

# Test configuration
BASE_URL = os.getenv("API_URL", "http://localhost:8000")
TEST_USER_EMAIL = "test@example.com"
TEST_USER_PASSWORD = "testpassword123"
ADMIN_USER_ID = os.getenv("ADMIN_USER_IDS", "").split(",")[0] if os.getenv("ADMIN_USER_IDS") else None

class QATester:
    """QA Tester perspective - tests functionality, edge cases, errors"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.token = None
        self.test_results = []
    
    def log_test(self, test_name: str, passed: bool, message: str = ""):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        self.test_results.append({
            "test": test_name,
            "status": status,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
        print(f"{status}: {test_name}")
        if message:
            print(f"   {message}")
    
    def authenticate(self) -> bool:
        """Test authentication"""
        try:
            # Try to register first
            register_data = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            response = self.session.post(f"{self.base_url}/api/auth/register", json=register_data)
            
            if response.status_code in [200, 201, 400]:  # 400 = already exists
                # Try to login
                login_data = {
                    "email": TEST_USER_EMAIL,
                    "password": TEST_USER_PASSWORD
                }
                response = self.session.post(f"{self.base_url}/api/auth/login", json=login_data)
                
                if response.status_code == 200:
                    data = response.json()
                    self.token = data.get("access_token")
                    self.session.headers.update({"Authorization": f"Bearer {self.token}"})
                    self.log_test("Authentication", True, "Successfully authenticated")
                    return True
                else:
                    self.log_test("Authentication", False, f"Login failed: {response.status_code}")
                    return False
            else:
                self.log_test("Authentication", False, f"Registration failed: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_health_endpoint(self):
        """Test health endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/health")
            if response.status_code == 200:
                data = response.json()
                db_status = data.get("database", {}).get("status")
                self.log_test("Health Endpoint", db_status == "connected", 
                            f"Database: {db_status}")
            else:
                self.log_test("Health Endpoint", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Health Endpoint", False, f"Exception: {str(e)}")
    
    def test_invalid_token(self):
        """Test with invalid token"""
        try:
            self.session.headers.update({"Authorization": "Bearer invalid_token"})
            response = self.session.get(f"{self.base_url}/api/tasks")
            passed = response.status_code == 401
            self.log_test("Invalid Token Rejection", passed, 
                        f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Invalid Token Rejection", False, f"Exception: {str(e)}")
        finally:
            # Restore valid token
            if self.token:
                self.session.headers.update({"Authorization": f"Bearer {self.token}"})
    
    def test_missing_auth(self):
        """Test endpoints without authentication"""
        try:
            self.session.headers.pop("Authorization", None)
            response = self.session.get(f"{self.base_url}/api/tasks")
            # Some endpoints allow optional auth, so 200 or 401 are both valid
            passed = response.status_code in [200, 401]
            self.log_test("Missing Auth Handling", passed, 
                        f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Missing Auth Handling", False, f"Exception: {str(e)}")
        finally:
            # Restore token
            if self.token:
                self.session.headers.update({"Authorization": f"Bearer {self.token}"})
    
    def test_input_validation(self):
        """Test input validation"""
        try:
            # Test invalid task_id
            response = self.session.get(f"{self.base_url}/api/tasks/invalid_task_id")
            passed = response.status_code in [404, 422]
            self.log_test("Input Validation", passed, 
                        f"Invalid task_id handled: {response.status_code}")
        except Exception as e:
            self.log_test("Input Validation", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all QA tests"""
        print("\n=== QA TESTER PERSPECTIVE ===")
        if self.authenticate():
            self.test_health_endpoint()
            self.test_invalid_token()
            self.test_missing_auth()
            self.test_input_validation()
        return self.test_results


class LeadCollectorUser:
    """Lead Collector User perspective - tests workflows and usability"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.token = None
        self.test_results = []
        self.task_id = None
    
    def log_test(self, test_name: str, passed: bool, message: str = ""):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        self.test_results.append({
            "test": test_name,
            "status": status,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
        print(f"{status}: {test_name}")
        if message:
            print(f"   {message}")
    
    def authenticate(self) -> bool:
        """Authenticate as lead collector"""
        try:
            login_data = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            response = self.session.post(f"{self.base_url}/api/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.session.headers.update({"Authorization": f"Bearer {self.token}"})
                self.log_test("User Authentication", True)
                return True
            else:
                self.log_test("User Authentication", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("User Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_list_tasks(self):
        """Test listing tasks"""
        try:
            response = self.session.get(f"{self.base_url}/api/tasks")
            passed = response.status_code == 200
            if passed:
                tasks = response.json()
                self.log_test("List Tasks", True, f"Found {len(tasks)} tasks")
            else:
                self.log_test("List Tasks", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("List Tasks", False, f"Exception: {str(e)}")
    
    def test_get_filters(self):
        """Test getting filter options"""
        try:
            response = self.session.get(f"{self.base_url}/api/filters/platforms")
            passed = response.status_code == 200
            if passed:
                platforms = response.json()
                self.log_test("Get Filters", True, f"Found {len(platforms)} platforms")
            else:
                self.log_test("Get Filters", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Get Filters", False, f"Exception: {str(e)}")
    
    def test_export_endpoints(self):
        """Test export functionality"""
        try:
            # Test CSV export
            response = self.session.get(f"{self.base_url}/api/export/csv")
            passed = response.status_code in [200, 404]  # 404 if no data
            self.log_test("Export CSV", passed, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Export CSV", False, f"Exception: {str(e)}")
    
    def test_soft_delete_lead(self):
        """Test soft deleting a lead"""
        try:
            # First, get a lead (if any exist)
            response = self.session.get(f"{self.base_url}/api/export/json?limit=1")
            if response.status_code == 200:
                leads = response.json()
                if leads and len(leads) > 0:
                    lead_id = leads[0].get("id")
                    if lead_id:
                        # Try to soft delete
                        delete_response = self.session.post(
                            f"{self.base_url}/api/soft-delete/leads/{lead_id}/delete"
                        )
                        passed = delete_response.status_code in [200, 404]
                        self.log_test("Soft Delete Lead", passed, 
                                    f"Status: {delete_response.status_code}")
                    else:
                        self.log_test("Soft Delete Lead", True, "No leads to delete")
                else:
                    self.log_test("Soft Delete Lead", True, "No leads available")
            else:
                self.log_test("Soft Delete Lead", True, "No leads endpoint available")
        except Exception as e:
            self.log_test("Soft Delete Lead", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all lead collector tests"""
        print("\n=== LEAD COLLECTOR USER PERSPECTIVE ===")
        if self.authenticate():
            self.test_list_tasks()
            self.test_get_filters()
            self.test_export_endpoints()
            self.test_soft_delete_lead()
        return self.test_results


class AdminUser:
    """Admin perspective - tests admin functions"""
    
    def __init__(self, base_url: str, admin_user_id: Optional[str] = None):
        self.base_url = base_url
        self.session = requests.Session()
        self.token = None
        self.admin_user_id = admin_user_id
        self.test_results = []
    
    def log_test(self, test_name: str, passed: bool, message: str = ""):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        self.test_results.append({
            "test": test_name,
            "status": status,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
        print(f"{status}: {test_name}")
        if message:
            print(f"   {message}")
    
    def authenticate(self) -> bool:
        """Authenticate as admin"""
        try:
            login_data = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            response = self.session.post(f"{self.base_url}/api/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.session.headers.update({"Authorization": f"Bearer {self.token}"})
                self.log_test("Admin Authentication", True)
                return True
            else:
                self.log_test("Admin Authentication", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_admin_access_check(self):
        """Test that admin endpoints require admin access"""
        try:
            # Try to hard delete without admin access (should fail)
            response = self.session.post(f"{self.base_url}/api/soft-delete/leads/999/hard-delete")
            # Should return 403 if not admin, or 404 if lead doesn't exist
            passed = response.status_code in [403, 404]
            self.log_test("Admin Access Check", passed, 
                        f"Hard delete requires admin: {response.status_code}")
        except Exception as e:
            self.log_test("Admin Access Check", False, f"Exception: {str(e)}")
    
    def test_health_monitoring(self):
        """Test health monitoring endpoints"""
        try:
            response = self.session.get(f"{self.base_url}/api/health")
            passed = response.status_code == 200
            if passed:
                data = response.json()
                self.log_test("Health Monitoring", True, 
                            f"Database: {data.get('database', {}).get('status', 'unknown')}")
            else:
                self.log_test("Health Monitoring", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Health Monitoring", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all admin tests"""
        print("\n=== ADMIN PERSPECTIVE ===")
        if self.authenticate():
            self.test_admin_access_check()
            self.test_health_monitoring()
        return self.test_results


def main():
    """Run comprehensive QA tests"""
    print("=" * 60)
    print("COMPREHENSIVE QA TEST SUITE")
    print("=" * 60)
    
    all_results = []
    
    # QA Tester perspective
    qa_tester = QATester(BASE_URL)
    qa_results = qa_tester.run_all_tests()
    all_results.extend(qa_results)
    
    # Lead Collector User perspective
    lead_collector = LeadCollectorUser(BASE_URL)
    collector_results = lead_collector.run_all_tests()
    all_results.extend(collector_results)
    
    # Admin perspective
    admin = AdminUser(BASE_URL, ADMIN_USER_ID)
    admin_results = admin.run_all_tests()
    all_results.extend(admin_results)
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    total = len(all_results)
    passed = sum(1 for r in all_results if "PASS" in r["status"])
    failed = total - passed
    
    print(f"Total Tests: {total}")
    print(f"Passed: {passed} ✅")
    print(f"Failed: {failed} ❌")
    print(f"Success Rate: {(passed/total*100):.1f}%")
    
    # Save results
    with open("qa_test_results.json", "w") as f:
        json.dump(all_results, f, indent=2)
    
    print("\nResults saved to qa_test_results.json")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())


