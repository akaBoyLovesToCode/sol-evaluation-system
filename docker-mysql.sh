#!/bin/bash

# MySQL Docker Management Script for Product Evaluation System
# This script provides convenient commands to manage the MySQL Docker container

set -e  # Exit on any error

# Color codes for output formatting
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration variables
COMPOSE_FILE="docker-compose.yml"
MYSQL_CONTAINER="evaluation_mysql"
PHPMYADMIN_CONTAINER="evaluation_phpmyadmin"

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}=== $1 ===${NC}"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
}

# Function to start MySQL container
start_mysql() {
    print_header "Starting MySQL Container"
    check_docker
    
    if docker-compose -f "$COMPOSE_FILE" ps | grep -q "$MYSQL_CONTAINER.*Up"; then
        print_warning "MySQL container is already running"
    else
        print_status "Starting MySQL and phpMyAdmin containers..."
        docker-compose -f "$COMPOSE_FILE" up -d
        
        # Wait for MySQL to be ready
        print_status "Waiting for MySQL to be ready..."
        timeout=60
        while [ $timeout -gt 0 ]; do
            if docker exec "$MYSQL_CONTAINER" mysqladmin ping -h localhost -u root -peval_root_2024 >/dev/null 2>&1; then
                print_status "MySQL is ready!"
                break
            fi
            sleep 2
            timeout=$((timeout - 2))
        done
        
        if [ $timeout -le 0 ]; then
            print_error "MySQL failed to start within 60 seconds"
            exit 1
        fi
        
        print_status "MySQL is running on port 3306"
        print_status "phpMyAdmin is available at http://localhost:8080"
        print_status "Database: evaluation"
        print_status "Username: eval_user"
        print_status "Password: eval_pass_2024"
    fi
}

# Function to stop MySQL container
stop_mysql() {
    print_header "Stopping MySQL Container"
    check_docker
    
    print_status "Stopping MySQL and phpMyAdmin containers..."
    docker-compose -f "$COMPOSE_FILE" down
    print_status "Containers stopped successfully"
}

# Function to restart MySQL container
restart_mysql() {
    print_header "Restarting MySQL Container"
    stop_mysql
    start_mysql
}

# Function to show container status
status_mysql() {
    print_header "MySQL Container Status"
    check_docker
    
    echo "Container Status:"
    docker-compose -f "$COMPOSE_FILE" ps
    
    echo -e "\nContainer Logs (last 20 lines):"
    docker-compose -f "$COMPOSE_FILE" logs --tail=20 mysql
}

# Function to connect to MySQL CLI
connect_mysql() {
    print_header "Connecting to MySQL CLI"
    check_docker
    
    if ! docker-compose -f "$COMPOSE_FILE" ps | grep -q "$MYSQL_CONTAINER.*Up"; then
        print_error "MySQL container is not running. Start it first with: $0 start"
        exit 1
    fi
    
    print_status "Connecting to MySQL as root user..."
    docker exec -it "$MYSQL_CONTAINER" mysql -u root -peval_root_2024 evaluation
}

# Function to backup database
backup_mysql() {
    print_header "Creating Database Backup"
    check_docker
    
    if ! docker-compose -f "$COMPOSE_FILE" ps | grep -q "$MYSQL_CONTAINER.*Up"; then
        print_error "MySQL container is not running. Start it first with: $0 start"
        exit 1
    fi
    
    # Create backup directory if it doesn't exist
    mkdir -p backups
    
    # Generate backup filename with timestamp
    backup_file="backups/evaluation_$(date +%Y%m%d_%H%M%S).sql"
    
    print_status "Creating backup: $backup_file"
    docker exec "$MYSQL_CONTAINER" mysqldump -u root -peval_root_2024 --single-transaction --routines --triggers evaluation > "$backup_file"
    
    print_status "Backup created successfully: $backup_file"
}

# Function to restore database from backup
restore_mysql() {
    print_header "Restoring Database from Backup"
    
    if [ -z "$1" ]; then
        print_error "Please specify backup file: $0 restore <backup_file>"
        exit 1
    fi
    
    backup_file="$1"
    if [ ! -f "$backup_file" ]; then
        print_error "Backup file not found: $backup_file"
        exit 1
    fi
    
    check_docker
    
    if ! docker-compose -f "$COMPOSE_FILE" ps | grep -q "$MYSQL_CONTAINER.*Up"; then
        print_error "MySQL container is not running. Start it first with: $0 start"
        exit 1
    fi
    
    print_warning "This will overwrite the current database. Are you sure? (y/N)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        print_status "Restore cancelled"
        exit 0
    fi
    
    print_status "Restoring from backup: $backup_file"
    docker exec -i "$MYSQL_CONTAINER" mysql -u root -peval_root_2024 evaluation < "$backup_file"
    
    print_status "Database restored successfully"
}

# Function to show logs
logs_mysql() {
    print_header "MySQL Container Logs"
    check_docker
    
    # Follow logs if -f flag is provided
    if [ "$1" = "-f" ]; then
        docker-compose -f "$COMPOSE_FILE" logs -f mysql
    else
        docker-compose -f "$COMPOSE_FILE" logs mysql
    fi
}

# Function to clean up (remove containers and volumes)
clean_mysql() {
    print_header "Cleaning Up MySQL Environment"
    
    print_warning "This will remove all containers and data volumes. Are you sure? (y/N)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        print_status "Cleanup cancelled"
        exit 0
    fi
    
    check_docker
    
    print_status "Stopping and removing containers..."
    docker-compose -f "$COMPOSE_FILE" down -v --remove-orphans
    
    print_status "Removing named volumes..."
    docker volume rm evaluation_mysql_data 2>/dev/null || true
    
    print_status "Cleanup completed"
}

# Function to show help
show_help() {
    echo "MySQL Docker Management Script for Product Evaluation System"
    echo ""
    echo "Usage: $0 <command> [options]"
    echo ""
    echo "Commands:"
    echo "  start     - Start MySQL and phpMyAdmin containers"
    echo "  stop      - Stop all containers"
    echo "  restart   - Restart all containers"
    echo "  status    - Show container status and recent logs"
    echo "  connect   - Connect to MySQL CLI"
    echo "  backup    - Create database backup"
    echo "  restore   - Restore database from backup file"
    echo "  logs      - Show container logs (use -f to follow)"
    echo "  clean     - Remove containers and volumes (destructive)"
    echo "  help      - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start                           # Start MySQL"
    echo "  $0 backup                          # Create backup"
    echo "  $0 restore backups/backup.sql      # Restore from backup"
    echo "  $0 logs -f                         # Follow logs"
    echo ""
    echo "Connection Information:"
    echo "  MySQL Host: localhost:3306"
    echo "  Database: evaluation"
    echo "  Username: eval_user"
    echo "  Password: eval_pass_2024"
    echo "  phpMyAdmin: http://localhost:8080"
}

# Main script logic
case "$1" in
    start)
        start_mysql
        ;;
    stop)
        stop_mysql
        ;;
    restart)
        restart_mysql
        ;;
    status)
        status_mysql
        ;;
    connect)
        connect_mysql
        ;;
    backup)
        backup_mysql
        ;;
    restore)
        restore_mysql "$2"
        ;;
    logs)
        logs_mysql "$2"
        ;;
    clean)
        clean_mysql
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac 