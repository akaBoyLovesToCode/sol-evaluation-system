# Solution Evaluation System

A comprehensive web-based system for managing product solution evaluations with workflow automation, real-time notifications, and collaborative features.

## 🌟 Features

### Core Functionality
- **Evaluation Management**: Create, track, and manage product evaluations through their lifecycle
- **Two Evaluation Types**:
  - New Product: DOE → PPQ → PRQ (parallel) → Part Leader Approval → Group Leader Approval
  - Mass Production: Production Test → AQL → Pass (no approval needed)
- **Workflow Automation**: Automated approval workflows with role-based permissions
- **Real-time Dashboard**: Analytics and statistics with visual charts
- **Multi-language Support**: English and Chinese interfaces

### Collaboration Features
- **Message Center**: Centralized notification hub for all system activities
- **@Mentions**: Tag users in comments and evaluations for instant notifications
- **Comments System**: Threaded discussions on evaluations with reply support
- **Task Assignment**: Assign head officers and SCS colleagues to evaluations

### Notification System
- **Real-time Notifications**: Instant alerts for mentions, approvals, and status changes
- **Mention Notifications**: Get notified when someone @mentions you
- **Approval Requests**: Automatic notifications to approvers
- **Status Updates**: Track evaluation progress through notifications

## 🛠️ Tech Stack

### Frontend
- **Vue 3** with Composition API
- **Element Plus** UI framework
- **Vue Router** for navigation
- **Pinia** for state management
- **Axios** for API communication
- **Vue I18n** for internationalization
- **ECharts** for data visualization
- **Date-fns** for date formatting

### Backend
- **Flask** (Python web framework)
- **SQLAlchemy** ORM
- **Flask-JWT-Extended** for authentication
- **MySQL** database
- **Alembic** for database migrations
- **Flask-CORS** for cross-origin support

## 📦 Installation

### Prerequisites
- Python 3.11+
- Node.js 18+
- MySQL 8.0+

### Backend Setup

