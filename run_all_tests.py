#!/usr/bin/env python3
"""
Comprehensive test runner for Lead Intelligence Platform.
Runs all tests and generates a detailed report.
"""
import subprocess
import sys
import json
import os
from datetime import datetime
from pathlib import Path

# Test categories from checklist
TEST_CATEGORIES = {
    "Frontend": {
        "unit": "frontend/__tests__",
        "e2e": "frontend/e2e",
        "description": "Frontend component and E2E tests"
    },
    "Backend API": {
        "unit": "tests/backend",
        "integration": "tests/integration",
        "description": "Backend API endpoint tests"
    },
    "Scrapers": {
        "unit": "tests/platform",
        "description": "Platform scraper tests"
    },
    "Phone Extraction": {
        "unit": "tests/phone",
        "description": "Phone number extraction tests"
    },
    "AI/ML Features": {
        "unit": "tests/intelligence",
        "description": "AI lead scoring and enrichment tests"
    },
    "Database": {
        "integration": "tests/integration/test_postgresql_storage.py",
        "description": "Database operations tests"
    },
    "WebSocket": {
        "integration": "tests/integration/test_websocket.py",
        "backend": "tests/backend/test_websocket.py",
        "description": "WebSocket real-time communication tests"
    },
    "Error Handling": {
        "unit": "tests/error_handling",
        "description": "Error handling and edge cases"
    },
    "Data Validation": {
        "unit": "tests/data_validation",
        "description": "Data validation tests"
    },
    "Performance": {
        "performance": "tests/performance",
        "description": "Performance and load tests"
    },
    "E2E": {
        "e2e": "tests/e2e",
        "description": "End-to-end workflow tests"
    },
    "New Endpoints": {
        "integration": "tests/test_new_endpoints.py",
        "description": "New API endpoints (Phases 4-6)"
    }
}

