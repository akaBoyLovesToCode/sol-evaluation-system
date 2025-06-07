# SSD Product Evaluation Management System

A web application for managing SSD product evaluations including new product evaluations and mass production evaluations (PGM, material changes, etc.) with statistical analysis and data visualization capabilities.

## System Architecture

- **Frontend**: Vue 3 + Element Plus + Tailwind CSS + ECharts
- **Backend**: Flask + SQLAlchemy + MySQL
- **Database**: MySQL 8.0+
- **Internationalization**: Chinese/English/Korean support

## Project Structure

```
ssd-evaluation-system/
├── frontend/                 # Vue 3 frontend application
│   ├── src/
│   │   ├── components/      # Reusable components
│   │   ├── views/          # Page components
│   │   ├── router/         # Vue Router configuration
│   │   ├── store/          # Pinia store
│   │   ├── api/            # API service layer
│   │   ├── utils/          # Utility functions
│   │   ├── locales/        # i18n translation files
│   │   └── assets/         # Static assets
│   ├── public/
│   └── package.json
├── backend/                 # Flask backend application
│   ├── app/
│   │   ├── models/         # SQLAlchemy models
│   │   ├── api/            # API endpoints
│   │   ├── services/       # Business logic
│   │   ├── utils/          # Utility functions
│   │   └── __init__.py
│   ├── migrations/         # Database migrations
│   ├── config.py          # Configuration settings
│   ├── requirements.txt   # Python dependencies
│   └── run.py            # Application entry point
└── docs/                  # Documentation
```

## Features

### Phase 1: Core Functionality
- [x] User authentication and authorization
- [x] Basic evaluation CRUD operations
- [x] Role-based access control (Admin, Group Leader, Part Leader, User)
- [x] Basic UI with Element Plus + Tailwind CSS

### Phase 2: Workflow Management
- [ ] Evaluation workflow engine
- [ ] Approval process (Part Leader → Group Leader)
- [ ] Status management
- [ ] In-app notification system

### Phase 3: Analytics & Reporting
- [ ] Statistical analysis
- [ ] Data visualization with charts
- [ ] Automated report generation
- [ ] Export functionality

### Phase 4: System Enhancement
- [ ] Operation logging
- [ ] Data backup system
- [ ] Full internationalization (CN/EN/KR)
- [ ] Performance optimization

## Quick Start

### Prerequisites
- Node.js 16+
- Python 3.8+
- MySQL 8.0+

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
python run.py
```

### Database Setup
```bash
# Create database
mysql -u root -p -e "CREATE DATABASE ssd_evaluation CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# Run migrations
cd backend
flask db upgrade
```

## Deployment

This system is designed for internal network deployment without external dependencies.

## License

Internal use only. 