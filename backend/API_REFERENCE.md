# API Quick Reference

## Base URL
- **Development**: `http://localhost:5001`
- **Production**: `https://your-api-domain.com`

## Authentication
All protected endpoints require JWT token in header:
```http
Authorization: Bearer <access_token>
```

## Quick Start
```bash
# Login
curl -X POST /api/auth/login -d '{"username":"demo","password":"demo123"}'

# Get evaluations (with token)
curl -H "Authorization: Bearer <token>" /api/evaluations
```

## Core Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login` | Login with username/password |
| POST | `/api/auth/refresh` | Refresh access token |
| POST | `/api/auth/logout` | Logout and invalidate token |

### Users
| Method | Endpoint | Description | Auth | Role |
|--------|----------|-------------|------|------|
| GET | `/api/users` | List users | ✅ | Any |
| GET | `/api/users/{id}` | Get user details | ✅ | Any |
| POST | `/api/users` | Create user | ✅ | Admin |
| PUT | `/api/users/{id}` | Update user | ✅ | Admin/Self |
| DELETE | `/api/users/{id}` | Deactivate user | ✅ | Admin |

### Evaluations
| Method | Endpoint | Description | Auth | Role |
|--------|----------|-------------|------|------|
| GET | `/api/evaluations` | List evaluations | ✅ | Any |
| GET | `/api/evaluations/{id}` | Get evaluation | ✅ | Any |
| POST | `/api/evaluations` | Create evaluation | ✅ | User+ |
| PUT | `/api/evaluations/{id}` | Update evaluation | ✅ | Owner/Leader+ |
| DELETE | `/api/evaluations/{id}` | Delete evaluation | ✅ | Owner/Admin |

### Workflow
| Method | Endpoint | Description | Auth | Role |
|--------|----------|-------------|------|------|
| POST | `/api/workflow/submit` | Submit for approval | ✅ | Owner |
| POST | `/api/workflow/approve` | Approve evaluation | ✅ | Leader+ |
| POST | `/api/workflow/reject` | Reject evaluation | ✅ | Leader+ |
| GET | `/api/workflow/pending` | Get pending approvals | ✅ | Leader+ |

### Dashboard & Analytics
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/dashboard/stats` | Dashboard statistics | ✅ |
| GET | `/api/dashboard/charts` | Chart data | ✅ |
| POST | `/api/analytics/export` | Export data | ✅ |

### Notifications
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/notifications` | Get notifications | ✅ |
| POST | `/api/notifications/{id}/read` | Mark as read | ✅ |
| POST | `/api/notifications/mark-all-read` | Mark all as read | ✅ |

## Common Query Parameters

### Pagination
- `page`: Page number (default: 1)
- `per_page`: Items per page (default: 20, max: 100)

### Filtering
- `status`: Filter by status
- `type`: Filter by type
- `date_from`: Start date (YYYY-MM-DD)
- `date_to`: End date (YYYY-MM-DD)
- `search`: Search term

### Examples
```bash
GET /api/evaluations?status=in_review&page=2&per_page=10
GET /api/users?role=part_leader&is_active=true
GET /api/dashboard/stats?period=month
```

## Response Format

### Success Response
```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": {
    // Response data
  }
}
```

## 9. Mentions and Notifications

### 9.1 Get User Notifications

**Endpoint:** `GET /api/notifications`

**Description:** Get notifications for the current user, including mentions

**Headers:**
- `Authorization: Bearer {access_token}` (required)

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `limit` | `integer` | No | Maximum number of notifications (default: 50) |
| `status` | `string` | No | Filter by status: unread, read |

**Success Response (200):**
```json
{
  "notifications": [
    {
      "id": 1,
      "title": "@john.doe mentioned you in evaluation EV2024001",
      "content": "John Doe mentioned you in a comment on evaluation EV2024001...",
      "message_type": "mention",
      "priority": "normal",
      "is_read": false,
      "created_at": "2024-01-15T10:30:00Z",
      "sender_name": "John Doe",
      "evaluation_number": "EV2024001"
    }
  ],
  "unread_count": 5,
  "total_returned": 10
}
```

### 9.2 Mark Notification as Read

**Endpoint:** `PUT /api/notifications/{message_id}/read`

**Description:** Mark a specific notification as read

**Headers:**
- `Authorization: Bearer {access_token}` (required)

**Success Response (200):**
```json
{
  "message": "Notification marked as read",
  "message_id": 123
}
```

### 9.3 Mark All Notifications as Read

**Endpoint:** `PUT /api/notifications/mark-all-read`

**Description:** Mark all notifications as read for the current user

**Headers:**
- `Authorization: Bearer {access_token}` (required)

**Success Response (200):**
```json
{
  "message": "Marked 10 notifications as read",
  "marked_count": 10
}
```

## 10. Comments API

### 10.1 Get Evaluation Comments

**Endpoint:** `GET /api/evaluations/{evaluation_id}/comments`

**Description:** Get comments for a specific evaluation

**Headers:**
- `Authorization: Bearer {access_token}` (required)

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `page` | `integer` | No | Page number for pagination (default: 1) |
| `per_page` | `integer` | No | Items per page (default: 20) |
| `include_replies` | `boolean` | No | Include nested replies (default: true) |

