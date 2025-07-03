# 🎖️ Pre-commit Testing Guide

## **🚀 AUTOMATIC TESTING ON COMMIT**

Your repository now runs tests automatically **every time you run `git commit`**. This ensures no broken code gets committed.

## **🎯 HOW IT WORKS**

### **When you run `git commit`:**
1. **Hook Triggers**: Git runs `.git/hooks/pre-commit`
2. **Tests Execute**: `poetry run python run_tests.py`
3. **Decision Point**:
   - ✅ **Tests Pass**: Commit proceeds normally
   - ❌ **Tests Fail**: Commit is blocked

### **What You'll See:**
```
🎖️ RUNNING TRANSCRIPTION OUTPOST TEST BATTALION BEFORE COMMIT
============================================================
[... test output ...]

✅ ALL TESTS PASSED - PROCEEDING WITH COMMIT
```

OR

```
❌ TESTS FAILED - COMMIT BLOCKED
Fix the failing tests before committing
```

## **🔥 TESTING THE SETUP**

### **Method 1: Use the Test Script**
```powershell
cd transcription-outpost
./test-hook.ps1
```

### **Method 2: Manual Test**
```powershell
cd transcription-outpost
echo "test" > my-test-file.txt
git add my-test-file.txt
git commit -m "Test commit"
```

## **⚡ BYPASSING THE HOOK (EMERGENCY ONLY)**

If you need to commit without running tests (emergency situations):
```bash
git commit --no-verify -m "Emergency commit"
```

**⚠️ WARNING**: Only use `--no-verify` in true emergencies!

## **🛠️ TROUBLESHOOTING**

### **Hook Not Running?**
Check if hook exists and is executable:
```powershell
ls .git/hooks/pre-commit*
```

### **Tests Taking Too Long?**
The hook runs the full test suite. To speed up:
1. Fix failing tests first
2. Consider running specific test files during development
3. Use `git commit --no-verify` sparingly

### **Permission Issues?**
Make sure the hook is executable:
```bash
chmod +x .git/hooks/pre-commit
```

## **🎯 HOOK VERSIONS**

Three hook versions are available:
- `.git/hooks/pre-commit` - Unix shell script
- `.git/hooks/pre-commit.ps1` - PowerShell script
- `.git/hooks/pre-commit.bat` - Windows batch file

Git automatically uses the one without extension.

## **🔧 CUSTOMIZATION**

To modify what tests run, edit `.git/hooks/pre-commit`:
```bash
# Change this line:
poetry run python run_tests.py

# To run specific tests:
poetry run pytest tests/specific_test.py
```

## **📊 CURRENT TEST COVERAGE**

Your test suite includes:
- **Unit Tests**: 44 tests across all services
- **Integration Tests**: 18 API integration tests
- **Total Coverage**: 62 tests

## **🎖️ BEST PRACTICES**

1. **Run tests locally** before committing: `poetry run python run_tests.py`
2. **Keep commits focused** - smaller commits = faster test runs
3. **Fix failing tests immediately** - don't bypass the hook
4. **Use descriptive commit messages** - they're visible in test output

## **⚡ QUICK COMMANDS**

```powershell
# Run tests manually
poetry run python run_tests.py

# Run specific test file
poetry run pytest tests/services/llm/test_chains.py

# Check test coverage
poetry run pytest --cov=app tests/

# Bypass hook (emergency only)
git commit --no-verify -m "Emergency commit"
```

---

🎖️ **Your tests now run automatically on every commit!** 

No more broken code in your repository. Every commit is battle-tested and ready for deployment. 