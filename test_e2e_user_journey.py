"""
Deep End-to-End Test: Real User Journey Simulation
Tests the complete user experience from registration to data export
"""
import os
import sys
import requests
import json
import time
from typing import Dict, Optional, List
from datetime import datetime
from urllib.parse import urljoin

# Test configuration
BASE_URL = os.getenv("API_URL", "http://localhost:8000")
TEST_USER_EMAIL = f"e2e_test_{int(time.time())}@example.com"
TEST_USER_PASSWORD = "TestPassword123!"
TEST_USER_NAME = "E2E Test User"

class E2EUserJourney:
    """Simulates a complete user journey through the platform"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.token = None
        self.user_id = None
        self.test_results = []
        self.task_id = None
        self.lead_ids = []
        
    def log_step(self, step_name: str, passed: bool, message: str = "", data: Dict = None):
        """Log test step result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        result = {
            "step": step_name,
            "status": status,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        if data:
            result["data"] = data
        self.test_results.append(result)
        
        print(f"\n{status}: {step_name}")
        if message:
            print(f"   {message}")
        if data:
            print(f"   Data: {json.dumps(data, indent=2)}")
    
    def make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make HTTP request with error handling"""
        url = urljoin(self.base_url, endpoint)
        try:
            response = self.session.request(method, url, timeout=30, **kwargs)
            return response
        except requests.exceptions.ConnectionError as e:
            error_msg = f"Cannot connect to {self.base_url}. Is the server running?"
            self.log_step(f"Connection Error: {endpoint}", False, error_msg)
            raise ConnectionError(error_msg) from e
        except requests.exceptions.RequestException as e:
            self.log_step(f"Request Error: {endpoint}", False, f"Exception: {str(e)}")
            raise
    
    # ==================== PHASE 1: AUTHENTICATION ====================
    
    def step_1_check_health(self) -> bool:
        """Step 1: Check API health before starting"""
        try:
            response = self.make_request("GET", "/api/health")
            if response.status_code == 200:
                data = response.json()
                db_status = data.get("database", {}).get("status", "unknown")
                self.log_step("1. Health Check", True, f"API is healthy. Database: {db_status}", data)
                return True
            else:
                self.log_step("1. Health Check", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_step("1. Health Check", False, f"Exception: {str(e)}")
            return False
    
    def step_2_register_user(self) -> bool:
        """Step 2: Register a new user"""
        try:
            register_data = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD,
                "name": TEST_USER_NAME,
                "plan_type": "free"
            }
            response = self.make_request("POST", "/api/auth/register", json=register_data)
            
            if response.status_code in [200, 201]:
                data = response.json()
                self.token = data.get("access_token")
                if self.token:
                    self.session.headers.update({"Authorization": f"Bearer {self.token}"})
                    self.log_step("2. User Registration", True, "User registered successfully", {
                        "email": TEST_USER_EMAIL,
                        "has_token": bool(self.token)
                    })
                    return True
                else:
                    self.log_step("2. User Registration", False, "No access token in response")
                    return False
            elif response.status_code == 400:
                # User might already exist, try login instead
                self.log_step("2. User Registration", True, "User already exists, will login instead")
                return self.step_3_login()
            else:
                error = response.text
                self.log_step("2. User Registration", False, f"Status: {response.status_code}, Error: {error}")
                return False
        except Exception as e:
            self.log_step("2. User Registration", False, f"Exception: {str(e)}")
            return False
    
    def step_3_login(self) -> bool:
        """Step 3: Login user"""
        try:
            login_data = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            response = self.make_request("POST", "/api/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                if self.token:
                    self.session.headers.update({"Authorization": f"Bearer {self.token}"})
                    self.log_step("3. User Login", True, "Logged in successfully", {
                        "email": TEST_USER_EMAIL,
                        "has_token": bool(self.token)
                    })
                    return True
                else:
                    self.log_step("3. User Login", False, "No access token in response")
                    return False
            else:
                error = response.text
                self.log_step("3. User Login", False, f"Status: {response.status_code}, Error: {error}")
                return False
        except Exception as e:
            self.log_step("3. User Login", False, f"Exception: {str(e)}")
            return False
    
    def step_4_get_user_profile(self) -> bool:
        """Step 4: Get current user profile"""
        try:
            response = self.make_request("GET", "/api/auth/me")
            if response.status_code == 200:
                data = response.json()
                self.user_id = data.get("id") or data.get("user_id")
                self.log_step("4. Get User Profile", True, "Profile retrieved", {
                    "user_id": self.user_id,
                    "email": data.get("email")
                })
                return True
            else:
                self.log_step("4. Get User Profile", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_step("4. Get User Profile", False, f"Exception: {str(e)}")
            return False
    
    # ==================== PHASE 2: EXPLORATION ====================
    
    def step_5_get_filters(self) -> bool:
        """Step 5: Get available filters"""
        try:
            filter_endpoints = [
                ("platforms", "/api/filters/platforms"),
                ("business_types", "/api/filters/business-types"),
                ("job_levels", "/api/filters/job-levels"),
                ("education_levels", "/api/filters/education-levels"),
                ("lead_objectives", "/api/filters/lead-objectives")
            ]
            
            all_passed = True
            filter_data = {}
            
            for name, endpoint in filter_endpoints:
                response = self.make_request("GET", endpoint)
                if response.status_code == 200:
                    filter_data[name] = response.json()
                else:
                    all_passed = False
            
            self.log_step("5. Get Filters", all_passed, 
                         f"Retrieved {len(filter_data)} filter types", filter_data)
            return all_passed
        except Exception as e:
            self.log_step("5. Get Filters", False, f"Exception: {str(e)}")
            return False
    
    def step_6_list_tasks(self) -> bool:
        """Step 6: List existing tasks"""
        try:
            response = self.make_request("GET", "/api/tasks")
            if response.status_code == 200:
                tasks = response.json()
                self.log_step("6. List Tasks", True, f"Found {len(tasks)} existing tasks", {
                    "task_count": len(tasks)
                })
                return True
            else:
                self.log_step("6. List Tasks", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_step("6. List Tasks", False, f"Exception: {str(e)}")
            return False
    
    def step_7_get_analytics_summary(self) -> bool:
        """Step 7: Get analytics summary"""
        try:
            response = self.make_request("GET", "/api/analytics/summary")
            if response.status_code == 200:
                data = response.json()
                self.log_step("7. Analytics Summary", True, "Analytics retrieved", {
                    "total_leads": data.get("total_leads", 0),
                    "total_phones": data.get("total_phones", 0)
                })
                return True
            else:
                self.log_step("7. Analytics Summary", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_step("7. Analytics Summary", False, f"Exception: {str(e)}")
            return False
    
    # ==================== PHASE 3: SCRAPING ====================
    
    def step_8_start_scraping_task(self) -> bool:
        """Step 8: Start a scraping task"""
        try:
            scrape_request = {
                "queries": ["test business toronto"],
                "platforms": ["google_maps"],
                "max_results": 5,
                "headless": True
            }
            
            response = self.make_request("POST", "/api/scraper/start", json=scrape_request)
            
            if response.status_code == 200:
                data = response.json()
                self.task_id = data.get("task_id")
                self.log_step("8. Start Scraping Task", True, "Task started", {
                    "task_id": self.task_id,
                    "usage": data.get("usage")
                })
                return True
            elif response.status_code == 403:
                # Limit exceeded
                error_data = response.json()
                self.log_step("8. Start Scraping Task", False, 
                            f"Limit exceeded: {error_data.get('detail', {}).get('message', 'Unknown error')}")
                return False
            else:
                error = response.text
                self.log_step("8. Start Scraping Task", False, 
                            f"Status: {response.status_code}, Error: {error}")
                return False
        except Exception as e:
            self.log_step("8. Start Scraping Task", False, f"Exception: {str(e)}")
            return False
    
    def step_9_monitor_task_status(self) -> bool:
        """Step 9: Monitor task status"""
        if not self.task_id:
            self.log_step("9. Monitor Task Status", False, "No task ID available")
            return False
        
        try:
            max_attempts = 10
            for attempt in range(max_attempts):
                response = self.make_request("GET", f"/api/scraper/status/{self.task_id}")
                
                if response.status_code == 200:
                    data = response.json()
                    status = data.get("status", "unknown")
                    progress = data.get("progress", {})
                    total_results = data.get("total_results", 0)
                    
                    self.log_step(f"9. Monitor Task Status (Attempt {attempt + 1})", True, 
                                f"Status: {status}, Results: {total_results}", data)
                    
                    if status in ["completed", "stopped", "failed"]:
                        return True
                    
                    # Wait before next check
                    time.sleep(2)
                elif response.status_code == 404:
                    self.log_step("9. Monitor Task Status", False, "Task not found")
                    return False
                else:
                    self.log_step("9. Monitor Task Status", False, 
                                f"Status: {response.status_code}")
                    return False
            
            # Timeout
            self.log_step("9. Monitor Task Status", False, "Task monitoring timeout")
            return False
        except Exception as e:
            self.log_step("9. Monitor Task Status", False, f"Exception: {str(e)}")
            return False
    
    def step_10_get_task_details(self) -> bool:
        """Step 10: Get detailed task information"""
        if not self.task_id:
            self.log_step("10. Get Task Details", False, "No task ID available")
            return False
        
        try:
            response = self.make_request("GET", f"/api/tasks/{self.task_id}")
            if response.status_code == 200:
                data = response.json()
                self.log_step("10. Get Task Details", True, "Task details retrieved", data)
                return True
            else:
                self.log_step("10. Get Task Details", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_step("10. Get Task Details", False, f"Exception: {str(e)}")
            return False
    
    # ==================== PHASE 4: DATA MANAGEMENT ====================
    
    def step_11_export_data_json(self) -> bool:
        """Step 11: Export data as JSON"""
        try:
            response = self.make_request("GET", "/api/export/json", params={"limit": 10})
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.lead_ids = [lead.get("id") for lead in data[:5] if lead.get("id")]
                    self.log_step("11. Export JSON", True, 
                                f"Exported {len(data)} leads", {
                                    "lead_count": len(data),
                                    "sample_ids": self.lead_ids[:3]
                                })
                    return True
                else:
                    self.log_step("11. Export JSON", True, "Export successful (empty or different format)")
                    return True
            elif response.status_code == 404:
                self.log_step("11. Export JSON", True, "No data to export")
                return True
            else:
                self.log_step("11. Export JSON", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_step("11. Export JSON", False, f"Exception: {str(e)}")
            return False
    
    def step_12_export_data_csv(self) -> bool:
        """Step 12: Export data as CSV"""
        try:
            response = self.make_request("GET", "/api/export/csv", params={"limit": 10})
            if response.status_code == 200:
                content_type = response.headers.get("content-type", "")
                self.log_step("12. Export CSV", True, 
                            f"CSV exported (Content-Type: {content_type})", {
                                "content_length": len(response.content)
                            })
                return True
            elif response.status_code == 404:
                self.log_step("12. Export CSV", True, "No data to export")
                return True
            else:
                self.log_step("12. Export CSV", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_step("12. Export CSV", False, f"Exception: {str(e)}")
            return False
    
    def step_13_soft_delete_lead(self) -> bool:
        """Step 13: Soft delete a lead"""
        if not self.lead_ids:
            self.log_step("13. Soft Delete Lead", True, "No leads available to delete")
            return True
        
        try:
            lead_id = self.lead_ids[0]
            response = self.make_request("POST", f"/api/soft-delete/leads/{lead_id}/delete")
            
            if response.status_code == 200:
                data = response.json()
                self.log_step("13. Soft Delete Lead", True, "Lead soft deleted", data)
                return True
            elif response.status_code == 404:
                self.log_step("13. Soft Delete Lead", True, "Lead not found (may already be deleted)")
                return True
            else:
                self.log_step("13. Soft Delete Lead", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_step("13. Soft Delete Lead", False, f"Exception: {str(e)}")
            return False
    
    def step_14_get_analytics_platforms(self) -> bool:
        """Step 14: Get platform analytics"""
        try:
            response = self.make_request("GET", "/api/analytics/platforms")
            if response.status_code == 200:
                data = response.json()
                self.log_step("14. Platform Analytics", True, "Platform analytics retrieved", data)
                return True
            else:
                self.log_step("14. Platform Analytics", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_step("14. Platform Analytics", False, f"Exception: {str(e)}")
            return False
    
    def step_15_get_analytics_timeline(self) -> bool:
        """Step 15: Get timeline analytics"""
        try:
            response = self.make_request("GET", "/api/analytics/timeline")
            if response.status_code == 200:
                data = response.json()
                self.log_step("15. Timeline Analytics", True, "Timeline analytics retrieved", data)
                return True
            else:
                self.log_step("15. Timeline Analytics", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_step("15. Timeline Analytics", False, f"Exception: {str(e)}")
            return False
    
    # ==================== PHASE 5: TASK MANAGEMENT ====================
    
    def step_16_stop_task(self) -> bool:
        """Step 16: Stop the scraping task"""
        if not self.task_id:
            self.log_step("16. Stop Task", True, "No task to stop")
            return True
        
        try:
            response = self.make_request("POST", f"/api/scraper/stop/{self.task_id}")
            if response.status_code == 200:
                data = response.json()
                self.log_step("16. Stop Task", True, "Task stopped", data)
                return True
            elif response.status_code == 404:
                self.log_step("16. Stop Task", True, "Task not found (may already be stopped)")
                return True
            else:
                self.log_step("16. Stop Task", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_step("16. Stop Task", False, f"Exception: {str(e)}")
            return False
    
    def step_17_test_token_refresh(self) -> bool:
        """Step 17: Test token refresh (if refresh token available)"""
        try:
            # This would require storing refresh token during login
            # For now, we'll just verify the current token still works
            response = self.make_request("GET", "/api/auth/me")
            if response.status_code == 200:
                self.log_step("17. Token Validation", True, "Token is still valid")
                return True
            else:
                self.log_step("17. Token Validation", False, f"Token invalid: {response.status_code}")
                return False
        except Exception as e:
            self.log_step("17. Token Validation", False, f"Exception: {str(e)}")
            return False
    
    # ==================== MAIN EXECUTION ====================
    
    def run_complete_journey(self) -> Dict:
        """Run the complete user journey"""
        print("=" * 80)
        print("DEEP END-TO-END TEST: REAL USER JOURNEY")
        print("=" * 80)
        print(f"Test User: {TEST_USER_EMAIL}")
        print(f"API URL: {self.base_url}")
        print("=" * 80)
        print("\n⚠️  NOTE: Ensure the backend server is running!")
        print("   Start with: python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000")
        print("   Or use: .\\start_backend.ps1")
        print("=" * 80)
        
        # Phase 1: Authentication
        print("\n📋 PHASE 1: AUTHENTICATION & SETUP")
        print("-" * 80)
        try:
            if not self.step_1_check_health():
                print("\n❌ Server is not running. Please start the backend server first.")
                print("   See E2E_TEST_GUIDE.md for instructions.")
                return self.generate_report()
        except ConnectionError:
            print("\n❌ Cannot connect to server. Please start the backend server first.")
            print("   See E2E_TEST_GUIDE.md for instructions.")
            return self.generate_report()
        
        if not self.step_2_register_user():
            if not self.step_3_login():
                return self.generate_report()
        
        if not self.step_4_get_user_profile():
            return self.generate_report()
        
        # Phase 2: Exploration
        print("\n📋 PHASE 2: EXPLORATION")
        print("-" * 80)
        self.step_5_get_filters()
        self.step_6_list_tasks()
        self.step_7_get_analytics_summary()
        
        # Phase 3: Scraping
        print("\n📋 PHASE 3: SCRAPING")
        print("-" * 80)
        if self.step_8_start_scraping_task():
            self.step_9_monitor_task_status()
            self.step_10_get_task_details()
        
        # Phase 4: Data Management
        print("\n📋 PHASE 4: DATA MANAGEMENT")
        print("-" * 80)
        self.step_11_export_data_json()
        self.step_12_export_data_csv()
        self.step_13_soft_delete_lead()
        self.step_14_get_analytics_platforms()
        self.step_15_get_analytics_timeline()
        
        # Phase 5: Task Management
        print("\n📋 PHASE 5: TASK MANAGEMENT")
        print("-" * 80)
        self.step_16_stop_task()
        self.step_17_test_token_refresh()
        
        return self.generate_report()
    
    def generate_report(self) -> Dict:
        """Generate final test report"""
        print("\n" + "=" * 80)
        print("TEST REPORT")
        print("=" * 80)
        
        total_steps = len(self.test_results)
        passed_steps = sum(1 for r in self.test_results if "PASS" in r["status"])
        failed_steps = total_steps - passed_steps
        
        print(f"\nTotal Steps: {total_steps}")
        print(f"✅ Passed: {passed_steps}")
        print(f"❌ Failed: {failed_steps}")
        print(f"Success Rate: {(passed_steps/total_steps*100):.1f}%")
        
        if failed_steps > 0:
            print("\n❌ Failed Steps:")
            for result in self.test_results:
                if "FAIL" in result["status"]:
                    print(f"   - {result['step']}: {result['message']}")
        
        report = {
            "summary": {
                "total_steps": total_steps,
                "passed": passed_steps,
                "failed": failed_steps,
                "success_rate": round(passed_steps/total_steps*100, 1),
                "test_user": TEST_USER_EMAIL,
                "task_id": self.task_id
            },
            "results": self.test_results,
            "timestamp": datetime.now().isoformat()
        }
        
        # Save report
        report_file = f"e2e_test_report_{int(time.time())}.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_file}")
        
        return report


def main():
    """Main entry point"""
    journey = E2EUserJourney(BASE_URL)
    report = journey.run_complete_journey()
    
    # Exit code based on results
    if report["summary"]["failed"] == 0:
        print("\n✅ All tests passed!")
        return 0
    else:
        print(f"\n❌ {report['summary']['failed']} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())

