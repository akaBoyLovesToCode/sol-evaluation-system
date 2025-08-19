# Solution Evaluation Management System API Documentation

## Overview

The Solution Evaluation Management System provides a comprehensive REST API for managing solution evaluations, workflows, analytics, and user management. The API follows RESTful principles and uses JSON for request and response payloads.

**Base URL**: `http://localhost:5001` (Development) | `https://your-production-domain.com` (Production)

**API Version**: 1.0.0

**Content Type**: `application/json`

## Authentication

The API uses JWT (JSON Web Token) based authentication with refresh token support.

### Authentication Flow

1. **Login** with username/password to receive access and refresh tokens
2. **Include** the access token in the `Authorization` header for protected endpoints
3. **Refresh** the access token using the refresh token when it expires
4. **Logout** to invalidate tokens

### Headers

```http
Authorization: Bearer <access_token>
Content-Type: application/json
```

---

## Authentication Endpoints

### POST /api/auth/login

Authenticate user and receive JWT tokens.

**Request:**
```json
{
  "username": "john_doe",
  "password": "secure_password"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "user": {
      "id": 1,
      "username": "john_doe",
      "email": "john@example.com",
      "full_name": "John Doe",
      "role": "part_leader",
      "department": "Engineering",
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z"
    },
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "expires_in": 3600
  }
}
```

**Error Response (401 Unauthorized):**
```json
{
  "success": false,
  "message": "Invalid username or password",
  "error": "INVALID_CREDENTIALS"
}
```

### POST /api/auth/refresh

Refresh the access token using a valid refresh token.

**Request:**
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "expires_in": 3600
  }
}
```

### POST /api/auth/logout

Logout and invalidate tokens.

**Headers Required:**
```http
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Logout successful"
}
```

---

## User Management

### GET /api/users

Get list of users with optional filtering and pagination.

**Headers Required:**
```http
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `page` (int, optional): Page number (default: 1)
- `per_page` (int, optional): Items per page (default: 20, max: 100)
- `role` (string, optional): Filter by role (admin, group_leader, part_leader, user)
- `department` (string, optional): Filter by department
- `is_active` (boolean, optional): Filter by active status
- `search` (string, optional): Search in username, email, full_name

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "users": [
      {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com",
        "full_name": "John Doe",
        "role": "part_leader",
        "department": "Engineering",
        "is_active": true,
        "created_at": "2024-01-01T00:00:00Z",
        "last_login": "2024-01-15T10:30:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 1,
      "pages": 1,
      "has_next": false,
      "has_prev": false
    }
  }
}
```

### GET /api/users/{id}

Get user details by ID.

**Headers Required:**
```http
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": 1,
      "username": "john_doe",
      "email": "john@example.com",
      "full_name": "John Doe",
      "role": "part_leader",
      "department": "Engineering",
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z",
      "last_login": "2024-01-15T10:30:00Z",
      "evaluation_stats": {
        "total_evaluations": 15,
        "pending_approvals": 3,
        "completed_this_month": 8
      }
    }
  }
}
```

### POST /api/users

Create a new user (Admin only).

**Headers Required:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "username": "jane_smith",
  "email": "jane@example.com",
  "full_name": "Jane Smith",
  "password": "secure_password",
  "role": "user",
  "department": "Quality Assurance",
  "is_active": true
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "User created successfully",
  "data": {
    "user": {
      "id": 2,
      "username": "jane_smith",
      "email": "jane@example.com",
      "full_name": "Jane Smith",
      "role": "user",
      "department": "Quality Assurance",
      "is_active": true,
      "created_at": "2024-01-15T10:30:00Z"
    }
  }
}
```

### PUT /api/users/{id}

Update user information.

