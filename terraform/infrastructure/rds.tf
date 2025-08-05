# RDS PostgreSQL Instance
resource "aws_db_instance" "main" {
  identifier     = "${var.project_name}-db"
  engine         = "postgres"
  engine_version = "16.1"
  instance_class = var.db_instance_class

  allocated_storage     = var.db_allocated_storage
  max_allocated_storage = var.db_allocated_storage * 2  # Allow some growth
  storage_encrypted     = true
  storage_type          = "gp3"

  db_name  = var.db_name
  username = var.db_username
  password = random_password.db_password.result

  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name

  # Portfolio optimization: minimal backup for cost savings
  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"

  # Portfolio optimization: allow deletion for easy cleanup
  skip_final_snapshot       = true
  deletion_protection       = false
  delete_automated_backups  = true

  # Performance monitoring
  performance_insights_enabled = false  # Save cost on small instance
  monitoring_interval         = 0       # Save cost on detailed monitoring

  tags = {
    Name = "${var.project_name}-database"
  }
}

# Store database password in SSM Parameter Store
resource "aws_ssm_parameter" "db_password" {
  name        = "/${var.project_name}/${var.environment}/database-password"
  description = "Database password for ${var.project_name}"
  type        = "SecureString"
  value       = random_password.db_password.result

  tags = {
    Name = "${var.project_name}-db-password"
  }
}

# Store database URL in SSM Parameter Store
resource "aws_ssm_parameter" "database_url" {
  name        = "/${var.project_name}/${var.environment}/database-url"
  description = "Database URL for ${var.project_name}"
  type        = "SecureString"
  value       = "postgresql://${var.db_username}:${random_password.db_password.result}@${aws_db_instance.main.endpoint}:${aws_db_instance.main.port}/${var.db_name}"

  tags = {
    Name = "${var.project_name}-database-url"
  }
}