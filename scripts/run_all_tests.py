"""
Test Runner

Discovers and executes all test scripts under the `scripts/` directory as Python modules.
Provides a comprehensive summary of passed/failed tests and exits with code 0 on success.
"""

import subprocess
import sys
import time
from pathlib import Path


def main() -> None:
    scripts_dir = Path(__file__).resolve().parent
    test_files = sorted(scripts_dir.glob("test_*.py"))

    if not test_files:
        print("No test files found in scripts/ directory.")
        sys.exit(1)

    print(f"Discovered {len(test_files)} test suite(s). Starting execution...\n")
    print(f"{'Test Module':<45} | {'Status':<8} | {'Duration':<8}")
    print("-" * 67)

    passed_count = 0
    failed_tests = []
    start_total_time = time.time()

    for test_file in test_files:
        module_name = f"scripts.{test_file.stem}"
        start_time = time.time()

        result = subprocess.run(
            [sys.executable, "-m", module_name],
            capture_output=True,
            text=True,
        )
        duration = time.time() - start_time

        if result.returncode == 0:
            passed_count += 1
            print(f"{module_name:<45} | \033[92mPASSED\033[0m   | {duration:6.2f}s")
        else:
            failed_tests.append((module_name, result.stdout, result.stderr))
            print(f"{module_name:<45} | \033[91mFAILED\033[0m   | {duration:6.2f}s")

    total_duration = time.time() - start_total_time

    print("\n" + "=" * 67)
    print(f"Summary: {passed_count}/{len(test_files)} passed in {total_duration:.2f}s")
    print("=" * 67)

    if failed_tests:
        print("\nFailures Detail:")
        for name, stdout, stderr in failed_tests:
            print(f"\n--- {name} ---")
            if stdout:
                print(f"STDOUT:\n{stdout}")
            if stderr:
                print(f"STDERR:\n{stderr}")
        sys.exit(1)
    else:
        print("\nAll test suites passed successfully.")
        sys.exit(0)


if __name__ == "__main__":
    main()
