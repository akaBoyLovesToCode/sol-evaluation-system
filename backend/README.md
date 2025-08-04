# Backend API Service

A Flask + SQLAlchemy + MySQL based backend API service for the evaluation management system.

## Technologies

### Core Framework
- **Flask** - Python web framework
- **Flask-SQLAlchemy** - SQLAlchemy ORM integration
- **Flask-Migrate** - Database migration tool
- **Flask-JWT-Extended** - JWT authentication
- **Flask-CORS** - Cross-origin resource sharing
- **Flask-SocketIO** - WebSocket support

### Database
- **MySQL 8.0** - Main database
- **PyMySQL** - Python MySQL client
- **cryptography** - Encryption library

### Utilities
- **python-dotenv** - Environment variable management
- **APScheduler** - Task scheduling
- **Werkzeug** - WSGI utilities
- **python-dateutil** - Date utilities

## Features

### Authentication System
- JWT Token based authentication
- Role-based access control
- User session management
- Role hierarchy: admin > group_leader > part_leader > user
- Token refresh mechanism
- Password hashing with Werkzeug

### Database Models
- User management
- Evaluation tracking
- Messaging
- Operation logging
- System configuration

### Evaluation System
- Evaluation CRUD operations
- Workflow management
- Approval process
- Status tracking
- Reporting

### Notification System
- Email notifications
- In-app messaging
- Status updates
- WebSocket real-time updates

### Security Features
- Password hashing
- Input validation
- SQL injection prevention
- XSS prevention
- CSRF protection

### Logging System
- Operation tracking
- Error logging
- Audit trails
- Activity monitoring

## Requirements

- Python >= 3.13
- MySQL >= 8.0
- uv (Python package manager)

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd evaluation/backend
```

### 2. Install dependencies

```bash
# uv manages virtual environment automatically
uv pip sync requirements.txt
```

### 3. Configure environment

Create a `.env` file:

```env
# Flask Configuration
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key

# Database Configuration
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your-password
MYSQL_DATABASE=evaluation

# Environment
FLASK_ENV=development
```

### 4. Database setup

```bash
# Initialize database
flask db init

# Create migration
flask db migrate -m "Initial migration"

# Apply migration
flask db upgrade
```

### 5. Run the application

```bash
# Development server
python run.py

# Or using Flask CLI
flask run --host=0.0.0.0 --port=5001
```

Access the API at `http://localhost:5001`

## Project Structure

```
backend/
   app/                    # Application package
      __init__.py        # Application factory
      api/               # API endpoints
         __init__.py
         auth.py        # Authentication API
         dashboard.py   # Dashboard API
         evaluation.py  # Evaluation API
         notifications.py # Notification API
         swagger.py     # API documentation
         user.py        # User API
         workflow.py    # Workflow API
      models/            # Database models
         __init__.py
         user.py        # User model
         evaluation.py  # Evaluation model
         message.py     # Message model
         operation_log.py # Operation log model
         system_config.py # System config model
      services/          # Business logic services
         __init__.py
         analytics_service.py    # Analytics service
         backup_service.py       # Backup service
         notification_service.py # Notification service
         workflow_service.py     # Workflow service
      utils/             # Utility functions
          __init__.py
          decorators.py  # Decorators
          helpers.py     # Helper functions
          validators.py  # Validation functions
   backups/               # Database backups
   uploads/               # File uploads
   config.py             # Configuration
   main.py               # Entry point
   run.py                # Development server
   requirements.txt      # Dependencies
   Dockerfile           # Docker configuration
   pyproject.toml       # Project configuration
   README.md            # Documentation
   tests/               # Test suite
      conftest.py       # Test configuration and fixtures
      helpers.py        # Test helper functions
      unit/             # Unit tests
         test_app.py    # Application tests
         test_evaluation_model.py # Evaluation model tests
         test_operation_log.py # Operation log tests
         test_user_model.py # User model tests
      README.md         # Test suite documentation
      bug_fixing_process.md # Test maintenance guide
```

