#!/usr/bin/env python3
"""
Test runner script for Atelier Cauchemar bot.
Runs all test suites and generates reports.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_tests():
    """Run all test suites."""
    print("🚀 Running Atelier Cauchemar Test Suite")
    print("=" * 50)

    # Ensure we're in the project root
    project_root = Path(__file__).parent
    os.chdir(project_root)

    # Run pytest with coverage
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "-v",
        "--tb=short",
        "--cov=atelier_bot",
        "--cov-report=term-missing",
        "--cov-report=html:htmlcov",
        "--cov-fail-under=25"
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)

        print("STDOUT:")
        print(result.stdout)

        if result.stderr:
            print("STDERR:")
            print(result.stderr)

        print(f"\nReturn code: {result.returncode}")

        if result.returncode == 0:
            print("✅ All tests passed!")
        else:
            print("❌ Some tests failed!")
            return False

    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

    return True


def run_health_check():
    """Run basic health checks."""
    print("\n🏥 Running Health Checks")
    print("=" * 30)

    # Check if database can be initialized
    try:
        from atelier_bot.db.db import init_db
        import asyncio

        async def check_db():
            await init_db()
            print("✅ Database initialization: OK")

        asyncio.run(check_db())
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

    # Check imports
    try:
        import atelier_bot.main  # noqa: F401
        import atelier_bot.handlers.print_handler  # noqa: F401
        import atelier_bot.services.notify  # noqa: F401
        import atelier_bot.keyboards.print_keyboards  # noqa: F401
        print("✅ All imports: OK")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

    print("✅ Health checks passed!")
    return True


if __name__ == "__main__":
    success = True

    # Run health checks first
    if not run_health_check():
        success = False

    # Run tests
    if not run_tests():
        success = False

    if success:
        print("\n🎉 All checks passed! Ready for deployment.")
        sys.exit(0)
    else:
        print("\n💥 Some checks failed. Please fix issues before deployment.")
        sys.exit(1)