1. Navigate to backend directory:
```bash
cd evaluation/backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure database:
```bash
# Create MySQL database
mysql -u root -p
CREATE DATABASE evaluation_system;
```

5. Set environment variables:
```bash
cp .env.example .env
# Edit .env with your database credentials
```

6. Run migrations:
```bash
alembic upgrade head
```

7. Initialize database with sample data:
```bash
python init_db.py
```

8. Start the server:
```bash
python run.py
```

The backend will be available at `http://localhost:5001`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd evaluation/frontend
```

2. Install dependencies:
```bash
npm install
```

3. Configure API endpoint:
```bash
# Edit src/utils/api.js to set the backend URL
```

4. Start development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## 👥 User Roles

| Role | Permissions |
|------|------------|
| **Admin** | Full system access, user management, system configuration |
| **Group Leader** | Final approval authority, view all evaluations |
| **Part Leader** | First-level approval, department oversight |
| **User** | Create and manage own evaluations |

## 📱 Key Features

### 1. Message Center
- **Unified Inbox**: All notifications in one place
- **Filter Options**: Filter by type (mentions, approvals, status changes)
- **Mark as Read/Unread**: Manage notification status
- **Real-time Updates**: Auto-refresh every 30 seconds
- **Quick Actions**: Navigate directly to related evaluations

### 2. @Mention System
- **User Tagging**: Use @username to mention users in comments
- **Auto-complete**: Smart suggestions while typing
- **Instant Notifications**: Mentioned users receive immediate alerts
- **Context Preservation**: See the full context of mentions
- **Reply Threading**: Maintain conversation context

### 3. Evaluation Comments
- **Threaded Discussions**: Nested comment replies
- **Rich Mentions**: @mention users in comments
- **Edit History**: Track edited comments
- **Soft Delete**: Remove comments without losing thread context
- **Real-time Updates**: See new comments instantly

### 4. Task Assignment
- **Head Officer**: Assign evaluation responsibility
- **SCS Colleague**: Assign technical assistance
- **Automatic Notifications**: Assigned users are notified immediately
- **Progress Tracking**: Monitor assigned evaluations

## 🗄️ Database Schema

### Core Tables
- **users**: User accounts and profiles
- **evaluations**: Main evaluation records
- **messages**: Notification and messaging system
- **comments**: Evaluation discussion threads
- **mentions**: User mention tracking
- **operation_logs**: Audit trail

### Key Relationships
- Evaluations have multiple comments
- Comments support nested replies
- Mentions link users to content
- Messages track all notifications

## 📊 API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `POST /api/auth/refresh` - Refresh token

### Evaluations
- `GET /api/evaluations` - List evaluations
- `POST /api/evaluations` - Create evaluation
- `PUT /api/evaluations/{id}` - Update evaluation
- `DELETE /api/evaluations/{id}` - Delete evaluation

### Comments
- `GET /api/evaluations/{id}/comments` - Get evaluation comments
- `POST /api/evaluations/{id}/comments` - Create comment with @mentions
- `PUT /api/comments/{id}` - Edit comment
- `DELETE /api/comments/{id}` - Delete comment

### Notifications
- `GET /api/notifications` - Get user notifications
- `PUT /api/notifications/{id}/read` - Mark as read
- `PUT /api/notifications/mark-all-read` - Mark all as read
- `DELETE /api/notifications/{id}` - Delete notification

### Dashboard
- `GET /api/dashboard/overview` - Dashboard statistics
- `GET /api/dashboard/statistics` - Detailed analytics

## 🎨 Frontend Structure

```
frontend/src/
├── views/
│   ├── Dashboard.vue       # Main dashboard
│   ├── Evaluations.vue     # Evaluation list
│   ├── NewEvaluation.vue   # Create/edit evaluation
│   ├── EvaluationDetail.vue # Evaluation details with comments
│   ├── Messages.vue        # Message center
│   └── Users.vue          # User management
├── components/
│   ├── MainLayout.vue     # App layout
│   └── AnimatedContainer.vue # Animations
├── stores/
│   └── auth.js            # Authentication state
├── utils/
│   ├── api.js             # API client
│   └── i18n.js            # Internationalization
└── locales/
    ├── en.json            # English translations
    └── zh.json            # Chinese translations
```

## 🚀 Deployment

### Production Build

Frontend:
```bash
cd frontend
npm run build
# Deploy dist/ folder to web server
```

Backend:
```bash
cd backend
# Use Gunicorn for production
gunicorn -w 4 -b 0.0.0.0:5001 run:app
```

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d
```

## 🔧 Configuration

### Environment Variables

Backend (.env):
```
DATABASE_URL=mysql://user:password@localhost/evaluation_system
JWT_SECRET_KEY=your-secret-key
FLASK_ENV=production
```

Frontend (.env):
```
VITE_API_BASE_URL=http://localhost:5001
VITE_APP_TITLE=Solution Evaluation System
```

## 📝 Default Credentials

| Username | Password | Role |
|----------|----------|------|
| admin | admin123 | Admin |
| john.doe | password123 | Group Leader |
| jane.smith | password123 | Part Leader |
| bob.wilson | password123 | User |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is proprietary software. All rights reserved.

## 📞 Support

For support and questions, please contact the development team.

## 🔄 Recent Updates

### Version 2.0.0 (2024-01-15)
- ✨ Added Message Center with real-time notifications
- ✨ Implemented @mention system for user tagging
- ✨ Added comment system with threaded discussions
- ✨ Task assignment with head officer and SCS colleague roles
- 🔧 Removed expected_end_date field
- 🔧 Enhanced notification system with mention support
- 🎨 Improved UI/UX for collaboration features
- 📝 Updated API documentation

### Version 1.0.0 (2024-01-01)
- 🚀 Initial release
- ✅ Core evaluation management
- ✅ Workflow automation
- ✅ Dashboard and analytics
- ✅ User management
- ✅ Multi-language support