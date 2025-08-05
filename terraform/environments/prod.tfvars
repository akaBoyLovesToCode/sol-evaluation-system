# Production Environment Configuration

# General
aws_region   = "us-east-1"
environment  = "prod"
project_name = "evaluation-system"

# Networking
vpc_cidr               = "10.0.0.0/16"
public_subnet_cidrs    = ["10.0.1.0/24", "10.0.2.0/24"]
private_subnet_cidrs   = ["10.0.10.0/24", "10.0.11.0/24"]

# ECS Configuration (Production - optimized for portfolio)
backend_cpu           = 512   # 0.5 vCPU
backend_memory        = 1024  # 1 GB
backend_desired_count = 2     # Two instances for availability

# RDS Configuration (Production - still cost-optimized)
db_instance_class     = "db.t3.micro"
db_allocated_storage  = 20
db_name              = "evaluation"
db_username          = "evaluation_user"

# Domain (add your domain if you have one)
domain_name = ""

# Additional tags
additional_tags = {
  Environment = "production"
  Purpose     = "portfolio-demo"
  CostCenter  = "personal"
}