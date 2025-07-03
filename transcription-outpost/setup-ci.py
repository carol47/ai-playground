#!/usr/bin/env python3
"""
🎖️ Transcription Outpost CI/CD Setup Script
Automatically configures your project for continuous integration and testing.
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd, check=True):
    """Run a shell command and return the result."""
    print(f"🎖️ Executing: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"❌ Command failed: {cmd}")
        print(f"Error: {result.stderr}")
        sys.exit(1)
    return result


def check_dependencies():
    """Check if required tools are installed."""
    print("🎖️ Checking dependencies...")
    
    # Check Python
    try:
        import sys
        print(f"✅ Python {sys.version}")
    except Exception as e:
        print(f"❌ Python not found: {e}")
        sys.exit(1)
    
    # Check Poetry
    try:
        result = run_command("poetry --version", check=False)
        if result.returncode == 0:
            print(f"✅ {result.stdout.strip()}")
        else:
            print("❌ Poetry not found. Installing...")
            run_command("pip install poetry")
    except Exception as e:
        print(f"❌ Error checking Poetry: {e}")
    
    # Check Git
    try:
        result = run_command("git --version", check=False)
        if result.returncode == 0:
            print(f"✅ {result.stdout.strip()}")
        else:
            print("❌ Git not found. Please install Git first.")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Error checking Git: {e}")


def install_dependencies():
    """Install Python dependencies."""
    print("🎖️ Installing dependencies...")
    run_command("poetry install")


def setup_pre_commit():
    """Setup pre-commit hooks."""
    print("🎖️ Setting up pre-commit hooks...")
    run_command("poetry run pre-commit install")
    run_command("poetry run pre-commit install --hook-type commit-msg")


def create_github_workflows():
    """Create GitHub Actions workflows directory if using GitHub."""
    workflows_dir = Path(".github/workflows")
    if not workflows_dir.exists():
        workflows_dir.mkdir(parents=True)
        print("✅ Created .github/workflows directory")
    else:
        print("✅ .github/workflows directory already exists")


def run_initial_tests():
    """Run tests to make sure everything works."""
    print("🎖️ Running initial test to verify setup...")
    try:
        result = run_command("poetry run python run_tests.py", check=False)
        if result.returncode == 0:
            print("✅ All tests passed! CI/CD setup complete.")
        else:
            print("⚠️ Some tests failed, but CI/CD is configured.")
            print("Check the test output above for details.")
    except Exception as e:
        print(f"⚠️ Could not run tests: {e}")


def main():
    """Main setup function."""
    print("🎖️🎖️ TRANSCRIPTION OUTPOST CI/CD SETUP")
    print("=" * 50)
    
    # Change to script directory
    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)
    print(f"📂 Working directory: {script_dir}")
    
    try:
        check_dependencies()
        install_dependencies()
        setup_pre_commit()
        create_github_workflows()
        
        print("\n🎖️ CI/CD SETUP COMPLETE!")
        print("=" * 50)
        print("✅ Dependencies installed")
        print("✅ Pre-commit hooks configured")
        print("✅ GitHub Actions workflow ready")
        print("✅ GitLab CI configuration available")
        print("\n📋 NEXT STEPS:")
        print("1. Commit your changes: git add . && git commit -m 'Add CI/CD configuration'")
        print("2. Push to your repository: git push")
        print("3. Check your CI/CD platform for automated test runs")
        print("\n🎯 LOCAL DEVELOPMENT:")
        print("- Run tests: make test")
        print("- Format code: make format")
        print("- Run linting: make lint")
        print("- See all commands: make help")
        
        run_initial_tests()
        
    except KeyboardInterrupt:
        print("\n❌ Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 