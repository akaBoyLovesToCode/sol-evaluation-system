# GitHub Actions CI/CD Setup

## Overview
Comprehensive CI/CD pipeline using GitHub Actions for both frontend and backend services with automatic Railway deployment.

## Workflows Created

### 1. Frontend CI (`.github/workflows/frontend.yml`)
- **Triggers**: Push to main/develop, PRs to main, changes in frontend/
- **Node.js**: 22.x (required for Vite 7)
- **Steps**:
  - Install dependencies with npm ci
  - Run ESLint with auto-fix
  - Check Prettier formatting
  - Run Jest tests with coverage
  - Build application
  - Upload coverage to Codecov

### 2. Backend CI (`.github/workflows/backend.yml`)
- **Triggers**: Push to main/develop, PRs to main, changes in backend/
- **Python**: 3.13 with pip package manager
- **Database**: PostgreSQL 16 service container
- **Steps**:
  - Setup Python with pip caching
  - Install dependencies with pip
  - Run ruff linter and formatter checks
  - Run pytest with coverage
  - Upload coverage to Codecov

### 3. Deployment (`.github/workflows/deploy.yml`)
- **Triggers**: Push to main, manual workflow dispatch
- **Services**: Conditional deployment based on changed files
- **Steps**:
  - Deploy backend/frontend to Railway using CLI
  - Health checks for both services
  - Deployment status notifications

## Required GitHub Secrets

Add these secrets to your GitHub repository settings:

```
RAILWAY_TOKEN=your_railway_api_token
```

To get Railway token:
1. Go to Railway dashboard
2. Settings → Tokens
3. Create new token and copy value

## Script Updates

Added `format:check` script to frontend package.json for CI formatting validation.

## Features

- **Path-based triggers**: Only runs workflows when relevant files change
- **Matrix builds**: Supports multiple Node.js/Python versions
- **Service containers**: PostgreSQL for backend testing
- **Coverage reporting**: Integrated with Codecov
- **Health checks**: Verifies deployment success
- **Conditional deployment**: Smart deployment based on file changes

## Usage

1. Push code to main branch → Triggers CI + deployment
2. Create PR → Triggers CI only
3. Manual deployment → Use workflow dispatch

The pipeline ensures code quality, runs comprehensive tests, and deploys automatically to Railway platform.