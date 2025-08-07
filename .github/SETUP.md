# GitHub Actions CI/CD Setup

## Overview
Comprehensive CI/CD pipeline using GitHub Actions for both frontend and backend services with automatic Railway deployment and intelligent health monitoring.

## Workflows Created

### 1. Frontend CI (`.github/workflows/frontend.yml`)
- **Triggers**: Push to main/develop, PRs to main, changes in `frontend/`
- **Node.js**: 22.x (required for Vite 7)
- **Steps**:
  - Install dependencies with npm ci
  - Run ESLint with auto-fix
  - Check Prettier formatting
  - Run Jest tests with coverage
  - Build application
  - Upload coverage to Codecov

### 2. Backend CI (`.github/workflows/backend.yml`)
- **Triggers**: Push to main/develop, PRs to main, changes in `backend/`
- **Python**: 3.13 with pip package manager
- **Database**: PostgreSQL 16 service container
- **Steps**:
  - Setup Python with pip caching
  - Install dependencies with pip
  - Run ruff linter and formatter checks
  - Run pytest with coverage
  - Upload coverage to Codecov

### 3. Deployment (`.github/workflows/deploy.yml`)
**Improved workflow with independent service deployment and health monitoring**

- **Triggers**: Push to main, manual workflow dispatch
- **Architecture**: Multi-job workflow with intelligent dependency management

#### Job Structure:

1. **Change Detection** (`changes`)
   - Uses `dorny/paths-filter@v3` for reliable file change detection
   - Outputs: `backend` and `frontend` change flags
   - Replaces unreliable `github.event.head_commit.modified` approach

2. **Service Deployment** (Parallel)
   - **Backend Deployment** (`deploy-backend`)
     - Runs when: Backend files changed OR manual dispatch
     - Deploys to Railway backend service
   - **Frontend Deployment** (`deploy-frontend`)
     - Runs when: Frontend files changed OR manual dispatch
     - Deploys to Railway frontend service

3. **Individual Health Checks** (Parallel)
   - **Backend Health Check** (`health-check-backend`)
     - Runs only after successful backend deployment
     - 5 retry attempts with 30-second intervals
     - Tests: `/api/health` endpoint availability
   - **Frontend Health Check** (`health-check-frontend`)
     - Runs only after successful frontend deployment
     - 5 retry attempts with 30-second intervals
     - Tests: Frontend application loading

4. **Integration Testing** (`integration-health-check`)
   - Runs only when BOTH services deploy successfully in same run
   - Tests frontend-backend communication
   - Verifies end-to-end system functionality

5. **Deployment Summary** (`deployment-summary`)
   - Always runs at the end
   - Provides comprehensive deployment report in GitHub Actions summary
   - Shows status of each service and health checks

## Key Improvements Over Previous Version

### ✅ **Independent Health Checks**
- **Before**: Health checks only ran when both services changed
- **After**: Each service gets health verification after deployment

### ✅ **Smart Change Detection**
- **Before**: Unreliable `github.event.head_commit.modified`
- **After**: Robust `dorny/paths-filter` with explicit path matching

### ✅ **Resilient Health Monitoring**
- **Before**: Single attempt health checks
- **After**: 5 retry attempts with proper error handling and timeouts

### ✅ **Clear Status Reporting**
- **Before**: Basic failure notifications
- **After**: Detailed summary with service status, health check results, and service URLs

### ✅ **Flexible Deployment Patterns**
- Single service changes → Individual deployment + health check
- Both services change → Independent deployments + integration test
- Manual dispatch → Deploy all services regardless of changes

## Required GitHub Secrets

Add these secrets to your GitHub repository settings:

```
RAILWAY_TOKEN=your_railway_api_token
CODECOV_TOKEN=your_codecov_token (optional)
```

To get Railway token:
1. Go to Railway dashboard → Settings → Tokens
2. Create new token and copy value

## Deployment Scenarios

### Scenario 1: Backend Only Changes
```
Push with backend/ changes → Backend deploys → Backend health check
Result: Backend verified, frontend unchanged
```

### Scenario 2: Frontend Only Changes
```
Push with frontend/ changes → Frontend deploys → Frontend health check
Result: Frontend verified, backend unchanged
```

### Scenario 3: Both Services Change
```
Push with both changes → Both deploy → Individual health checks → Integration test
Result: Full system verification
```

### Scenario 4: Manual Deployment
```
Workflow dispatch → Both services deploy → All health checks run
Result: Complete redeployment verification
```

## Monitoring & Debugging

### Health Check URLs
- **Backend**: `https://sol-evaluation-system.up.railway.app/api/health`
- **Frontend**: `https://frontend-production-d9f6.up.railway.app/`

### Debugging Failed Deployments
1. Check GitHub Actions logs for specific job failures
2. Review Railway service logs in dashboard
3. Use workflow summary for quick status overview
4. Manual health checks using curl commands from workflow

### Retry Logic
Health checks automatically retry up to 5 times with:
- 30-second intervals between attempts
- 30-second timeout per request
- Clear logging of each attempt

## Features

- **Path-based triggers**: Only runs workflows when relevant files change
- **Matrix builds**: Supports multiple Node.js/Python versions
- **Service containers**: PostgreSQL for backend testing
- **Coverage reporting**: Integrated with Codecov
- **Independent health monitoring**: Each service verified separately
- **Integration testing**: End-to-end verification when both services deploy
- **Resilient retry logic**: Handles temporary deployment issues
- **Comprehensive reporting**: Clear status summaries and debugging information

## Usage

1. **Development**: Push code to main branch → Triggers CI + smart deployment
2. **Pull Requests**: Create PR → Triggers CI only (no deployment)
3. **Manual Deployment**: Use workflow dispatch → Forces full redeployment
4. **Monitoring**: Check Actions summary tab for deployment status

The pipeline ensures code quality, runs comprehensive tests, deploys services independently, and provides robust health monitoring for the Railway platform.