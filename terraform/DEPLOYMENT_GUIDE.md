# AWS Deployment Guide

This guide walks through deploying the Product Evaluation Management System to AWS using the portfolio-optimized infrastructure.

## 🎯 Portfolio Architecture Benefits

- **Cost-Effective**: ~$30/month total
- **Industry-Standard**: ECS Fargate + S3 + CloudFront + RDS
- **Recruiter-Friendly**: Demonstrates modern DevOps skills
- **Production-Ready**: Monitoring, logging, auto-scaling

## 📋 Prerequisites

### Required Tools
```bash
# Install Terraform
curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo apt-key add -
sudo apt-add-repository "deb [arch=amd64] https://apt.releases.hashicorp.com $(lsb_release -cs) main"
sudo apt-get update && sudo apt-get install terraform

# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip && sudo ./aws/install

# Install Docker
sudo apt-get update
sudo apt-get install docker.io
sudo usermod -aG docker $USER
```

### AWS Setup
```bash
# Configure AWS credentials
aws configure
# Enter your Access Key ID, Secret Access Key, Region (us-east-1), Output format (json)

# Verify access
aws sts get-caller-identity
```

### Required AWS Permissions
Your AWS user needs these permissions:
- EC2 (VPC, Subnets, Security Groups, Load Balancers)
- ECS (Clusters, Services, Task Definitions)
- ECR (Repositories)
- RDS (DB Instances, Subnet Groups)
- S3 (Buckets, Objects)
- CloudFront (Distributions)
- IAM (Roles, Policies)
- CloudWatch (Logs, Metrics, Alarms)
- SSM (Parameters)
- SNS (Topics)

## 🚀 Deployment Steps

### Step 1: Initialize Terraform
```bash
cd terraform/infrastructure
terraform init
```

### Step 2: Plan the Deployment
```bash
# For development environment
terraform plan -var-file=../environments/dev.tfvars

# Review the plan carefully - should show ~50 resources to create
```

### Step 3: Deploy Infrastructure
```bash
# Deploy to development
terraform apply -var-file=../environments/dev.tfvars

# Type 'yes' when prompted
# Deployment takes ~15-20 minutes
```

### Step 4: Build and Push Backend Container
```bash
# Get ECR login
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $(terraform output -raw ecr_backend_repository_url | cut -d'/' -f1)

# Build backend image
cd ../../backend
docker build -t evaluation-backend .

# Tag and push to ECR
ECR_REPO=$(cd ../terraform/infrastructure && terraform output -raw ecr_backend_repository_url)
docker tag evaluation-backend:latest $ECR_REPO:latest
docker push $ECR_REPO:latest
```

### Step 5: Deploy Frontend to S3
```bash
# Build frontend
cd ../frontend
npm install
npm run build

# Upload to S3
BUCKET_NAME=$(cd ../terraform/infrastructure && terraform output -raw s3_frontend_bucket)
aws s3 sync dist/ s3://$BUCKET_NAME/ --delete

# Invalidate CloudFront cache
DISTRIBUTION_ID=$(cd ../terraform/infrastructure && terraform output -raw cloudfront_distribution_id)
aws cloudfront create-invalidation --distribution-id $DISTRIBUTION_ID --paths "/*"
```

### Step 6: Run Database Migrations
```bash
# Get database URL from Terraform output
cd ../terraform/infrastructure
DATABASE_URL=$(terraform output -raw database_url)

# Run migrations
cd ../../backend
export DATABASE_URL="$DATABASE_URL"
flask db upgrade

# Create initial admin user (optional)
python -c "
from app import create_app
from app.models import User, db
app = create_app()
with app.app_context():
    admin = User(username='admin', email='admin@example.com', role='admin')
    admin.set_password('admin123')
    admin.is_active = True
    db.session.add(admin)
    db.session.commit()
    print('Admin user created')
"
```

### Step 7: Verify Deployment
```bash
# Get application URLs
cd ../terraform/infrastructure
echo "Frontend URL: $(terraform output -raw frontend_url)"
echo "Backend URL: $(terraform output -raw backend_url)"

# Test backend health
curl "$(terraform output -raw backend_url)/health"

# Test frontend (should return HTML)
curl "$(terraform output -raw frontend_url)"
```

## 📊 Monitoring Setup

### CloudWatch Dashboard
Access your dashboard at:
`https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards:name=evaluation-system-dashboard`

