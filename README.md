# Product Evaluation Management System

A modern web application for managing product evaluations including new product evaluations and mass production evaluations (PGM, material changes, etc.) with comprehensive statistical analysis and interactive data visualization capabilities.

## System Architecture

- **Frontend**: Vue 3.5.17 + Element Plus 2.10.4 + Tailwind CSS 4.1.11 + ECharts 5.6.0
- **Backend**: Flask + SQLAlchemy + MySQL + JWT Authentication
- **Database**: MySQL 8.0+
- **Build Tools**: Vite 7.0.4 (Frontend), Docker (Containerization)
- **Internationalization**: Complete Chinese/English/Korean support

## Key Features

### 🔐 Authentication & Authorization
- JWT-based authentication system with refresh tokens
- Role-based access control (RBAC)
- Four-tier permission system: Admin > Group Leader > Part Leader > User
- Token blacklisting and session management

### 📊 Data Visualization & Analytics
- Interactive charts powered by ECharts 5.6
- Responsive dashboard with real-time statistics
- Custom chart utilities library with export functionality
- Monthly trend analysis and status distribution charts

### 📝 Evaluation Workflow Management
- Two-tier approval process for new product evaluations
- Direct completion for mass production evaluations
- Comprehensive status tracking and history
- Automated workflow transitions
- Operation logging and audit trails

### 🌍 Multi-language Support
- Complete internationalization (i18n) implementation
- Dynamic language switching: Chinese/English/Korean
- Localized date formats and number formatting
- RTL language support ready

### 🎨 Modern UI/UX
- Responsive design with mobile support
- Glassmorphism effects and gradient backgrounds
- Smooth animations and transitions
- Dark mode ready architecture
- Customizable theme system

### ⚡ Performance & Optimization
- Code splitting and lazy loading
- Optimized bundle size with chunk splitting
- Image lazy loading and CDN optimization
- Database query optimization
- Comprehensive caching strategies

## Project Structure

```
evaluation-system/
├── frontend/                    # Vue 3 frontend application
│   ├── src/
│   │   ├── components/         # Reusable components
│   │   │   └── AnimatedContainer.vue
│   │   ├── views/              # Page components
│   │   │   ├── Dashboard.vue   # Interactive dashboard
│   │   │   ├── Evaluations.vue # Evaluation management
│   │   │   ├── Login.vue       # Authentication
│   │   │   └── ...
│   │   ├── router/             # Vue Router configuration
│   │   ├── stores/             # Pinia state management
│   │   │   └── auth.js         # Authentication store
│   │   ├── utils/              # Utility functions
│   │   │   ├── api.js          # HTTP client
│   │   │   └── charts.js       # Chart utilities
│   │   ├── locales/            # i18n translation files
│   │   │   ├── zh.json         # Chinese
│   │   │   ├── en.json         # English
│   │   │   └── ko.json         # Korean
│   │   └── styles/             # Global styles
│   ├── vite.config.js          # Vite configuration
│   ├── tailwind.config.js      # Tailwind CSS config
│   └── package.json
├── backend/                     # Flask backend application
│   ├── app/
│   │   ├── models/             # SQLAlchemy models
│   │   │   ├── user.py         # User model
│   │   │   ├── evaluation.py   # Evaluation model
│   │   │   └── operation_log.py # Audit logs
│   │   ├── api/                # API endpoints
│   │   │   ├── auth.py         # Authentication
│   │   │   ├── evaluation.py   # Evaluation CRUD
│   │   │   ├── dashboard.py    # Analytics
│   │   │   └── workflow.py     # Workflow management
│   │   ├── services/           # Business logic
│   │   │   ├── analytics_service.py
│   │   │   ├── workflow_service.py
│   │   │   └── notification_service.py
│   │   ├── utils/              # Utility functions
│   │   │   ├── decorators.py   # Auth decorators
│   │   │   ├── helpers.py      # Helper functions
│   │   │   └── validators.py   # Input validation
│   │   └── __init__.py         # App factory
│   ├── config.py               # Configuration settings
│   ├── requirements.txt        # Python dependencies
│   ├── Dockerfile              # Container config
│   └── run.py                 # Application entry point
├── docker-compose.yml          # Docker orchestration
└── README.md                   # This file
```

## Development Progress

### ✅ Phase 1: Core Functionality
- [x] User authentication and authorization (JWT)
- [x] Basic evaluation CRUD operations
- [x] Role-based access control (Admin, Group Leader, Part Leader, User)
- [x] Modern UI with Element Plus + Tailwind CSS

### ✅ Phase 2: Workflow Management
- [x] Evaluation workflow engine
- [x] Two-tier approval process (Part Leader → Group Leader)
- [x] Comprehensive status management
- [x] In-app notification system