class TestRunner:
    def __init__(self):
        self.results = {}
        self.start_time = datetime.now()
        self.report_file = Path("test_results.json")
        self.html_report = Path("test_report.html")
        
    def run_pytest(self, test_path, category, test_type):
        """Run pytest for a specific test path."""
        print(f"\n{'='*80}")
        print(f"Running {category} - {test_type} tests: {test_path}")
        print(f"{'='*80}\n")
        
        cmd = [
            "pytest",
            test_path,
            "-v",
            "--tb=short",
            "--json-report",
            "--json-report-file=test_results_temp.json"
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout per test suite
            )
            
            # Parse results
            passed = result.returncode == 0
            output = result.stdout + result.stderr
            
            # Try to parse JSON report if it exists
            json_data = {}
            temp_json = Path("test_results_temp.json")
            if temp_json.exists():
                try:
                    with open(temp_json, 'r') as f:
                        json_data = json.load(f)
                    temp_json.unlink()
                except:
                    pass
            
            # Count tests from output
            test_count = output.count("PASSED") + output.count("FAILED") + output.count("ERROR")
            
            return {
                "passed": passed,
                "returncode": result.returncode,
                "output": output,
                "test_count": test_count,
                "json_data": json_data
            }
        except subprocess.TimeoutExpired:
            return {
                "passed": False,
                "returncode": -1,
                "output": "Test suite timed out after 5 minutes",
                "test_count": 0,
                "json_data": {}
            }
        except Exception as e:
            return {
                "passed": False,
                "returncode": -1,
                "output": f"Error running tests: {str(e)}",
                "test_count": 0,
                "json_data": {}
            }
    
    def run_npm_tests(self, category):
        """Run frontend npm tests."""
        print(f"\n{'='*80}")
        print(f"Running {category} - Frontend tests")
        print(f"{'='*80}\n")
        
        # Change to frontend directory
        original_dir = os.getcwd()
        frontend_dir = Path("frontend")
        
        if not frontend_dir.exists():
            return {
                "passed": False,
                "output": "Frontend directory not found",
                "test_count": 0
            }
        
        try:
            os.chdir(frontend_dir)
            
            # Check if node_modules exists
            if not Path("node_modules").exists():
                print("Installing dependencies...")
                subprocess.run(["npm", "install"], check=True, capture_output=True)
            
            # Run tests
            result = subprocess.run(
                ["npm", "test", "--", "--watchAll=false", "--coverage=false"],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            test_count = result.stdout.count("PASS") + result.stdout.count("FAIL")
            
            return {
                "passed": result.returncode == 0,
                "returncode": result.returncode,
                "output": result.stdout + result.stderr,
                "test_count": test_count
            }
        except subprocess.TimeoutExpired:
            return {
                "passed": False,
                "output": "Frontend tests timed out",
                "test_count": 0
            }
        except Exception as e:
            return {
                "passed": False,
                "output": f"Error: {str(e)}",
                "test_count": 0
            }
        finally:
            os.chdir(original_dir)
    
    def run_all_tests(self):
        """Run all test categories."""
        print("\n" + "="*80)
        print("LEAD INTELLIGENCE PLATFORM - COMPREHENSIVE TEST SUITE")
        print("="*80)
        print(f"Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        total_tests = 0
        total_passed = 0
        total_failed = 0
        
        # Run backend tests
        for category, config in TEST_CATEGORIES.items():
            if category == "Frontend":
                # Handle frontend separately
                result = self.run_npm_tests(category)
                self.results[category] = {
                    "type": "frontend",
                    "result": result,
                    "description": config.get("description", "")
                }
                if result.get("passed"):
                    total_passed += 1
                else:
                    total_failed += 1
                total_tests += result.get("test_count", 0)
                continue
            
            category_results = {}
            
            # Run unit tests
            if "unit" in config:
                result = self.run_pytest(config["unit"], category, "unit")
                category_results["unit"] = result
                total_tests += result.get("test_count", 0)
            
            # Run integration tests
            if "integration" in config:
                result = self.run_pytest(config["integration"], category, "integration")
                category_results["integration"] = result
                total_tests += result.get("test_count", 0)
            
            # Run other test types
            for test_type in ["backend", "performance", "e2e"]:
                if test_type in config:
                    result = self.run_pytest(config[test_type], category, test_type)
                    category_results[test_type] = result
                    total_tests += result.get("test_count", 0)
            
            # Determine overall category status
            all_passed = all(
                r.get("passed", False) 
                for r in category_results.values()
            )
            
            if all_passed:
                total_passed += 1
            else:
                total_failed += 1
            
            self.results[category] = {
                "type": "backend",
                "results": category_results,
                "description": config.get("description", ""),
                "overall_passed": all_passed
            }
        
        # Calculate summary
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        summary = {
            "start_time": self.start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_seconds": duration,
            "total_categories": len(TEST_CATEGORIES),
            "categories_passed": total_passed,
            "categories_failed": total_failed,
            "total_tests": total_tests,
            "results": self.results
        }
        
        # Save results
        self.save_results(summary)
        self.print_summary(summary)
        
        return summary
    
    def save_results(self, summary):
        """Save test results to JSON file."""
        with open(self.report_file, 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"\n✓ Results saved to {self.report_file}")
    
    def print_summary(self, summary):
        """Print test summary."""
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        print(f"Duration: {summary['duration_seconds']:.2f} seconds")
        print(f"Total Categories: {summary['total_categories']}")
        print(f"Categories Passed: {summary['categories_passed']}")
        print(f"Categories Failed: {summary['categories_failed']}")
        print(f"Total Tests: {summary['total_tests']}")
        print("\nCategory Results:")
        print("-" * 80)
        
        for category, data in summary['results'].items():
            status = "✓ PASS" if data.get('overall_passed', False) or data.get('result', {}).get('passed', False) else "✗ FAIL"
            print(f"{status} - {category}")
            
            # Print sub-results if available
            if 'results' in data:
                for test_type, result in data['results'].items():
                    sub_status = "✓" if result.get('passed', False) else "✗"
                    print(f"  {sub_status} {test_type}: {result.get('test_count', 0)} tests")
        
        print("="*80)
        
        # Exit with appropriate code
        if summary['categories_failed'] > 0:
            print("\n⚠️  Some test categories failed. Check detailed results above.")
            sys.exit(1)
        else:
            print("\n✓ All test categories passed!")
            sys.exit(0)

if __name__ == "__main__":
    runner = TestRunner()
    runner.run_all_tests()