## API Documentation

The API is documented using Swagger/OpenAPI. You can access the interactive API documentation at:

```
http://localhost:5001/api/docs
```

This provides a comprehensive interface to:
- Browse all available endpoints
- View request/response schemas
- Test API calls directly from the browser
- Understand authentication requirements
- See example requests and responses

The Swagger documentation is automatically generated from API endpoint definitions and includes:
- Authentication endpoints with JWT token details
- Evaluation management endpoints with full CRUD operations
- User management endpoints for profile and admin operations
- Operation logging endpoints for audit trail access
- Dashboard and analytics endpoints

To use the Swagger UI:
1. Start the backend server
2. Navigate to http://localhost:5001/api/docs in your browser
3. Use the "Authorize" button to authenticate with your JWT token
4. Explore and test endpoints directly from the browser interface

### Authentication

#### POST /api/auth/login
User login

**Request Body**
```json
{
  "username": "user@example.com",
  "password": "password123"
}
```

**Response**
```json
{
  "message": "Login successful",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "username": "user@example.com",
    "role": "user"
  }
}
```

#### POST /api/auth/logout
User logout (requires authentication)

#### POST /api/auth/refresh
Refresh access token

#### GET /api/auth/me
Get current user info (requires authentication)

### Evaluation API

#### GET /api/evaluations
Get evaluation list (requires authentication)

**Query Parameters**
- `page` - Page number (default: 1)
- `per_page` - Items per page (default: 20)
- `evaluation_type` - Filter by evaluation type
- `status` - Filter by status
- `sort_by` - Sort field
- `sort_order` - Sort order (asc/desc)

#### POST /api/evaluations
Create evaluation (requires authentication)

**Request Body:**
- `evaluation_type` (required) - Type: "new_product" or "mass_production"
- `product_name` (required) - Product name
- `part_number` (required) - Part number
- `start_date` (required) - Start date (YYYY-MM-DD)
- `expected_end_date` (required) - Expected end date (YYYY-MM-DD)
- `process_step` (required) - Process step identifier
- `evaluation_number` (optional) - Auto-generated if not provided (format: EVAL-YYYYMMDD-NNNN)
- `status` (optional) - Initial status: "draft" or "in_progress" (defaults to "draft")
- `evaluation_reason` (optional) - Reason for evaluation
- `description` (optional) - Detailed description

**Note:** The `evaluation_number` is automatically generated in the format `EVAL-YYYYMMDD-NNNN` if not provided. Each day starts from 0001 and increments sequentially.

#### GET /api/evaluations/{id}
Get evaluation details (requires authentication)

#### PUT /api/evaluations/{id}
Update evaluation (requires appropriate permissions)

#### DELETE /api/evaluations/{id}
Delete evaluation (requires appropriate permissions)

### Dashboard API

#### GET /api/dashboard/overview
Get dashboard overview data (requires authentication)

#### GET /api/dashboard/statistics
Get statistical data (requires authentication)

**Query Parameters**
- `start_date` - Start date
- `end_date` - End date
- `group_by` - Group by (day/week/month)

## Database Schema

### Users (users)
- `id` - Primary key
- `username` - Username (unique)
- `email` - Email (unique)
- `password_hash` - Hashed password
- `full_name` - Full name
- `role` - Role (admin/group_leader/part_leader/user)
- `department` - Department
- `position` - Position/title
- `is_active` - Active status
- `created_at` - Creation timestamp
- `updated_at` - Update timestamp

### Evaluations (evaluations)
- `id` - Primary key
- `evaluation_number` - Evaluation number (unique)
- `evaluation_type` - Evaluation type
- `product_name` - Product name
- `part_number` - Part number
- `status` - Status
- `evaluator_id` - Evaluator ID
- `start_date` - Start date
- `expected_end_date` - Expected end date
- `actual_end_date` - Actual end date
- `process_step` - Process step identifier
- `evaluation_reason` - Reason for evaluation
- `created_at` - Creation timestamp
- `updated_at` - Update timestamp

