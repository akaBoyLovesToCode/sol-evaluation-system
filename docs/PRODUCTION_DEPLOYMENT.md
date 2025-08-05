# Production Deployment Guide

## Overview
Comprehensive production deployment guide for the Product Evaluation Management System with enterprise-grade infrastructure, monitoring, and operational procedures.

## Prerequisites

### Infrastructure Requirements
- AWS Account with appropriate IAM permissions
- Domain name registered and managed via Route53
- SSL certificates provisioned via AWS Certificate Manager
- Terraform >= 1.0 installed locally
- Docker and AWS CLI configured

### Development Tools
- Git with GitHub account and repository access
- Node.js 22+ for frontend development
- Python 3.13+ with pip for backend development
- Railway CLI (for current deployment) or kubectl (for Kubernetes)

## Current Railway Deployment

### Live Environment
- **Frontend**: https://frontend-production-d9f6.up.railway.app/
- **Backend**: https://sol-evaluation-system.up.railway.app/api
- **Database**: PostgreSQL 16 managed by Railway
- **Authentication**: admin / admin123

### Railway Configuration
```bash
# Frontend Environment Variables
VITE_API_BASE_URL=https://sol-evaluation-system.up.railway.app/api

# Backend Environment Variables  
DATABASE_URL=postgresql://postgres:[password]@[host]:[port]/railway
CORS_ORIGINS=https://frontend-production-d9f6.up.railway.app
SECRET_KEY=[generated-secret]
JWT_SECRET_KEY=[generated-jwt-secret]
FLASK_ENV=production
```

### Deployment Commands
```bash
# Deploy frontend
cd frontend
railway up --service frontend

# Deploy backend  
cd backend
railway up --service backend

# Check logs
railway logs --service backend
railway logs --service frontend
```

## AWS Production Migration

### 1. Infrastructure Setup with Terraform

```bash
# Clone and setup infrastructure
git clone [repository]
cd terraform/infrastructure

# Configure variables
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your values

# Initialize and deploy
terraform init
terraform plan -var-file=terraform.tfvars
terraform apply -var-file=terraform.tfvars
```

### 2. Container Registry Setup

```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin [account].dkr.ecr.us-east-1.amazonaws.com

# Build and push backend
cd backend
docker build -t evaluation-backend .
docker tag evaluation-backend:latest [account].dkr.ecr.us-east-1.amazonaws.com/evaluation-backend:latest
docker push [account].dkr.ecr.us-east-1.amazonaws.com/evaluation-backend:latest

# Build and push frontend
cd frontend  
docker build -t evaluation-frontend .
docker tag evaluation-frontend:latest [account].dkr.ecr.us-east-1.amazonaws.com/evaluation-frontend:latest
docker push [account].dkr.ecr.us-east-1.amazonaws.com/evaluation-frontend:latest
```

### 3. Database Migration

```bash
# Connect to RDS via bastion host
ssh -i production-key.pem -L 5432:[rds-endpoint]:5432 ec2-user@[bastion-ip]

# Export data from Railway PostgreSQL
pg_dump [railway-database-url] > railway-backup.sql

# Import to AWS RDS
psql [rds-database-url] < railway-backup.sql

# Run migrations
cd backend
export DATABASE_URL=[rds-database-url]
flask db upgrade
```

### 4. ECS Service Deployment

```bash
# Update ECS services with new images
aws ecs update-service \
  --cluster evaluation-system \
  --service evaluation-backend \
  --force-new-deployment

aws ecs update-service \
  --cluster evaluation-system \
  --service evaluation-frontend \
  --force-new-deployment

# Monitor deployment
aws ecs describe-services \
  --cluster evaluation-system \
  --services evaluation-backend evaluation-frontend
```

## CI/CD Pipeline

### GitHub Actions Workflow
The system includes automated CI/CD with GitHub Actions:

1. **Frontend CI**: ESLint, Prettier, Jest tests, build validation
2. **Backend CI**: Ruff linting, pytest with coverage, PostgreSQL testing
3. **Deployment**: Automatic Railway deployment on main branch push

