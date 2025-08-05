terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.1"
    }
  }
  
  # Uncomment for production use with S3 backend
  # backend "s3" {
  #   bucket = "evaluation-system-terraform-state"
  #   key    = "infrastructure/terraform.tfstate"
  #   region = "us-east-1"
  # }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "evaluation-system"
      Environment = var.environment
      ManagedBy   = "terraform"
      Purpose     = "portfolio-demo"
    }
  }
}

# Data sources
data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_caller_identity" "current" {}

# Generate random password for RDS
resource "random_password" "db_password" {
  length  = 32
  special = true
}