**Success Response (200):**
```json
{
  "comments": [
    {
      "id": 1,
      "evaluation_id": 123,
      "user_id": 456,
      "content": "Great progress on this evaluation! @jane.smith can you review the test results?",
      "user_name": "John Doe",
      "user_username": "john.doe",
      "created_at": "2024-01-15T10:30:00Z",
      "is_edited": false,
      "reply_count": 2,
      "mention_count": 1,
      "replies": [
        {
          "id": 2,
          "content": "Sure, I'll review them today.",
          "user_name": "Jane Smith",
          "user_username": "jane.smith",
          "created_at": "2024-01-15T11:00:00Z"
        }
      ]
    }
  ],
  "total": 25,
  "page": 1,
  "per_page": 20,
  "total_pages": 2
}
```

### 10.2 Create Comment

**Endpoint:** `POST /api/evaluations/{evaluation_id}/comments`

**Description:** Create a new comment on an evaluation with optional @mentions

**Headers:**
- `Authorization: Bearer {access_token}` (required)
- `Content-Type: application/json` (required)

**Request Body:**
```json
{
  "content": "The test results look good. @jane.smith please proceed with the next phase.",
  "mentioned_usernames": ["jane.smith"],
  "parent_comment_id": null
}
```

**Success Response (201):**
```json
{
  "message": "Comment created successfully",
  "comment": {
    "id": 3,
    "content": "The test results look good. @jane.smith please proceed with the next phase.",
    "user_name": "John Doe",
    "user_username": "john.doe",
    "created_at": "2024-01-15T14:00:00Z",
    "mention_count": 1
  }
}
```

### 10.3 Edit Comment

**Endpoint:** `PUT /api/comments/{comment_id}`

**Description:** Edit an existing comment

**Headers:**
- `Authorization: Bearer {access_token}` (required)
- `Content-Type: application/json` (required)

**Request Body:**
```json
{
  "content": "Updated comment content with @new.mention",
  "mentioned_usernames": ["new.mention"]
}
```

**Success Response (200):**
```json
{
  "message": "Comment updated successfully",
  "comment": {
    "id": 3,
    "content": "Updated comment content with @new.mention",
    "is_edited": true,
    "edited_at": "2024-01-15T15:00:00Z"
  }
}
```

### 10.4 Delete Comment

**Endpoint:** `DELETE /api/comments/{comment_id}`

**Description:** Soft delete a comment (content replaced with "[Comment deleted]")

**Headers:**
- `Authorization: Bearer {access_token}` (required)

**Success Response (200):**
```json
{
  "message": "Comment deleted successfully"
}
```

### 10.5 Get Comment Replies

**Endpoint:** `GET /api/comments/{comment_id}/replies`

**Description:** Get direct replies to a specific comment

**Headers:**
- `Authorization: Bearer {access_token}` (required)

**Success Response (200):**
```json
{
  "replies": [
    {
      "id": 4,
      "content": "I agree with this assessment.",
      "user_name": "Jane Smith",
      "created_at": "2024-01-15T16:00:00Z"
    }
  ],
  "total": 2
}
```

### 10.6 Get Comment Tree

**Endpoint:** `GET /api/comments/{comment_id}/tree`

**Description:** Get complete nested reply tree for a comment

**Headers:**
- `Authorization: Bearer {access_token}` (required)

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `max_depth` | `integer` | No | Maximum nesting depth (default: 5) |

**Success Response (200):**
```json
{
  "comment": {
    "id": 1,
    "content": "Initial comment",
    "user_name": "John Doe"
  },
  "reply_tree": [
    {
      "id": 2,
      "content": "First reply",
      "replies": [
        {
          "id": 3,
          "content": "Nested reply",
          "replies": []
        }
      ]
    }
  ],
  "total_replies": 2
}
```

## 11. Error Responses
```json
{
  "success": false,
  "message": "Human readable error",
  "error": "ERROR_CODE",
  "details": {
    "field": "Validation error details"
  }
}
```

## Status Codes
- `200` - OK
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `422` - Validation Error
- `500` - Server Error

## Evaluation Status Flow
```
draft → submitted → in_review → approved/rejected → completed
```

## User Roles (Ascending Permissions)
1. **user** - Basic operations
2. **part_leader** - First-level approvals
3. **group_leader** - Final approvals
4. **admin** - System administration

## Rate Limits
- Authenticated: 1000/hour
- Auth endpoints: 10/minute
- Export operations: 100/hour

## Development URLs
- **API Base**: http://localhost:5001
- **Swagger UI**: http://localhost:5001/api/docs
- **Health Check**: http://localhost:5001/api/health

## Environment Variables
```bash
DATABASE_URL=mysql://user:pass@host/db
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
FLASK_ENV=development
```

## Testing with cURL

### Login Flow
```bash
# 1. Login
response=$(curl -s -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"demo123"}')

# 2. Extract token
token=$(echo $response | jq -r '.data.access_token')

# 3. Use token
curl -H "Authorization: Bearer $token" \
  http://localhost:5001/api/evaluations
```

### Common Operations
```bash
# Get dashboard stats
curl -H "Authorization: Bearer $token" \
  http://localhost:5001/api/dashboard/stats

# Create evaluation
curl -X POST -H "Authorization: Bearer $token" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test","type":"new_product","priority":"medium"}' \
  http://localhost:5001/api/evaluations

# Get pending approvals
curl -H "Authorization: Bearer $token" \
  http://localhost:5001/api/workflow/pending
```

## Error Troubleshooting

### Common Issues
- **401 Unauthorized**: Check token format and expiration
- **403 Forbidden**: Insufficient role permissions
- **422 Validation Error**: Check request data format
- **429 Rate Limited**: Reduce request frequency

### Debug Mode
Set `FLASK_DEBUG=True` for detailed error responses.

## Related Documentation
- [Full API Documentation](../docs/API.md)
- [Backend README](./README.md)
- [Production Deployment](../docs/PRODUCTION_DEPLOYMENT.md)