**Headers Required:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "email": "jane.smith@example.com",
  "full_name": "Jane Smith",
  "department": "Quality Assurance",
  "role": "part_leader"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "User updated successfully",
  "data": {
    "user": {
      "id": 2,
      "username": "jane_smith",
      "email": "jane.smith@example.com",
      "full_name": "Jane Smith",
      "role": "part_leader",
      "department": "Quality Assurance",
      "is_active": true,
      "updated_at": "2024-01-15T11:00:00Z"
    }
  }
}
```

### DELETE /api/users/{id}

Deactivate a user (Admin only).

**Headers Required:**
```http
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "User deactivated successfully"
}
```

---

## Evaluation Management

### GET /api/evaluations

Get list of evaluations with filtering and pagination.

**Headers Required:**
```http
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `page` (int, optional): Page number (default: 1)
- `per_page` (int, optional): Items per page (default: 20)
- `status` (string, optional): Filter by status (draft, submitted, in_review, approved, rejected, completed, cancelled)
- `type` (string, optional): Filter by type (new_product, mass_production)
- `evaluator_id` (int, optional): Filter by evaluator ID
- `part_leader_id` (int, optional): Filter by part leader ID
- `group_leader_id` (int, optional): Filter by group leader ID
- `date_from` (string, optional): Filter from date (YYYY-MM-DD)
- `date_to` (string, optional): Filter to date (YYYY-MM-DD)
- `search` (string, optional): Search in title, description, evaluation_number

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "evaluations": [
      {
        "id": 1,
        "evaluation_number": "EVAL-2024-001",
        "title": "New SSD Controller Evaluation",
        "description": "Evaluation of new SSD controller performance",
        "type": "new_product",
        "status": "in_review",
        "priority": "high",
        "created_at": "2024-01-10T09:00:00Z",
        "updated_at": "2024-01-15T10:30:00Z",
        "due_date": "2024-01-30T23:59:59Z",
        "evaluator": {
          "id": 3,
          "username": "engineer1",
          "full_name": "Alice Engineer"
        },
        "part_leader": {
          "id": 2,
          "username": "part_lead1",
          "full_name": "Bob Leader"
        },
        "group_leader": {
          "id": 1,
          "username": "group_lead1",
          "full_name": "Carol Manager"
        },
        "progress_percentage": 75,
        "estimated_completion": "2024-01-25T00:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 1,
      "pages": 1
    }
  }
}
```

### GET /api/evaluations/{id}

Get detailed evaluation information.

**Headers Required:**
```http
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "evaluation": {
      "id": 1,
      "evaluation_number": "EVAL-2024-001",
      "title": "New SSD Controller Evaluation",
      "description": "Evaluation of new SSD controller performance",
      "type": "new_product",
      "status": "in_review",
      "priority": "high",
      "created_at": "2024-01-10T09:00:00Z",
      "updated_at": "2024-01-15T10:30:00Z",
      "due_date": "2024-01-30T23:59:59Z",
      "evaluator": {
        "id": 3,
        "username": "engineer1",
        "full_name": "Alice Engineer",
        "email": "alice@example.com"
      },
      "part_leader": {
        "id": 2,
        "username": "part_lead1",
        "full_name": "Bob Leader"
      },
      "group_leader": {
        "id": 1,
        "username": "group_lead1",
        "full_name": "Carol Manager"
      },
      "progress_percentage": 75,
      "estimated_completion": "2024-01-25T00:00:00Z",
      "evaluation_details": [
        {
          "id": 1,
          "category": "Performance",
          "subcategory": "Read Speed",
          "criteria": "Sequential read speed",
          "target_value": "7000 MB/s",
          "actual_value": "6800 MB/s",
          "result": "pass",
          "notes": "Meets minimum requirements",
          "test_date": "2024-01-12T14:00:00Z"
        }
      ],
      "attachments": [
        {
          "id": 1,
          "filename": "test_results.pdf",
          "file_size": 2048576,
          "uploaded_at": "2024-01-12T15:00:00Z",
          "uploaded_by": "Alice Engineer"
        }
      ],
      "operation_logs": [
        {
          "id": 1,
          "action": "evaluation_created",
          "description": "Evaluation created",
          "user": "Alice Engineer",
          "timestamp": "2024-01-10T09:00:00Z"
        },
        {
          "id": 2,
          "action": "evaluation_submitted",
          "description": "Evaluation submitted for review",
          "user": "Alice Engineer",
          "timestamp": "2024-01-15T10:30:00Z"
        }
      ]
    }
  }
}
```

### POST /api/evaluations

Create a new evaluation.

**Headers Required:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "title": "New Memory Module Evaluation",
  "description": "Performance evaluation of new DDR5 memory modules",
  "type": "new_product",
  "priority": "medium",
  "due_date": "2024-02-15T23:59:59Z",
  "part_leader_id": 2,
  "group_leader_id": 1,
  "evaluation_details": [
    {
      "category": "Performance",
      "subcategory": "Speed",
      "criteria": "Data transfer rate",
      "target_value": "6400 MT/s",
      "notes": "Must meet JEDEC standards"
    }
  ]
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Evaluation created successfully",
  "data": {
    "evaluation": {
      "id": 2,
      "evaluation_number": "EVAL-2024-002",
      "title": "New Memory Module Evaluation",
      "description": "Performance evaluation of new DDR5 memory modules",
      "type": "new_product",
      "status": "draft",
      "priority": "medium",
      "created_at": "2024-01-15T11:00:00Z",
      "due_date": "2024-02-15T23:59:59Z",
      "evaluator_id": 3,
      "part_leader_id": 2,
      "group_leader_id": 1
    }
  }
}
```

