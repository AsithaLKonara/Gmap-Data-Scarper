# Test Automation Scripts

**QA Document**  
**Date:** 2025-01-17  
**Purpose:** Automated test execution and reporting scripts

---

## Quick Test Execution Scripts

### 1. Run All Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=backend --cov=frontend --cov-report=html --cov-report=term

# Run with verbose output
pytest -v

# Run and stop on first failure
pytest -x
```

### 2. Run by Category
```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# E2E tests only
pytest -m e2e

# Performance tests only
pytest -m performance
```

### 3. Run Specific Test Files
```bash
# API tests
pytest tests/test_comprehensive_api.py

# Phone extraction tests
pytest tests/extractors/test_phone_extractor.py

# Frontend tests
cd frontend && npm test
```

### 4. Run with Test Environment
```bash
# Set test environment
export TESTING=true
export DISABLE_RATE_LIMIT=true

# Run tests
pytest
```

---

## Test Execution Scripts

### run_tests.sh (Linux/Mac)
```bash
#!/bin/bash
# Run all tests with coverage and reporting

set -e

echo "🧪 Running test suite..."

# Set test environment
export TESTING=true
export DISABLE_RATE_LIMIT=true

# Run tests with coverage
pytest \
    --cov=backend \
    --cov=frontend \
    --cov-report=html \
    --cov-report=term-missing \
    --cov-report=xml \
    -v \
    --tb=short \
    --maxfail=5

# Generate coverage report
echo "📊 Coverage report generated in htmlcov/index.html"

# Check coverage threshold
coverage report --fail-under=60

echo "✅ Tests completed!"
```

### run_tests.ps1 (Windows)
```powershell
# Run all tests with coverage and reporting

$env:TESTING = "true"
$env:DISABLE_RATE_LIMIT = "true"

Write-Host "🧪 Running test suite..." -ForegroundColor Cyan

# Run tests
pytest `
    --cov=backend `
    --cov-report=html `
    --cov-report=term-missing `
    -v `
    --tb=short

Write-Host "✅ Tests completed!" -ForegroundColor Green
```

---

## Test Data Generation Scripts

### generate_test_data.py
```python
"""Generate test data for testing."""
import json
import csv
from datetime import datetime, timedelta
import random

def generate_leads(count=100):
    """Generate test leads."""
    leads = []
    platforms = ["google_maps", "facebook", "instagram", "linkedin"]
    cities = ["Toronto", "Vancouver", "Montreal", "Calgary"]
    
    for i in range(count):
        lead = {
            "Search Query": f"test query {i}",
            "Platform": random.choice(platforms),
            "Profile URL": f"https://example.com/profile/{i}",
            "Display Name": f"Test Business {i}",
            "Phone": f"+1{random.randint(2000000000, 9999999999)}",
            "Email": f"test{i}@example.com",
            "Location": random.choice(cities),
            "Category": "Restaurant",
            "Extracted At": (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat()
        }
        leads.append(lead)
    
    return leads

def save_to_csv(leads, filename="test_leads.csv"):
    """Save leads to CSV."""
    if not leads:
        return
    
    fieldnames = leads[0].keys()
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(leads)
    
    print(f"✅ Generated {len(leads)} leads in {filename}")

if __name__ == "__main__":
    leads = generate_leads(1000)
    save_to_csv(leads)
```

---

## Test Report Generation

### generate_test_report.py
```python
"""Generate test execution report."""
import json
import subprocess
from datetime import datetime
from pathlib import Path

def run_tests():
    """Run tests and capture output."""
    result = subprocess.run(
        ["pytest", "--json-report", "--json-report-file=test_report.json", "-v"],
        capture_output=True,
        text=True
    )
    return result.returncode == 0, result.stdout, result.stderr

def generate_html_report():
    """Generate HTML test report."""
    # Read JSON report
    with open("test_report.json", "r") as f:
        report = json.load(f)
    
    # Generate HTML
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .summary {{ background: #f0f0f0; padding: 20px; border-radius: 5px; }}
            .passed {{ color: green; }}
            .failed {{ color: red; }}
            .skipped {{ color: orange; }}
        </style>
    </head>
    <body>
        <h1>Test Execution Report</h1>
        <div class="summary">
            <h2>Summary</h2>
            <p>Total: {report['summary']['total']}</p>
            <p class="passed">Passed: {report['summary']['passed']}</p>
            <p class="failed">Failed: {report['summary']['failed']}</p>
            <p class="skipped">Skipped: {report['summary']['skipped']}</p>
            <p>Duration: {report['duration']:.2f}s</p>
        </div>
        <!-- Add detailed results -->
    </body>
    </html>
    """
    
    with open("test_report.html", "w") as f:
        f.write(html)
    
    print("✅ Test report generated: test_report.html")

if __name__ == "__main__":
    success, stdout, stderr = run_tests()
    if success:
        generate_html_report()
    else:
        print("❌ Tests failed")
        print(stderr)
```

