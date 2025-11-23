#!/usr/bin/env python3
"""
Systematic test runner that handles missing dependencies gracefully.
Runs all available tests and generates a comprehensive report.
"""
import subprocess
import sys
import json
import os
from datetime import datetime
from pathlib import Path

class TestRunner:
    def __init__(self):
        self.results = {}
        self.start_time = datetime.now()
        self.report_file = Path("test_execution_report.json")
        
    def run_test_category(self, name, test_path, description=""):
        """Run a test category and return results."""
        print(f"\n{'='*80}")
        print(f"Testing: {name}")
        if description:
            print(f"Description: {description}")
        print(f"Path: {test_path}")
        print(f"{'='*80}\n")
        
        if not Path(test_path).exists():
            return {
                "status": "skipped",
                "reason": f"Test path not found: {test_path}",
                "tests_run": 0,
                "tests_passed": 0,
                "tests_failed": 0
            }
        
        # Increase timeout for CLI tests
        timeout_seconds = 1200 if "CLI" in name else 600  # 20 min for CLI, 10 min for others
        
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", test_path, "-v", "--tb=short"],
                capture_output=True,
                text=True,
                timeout=timeout_seconds
            )
            
            output = result.stdout + result.stderr
            
            # Parse test results
            tests_run = output.count("PASSED") + output.count("FAILED") + output.count("ERROR")
            tests_passed = output.count("PASSED")
            tests_failed = output.count("FAILED") + output.count("ERROR")
            
            return {
                "status": "passed" if result.returncode == 0 else "failed",
                "returncode": result.returncode,
                "tests_run": tests_run,
                "tests_passed": tests_passed,
                "tests_failed": tests_failed,
                "output": output[:5000]  # Limit output size
            }
        except subprocess.TimeoutExpired:
            return {
                "status": "timeout",
                "reason": "Test suite exceeded 10 minute timeout",
                "tests_run": 0,
                "tests_passed": 0,
                "tests_failed": 0
            }
        except Exception as e:
            return {
                "status": "error",
                "reason": str(e),
                "tests_run": 0,
                "tests_passed": 0,
                "tests_failed": 0
            }
    
    def run_all_tests(self):
        """Run all test categories systematically."""
        print("\n" + "="*80)
        print("LEAD INTELLIGENCE PLATFORM - SYSTEMATIC TEST EXECUTION")
        print("="*80)
        print(f"Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Test categories from checklist
        test_categories = [
            # Backend API Tests
            ("Backend API - New Endpoints", "tests/test_new_endpoints.py", "New API endpoints from Phases 4-6"),
            
            # Integration Tests
            ("Integration - WebSocket", "tests/integration/test_websocket.py", "WebSocket real-time communication"),
            ("Integration - PostgreSQL", "tests/integration/test_postgresql_storage.py", "Database operations"),
            ("Integration - File Operations", "tests/integration/test_file_operations.py", "File handling"),
            ("Integration - Push Notifications", "tests/integration/test_push_notifications.py", "Push notification system"),
            ("Integration - E2E", "tests/integration/test_e2e.py", "End-to-end integration tests"),
            ("Integration - Orchestrator", "tests/integration/test_orchestrator.py", "Orchestrator service"),
            
            # Platform Scraper Tests
            ("Scraper - Google Maps", "tests/platform/test_google_maps_scraper.py", "Google Maps scraper"),
            ("Scraper - Facebook", "tests/platform/test_facebook_scraper.py", "Facebook scraper"),
            ("Scraper - Instagram", "tests/platform/test_instagram_scraper.py", "Instagram scraper"),
            ("Scraper - LinkedIn", "tests/platform/test_linkedin_scraper.py", "LinkedIn scraper"),
            ("Scraper - X/Twitter", "tests/platform/test_x_twitter_scraper.py", "X/Twitter scraper"),
            ("Scraper - YouTube", "tests/platform/test_youtube_scraper.py", "YouTube scraper"),
            ("Scraper - TikTok", "tests/platform/test_tiktok_scraper.py", "TikTok scraper"),
            
            # Phone Extraction Tests
            ("Phone - Extraction", "tests/phone/test_extraction.py", "Phone number extraction"),
            ("Phone - Normalizer", "tests/normalize/test_phone_normalizer.py", "Phone number normalization"),
            ("Phone - Extractor", "tests/extractors/test_phone_extractor.py", "Phone extractor utilities"),
            ("Phone - OCR", "tests/ocr/test_image_phone_ocr.py", "OCR phone extraction"),
            
            # Intelligence & AI Tests
            ("Intelligence - Lead Scorer", "tests/intelligence/test_lead_scorer.py", "AI lead scoring"),
            ("Classification - Business", "tests/classification/test_business_classifier.py", "Business classification"),
            ("Classification - Job", "tests/classification/test_job_classifier.py", "Job classification"),
            ("Enrichment - Activity", "tests/enrichment/test_activity_scraper.py", "Activity enrichment"),
            
            # Unit Tests
            ("Unit - Base Scraper", "tests/unit/test_base_scraper.py", "Base scraper functionality"),
            ("Unit - Config", "tests/unit/test_config.py", "Configuration management"),
            ("Unit - CSV Writer", "tests/unit/test_csv_writer.py", "CSV export functionality"),
            ("Unit - Site Search", "tests/unit/test_site_search.py", "Site search functionality"),
            
            # Error Handling
            ("Error Handling - Network", "tests/error_handling/test_network_errors.py", "Network error handling"),
            
            # Data Validation
            ("Data Validation - Results", "tests/data_validation/test_result_validation.py", "Result data validation"),
            
            # E2E Tests
            ("E2E - Scraping Flow", "tests/e2e/test_scraping_flow.py", "Complete scraping workflow"),
            ("E2E - WebSocket Stability", "tests/e2e/test_websocket_stability.py", "WebSocket stability"),
            ("E2E - Concurrency", "tests/e2e/test_concurrency.py", "Concurrent operations"),
            ("E2E - Data Volume", "tests/e2e/test_data_volume.py", "Large data handling"),
            ("E2E - Deployment", "tests/e2e/test_deployment.py", "Deployment scenarios"),
            
            # Performance Tests
            ("Performance - Benchmarks", "tests/performance/test_benchmarks.py", "Performance benchmarks"),
            
            # Backend WebSocket
            ("Backend - WebSocket", "tests/backend/test_websocket.py", "Backend WebSocket implementation"),
            
            # CLI Tests
            ("CLI - Main", "tests/cli/test_main_cli.py", "Command-line interface"),
        ]
        
        total_tests = 0
        total_passed = 0
        total_failed = 0
        categories_passed = 0
        categories_failed = 0
        
        for name, path, description in test_categories:
            result = self.run_test_category(name, path, description)
            self.results[name] = result
            
            total_tests += result.get("tests_run", 0)
            total_passed += result.get("tests_passed", 0)
            total_failed += result.get("tests_failed", 0)
            
            if result.get("status") == "passed":
                categories_passed += 1
            elif result.get("status") in ["failed", "error", "timeout"]:
                categories_failed += 1
        
        # Generate summary
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        summary = {
            "start_time": self.start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_seconds": duration,
            "total_categories": len(test_categories),
            "categories_passed": categories_passed,
            "categories_failed": categories_failed,
            "categories_skipped": len(test_categories) - categories_passed - categories_failed,
            "total_tests": total_tests,
            "tests_passed": total_passed,
            "tests_failed": total_failed,
            "pass_rate": (total_passed / total_tests * 100) if total_tests > 0 else 0,
            "results": self.results
        }
        
        self.save_report(summary)
        self.print_summary(summary)
        
        return summary
    
    def save_report(self, summary):
        """Save test report to JSON file."""
        with open(self.report_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        print(f"\n✓ Detailed report saved to {self.report_file}")
    
    def print_summary(self, summary):
        """Print test execution summary."""
        print("\n" + "="*80)
        print("TEST EXECUTION SUMMARY")
        print("="*80)
        print(f"Duration: {summary['duration_seconds']:.2f} seconds ({summary['duration_seconds']/60:.2f} minutes)")
        print(f"\nCategories:")
        print(f"  Total: {summary['total_categories']}")
        print(f"  Passed: {summary['categories_passed']} ✓")
        print(f"  Failed: {summary['categories_failed']} ✗")
        print(f"  Skipped: {summary['categories_skipped']} ⊘")
        print(f"\nTests:")
        print(f"  Total: {summary['total_tests']}")
        print(f"  Passed: {summary['tests_passed']} ✓")
        print(f"  Failed: {summary['tests_failed']} ✗")
        print(f"  Pass Rate: {summary['pass_rate']:.1f}%")
        print("\n" + "="*80)
        print("\nCategory Details:")
        print("-" * 80)
        
        for name, result in summary['results'].items():
            status_icon = {
                "passed": "✓",
                "failed": "✗",
                "error": "⚠",
                "timeout": "⏱",
                "skipped": "⊘"
            }.get(result.get("status", "unknown"), "?")
            
            status = result.get("status", "unknown").upper()
            tests_run = result.get("tests_run", 0)
            tests_passed = result.get("tests_passed", 0)
            tests_failed = result.get("tests_failed", 0)
            
            print(f"{status_icon} {name}")
            print(f"   Status: {status}")
            if tests_run > 0:
                print(f"   Tests: {tests_passed} passed, {tests_failed} failed (total: {tests_run})")
            if result.get("reason"):
                print(f"   Reason: {result['reason']}")
            print()
        
        print("="*80)
        
        # Exit code
        if summary['categories_failed'] > 0 or summary['tests_failed'] > 0:
            print("\n⚠️  Some tests failed. Review the detailed report above.")
            sys.exit(1)
        else:
            print("\n✓ All tests passed!")
            sys.exit(0)

if __name__ == "__main__":
    runner = TestRunner()
    runner.run_all_tests()