### Setting up GitHub Secrets
```bash
# Required secrets in GitHub repository settings
RAILWAY_TOKEN=your_railway_api_token
CODECOV_TOKEN=your_codecov_token

# For AWS deployment (optional)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
```

## Monitoring and Observability

### Application Performance Monitoring

#### DataDog Setup (Recommended)
```bash
# Install DataDog agent
DD_API_KEY=[your-key] DD_SITE="datadoghq.com" bash -c "$(curl -L https://s3.amazonaws.com/dd-agent/scripts/install_script.sh)"

# Configure application tracing
# Add to backend requirements.txt:
# ddtrace>=2.0.0

# Environment variables for backend
DD_SERVICE=evaluation-backend
DD_ENV=production
DD_VERSION=1.0.0
DD_TRACE_ENABLED=true
```

#### CloudWatch Setup (AWS)
```bash
# Install CloudWatch agent
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
sudo dpkg -i amazon-cloudwatch-agent.deb

# Configure logs forwarding
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
  -a fetch-config -m ec2 -c file:/opt/aws/amazon-cloudwatch-agent/etc/config.json -s
```

### Key Metrics Dashboard

#### Business Metrics
- User registration rate
- Evaluation completion rate  
- Approval workflow efficiency
- System utilization by role

#### Technical Metrics
- Response time percentiles (p50, p95, p99)
- Error rate by endpoint
- Database query performance
- Container resource utilization

### Alerting Configuration

#### Critical Alerts (PagerDuty)
- Service downtime (>5 min)
- Error rate >5% (>10 min)
- Database connection failures
- Authentication service failures

#### Warning Alerts (Slack)
- High response time >2s (>15 min)
- Database connection pool >80%
- Memory usage >85%
- Disk space >90%

## Security Configuration

### SSL/TLS Setup
```bash
# AWS Certificate Manager
aws acm request-certificate \
  --domain-name evaluation.company.com \
  --validation-method DNS \
  --subject-alternative-names *.evaluation.company.com

# Let's Encrypt (alternative)
certbot certonly --standalone -d evaluation.company.com
```

### WAF Configuration
```bash
# AWS WAF rules for common attacks
aws wafv2 create-web-acl \
  --name evaluation-system-waf \
  --scope CLOUDFRONT \
  --default-action Allow={} \
  --rules file://waf-rules.json
```

### Secrets Management
```bash
# Store secrets in AWS Parameter Store
aws ssm put-parameter \
  --name "/evaluation-system/production/database-url" \
  --value "postgresql://..." \
  --type "SecureString"

aws ssm put-parameter \
  --name "/evaluation-system/production/jwt-secret" \
  --value "[generated-secret]" \
  --type "SecureString"
```

## Backup and Disaster Recovery

### Database Backup Strategy
```bash
# Automated daily backups
aws rds create-db-snapshot \
  --db-instance-identifier evaluation-system-db \
  --db-snapshot-identifier evaluation-system-$(date +%Y%m%d)

# Cross-region backup replication
aws rds copy-db-snapshot \
  --source-db-snapshot-identifier evaluation-system-$(date +%Y%m%d) \
  --target-db-snapshot-identifier evaluation-system-$(date +%Y%m%d)-dr \
  --source-region us-east-1 \
  --target-region us-west-2
```

### Application State Backup
```bash
# File upload backup to S3
aws s3 sync /app/uploads s3://evaluation-system-backups/uploads/ --delete

# Configuration backup
kubectl get configmaps -o yaml > configmaps-backup.yaml
kubectl get secrets -o yaml > secrets-backup.yaml
```

### Recovery Procedures
```bash
# Database recovery from snapshot
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier evaluation-system-restored \
  --db-snapshot-identifier evaluation-system-20240101

# Application recovery
terraform apply -var-file=disaster-recovery.tfvars
kubectl apply -f k8s/
```

## Performance Optimization

