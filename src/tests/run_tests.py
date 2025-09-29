#!/usr/bin/env python3
"""
Test runner script for the Language App.

This script should be run from the tests directory (src/tests/).

Usage:
    cd src/tests
    python run_tests.py                    # Run all tests
    python run_tests.py models             # Run model tests only
    python run_tests.py processors         # Run processor tests only
    python run_tests.py pipeline           # Run pipeline tests only
    python run_tests.py utils              # Run utility tests only
    python run_tests.py --coverage         # Run with coverage report
    python run_tests.py --verbose          # Run with verbose output
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_tests(test_category=None, coverage=False, verbose=False):
    """Run tests with the specified options."""
    
    # Base command
    cmd = ["python", "-m", "pytest"]
    
    # Add test path
    if test_category:
        test_path = f"{test_category}/"
    else:
        test_path = "."
    
    cmd.append(test_path)
    
    # Add options
    if verbose:
        cmd.append("-v")
    
    if coverage:
        cmd.extend(["--cov=src", "--cov-report=html", "--cov-report=term"])
    
    # Run the command
    print(f"Running: {' '.join(cmd)}")
    print("-" * 50)
    
    try:
        result = subprocess.run(cmd, check=True)
        print("\n" + "=" * 50)
        print("✅ All tests passed!")
        if coverage:
            print("📊 Coverage report generated in htmlcov/index.html")
        return 0
    except subprocess.CalledProcessError as e:
        print("\n" + "=" * 50)
        print("❌ Tests failed!")
        return e.returncode


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run Language App tests")
    parser.add_argument(
        "category", 
        nargs="?", 
        choices=["models", "processors", "pipeline", "utils"],
        help="Test category to run (default: all)"
    )
    parser.add_argument(
        "--coverage", 
        action="store_true", 
        help="Run with coverage report"
    )
    parser.add_argument(
        "--verbose", "-v", 
        action="store_true", 
        help="Run with verbose output"
    )
    
    args = parser.parse_args()
    
    # Check if we're in the right directory
    if not Path(".").exists() or not Path("models").exists():
        print("❌ Error: Please run this script from the tests directory")
        return 1
    
    # Run tests
    return run_tests(args.category, args.coverage, args.verbose)


if __name__ == "__main__":
    sys.exit(main())
