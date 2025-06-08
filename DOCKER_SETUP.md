# MySQL Docker Setup for SSD Evaluation System

This document explains how to set up and use the MySQL Docker container for testing the SSD Evaluation Management System.

## Prerequisites

- Docker Desktop installed and running
- Docker Compose (usually included with Docker Desktop)
- At least 1GB of free disk space for MySQL data

## Quick Start

### 1. Start MySQL Container

```bash
# Start MySQL and phpMyAdmin containers
./docker-mysql.sh start
```

This will:
- Pull MySQL 8.0 Docker image if not already present
- Create and start MySQL container with proper configuration
- Create and start phpMyAdmin container for web-based database management
- Initialize the database with basic schema
- Wait for MySQL to be fully ready

### 2. Access Database

**Web Interface (phpMyAdmin)**
- Open browser: http://localhost:8080
- Username: `root`
- Password: `ssd_eval_root_2024`

**Application Connection**
- Host: `localhost`
- Port: `3306`
- Database: `ssd_evaluation`
- Username: `ssd_eval_user`
- Password: `ssd_eval_pass_2024`

## Management Commands

```bash
./docker-mysql.sh start     # Start containers
./docker-mysql.sh stop      # Stop containers
./docker-mysql.sh status    # Show status
./docker-mysql.sh connect   # MySQL CLI
./docker-mysql.sh backup    # Create backup
./docker-mysql.sh help      # Show all commands
```

## Flask Integration

Add to your Flask configuration:

```python
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://ssd_eval_user:ssd_eval_pass_2024@localhost:3306/ssd_evaluation'
```

Required packages in `requirements.txt`:
```
PyMySQL>=1.0.2
SQLAlchemy>=1.4.0
Flask-SQLAlchemy>=2.5.1
``` 