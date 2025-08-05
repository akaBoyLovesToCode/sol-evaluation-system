# Development Environment Configuration

# General
aws_region   = "us-east-1"
environment  = "dev"
project_name = "evaluation-system-dev"

# Networking
vpc_cidr               = "10.0.0.0/16"
public_subnet_cidrs    = ["10.0.1.0/24", "10.0.2.0/24"]
private_subnet_cidrs   = ["10.0.10.0/24", "10.0.11.0/24"]

# ECS Configuration (Development - minimal resources)
backend_cpu           = 256   # 0.25 vCPU
backend_memory        = 512   # 512 MB
backend_desired_count = 1     # Single instance

# RDS Configuration (Development - smallest instance)
db_instance_class     = "db.t3.micro"
db_allocated_storage  = 20
db_name              = "evaluation_dev"
db_username          = "evaluation_user"

# Domain (leave empty for development)
domain_name = ""

# Additional tags
additional_tags = {
  Environment = "development"
  Purpose     = "portfolio-demo"
  CostCenter  = "personal"
}