### Key Metrics to Monitor
- **ECS CPU/Memory**: Should be <70% under normal load
- **ALB Response Time**: Should be <2 seconds
- **RDS Connections**: Monitor for connection leaks
- **Error Rates**: Watch for 4xx/5xx responses

### Log Analysis
```bash
# View backend logs
aws logs tail /ecs/evaluation-system-backend --follow

# Query error logs
aws logs start-query \
  --log-group-name "/ecs/evaluation-system-backend" \
  --start-time $(date -d '1 hour ago' +%s) \
  --end-time $(date +%s) \
  --query-string 'fields @timestamp, @message | filter @message like /ERROR/'
```

## 💰 Cost Optimization

### Monthly Cost Breakdown
| Service | Configuration | Cost |
|---------|---------------|------|
| ECS Fargate | 0.5 vCPU, 1GB RAM, 2 tasks | ~$15 |
| RDS PostgreSQL | db.t3.micro | ~$15 |
| S3 + CloudFront | Static hosting + CDN | ~$2 |
| Data Transfer | Normal usage | ~$3 |
| CloudWatch | Logs + Metrics | ~$3 |
| **Total** | | **~$38** |

### Cost Reduction Tips
```bash
# Stop development environment when not in use
terraform destroy -var-file=../environments/dev.tfvars

# Use single ECS task for development
# Set backend_desired_count = 1 in dev.tfvars

# Monitor costs
aws budgets describe-budgets --account-id $(aws sts get-caller-identity --query Account --output text)
```

## 🔧 Troubleshooting

### Common Issues

#### ECS Service Won't Start
```bash
# Check service events
aws ecs describe-services --cluster evaluation-system-cluster --services evaluation-system-backend

# Check task logs
aws logs tail /ecs/evaluation-system-backend --since 1h
```

#### Database Connection Issues
```bash
# Test database connectivity from ECS task
aws ecs execute-command \
  --cluster evaluation-system-cluster \
  --task $(aws ecs list-tasks --cluster evaluation-system-cluster --service evaluation-system-backend --query 'taskArns[0]' --output text) \
  --container backend \
  --interactive \
  --command "/bin/bash"

# Inside the container:
# psql $DATABASE_URL -c "SELECT version();"
```

#### Frontend Not Loading
```bash
# Check S3 bucket contents
aws s3 ls s3://$(terraform output -raw s3_frontend_bucket)/ --recursive

# Check CloudFront distribution status
aws cloudfront get-distribution --id $(terraform output -raw cloudfront_distribution_id)
```

### Recovery Procedures
```bash
# Redeploy ECS service
aws ecs update-service \
  --cluster evaluation-system-cluster \
  --service evaluation-system-backend \
  --force-new-deployment

# Restore database from snapshot (if needed)
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier evaluation-system-db-restored \
  --db-snapshot-identifier evaluation-system-db-snapshot-$(date +%Y%m%d)
```

## 🧹 Cleanup

### Destroy Infrastructure
```bash
# WARNING: This will delete everything!
terraform destroy -var-file=../environments/dev.tfvars

# Confirm by typing 'yes'
```

### Manual Cleanup (if needed)
```bash
# Empty S3 buckets first
aws s3 rm s3://$(terraform output -raw s3_frontend_bucket) --recursive
aws s3 rm s3://$(terraform output -raw s3_codepipeline_artifacts_bucket) --recursive

# Delete ECR images
aws ecr batch-delete-image \
  --repository-name evaluation-system-backend \
  --image-ids imageTag=latest
```

## 🎯 Portfolio Presentation

### Key Points for Interviews
1. **Infrastructure as Code**: "I use Terraform to manage all AWS resources"
2. **Container Orchestration**: "Backend runs on ECS Fargate for scalability"
3. **Cost Optimization**: "Designed for ~$30/month while maintaining production practices"
4. **Monitoring**: "Full observability with CloudWatch, X-Ray, and custom dashboards"
5. **CI/CD Ready**: "Infrastructure supports automated deployments"

### Demo Script
```bash
# Show infrastructure
terraform show

# Show monitoring
open "https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards"

# Show application
open "$(terraform output -raw frontend_url)"

# Show logs
aws logs tail /ecs/evaluation-system-backend --follow
```

This deployment demonstrates enterprise-grade practices while remaining cost-effective for portfolio use.