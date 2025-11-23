#!/usr/bin/env python3
"""Simple test runner script."""
import sys
import subprocess

def main():
    """Run pytest with appropriate options."""
    args = sys.argv[1:] if len(sys.argv) > 1 else []
    
    # Default: run all tests with coverage
    if not args:
        args = ["-v", "--cov=scrapers", "--cov=utils", "--cov=orchestrator_core", "--cov-report=term-missing"]
    
    cmd = ["pytest"] + args
    
    print("Running tests...")
    print(f"Command: {' '.join(cmd)}")
    print("-" * 80)
    
    result = subprocess.run(cmd)
    sys.exit(result.returncode)

if __name__ == "__main__":
    main()