### Database Optimization
```sql
-- Create optimized indexes
CREATE INDEX CONCURRENTLY idx_evaluations_status_created 
ON evaluations(status, created_at);

CREATE INDEX CONCURRENTLY idx_users_role_active 
ON users(role, is_active) WHERE is_active = true;

CREATE INDEX CONCURRENTLY idx_operation_logs_timestamp 
ON operation_logs(timestamp) WHERE timestamp > NOW() - INTERVAL '30 days';

-- Analyze query performance
EXPLAIN (ANALYZE, BUFFERS) 
SELECT e.*, u.full_name 
FROM evaluations e 
JOIN users u ON e.created_by = u.id 
WHERE e.status = 'pending' 
ORDER BY e.created_at DESC 
LIMIT 50;
```

### Application Caching
```python
# Redis caching configuration
CACHE_TYPE = "redis"
CACHE_REDIS_URL = "redis://evaluation-cache:6379/0"
CACHE_DEFAULT_TIMEOUT = 300

# Cache frequently accessed data
@cache.memoize(timeout=300)
def get_user_evaluations(user_id, status=None):
    query = Evaluation.query.filter_by(created_by=user_id)
    if status:
        query = query.filter_by(status=status)
    return query.all()
```

### Frontend Optimization
```javascript
// Lazy loading for Vue components
const Dashboard = () => import('./views/Dashboard.vue')
const Evaluations = () => import('./views/Evaluations.vue')

// Image optimization
const imageOptimization = {
  quality: 85,
  progressive: true,
  webp: true
}

// Bundle splitting
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['vue', 'vue-router', 'pinia'],
          ui: ['element-plus'],
          charts: ['echarts']
        }
      }
    }
  }
})
```

## Scaling Strategy

### Horizontal Scaling
```bash
# Scale ECS services
aws ecs update-service \
  --cluster evaluation-system \
  --service evaluation-backend \
  --desired-count 5

# Auto Scaling based on CPU
aws application-autoscaling put-scaling-policy \
  --policy-name backend-scale-out \
  --service-namespace ecs \
  --resource-id service/evaluation-system/evaluation-backend \
  --scalable-dimension ecs:service:DesiredCount \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration TargetValue=70.0,PredefinedMetricSpecification='{PredefinedMetricType=ECSServiceAverageCPUUtilization}'
```

### Database Scaling
```bash
# Read replicas for read-heavy workloads
aws rds create-db-instance-read-replica \
  --db-instance-identifier evaluation-system-read-replica \
  --source-db-instance-identifier evaluation-system-db

# Connection pooling with PgBouncer
docker run -d --name pgbouncer \
  -e DATABASES_HOST=evaluation-db.cluster-xxx.us-east-1.rds.amazonaws.com \
  -e DATABASES_PORT=5432 \
  -e DATABASES_USER=evaluation_user \
  -e DATABASES_PASSWORD=[password] \
  -e DATABASES_DBNAME=evaluation \
  -p 5432:5432 \
  pgbouncer/pgbouncer:latest
```

## Troubleshooting Guide

### Common Issues

#### Database Connection Issues
```bash
# Check connection
psql $DATABASE_URL -c "SELECT version();"

# Check connection pool
psql $DATABASE_URL -c "SELECT count(*) FROM pg_stat_activity;"

# Reset connections
docker restart evaluation-backend
```

#### Authentication Issues
```bash
# Verify JWT configuration
curl -X POST https://api.evaluation.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Check user in database
psql $DATABASE_URL -c "SELECT username, role, is_active FROM users WHERE username='admin';"
```

#### Performance Issues
```bash
# Check resource usage
docker stats evaluation-backend
kubectl top pods

# Database performance
psql $DATABASE_URL -c "SELECT query, calls, total_time, mean_time FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"
```

### Log Analysis
```bash
# Application logs
docker logs evaluation-backend --tail=100 -f
kubectl logs -f deployment/evaluation-backend

# Database logs
aws rds describe-db-log-files --db-instance-identifier evaluation-system-db
aws rds download-db-log-file-portion --db-instance-identifier evaluation-system-db --log-file-name error/postgresql.log.2024-01-01-12
```

This production deployment guide provides comprehensive procedures for deploying, monitoring, and maintaining the Product Evaluation Management System in production environments.