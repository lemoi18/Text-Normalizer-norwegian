#!/usr/bin/env python3
"""
Simple test runner for the Norwegian text normalizer project.
This script runs all unit tests for the grammar modules.
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_tests():
    """Run all tests and return the result."""
    try:
        # Import and run the test modules directly
        import subprocess

        test_files = [
            "tests/test_norwegian_normalizer.py",
            "tests/test_out_of_distribution.py",
            "tests/test_enhanced_ood.py"
        ]

        total_exit_code = 0

        for test_file in test_files:
            print(f"\nRunning {os.path.basename(test_file)}...")
            print("-" * 40)

            result = subprocess.run([sys.executable, test_file],
                                  capture_output=True, text=True, cwd=os.path.dirname(__file__))
            print(result.stdout)
            if result.stderr:
                print("Errors:", result.stderr)

            if result.returncode != 0:
                total_exit_code = result.returncode

        return total_exit_code
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1

if __name__ == '__main__':
    print("Running Norwegian Text Normalizer Tests...")
    print("=" * 50)
    exit_code = run_tests()

    if exit_code == 0:
        print("\n" + "=" * 50)
        print("All tests passed successfully!")
    else:
        print("\n" + "=" * 50)
        print("Some tests failed.")

    sys.exit(exit_code)