---

## Continuous Integration Scripts

### .github/workflows/tests.yml
```yaml
name: Test Suite

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov pytest-json-report
    
    - name: Run tests
      env:
        TESTING: true
        DISABLE_RATE_LIMIT: true
      run: |
        pytest \
          --cov=backend \
          --cov-report=xml \
          --cov-report=html \
          --json-report \
          --json-report-file=test_report.json \
          -v
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
    
    - name: Upload test report
      uses: actions/upload-artifact@v3
      with:
        name: test-report
        path: test_report.json
    
    - name: Check coverage threshold
      run: |
        coverage report --fail-under=60
```

---

## Performance Test Scripts

### run_performance_tests.sh
```bash
#!/bin/bash
# Run performance tests

echo "🚀 Running performance tests..."

# Run Locust load tests
locust -f tests/performance/locustfile.py \
    --headless \
    --users 100 \
    --spawn-rate 10 \
    --run-time 5m \
    --html=performance_report.html

echo "✅ Performance tests completed!"
echo "📊 Report: performance_report.html"
```

---

## Security Test Scripts

### run_security_tests.sh
```bash
#!/bin/bash
# Run security tests

echo "🔒 Running security tests..."

# Run bandit (Python security linter)
bandit -r backend -f json -o security_report.json

# Run safety (dependency vulnerability checker)
safety check --json > safety_report.json

echo "✅ Security tests completed!"
```

---

## Test Maintenance Scripts

### cleanup_test_data.sh
```bash
#!/bin/bash
# Clean up test data

echo "🧹 Cleaning up test data..."

# Remove test CSV files
rm -f tests/data/*.csv

# Remove test screenshots
rm -f tests/screenshots/*.png

# Remove test databases
rm -f tests/*.db
rm -f tests/*.sqlite

# Remove coverage reports
rm -rf htmlcov/
rm -f .coverage
rm -f coverage.xml

echo "✅ Test data cleaned up!"
```

---

## Test Monitoring Scripts

### monitor_test_health.py
```python
"""Monitor test health and trends."""
import json
from pathlib import Path
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

def load_test_reports(days=7):
    """Load test reports from last N days."""
    reports = []
    base_path = Path("test_reports")
    
    for i in range(days):
        date = datetime.now() - timedelta(days=i)
        report_file = base_path / f"test_report_{date.strftime('%Y%m%d')}.json"
        if report_file.exists():
            with open(report_file) as f:
                reports.append(json.load(f))
    
    return reports

def analyze_trends(reports):
    """Analyze test trends."""
    dates = []
    pass_rates = []
    coverage = []
    
    for report in reports:
        dates.append(report['date'])
        total = report['summary']['total']
        passed = report['summary']['passed']
        pass_rates.append((passed / total) * 100 if total > 0 else 0)
        coverage.append(report.get('coverage', 0))
    
    return dates, pass_rates, coverage

def generate_trend_chart(dates, pass_rates, coverage):
    """Generate trend chart."""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    
    ax1.plot(dates, pass_rates, marker='o')
    ax1.set_title('Test Pass Rate Trend')
    ax1.set_ylabel('Pass Rate (%)')
    ax1.grid(True)
    
    ax2.plot(dates, coverage, marker='o', color='green')
    ax2.set_title('Code Coverage Trend')
    ax2.set_ylabel('Coverage (%)')
    ax2.grid(True)
    
    plt.tight_layout()
    plt.savefig('test_trends.png')
    print("✅ Trend chart generated: test_trends.png")

if __name__ == "__main__":
    reports = load_test_reports(7)
    if reports:
        dates, pass_rates, coverage = analyze_trends(reports)
        generate_trend_chart(dates, pass_rates, coverage)
```

---

## Quick Reference

### Common Test Commands
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=backend --cov-report=html

# Run specific test
pytest tests/test_comprehensive_api.py::TestScraperEndpoints::test_start_scraper_valid

# Run tests matching pattern
pytest -k "phone"

# Run with markers
pytest -m "not slow"

# Run in parallel (requires pytest-xdist)
pytest -n auto

# Show print statements
pytest -s

# Show local variables on failure
pytest -l
```

---

**Document Version:** 1.0  
**Last Updated:** 2025-01-17