### ✅ Phase 3: Analytics & Reporting
- [x] Statistical analysis with dedicated service
- [x] Interactive data visualization with ECharts
- [x] Automated report generation
- [x] Chart export functionality

### ✅ Phase 4: System Enhancement
- [x] Comprehensive operation logging
- [x] Data backup system
- [x] Full internationalization (CN/EN/KR)
- [x] Performance optimization with code splitting
- [x] Docker containerization
- [x] Custom chart utilities library
- [x] Swagger API documentation

### 🔄 Phase 5: Advanced Features (In Progress)
- [ ] Real-time notifications via WebSocket
- [ ] Advanced analytics dashboards
- [ ] Email notification system
- [ ] File attachment management
- [ ] API rate limiting and monitoring

## Quick Start

### Prerequisites
- Node.js 16+ and npm 8+
- Python 3.8+
- MySQL 8.0+
- Docker (optional, for containerized deployment)

### Option 1: Manual Setup

#### Frontend Setup
```bash
cd frontend
npm install
npm run dev
# Application runs at http://localhost:3000
```

#### Backend Setup
```bash
cd backend
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment (create .env file)
cp .env.example .env
# Edit .env with your database credentials

# Initialize database
flask db upgrade

# Start server
python run.py
# API runs at http://localhost:5001
```

### Option 2: Docker Setup

```bash
# Start MySQL database
docker-compose up -d mysql

# Wait for MySQL to be ready, then start application
# Frontend and backend can be run manually or containerized
```

### Database Setup
```bash
# Create database with proper character set
mysql -u root -p -e "CREATE DATABASE evaluation CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# Run migrations (from backend directory)
flask db upgrade

# Optional: Create initial admin user
python -c "from app.models import User; from app import create_app, db; app=create_app(); app.app_context().push(); user=User(username='admin', email='admin@example.com', full_name='Administrator', role='admin'); user.set_password('admin123'); db.session.add(user); db.session.commit(); print('Admin user created')"
```

## Deployment

### Production Environment

This system is designed for internal network deployment with the following options:

#### Option 1: Traditional Deployment
- **Frontend**: Build and serve with Nginx/Apache
- **Backend**: Deploy with Gunicorn + Nginx
- **Database**: MySQL 8.0 with proper tuning

#### Option 2: Docker Deployment
```bash
# Production deployment with Docker Compose
docker-compose -f docker-compose.prod.yml up -d

# Scale services as needed
docker-compose -f docker-compose.prod.yml up -d --scale backend=3
```

#### Option 3: Kubernetes (Enterprise)
- Helm charts available for Kubernetes deployment
- Support for horizontal pod autoscaling
- Persistent volume claims for database storage

### Environment Configuration

**Frontend (.env.production):**
```env
VITE_API_BASE_URL=https://your-api-domain.com
VITE_APP_TITLE=Product Evaluation System
```

**Backend (.env):**
```env
FLASK_ENV=production
SECRET_KEY=your-production-secret-key
JWT_SECRET_KEY=your-jwt-secret-key
MYSQL_HOST=your-mysql-host
MYSQL_DATABASE=evaluation
```

### Security Considerations
- JWT tokens with appropriate expiration times
- HTTPS enforcement in production
- Database connection encryption
- CORS configuration for production domains
- Regular security updates and monitoring

## Technology Decisions

### Why Vue 3?
- **Composition API**: Better logic reuse and TypeScript support
- **Performance**: Smaller bundle size and faster rendering
- **Ecosystem**: Rich ecosystem with Element Plus and Vue Router

### Why Flask?
- **Simplicity**: Lightweight and easy to customize
- **Flexibility**: Can be extended with various libraries
- **SQLAlchemy**: Powerful ORM with migration support

### Why ECharts?
- **Performance**: Handles large datasets efficiently
- **Customization**: Highly customizable with rich APIs
- **Framework Agnostic**: Can be used without Vue wrappers

### Why Tailwind CSS?
- **Utility-first**: Rapid UI development
- **Consistency**: Design system built-in
- **Optimization**: Automatic purging of unused styles

## Contributing

### Development Guidelines
1. Follow conventional commit messages
2. Use TypeScript for new Vue components
3. Write tests for new features
4. Update documentation when adding features
5. Follow the existing code style and patterns

### Code Quality
- ESLint and Prettier for frontend
- Black and isort for backend
- Pre-commit hooks for code formatting
- Comprehensive test coverage

## Support

For internal support and questions:
- Check the individual README files in `/frontend` and `/backend`
- Review the API documentation in backend
- Consult the troubleshooting guides

## License

Internal use only - Proprietary software for company use. 