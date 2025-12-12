"""
Local Test Runner - Runs all tests locally with automatic server management
Starts backend server automatically for WebSocket and E2E tests
"""
import subprocess
import sys
import os
import time
import requests
import signal
from pathlib import Path
from typing import Optional

# Test configuration
BASE_URL = "http://localhost:8000"
HEALTH_URL = f"{BASE_URL}/api/health"
SERVER_START_TIMEOUT = 30
SERVER_STOP_TIMEOUT = 10

class LocalTestRunner:
    """Runs all tests locally with automatic server management"""
    
    def __init__(self):
        self.server_process: Optional[subprocess.Popen] = None
        self.server_started = False
    
    def start_server(self) -> bool:
        """Start backend server for tests"""
        if self.server_started:
            return True
        
        print("=" * 80)
        print("STARTING BACKEND SERVER FOR TESTS")
        print("=" * 80)
        
        try:
            # Start uvicorn server
            self.server_process = subprocess.Popen(
                [
                    sys.executable, "-m", "uvicorn",
                    "backend.main:app",
                    "--host", "0.0.0.0",
                    "--port", "8000",
                    "--log-level", "warning"
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env={**os.environ, "TESTING": "true"},
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0
            )
            
            # Wait for server to be ready
            print("Waiting for server to start...")
            elapsed = 0
            wait_interval = 0.5
            
            while elapsed < SERVER_START_TIMEOUT:
                try:
                    response = requests.get(HEALTH_URL, timeout=2)
                    if response.status_code == 200:
                        print(f"✅ Server started successfully at {BASE_URL}")
                        self.server_started = True
                        return True
                except (requests.exceptions.RequestException, ConnectionError):
                    pass
                
                # Check if process died
                if self.server_process.poll() is not None:
                    stdout, stderr = self.server_process.communicate()
                    print(f"❌ Server process died")
                    print(f"STDOUT: {stdout.decode() if stdout else 'None'}")
                    print(f"STDERR: {stderr.decode() if stderr else 'None'}")
                    return False
                
                time.sleep(wait_interval)
                elapsed += wait_interval
                if elapsed % 5 == 0:
                    print(f"   Still waiting... ({elapsed:.0f}s)")
            
            print(f"❌ Server failed to start within {SERVER_START_TIMEOUT} seconds")
            return False
            
        except Exception as e:
            print(f"❌ Error starting server: {str(e)}")
            return False
    
    def stop_server(self):
        """Stop backend server"""
        if not self.server_process:
            return
        
        print("\n" + "=" * 80)
        print("STOPPING BACKEND SERVER")
        print("=" * 80)
        
        try:
            if sys.platform == "win32":
                # Windows: Use taskkill
                subprocess.run(
                    ["taskkill", "/F", "/T", "/PID", str(self.server_process.pid)],
                    capture_output=True,
                    timeout=SERVER_STOP_TIMEOUT
                )
            else:
                # Unix: Send SIGTERM
                self.server_process.terminate()
                try:
                    self.server_process.wait(timeout=SERVER_STOP_TIMEOUT)
                except subprocess.TimeoutExpired:
                    self.server_process.kill()
            
            print("✅ Server stopped")
        except Exception as e:
            print(f"⚠️  Error stopping server: {str(e)}")
        finally:
            self.server_process = None
            self.server_started = False
    
    def check_server_running(self) -> bool:
        """Check if server is already running"""
        try:
            response = requests.get(HEALTH_URL, timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def run_pytest_tests(self, start_server: bool = True) -> int:
        """Run pytest test suite"""
        print("\n" + "=" * 80)
        print("RUNNING PYTEST TEST SUITE")
        print("=" * 80)
        
        # Set environment variable for tests
        env = os.environ.copy()
        env["API_URL"] = BASE_URL
        env["TESTING"] = "true"
        
        # Check if server is needed
        if start_server:
            # Check if server already running
            if not self.check_server_running():
                if not self.start_server():
                    print("⚠️  Server not started, some tests may fail")
            else:
                print(f"✅ Server already running at {BASE_URL}")
                self.server_started = True
        
        try:
            # Run pytest
            result = subprocess.run(
                ["pytest", "tests/", "-v", "--tb=short", "--maxfail=10"],
                env=env,
                cwd=Path.cwd()
            )
            return result.returncode
        except Exception as e:
            print(f"❌ Error running pytest: {str(e)}")
            return 1
    
    def run_e2e_test(self) -> int:
        """Run E2E user journey test"""
        print("\n" + "=" * 80)
        print("RUNNING E2E USER JOURNEY TEST")
        print("=" * 80)
        
        # Ensure server is running
        if not self.check_server_running():
            if not self.start_server():
                print("❌ Cannot run E2E test without server")
                return 1
        
        # Set environment
        env = os.environ.copy()
        env["API_URL"] = BASE_URL
        
        try:
            result = subprocess.run(
                [sys.executable, "test_e2e_user_journey.py"],
                env=env,
                cwd=Path.cwd()
            )
            return result.returncode
        except Exception as e:
            print(f"❌ Error running E2E test: {str(e)}")
            return 1
    
    def run_qa_test(self) -> int:
        """Run QA comprehensive test"""
        print("\n" + "=" * 80)
        print("RUNNING QA COMPREHENSIVE TEST")
        print("=" * 80)
        
        # Ensure server is running
        if not self.check_server_running():
            if not self.start_server():
                print("❌ Cannot run QA test without server")
                return 1
        
        # Set environment
        env = os.environ.copy()
        env["API_URL"] = BASE_URL
        
        try:
            result = subprocess.run(
                [sys.executable, "test_qa_comprehensive.py"],
                env=env,
                cwd=Path.cwd()
            )
            return result.returncode
        except Exception as e:
            print(f"❌ Error running QA test: {str(e)}")
            return 1
    
    def run_all_tests(self, include_e2e: bool = True, include_qa: bool = True) -> int:
        """Run all tests"""
        start_time = time.time()
        
        print("=" * 80)
        print("LOCAL TEST RUNNER - ALL TESTS")
        print("=" * 80)
        print("This will:")
        print("  1. Start backend server automatically")
        print("  2. Run all pytest tests")
        if include_e2e:
            print("  3. Run E2E user journey test")
        if include_qa:
            print("  4. Run QA comprehensive test")
        print("  5. Stop server automatically")
        print("=" * 80)
        
        results = {}
        exit_code = 0
        
        try:
            # 1. Run pytest tests
            pytest_result = self.run_pytest_tests(start_server=True)
            results["pytest"] = pytest_result
            if pytest_result != 0:
                exit_code = 1
            
            # 2. Run E2E test
            if include_e2e:
                e2e_result = self.run_e2e_test()
                results["e2e"] = e2e_result
                if e2e_result != 0:
                    exit_code = 1
            
            # 3. Run QA test
            if include_qa:
                qa_result = self.run_qa_test()
                results["qa"] = qa_result
                if qa_result != 0:
                    exit_code = 1
            
        finally:
            # Always stop server
            self.stop_server()
        
        # Summary
        duration = time.time() - start_time
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print(f"Duration: {duration:.2f} seconds")
        print(f"Pytest: {'✅ PASSED' if results.get('pytest') == 0 else '❌ FAILED'}")
        if include_e2e:
            print(f"E2E: {'✅ PASSED' if results.get('e2e') == 0 else '❌ FAILED'}")
        if include_qa:
            print(f"QA: {'✅ PASSED' if results.get('qa') == 0 else '❌ FAILED'}")
        print("=" * 80)
        
        return exit_code


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run all tests locally with automatic server management")
    parser.add_argument("--no-e2e", action="store_true", help="Skip E2E user journey test")
    parser.add_argument("--no-qa", action="store_true", help="Skip QA comprehensive test")
    parser.add_argument("--pytest-only", action="store_true", help="Run only pytest tests")
    parser.add_argument("--e2e-only", action="store_true", help="Run only E2E test")
    parser.add_argument("--qa-only", action="store_true", help="Run only QA test")
    
    args = parser.parse_args()
    
    runner = LocalTestRunner()
    
    try:
        if args.pytest_only:
            exit_code = runner.run_pytest_tests(start_server=True)
        elif args.e2e_only:
            exit_code = runner.run_e2e_test()
        elif args.qa_only:
            exit_code = runner.run_qa_test()
        else:
            exit_code = runner.run_all_tests(
                include_e2e=not args.no_e2e,
                include_qa=not args.no_qa
            )
        
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        runner.stop_server()
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {str(e)}")
        runner.stop_server()
        sys.exit(1)


if __name__ == "__main__":
    main()