### PUT /api/evaluations/{id}

Update evaluation information.

**Headers Required:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "title": "Updated Memory Module Evaluation",
  "description": "Updated description with new requirements",
  "priority": "high",
  "due_date": "2024-02-10T23:59:59Z"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Evaluation updated successfully",
  "data": {
    "evaluation": {
      "id": 2,
      "title": "Updated Memory Module Evaluation",
      "description": "Updated description with new requirements",
      "priority": "high",
      "updated_at": "2024-01-15T11:30:00Z"
    }
  }
}
```

### DELETE /api/evaluations/{id}

Delete an evaluation (only in draft status).

**Headers Required:**
```http
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Evaluation deleted successfully"
}
```

---

## Workflow Management

### POST /api/workflow/submit

Submit evaluation for approval.

**Headers Required:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "evaluation_id": 1,
  "comments": "All test results are within acceptable parameters"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Evaluation submitted for approval",
  "data": {
    "evaluation": {
      "id": 1,
      "status": "submitted",
      "submitted_at": "2024-01-15T12:00:00Z",
      "next_approver": {
        "id": 2,
        "full_name": "Bob Leader",
        "role": "part_leader"
      }
    }
  }
}
```

### POST /api/workflow/approve

Approve an evaluation.

**Headers Required:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "evaluation_id": 1,
  "comments": "Approved. Results meet all requirements.",
  "action": "approve"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Evaluation approved successfully",
  "data": {
    "evaluation": {
      "id": 1,
      "status": "approved",
      "approved_at": "2024-01-15T14:00:00Z",
      "approved_by": {
        "id": 2,
        "full_name": "Bob Leader"
      },
      "next_approver": {
        "id": 1,
        "full_name": "Carol Manager",
        "role": "group_leader"
      }
    }
  }
}
```

### POST /api/workflow/reject

Reject an evaluation.

**Headers Required:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "evaluation_id": 1,
  "comments": "Performance results do not meet minimum requirements. Please retest.",
  "action": "reject"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Evaluation rejected",
  "data": {
    "evaluation": {
      "id": 1,
      "status": "rejected",
      "rejected_at": "2024-01-15T14:00:00Z",
      "rejected_by": {
        "id": 2,
        "full_name": "Bob Leader"
      },
      "rejection_reason": "Performance results do not meet minimum requirements. Please retest."
    }
  }
}
```

### GET /api/workflow/pending

Get pending approvals for the current user.

**Headers Required:**
```http
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `page` (int, optional): Page number (default: 1)
- `per_page` (int, optional): Items per page (default: 20)

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "pending_approvals": [
      {
        "id": 1,
        "evaluation_number": "EVAL-2024-001",
        "title": "New SSD Controller Evaluation",
        "type": "new_product",
        "priority": "high",
        "submitted_at": "2024-01-15T12:00:00Z",
        "due_date": "2024-01-30T23:59:59Z",
        "evaluator": {
          "id": 3,
          "full_name": "Alice Engineer"
        },
        "approval_level": "part_leader",
        "days_pending": 1
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 1,
      "pages": 1
    }
  }
}
```

