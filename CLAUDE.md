# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Frontend (Vue 3 + Vite)
Located in `frontend/` directory:

```bash
# Development server
npm run dev                    # Start development server at http://localhost:3000

# Building and testing
npm run build                  # Build for production
npm run preview                # Preview production build locally
npm run lint                   # Run ESLint with auto-fix
npm run format                 # Format code with Prettier

# Testing
npm test                       # Run Jest tests
npm run test:watch             # Run tests in watch mode
npm run test:coverage          # Run tests with coverage report
```

### Backend (Flask + SQLAlchemy)
Located in `backend/` directory:

```bash
# Setup and dependencies (using uv)
uv venv .venv                  # Create virtual environment
source .venv/bin/activate      # Activate virtual environment (Linux/Mac)
uv pip sync requirements.txt   # Install dependencies from lock file

# Development server
python run.py                  # Start Flask development server at http://localhost:5001

# Database management
flask db upgrade               # Run database migrations
flask db migrate -m "message"  # Create new migration

# Testing
pytest                         # Run all tests
pytest tests/unit/             # Run unit tests only
pytest tests/integration/      # Run integration tests only
pytest --cov=app tests/        # Run tests with coverage
pytest -v tests/path/to/test_file.py::test_function_name  # Run specific test

# Production deployment
gunicorn -w 4 -b 0.0.0.0:5001 run:app  # Run with Gunicorn
```

### Database Setup
```bash
# Start MySQL with Docker
docker-compose up -d mysql

# Create database manually (if needed)
mysql -u root -p -e "CREATE DATABASE evaluation CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# Run migrations
cd backend && flask db upgrade
```

## Architecture Overview

This is a full-stack **Product Evaluation Management System** with distinct frontend and backend services:

### Technology Stack
- **Frontend**: Vue 3.5 + Element Plus + Tailwind CSS + ECharts for data visualization
- **Backend**: Flask + SQLAlchemy + MySQL 8.0 + JWT authentication
- **Testing**: Jest (frontend), pytest (backend)
- **Build Tools**: Vite (frontend), uv for Python package management
- **Deployment**: Docker Compose, Gunicorn for production

### Core Business Logic

**Evaluation Workflow System**: The system manages two types of evaluations:
1. **New Product Evaluations**: Require two-tier approval (Part Leader → Group Leader)
2. **Mass Production Evaluations**: Direct completion by authorized users

**Key Models**:
- `User` (backend/app/models/user.py): Four-tier role system (Admin > Group Leader > Part Leader > User)
- `Evaluation` (backend/app/models/evaluation.py): Core evaluation entity with workflow states
- `OperationLog` (backend/app/models/operation_log.py): Comprehensive audit trail

**Service Layer** (backend/app/services/):
- `workflow_service.py`: Handles evaluation state transitions and approval logic
- `analytics_service.py`: Statistical analysis and dashboard data
- `notification_service.py`: In-app notification system

### Frontend Architecture

**State Management**: Uses Pinia with `auth.js` store for authentication state

**Key Views**:
- `Dashboard.vue`: Interactive analytics with ECharts visualizations
- `Evaluations.vue`: Main evaluation management interface
- `NewEvaluation.vue`: Evaluation creation form with workflow logic

**Utilities**:
- `api.js`: Centralized HTTP client with JWT token handling
- `charts.js`: Custom ECharts configuration and utilities

**Internationalization**: Complete i18n support with Chinese/English/Korean translations in `locales/`

### API Structure

RESTful API endpoints in `backend/app/api/`:
- `auth.py`: JWT authentication, login/logout, token refresh
- `evaluation.py`: CRUD operations, workflow transitions, bulk operations
- `dashboard.py`: Analytics endpoints for charts and statistics
- `workflow.py`: Approval workflow management

Swagger documentation available at `/api/docs` when running backend.

### Database Schema

**Key Tables**:
- `users`: User management with role-based permissions
- `evaluations`: Core evaluation data with status tracking
- `operation_logs`: Audit trail for all system operations
- `messages`: In-app notification system

Migration files in `backend/migrations/versions/` track schema evolution.

### Development Workflow

1. **Database First**: Always run migrations before starting development
2. **Service Layer**: Business logic should be implemented in service classes, not directly in API endpoints
3. **JWT Authentication**: All API endpoints (except auth) require valid JWT tokens
4. **Workflow States**: Evaluations follow strict state transitions defined in `workflow_service.py`
5. **Audit Logging**: All significant operations are logged via `OperationLog` model

### Testing Strategy

**Backend Testing**:
- Unit tests for models and services in `tests/unit/`
- Integration tests for API endpoints in `tests/integration/`
- Test configuration in `pytest.ini`

**Frontend Testing**:
- Jest configuration for Vue components
- Test utilities in `tests/setup.js`
- Mock configurations in `tests/mocks/`

### Common Development Patterns

**Error Handling**: Use custom decorators in `backend/app/utils/decorators.py` for consistent API responses

**Validation**: Input validation handled by `backend/app/utils/validators.py`

**Chart Integration**: Use utilities in `frontend/src/utils/charts.js` for consistent ECharts implementation

**Permission Checks**: Role-based access control enforced at both API and frontend levels

### Environment Configuration

**Backend** requires `.env` file with:
- Database connection parameters
- JWT secret keys
- Flask configuration

**Frontend** uses `VITE_API_BASE_URL` environment variable for API endpoint configuration.