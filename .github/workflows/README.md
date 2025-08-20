# GitHub Actions Workflows

This directory contains the CI/CD workflows for the h5forest project.

## test.yml

Automatically runs on:
- Pull requests to `main` or `develop` branches
- Pushes to `main` or `develop` branches

**What it does:**
- Tests against Python 3.8, 3.9, 3.10, 3.11, 3.12
- Installs system dependencies (HDF5 libraries)
- Runs code linting with ruff
- Executes the full test suite with pytest
- Generates coverage reports
- Uploads coverage to Codecov (optional)

**Requirements for PRs:**
- All tests must pass
- Code must pass ruff linting
- Code formatting must be consistent

The workflow will automatically comment on PRs with test results and coverage information.