---

## Dashboard & Analytics

### GET /api/dashboard/stats

Get dashboard statistics.

**Headers Required:**
```http
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `period` (string, optional): Time period (week, month, quarter, year) (default: month)
- `department` (string, optional): Filter by department

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "summary": {
      "total_evaluations": 156,
      "active_evaluations": 23,
      "completed_this_month": 18,
      "pending_approvals": 7,
      "overdue_evaluations": 2,
      "average_completion_time": 8.5
    },
    "status_distribution": {
      "draft": 5,
      "submitted": 8,
      "in_review": 10,
      "approved": 3,
      "completed": 127,
      "rejected": 2,
      "cancelled": 1
    },
    "type_distribution": {
      "new_product": 89,
      "mass_production": 67
    },
    "priority_distribution": {
      "low": 34,
      "medium": 78,
      "high": 32,
      "critical": 12
    },
    "department_stats": [
      {
        "department": "Engineering",
        "total": 89,
        "completed": 76,
        "completion_rate": 85.4
      },
      {
        "department": "Quality Assurance",
        "total": 67,
        "completed": 51,
        "completion_rate": 76.1
      }
    ]
  }
}
```

### GET /api/dashboard/charts

Get chart data for dashboard visualizations.

**Headers Required:**
```http
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `chart_type` (string, optional): Specific chart type (monthly_trend, status_trend, completion_rate)
- `period` (string, optional): Time period (3months, 6months, year) (default: 6months)

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "monthly_trend": {
      "labels": ["2023-08", "2023-09", "2023-10", "2023-11", "2023-12", "2024-01"],
      "datasets": [
        {
          "label": "Created",
          "data": [12, 15, 18, 22, 20, 16]
        },
        {
          "label": "Completed",
          "data": [10, 13, 16, 19, 18, 14]
        }
      ]
    },
    "status_distribution": {
      "labels": ["Draft", "Submitted", "In Review", "Approved", "Completed", "Rejected"],
      "data": [5, 8, 10, 3, 127, 2]
    },
    "completion_rate_by_department": {
      "labels": ["Engineering", "Quality Assurance", "Manufacturing", "Design"],
      "data": [85.4, 76.1, 92.3, 78.8]
    },
    "average_completion_time": {
      "labels": ["Week 1", "Week 2", "Week 3", "Week 4"],
      "data": [7.2, 8.1, 9.3, 8.5]
    }
  }
}
```

### POST /api/analytics/export

Export analytics data.