### Operation Logs (operation_logs)
- `id` - Primary key
- `user_id` - User ID
- `operation_type` - Operation type
- `target_type` - Target type
- `target_id` - Target ID
- `operation_description` - Operation description
- `ip_address` - IP address
- `user_agent` - User agent
- `created_at` - Creation timestamp

## Role Permissions

### Role Hierarchy
1. **admin** - Full access
   - System configuration
   - User management
   - System settings

2. **group_leader** - Group management
   - Evaluation approval
   - Final review
   - Report generation

3. **part_leader** - Part management
   - Initial evaluation approval
   - Team management

4. **user** - Basic user
   - Create evaluations
   - View own evaluations
   - Submit requests

### Permission Decorators
```python
# Single role requirement
@require_role('admin')
@require_group_leader
@require_part_leader

# Multiple role options
@role_required(['admin', 'group_leader'])
```

## Deployment

### Production Configuration

Production environment configuration
- `SECRET_KEY` - Flask secret key
- `JWT_SECRET_KEY` - JWT secret key
- `MYSQL_*` - Database connection parameters
- `FLASK_ENV=production` - Production mode

### Docker Deployment

```bash
# Build image
docker build -t evaluation-backend .

# Run container
docker run -p 5001:5001 evaluation-backend
```

### Docker Compose

```bash
# Start services (including MySQL)
docker-compose up -d

# Check services
docker-compose ps

# Stop services
docker-compose down
```

## Development

### Adding New API Endpoints

1. Create file in `app/api/` directory
2. Register blueprint in `app/__init__.py`
3. Add appropriate permission decorators
4. Document API endpoints

### Adding New Database Models

1. Create file in `app/models/` directory
2. Inherit from `db.Model` class
3. Define relationships with other models
4. Create database migration

### Adding New Services

1. Create file in `app/services/` directory
2. Implement business logic
3. Use from API endpoints

## Testing

### Current Test Status

The backend includes a focused test suite covering core functionality:

- **8 passing tests** covering essential features
- **Unit tests** for models, services, and business logic
- **Database testing** with SQLite in-memory database
- **Authentication testing** with JWT tokens

### Running Tests

```bash
# Run all tests
PYTHONPATH=. uv run pytest

# Run with verbose output
PYTHONPATH=. uv run pytest -v

# Run specific test files
PYTHONPATH=. uv run pytest tests/unit/test_user_model.py

# Run with coverage
PYTHONPATH=. uv run pytest --cov=app
```

### Test Structure

- `tests/conftest.py`: Test fixtures and configuration
- `tests/helpers.py`: Helper functions for tests
- `tests/unit/`: Unit tests for individual components
  - `test_user_model.py`: User model functionality and validation
  - `test_evaluation_model.py`: Evaluation model and relationships
  - `test_operation_log.py`: Operation logging functionality
  - `test_app.py`: Flask application setup

### Test Coverage

**User Model Tests** verify:
- User creation with password hashing
- Role validation and permissions  
- Profile field management
- Data serialization methods

**Evaluation Model Tests** verify:
- Evaluation creation with required fields
- Status and type validation
- Model relationships and data integrity
- Serialization methods

**Operation Log Tests** verify:
- Operation logging functionality
- Data storage and retrieval
- JSON data handling

### Documentation

See `tests/README.md` for comprehensive test suite documentation and `tests/bug_fixing_process.md` for maintenance guidelines.

## Monitoring

### Logging Configuration
- Configure logging levels
- Log to file at `logs/app.log`
- Set appropriate INFO/WARNING/ERROR levels

### Audit Trails
- Track user operations
- Database changes tracking
- Login attempts
- Report generation