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

### Error Response
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