**Headers Required:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "format": "csv",
  "data_type": "evaluations",
  "date_from": "2024-01-01",
  "date_to": "2024-01-31",
  "filters": {
    "status": ["completed", "approved"],
    "department": "Engineering"
  }
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Export generated successfully",
  "data": {
    "download_url": "/api/downloads/export_20240115_120000.csv",
    "filename": "evaluations_export_20240115.csv",
    "file_size": 15360,
    "record_count": 45,
    "expires_at": "2024-01-16T12:00:00Z"
  }
}
```

---

## Notifications

### GET /api/notifications

Get notifications for the current user.

**Headers Required:**
```http
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `page` (int, optional): Page number (default: 1)
- `per_page` (int, optional): Items per page (default: 20)
- `unread_only` (boolean, optional): Show only unread notifications

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "notifications": [
      {
        "id": 1,
        "type": "evaluation_submitted",
        "title": "New Evaluation Awaiting Approval",
        "message": "EVAL-2024-001 has been submitted for your review",
        "is_read": false,
        "created_at": "2024-01-15T12:00:00Z",
        "related_object": {
          "type": "evaluation",
          "id": 1,
          "url": "/evaluations/1"
        }
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 1,
      "pages": 1
    },
    "unread_count": 3
  }
}
```

### POST /api/notifications/{id}/read

Mark notification as read.

**Headers Required:**
```http
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Notification marked as read"
}
```

### POST /api/notifications/mark-all-read

Mark all notifications as read.

**Headers Required:**
```http
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "All notifications marked as read"
}
```

---

## Operation Logs

### GET /api/logs/operations

Get operation logs with filtering.

**Headers Required:**
```http
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `page` (int, optional): Page number (default: 1)
- `per_page` (int, optional): Items per page (default: 50)
- `user_id` (int, optional): Filter by user ID
- `action` (string, optional): Filter by action type
- `date_from` (string, optional): Filter from date (YYYY-MM-DD)
- `date_to` (string, optional): Filter to date (YYYY-MM-DD)
- `evaluation_id` (int, optional): Filter by evaluation ID

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "logs": [
      {
        "id": 1,
        "action": "evaluation_created",
        "description": "Created evaluation EVAL-2024-001",
        "user": {
          "id": 3,
          "username": "engineer1",
          "full_name": "Alice Engineer"
        },
        "ip_address": "192.168.1.100",
        "user_agent": "Mozilla/5.0...",
        "evaluation_id": 1,
        "timestamp": "2024-01-10T09:00:00Z",
        "details": {
          "evaluation_title": "New SSD Controller Evaluation",
          "evaluation_type": "new_product"
        }
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 50,
      "total": 1,
      "pages": 1
    }
  }
}
```

---

## Health Check

### GET /api/health

Get API health status.

**Response (200 OK):**
```json
{
  "status": "healthy",
  "message": "Solution Evaluation System is running",
  "timestamp": "2024-01-15T12:00:00Z",
  "version": "1.0.0",
  "database_status": "connected",
  "uptime": 86400
}
```

---

## Error Handling

The API uses standard HTTP status codes and returns errors in a consistent format:

### Error Response Format

```json
{
  "success": false,
  "message": "Human-readable error message",
  "error": "ERROR_CODE",
  "details": {
    "field": "Additional error details"
  }
}
```

### HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | OK - Request successful |
| 201 | Created - Resource created successfully |
| 400 | Bad Request - Invalid request data |
| 401 | Unauthorized - Authentication required or invalid |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource not found |
| 409 | Conflict - Resource conflict (duplicate, etc.) |
| 422 | Unprocessable Entity - Validation errors |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error - Server error |

### Common Error Codes

| Error Code | Description |
|------------|-------------|
| `INVALID_CREDENTIALS` | Invalid username or password |
| `TOKEN_EXPIRED` | JWT token has expired |
| `TOKEN_INVALID` | JWT token is invalid |
| `INSUFFICIENT_PERMISSIONS` | User lacks required permissions |
| `VALIDATION_ERROR` | Request data validation failed |
| `RESOURCE_NOT_FOUND` | Requested resource does not exist |
| `DUPLICATE_RESOURCE` | Resource already exists |
| `OPERATION_NOT_ALLOWED` | Operation not allowed in current state |

### Validation Error Example

```json
{
  "success": false,
  "message": "Validation errors occurred",
  "error": "VALIDATION_ERROR",
  "details": {
    "title": "Title is required",
    "due_date": "Due date must be in the future",
    "email": "Invalid email format"
  }
}
```

---

## Rate Limiting

The API implements rate limiting to ensure fair usage:

- **Authenticated users**: 1000 requests per hour
- **Authentication endpoints**: 10 requests per minute
- **Heavy operations** (exports, bulk operations): 100 requests per hour

Rate limit headers are included in responses:

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1642248000
```

---

## Pagination

List endpoints support pagination with the following parameters:

- `page`: Page number (starting from 1)
- `per_page`: Items per page (default: 20, max: 100)

Pagination information is included in the response:

```json
{
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 156,
    "pages": 8,
    "has_next": true,
    "has_prev": false,
    "next_page": 2,
    "prev_page": null
  }
}
```

---

## Testing the API

### Interactive API Documentation

Access the Swagger UI at `http://localhost:5001/api/docs` when running the backend locally. This provides:

- **Interactive testing** of all endpoints
- **Authentication** via the "Authorize" button
- **Request/response examples** for each endpoint
- **Schema documentation** for all data models

