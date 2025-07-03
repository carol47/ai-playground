# 🎖️ CI/CD Configuration for Transcription Outpost

This document explains how to set up automated testing that runs after every commit using various CI/CD platforms.

## 🚀 Quick Setup (Recommended)

Run the automated setup script:

```bash
python setup-ci.py
```

This will:
- Install all dependencies
- Configure pre-commit hooks
- Set up GitHub Actions (if using GitHub)
- Run initial tests to verify everything works

## 🎯 Available CI/CD Options

### 1. GitHub Actions (Most Popular)

**File**: `.github/workflows/ci.yml`

**Features**:
- ✅ Runs on Python 3.9, 3.10, 3.11, 3.12
- ✅ Full test suite execution
- ✅ Code linting and formatting checks
- ✅ Security scanning
- ✅ Coverage reporting
- ✅ Caching for faster builds

**Setup**:
1. Push your repository to GitHub
2. The workflow will run automatically on every commit and pull request
3. View results in the "Actions" tab of your repository

### 2. GitLab CI/CD

**File**: `.gitlab-ci.yml`

**Features**:
- ✅ Multi-stage pipeline (test, lint, security, deploy)
- ✅ Parallel testing across Python versions
- ✅ Coverage reporting
- ✅ Performance testing
- ✅ Automatic API documentation generation

**Setup**:
1. Push your repository to GitLab
2. The pipeline will run automatically
3. View results in the "CI/CD" → "Pipelines" section

### 3. Pre-commit Hooks (Local)

**File**: `.pre-commit-config.yaml`

**Features**:
- ✅ Runs tests before every commit
- ✅ Code formatting and linting
- ✅ Prevents committing broken code
- ✅ Fast feedback loop

**Setup**:
```bash
# Install pre-commit
poetry run pre-commit install

# Run manually (optional)
poetry run pre-commit run --all-files
```

### 4. Local Development Tools

**File**: `Makefile`

**Available Commands**:
```bash
make help           # Show all available commands
make test           # Run full test suite
make test-unit      # Run unit tests only
make test-api       # Run API integration tests  
make test-coverage  # Run tests with coverage
make lint           # Run linting checks
make format         # Auto-format code
make security       # Run security scans
make clean          # Clean up cache files
make dev-server     # Start development server
make watch-tests    # Watch for changes and run tests
```

## 🛠️ Manual Setup Instructions

### For GitHub Actions:

1. Create directory structure:
```bash
mkdir -p .github/workflows
```

2. Copy the `ci.yml` file to `.github/workflows/`

3. Push to GitHub:
```bash
git add .github/
git commit -m "Add GitHub Actions CI"
git push
```

### For GitLab CI:

1. Copy `.gitlab-ci.yml` to your repository root

2. Push to GitLab:
```bash
git add .gitlab-ci.yml
git commit -m "Add GitLab CI configuration"
git push
```

### For Pre-commit Hooks:

1. Install pre-commit:
```bash
poetry add --group dev pre-commit
```

2. Install hooks:
```bash
poetry run pre-commit install
```

## 📊 Test Coverage

The CI/CD pipelines include coverage reporting:

- **HTML Report**: Generated in `htmlcov/` directory
- **XML Report**: For CI/CD integration
- **Terminal Report**: Shown during test runs

To generate coverage locally:
```bash
make test-coverage
```

## 🔒 Security Scanning

Automated security scanning includes:

- **Safety**: Checks for known vulnerabilities in dependencies
- **Bandit**: Static analysis for common security issues
- **Dependency scanning**: Monitors for outdated packages

Run security scans locally:
```bash
make security
```

## 🎯 Branch Protection

### GitHub Branch Protection Rules:

1. Go to Settings → Branches in your GitHub repository
2. Add rule for `main` branch:
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging
   - ✅ Include administrators

### GitLab Protected Branches:

1. Go to Settings → Repository → Protected Branches
2. Protect `main` branch:
   - ✅ Allowed to merge: Maintainers
   - ✅ Allowed to push: No one

## 🚨 Troubleshooting

### Common Issues:

**1. Tests fail due to missing dependencies**
```bash
poetry install
```

**2. Pre-commit hooks are slow**
```bash
# Run specific hook only
poetry run pre-commit run black --all-files
```

**3. Coverage reports not generated**
```bash
# Install coverage tools
poetry add --group dev pytest-cov coverage
```

**4. CI/CD pipeline fails on specific Python version**
- Check the error logs in your CI/CD platform
- Update dependencies in `pyproject.toml`
- Test locally with that Python version

### Debug Commands:

```bash
# Run tests with verbose output
poetry run python run_tests.py --verbose

# Check pre-commit configuration
poetry run pre-commit run --all-files --show-diff-on-failure

# Validate CI/CD configuration
# For GitHub Actions:
gh workflow view

# For GitLab CI:
gitlab-ci-multi-runner verify
```

## 📈 Performance Optimization

### Speed Up CI/CD:

1. **Use caching**: Both GitHub Actions and GitLab CI configurations include caching
2. **Parallel testing**: Tests run in parallel across multiple Python versions
3. **Incremental testing**: Only run affected tests (coming soon)

### Monitor Performance:

```bash
# Run performance tests
poetry run python temp_performance.py

# Profile test execution
poetry run pytest --profile
```

## 🎖️ Best Practices

1. **Commit Frequently**: Small, focused commits are easier to debug
2. **Write Good Commit Messages**: Use conventional commit format
3. **Keep Dependencies Updated**: Regularly update `poetry.lock`
4. **Monitor CI/CD**: Check pipeline status regularly
5. **Use Feature Branches**: Don't push directly to `main`

## 📋 Next Steps

1. **Set up branch protection** on your git platform
2. **Configure notifications** for failed builds
3. **Add badges** to your README showing build status
4. **Consider deploying** successful builds automatically
5. **Set up monitoring** for production deployments

---

🎖️ **Your tests now run automatically after every commit!** 

For questions or issues, check the troubleshooting section above or review the CI/CD logs in your platform. 