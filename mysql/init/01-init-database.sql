-- Initial database setup for SSD Evaluation System
-- This script runs automatically when the MySQL container starts for the first time

-- Ensure we're using the correct database
USE ssd_evaluation;

-- Set session variables for consistent character handling
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

-- Create additional database user with specific privileges if needed
-- (The main user is already created via environment variables)

-- Grant necessary privileges to the application user
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, INDEX, ALTER, CREATE TEMPORARY TABLES, LOCK TABLES ON ssd_evaluation.* TO 'ssd_eval_user'@'%';

-- Create a read-only user for reporting purposes
CREATE USER IF NOT EXISTS 'ssd_eval_readonly'@'%' IDENTIFIED BY 'ssd_eval_readonly_2024';
GRANT SELECT ON ssd_evaluation.* TO 'ssd_eval_readonly'@'%';

-- Flush privileges to ensure changes take effect
FLUSH PRIVILEGES;

-- Create initial tables structure (basic example - adjust based on your actual schema)
-- Note: In production, you should use Flask-Migrate for schema management

-- Users table for authentication
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('Admin', 'Group Leader', 'Part Leader', 'User') NOT NULL DEFAULT 'User',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_role (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Evaluations table for storing evaluation records
CREATE TABLE IF NOT EXISTS evaluations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    evaluation_type ENUM('New Product', 'Mass Production', 'PGM', 'Material Change') NOT NULL,
    status ENUM('Draft', 'Pending', 'In Progress', 'Completed', 'Rejected') NOT NULL DEFAULT 'Draft',
    created_by INT NOT NULL,
    assigned_to INT,
    part_leader_id INT,
    group_leader_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    due_date DATE,
    completed_at TIMESTAMP NULL,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE RESTRICT,
    FOREIGN KEY (assigned_to) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (part_leader_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (group_leader_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_evaluation_type (evaluation_type),
    INDEX idx_status (status),
    INDEX idx_created_by (created_by),
    INDEX idx_assigned_to (assigned_to),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert default admin user (password should be changed after first login)
-- Note: This is a placeholder - in production, use proper password hashing
INSERT IGNORE INTO users (username, email, password_hash, role) VALUES 
('admin', 'admin@company.com', 'placeholder_hash', 'Admin');

-- Create a test user for development
INSERT IGNORE INTO users (username, email, password_hash, role) VALUES 
('testuser', 'test@company.com', 'placeholder_hash', 'User');

-- Log the initialization completion
SELECT 'Database initialization completed successfully' AS status; 