### Using cURL

#### Authentication Flow
```bash
# Login and get tokens
curl -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "demo",
    "password": "demo123"
  }'

# Save the access token from the response
export ACCESS_TOKEN="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."

# Use the token for authenticated requests
curl -X GET http://localhost:5001/api/evaluations \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

#### Common API Operations
```bash
# Get dashboard statistics
curl -X GET http://localhost:5001/api/dashboard/stats \
  -H "Authorization: Bearer $ACCESS_TOKEN"

# Create a new evaluation
curl -X POST http://localhost:5001/api/evaluations \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Evaluation",
    "description": "API testing evaluation",
    "type": "new_product",
    "priority": "medium"
  }'

# Get pending approvals
curl -X GET http://localhost:5001/api/workflow/pending \
  -H "Authorization: Bearer $ACCESS_TOKEN"

# Approve an evaluation
curl -X POST http://localhost:5001/api/workflow/approve \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "evaluation_id": 1,
    "comments": "Approved via API test",
    "action": "approve"
  }'
```

### Using JavaScript/Axios

```javascript
// Setup axios with base configuration
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:5001',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add token to requests
api.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Authentication
async function login(username, password) {
  try {
    const response = await api.post('/api/auth/login', {
      username,
      password
    });
    
    const { access_token } = response.data.data;
    localStorage.setItem('access_token', access_token);
    return response.data;
  } catch (error) {
    console.error('Login failed:', error.response.data);
    throw error;
  }
}

// Get evaluations
async function getEvaluations(filters = {}) {
  try {
    const response = await api.get('/api/evaluations', {
      params: filters
    });
    return response.data.data;
  } catch (error) {
    console.error('Failed to fetch evaluations:', error);
    throw error;
  }
}

// Create evaluation
async function createEvaluation(evaluationData) {
  try {
    const response = await api.post('/api/evaluations', evaluationData);
    return response.data.data;
  } catch (error) {
    console.error('Failed to create evaluation:', error);
    throw error;
  }
}

// Usage examples
async function example() {
  // Login
  await login('demo', 'demo123');
  
  // Get all evaluations
  const evaluations = await getEvaluations();
  
  // Get evaluations with filters
  const filteredEvaluations = await getEvaluations({
    status: 'in_review',
    type: 'new_product',
    page: 1,
    per_page: 10
  });
  
  // Create new evaluation
  const newEvaluation = await createEvaluation({
    title: 'API Test Evaluation',
    description: 'Created via JavaScript API',
    type: 'new_product',
    priority: 'medium'
  });
}
```

### Using Python Requests

```python
import requests
import json

class SolutionEvaluationAPI:
    def __init__(self, base_url="http://localhost:5001"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
    
    def login(self, username, password):
        """Authenticate and set authorization header"""
        response = self.session.post(f"{self.base_url}/api/auth/login", 
            json={"username": username, "password": password})
        response.raise_for_status()
        
        data = response.json()
        access_token = data['data']['access_token']
        self.session.headers.update({'Authorization': f'Bearer {access_token}'})
        return data
    
    def get_evaluations(self, **filters):
        """Get evaluations with optional filters"""
        response = self.session.get(f"{self.base_url}/api/evaluations", 
            params=filters)
        response.raise_for_status()
        return response.json()['data']
    
    def create_evaluation(self, evaluation_data):
        """Create a new evaluation"""
        response = self.session.post(f"{self.base_url}/api/evaluations", 
            json=evaluation_data)
        response.raise_for_status()
        return response.json()['data']
    
    def get_dashboard_stats(self, period="month"):
        """Get dashboard statistics"""
        response = self.session.get(f"{self.base_url}/api/dashboard/stats", 
            params={"period": period})
        response.raise_for_status()
        return response.json()['data']
    
    def approve_evaluation(self, evaluation_id, comments=""):
        """Approve an evaluation"""
        response = self.session.post(f"{self.base_url}/api/workflow/approve", 
            json={
                "evaluation_id": evaluation_id,
                "comments": comments,
                "action": "approve"
            })
        response.raise_for_status()
        return response.json()['data']

# Usage example
if __name__ == "__main__":
    api = SolutionEvaluationAPI()
    
    # Login
    api.login("demo", "demo123")
    
    # Get dashboard stats
    stats = api.get_dashboard_stats()
    print(f"Total evaluations: {stats['summary']['total_evaluations']}")
    
    # Get evaluations
    evaluations = api.get_evaluations(status="in_review", page=1, per_page=5)
    print(f"Found {len(evaluations['evaluations'])} evaluations in review")
    
    # Create new evaluation
    new_eval = api.create_evaluation({
        "title": "Python API Test",
        "description": "Created via Python API client",
        "type": "new_product",
        "priority": "low"
    })
    print(f"Created evaluation: {new_eval['evaluation']['evaluation_number']}")
```

---

## WebSocket Support (Future)

While not currently implemented, the API is designed to support real-time updates via WebSocket connections for:

- **Live notifications** when evaluations are submitted/approved
- **Real-time dashboard updates** for metrics and charts
- **Collaborative editing** of evaluation details
- **Status change broadcasts** to relevant users

**Planned WebSocket endpoints:**
- `ws://localhost:5001/ws/notifications` - User-specific notifications
- `ws://localhost:5001/ws/dashboard` - Dashboard updates
- `ws://localhost:5001/ws/evaluations/{id}` - Evaluation-specific updates

---

## API Versioning

The current API version is **v1.0.0**. Future versions will maintain backward compatibility where possible.

**Version Strategy:**
- **Major versions** (v2.x.x): Breaking changes
- **Minor versions** (v1.x.x): New features, backward compatible
- **Patch versions** (v1.0.x): Bug fixes, backward compatible

**Version Headers:**
```http
API-Version: 1.0.0
Accept-Version: 1.0.0
```

---

## Performance Guidelines

### Request Optimization
- **Use pagination** for large datasets
- **Apply filters** to reduce response size
- **Cache responses** when appropriate
- **Batch operations** when possible

### Response Times
- **Authentication**: < 100ms
- **Simple queries**: < 200ms
- **Complex analytics**: < 1s
- **File exports**: < 5s

### Best Practices
1. **Implement exponential backoff** for retries
2. **Use HTTP caching headers** when available
3. **Compress requests** for large payloads
4. **Monitor rate limits** and adjust accordingly
5. **Use persistent connections** for multiple requests

---

## Security Considerations

### API Security Features
- **JWT Authentication** with configurable expiration
- **Role-based authorization** for all endpoints
- **Input validation** and sanitization
- **SQL injection prevention** via ORM
- **CORS configuration** for cross-origin requests
- **Rate limiting** to prevent abuse

### Security Best Practices
1. **Use HTTPS** in production
2. **Store tokens securely** (HttpOnly cookies recommended)
3. **Implement proper logout** to invalidate tokens
4. **Validate all inputs** on client and server
5. **Monitor for suspicious activity**
6. **Keep dependencies updated**

### Token Security
- **Short-lived access tokens** (15-60 minutes)
- **Longer-lived refresh tokens** (7-30 days)
- **Token rotation** on refresh
- **Secure token storage** recommendations

---

## Changelog

### Version 1.0.0 (Current)
- Initial API release
- Full authentication and authorization
- Complete evaluation management
- Workflow approval system
- Dashboard analytics
- Notification system
- Operation logging
- Swagger documentation

### Upcoming Features
- Real-time WebSocket support
- File upload/download endpoints
- Advanced search and filtering
- Bulk operations
- API webhooks
- Enhanced analytics
- Mobile app support

---

## Support & Contact

### API Support
- **Documentation**: This document and Swagger UI
- **Issues**: GitHub repository issues

### Response Times
- **Critical issues**: 2-4 hours
- **General support**: 1-2 business days
- **Feature requests**: Reviewed monthly

### Community
- **GitHub Discussions**: Feature requests and general questions
- **Stack Overflow**: Tag questions with `solution-evaluation-api`
- **Discord**: Real-time community support

---

*This documentation is automatically updated with each API release. Last updated: July 2025*