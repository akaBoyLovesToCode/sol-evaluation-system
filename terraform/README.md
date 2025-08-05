# Portfolio-Optimized Terraform Infrastructure

This directory contains Infrastructure as Code for deploying the Product Evaluation Management System on AWS.

## 🎯 Portfolio Design Goals
- **Cost-Effective:** $10-30/month total
- **Industry-Standard:** ECS Fargate + S3 + CloudFront + RDS
- **Recruiter-Friendly:** Shows modern DevOps skills
- **Maintainable:** Simple, well-documented infrastructure

## 🏗️ Architecture Overview
```
Frontend (Vue.js) → S3 + CloudFront (~$2/mo)
Backend (Flask) → ECS Fargate (~$15/mo) 
Database → RDS PostgreSQL t3.micro (~$15/mo)
Monitoring → CloudWatch + X-Ray (mostly free tier)
```

## 📁 Directory Structure
```
terraform/
├── infrastructure/          # Main infrastructure resources
│   ├── main.tf             # Provider and backend config
│   ├── variables.tf        # Input variables
│   ├── outputs.tf          # Output values
│   ├── vpc.tf              # VPC and networking
│   ├── ecs.tf              # ECS cluster and services
│   ├── rds.tf              # PostgreSQL database
│   ├── s3.tf               # S3 buckets and CloudFront
│   ├── iam.tf              # IAM roles and policies
│   └── monitoring.tf       # CloudWatch and X-Ray
├── modules/                # Reusable modules
│   ├── ecs-fargate/        # ECS Fargate service module
│   ├── s3-cloudfront/      # S3 + CloudFront module
│   └── rds-postgres/       # RDS PostgreSQL module
└── environments/           # Environment-specific configs
    ├── dev.tfvars
    ├── staging.tfvars
    └── prod.tfvars
```

## 🚀 Quick Start

### Prerequisites
- AWS CLI configured with appropriate permissions
- Terraform >= 1.0 installed
- Docker for local testing

### Deployment Commands
```bash
# Initialize Terraform
cd terraform/infrastructure
terraform init

# Plan deployment
terraform plan -var-file=../environments/dev.tfvars

# Apply infrastructure
terraform apply -var-file=../environments/dev.tfvars

# Destroy when done
terraform destroy -var-file=../environments/dev.tfvars
```

## 💰 Cost Breakdown
| Service | Instance Type | Monthly Cost |
|---------|---------------|--------------|
| ECS Fargate | 0.5 vCPU, 1GB RAM | ~$15 |
| RDS PostgreSQL | db.t3.micro | ~$15 |
| S3 + CloudFront | Static hosting | ~$2 |
| CloudWatch | Basic monitoring | ~$3 |
| **Total** |  | **~$35** |

## 🔧 Customization
- Adjust instance sizes in `variables.tf`
- Modify environment configs in `environments/`
- Add additional monitoring in `monitoring.tf`

## 🎯 What This Shows Recruiters
- Infrastructure as Code expertise
- AWS cloud architecture knowledge
- Cost optimization awareness
- Production-ready security practices
- Modern containerization approach