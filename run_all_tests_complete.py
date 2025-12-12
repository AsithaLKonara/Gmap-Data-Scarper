"""
Master Test Runner - Runs all test suites
Includes: pytest tests, E2E user journey, QA comprehensive tests
"""
import subprocess
import sys
import os
import time
from datetime import datetime
from pathlib import Path

def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 80)
    print(text)
    print("=" * 80)

def check_server_running(base_url="http://localhost:8000"):
    """Check if backend server is running"""
    try:
        import requests
        response = requests.get(f"{base_url}/api/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def run_pytest_tests():
    """Run pytest test suite"""
    print_header("RUNNING PYTEST TEST SUITE")
    
    try:
        result = subprocess.run(
            ["pytest", "tests/", "-v", "--tb=short", "--maxfail=10"],
            capture_output=False,
            text=True
        )
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running pytest: {str(e)}")
        return False

def run_e2e_user_journey():
    """Run E2E user journey test"""
    print_header("RUNNING E2E USER JOURNEY TEST")
    
    if not check_server_running():
        print("⚠️  Backend server not running. Skipping E2E test.")
        print("   Start server with: python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000")
        return None
    
    try:
        result = subprocess.run(
            [sys.executable, "test_e2e_user_journey.py"],
            capture_output=False,
            text=True
        )
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running E2E test: {str(e)}")
        return False

def run_qa_comprehensive():
    """Run QA comprehensive test"""
    print_header("RUNNING QA COMPREHENSIVE TEST")
    
    if not check_server_running():
        print("⚠️  Backend server not running. Skipping QA test.")
        print("   Start server with: python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000")
        return None
    
    try:
        result = subprocess.run(
            [sys.executable, "test_qa_comprehensive.py"],
            capture_output=False,
            text=True
        )
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running QA test: {str(e)}")
        return False

def main():
    """Run all test suites"""
    start_time = datetime.now()
    
    print_header("COMPREHENSIVE TEST SUITE - ALL TESTS")
    print(f"Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nThis will run:")
    print("  1. Pytest test suite (unit, integration, platform tests)")
    print("  2. E2E user journey test (requires server)")
    print("  3. QA comprehensive test (requires server)")
    
    results = {}
    
    # 1. Run pytest tests
    print("\n" + "=" * 80)
    print("PHASE 1: PYTEST TEST SUITE")
    print("=" * 80)
    pytest_passed = run_pytest_tests()
    results["pytest"] = pytest_passed
    print(f"\n✅ Pytest tests: {'PASSED' if pytest_passed else 'FAILED'}")
    
    # 2. Run E2E user journey
    print("\n" + "=" * 80)
    print("PHASE 2: E2E USER JOURNEY TEST")
    print("=" * 80)
    e2e_result = run_e2e_user_journey()
    results["e2e"] = e2e_result
    if e2e_result is not None:
        print(f"\n✅ E2E test: {'PASSED' if e2e_result else 'FAILED'}")
    else:
        print(f"\n⚠️  E2E test: SKIPPED (server not running)")
    
    # 3. Run QA comprehensive
    print("\n" + "=" * 80)
    print("PHASE 3: QA COMPREHENSIVE TEST")
    print("=" * 80)
    qa_result = run_qa_comprehensive()
    results["qa"] = qa_result
    if qa_result is not None:
        print(f"\n✅ QA test: {'PASSED' if qa_result else 'FAILED'}")
    else:
        print(f"\n⚠️  QA test: SKIPPED (server not running)")
    
    # Summary
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print_header("TEST SUMMARY")
    print(f"Duration: {duration:.2f} seconds")
    print(f"Start: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"End: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nResults:")
    print(f"  Pytest: {'✅ PASSED' if results['pytest'] else '❌ FAILED'}")
    
    if results['e2e'] is not None:
        print(f"  E2E: {'✅ PASSED' if results['e2e'] else '❌ FAILED'}")
    else:
        print(f"  E2E: ⚠️  SKIPPED (server not running)")
    
    if results['qa'] is not None:
        print(f"  QA: {'✅ PASSED' if results['qa'] else '❌ FAILED'}")
    else:
        print(f"  QA: ⚠️  SKIPPED (server not running)")
    
    # Determine overall status
    all_passed = results['pytest']
    if results['e2e'] is not None:
        all_passed = all_passed and results['e2e']
    if results['qa'] is not None:
        all_passed = all_passed and results['qa']
    
    print("\n" + "=" * 80)
    if all_passed:
        print("✅ ALL TESTS PASSED!")
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())

