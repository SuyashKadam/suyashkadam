# AWS Production Architecture — Deployment Guide

## Architecture Overview

```
Internet Users
     │
     ▼
┌─────────────────────────────────────────────┐
│  AWS WAF  ──►  CloudFront CDN               │  ← Security + Global CDN
│  (OWASP rules, rate limiting, SQLi block)   │
└─────────────────┬───────────────────────────┘
                  │ HTTPS (redirect-to-https)
                  ▼
┌─────────────────────────────────────────────┐
│  Application Load Balancer (Multi-AZ)       │  ← Public Subnets
│  HTTP:80 → Target Group                    │
└──────┬──────────┬──────────┬───────────────┘
       │          │          │
       ▼          ▼          ▼
┌─────────────────────────────────────────────┐
│  ECS Fargate Tasks (PRIVATE SUBNETS)        │  ← Private Subnets
│  Min: 3 containers  /  Max: 6 containers    │
│  Nginx reverse proxy (Ubuntu 22.04)         │
│  Auto-scale at 80% CPU or Memory           │
└──────┬──────────┬──────────┬───────────────┘
       │          │          │
       ▼          ▼          ▼
┌─────────────────────────────────────────────┐
│  NAT Gateway (per AZ, for HA)               │  ← Outbound internet from private subnets
│  → ECR image pulls, AWS API calls           │
└─────────────────────────────────────────────┘

CI/CD Pipeline:
GitHub Push → CodeBuild → Docker Build → ECR Push → ECS Update

Monitoring:
CloudWatch → SNS → Email Alert (yogiraj123ano@gmail.com)
Alarms: CPU >80%, Memory >80%, 5xx spike, Unhealthy hosts, P99 latency >2s
```

---

## Prerequisites

Install on your local machine:

```bash
# 1. AWS CLI v2
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o awscliv2.zip
unzip awscliv2.zip && sudo ./aws/install
aws --version

# 2. Terraform >= 1.5
wget https://releases.hashicorp.com/terraform/1.7.5/terraform_1.7.5_linux_amd64.zip
unzip terraform_1.7.5_linux_amd64.zip && sudo mv terraform /usr/local/bin/
terraform --version

# 3. Docker
sudo apt-get install docker.io -y
sudo usermod -aG docker $USER  # then logout/login

# 4. Git
sudo apt-get install git -y
```

---

## Step 1 — Configure AWS Credentials

```bash
aws configure
# AWS Access Key ID: <your-access-key>
# AWS Secret Access Key: <your-secret-key>
# Default region: us-east-1
# Default output format: json

# Verify
aws sts get-caller-identity
```

**Required IAM permissions** (attach to your user/role):
- `AdministratorAccess` (for initial setup) OR at minimum:
  - `AmazonECS_FullAccess`
  - `AmazonEC2FullAccess`
  - `CloudFrontFullAccess`
  - `AWSCodeBuildAdminAccess`
  - `AmazonECRFullAccess`
  - `CloudWatchFullAccess`
  - `AmazonSNSFullAccess`
  - `IAMFullAccess`
  - `AWSWAFv2FullAccess`
  - `AmazonS3FullAccess`

---

## Step 2 — Clone and Review the Repo

```bash
git clone https://github.com/suyashkadam/suyashkadam.git
cd suyashkadam
```

---

## Step 3 — Connect GitHub to CodeBuild

CodeBuild needs permission to clone your GitHub repo and create webhooks.

```bash
# Go to AWS Console → CodeBuild → Source providers
# OR use AWS CLI to add GitHub token:
aws codebuild import-source-credentials \
  --server-type GITHUB \
  --auth-type PERSONAL_ACCESS_TOKEN \
  --token <your-github-personal-access-token>

# Verify
aws codebuild list-source-credentials
```

**Create GitHub Personal Access Token:**
1. GitHub → Settings → Developer Settings → Personal Access Tokens → Tokens (classic)
2. Scopes needed: `repo`, `admin:repo_hook`
3. Copy the token and use above

---

## Step 4 — Deploy with Terraform

```bash
cd terraform/environments/prod

# Initialize (downloads providers)
terraform init

# Preview what will be created (review carefully)
terraform plan -out=tfplan

# Deploy! (~10-15 minutes)
terraform apply tfplan
```

### What gets created (47 resources):
| Resource | Count | Purpose |
|----------|-------|---------|
| VPC | 1 | Isolated network |
| Public Subnets | 3 | ALB, NAT Gateways |
| Private Subnets | 3 | ECS tasks |
| NAT Gateways | 3 | HA outbound access |
| Internet Gateway | 1 | Public internet access |
| ALB | 1 | Load balancing across containers |
| ECS Cluster | 1 | Container orchestration |
| ECS Service | 1 | Maintains 3-6 tasks |
| ECS Task Definition | 1 | Nginx container spec |
| ECR Repository | 1 | Docker image registry |
| CloudFront Distribution | 1 | Global CDN |
| WAF WebACL | 1 | Security rules |
| CloudWatch Alarms | 5 | CPU, Memory, 5xx, Latency, Health |
| SNS Topic | 1 | Alert routing |
| SNS Email Subscription | 1 | Email to yogiraj123ano@gmail.com |
| CodeBuild Project | 1 | CI/CD build |
| Security Groups | 2 | ALB + ECS network control |
| IAM Roles | 4 | ECS execution, task, CodeBuild, VPC flow |
| S3 Buckets | 3 | ALB logs, CF logs, build artifacts |
| CloudWatch Dashboard | 1 | Metrics visualization |

---

## Step 5 — Confirm SNS Email Subscription

After `terraform apply`:
1. Check email: **yogiraj123ano@gmail.com**
2. Look for email from `AWS Notifications`
3. Click **"Confirm subscription"** link
4. You will now receive CloudWatch alerts via email

---

## Step 6 — Build and Push Initial Docker Image

After Terraform deploys, run the first build manually:

```bash
# Get outputs
cd terraform/environments/prod
ECR_URL=$(terraform output -raw ecr_repository_url)
CLUSTER=$(terraform output -raw ecs_cluster_name)
SERVICE=$(terraform output -raw ecs_service_name)
REGION="us-east-1"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

echo "ECR URL: $ECR_URL"

# Login to ECR
aws ecr get-login-password --region $REGION | \
  docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com

# Build image from the app/ directory
cd ../../..  # back to repo root
docker build -t $ECR_URL:latest ./app/

# Push to ECR
docker push $ECR_URL:latest

# Force ECS service to pull the new image
aws ecs update-service --cluster $CLUSTER --service $SERVICE --force-new-deployment --region $REGION

# Watch deployment (wait for all tasks to be running)
aws ecs wait services-stable --cluster $CLUSTER --services $SERVICE --region $REGION
echo "✓ Deployment complete!"
```

---

## Step 7 — Access Your Website

```bash
cd terraform/environments/prod
terraform output cloudfront_url
```

Copy the URL — it looks like: `https://d1234abcde.cloudfront.net`

**Note:** CloudFront takes 5-10 minutes to fully propagate globally on first deployment.

---

## Step 8 — Verify Everything is Working

```bash
# Check ECS tasks are running (should show 3 tasks)
aws ecs describe-services \
  --cluster $(terraform output -raw ecs_cluster_name) \
  --services $(terraform output -raw ecs_service_name) \
  --query 'services[0].{Desired:desiredCount,Running:runningCount,Pending:pendingCount}'

# Check ALB health
aws elbv2 describe-target-health \
  --target-group-arn $(terraform output -raw alb_target_group_arn | \
    sed 's/.*targetgroup/targetgroup/') \
  --query 'TargetHealthDescriptions[*].{IP:Target.Id,Status:TargetHealth.State}'

# Hit the health endpoint
curl https://$(terraform output -raw cloudfront_url | sed 's|https://||')/health

# Check CloudWatch dashboard
echo "Dashboard: https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards:name=suyashkadam-prod-dashboard"
```

---

## CI/CD — How It Works After Setup

Every `git push` to `master` branch:

```
git add .
git commit -m "feat: update website"
git push origin master
          │
          ▼
    GitHub Webhook
          │
          ▼
    CodeBuild starts
    ├── docker build ./app/
    ├── docker push ECR :sha1234 + :latest
    ├── register new ECS task definition
    └── aws ecs update-service (rolling deploy)
          │
          ▼
    ECS rolls out new containers (zero downtime)
    (min_healthy_percent: 100%, max_percent: 200%)
```

---

## Auto-Scaling Behavior

| Metric | Threshold | Action |
|--------|-----------|--------|
| CPU Utilization | > 80% | Scale out (add containers), Email alert |
| Memory Utilization | > 80% | Scale out, Email alert |
| ALB 5xx Errors | > 10/min | Email alert |
| Unhealthy Hosts | > 0 | Email alert |
| P99 Latency | > 2s | Email alert |

- Scale-out cooldown: 60 seconds (fast response)
- Scale-in cooldown: 300 seconds (don't scale in too quickly)
- Min tasks: 3 (always 3 running across 3 AZs)
- Max tasks: 6

---

## Tear Down (When Done Testing)

```bash
cd terraform/environments/prod

# First empty the S3 buckets (Terraform can't delete non-empty buckets)
# (force_destroy = true handles this automatically)

terraform destroy
# Type 'yes' when prompted
```

---

## Troubleshooting

### ECS tasks not starting
```bash
# Check task stopped reason
aws ecs describe-tasks \
  --cluster suyashkadam-prod-cluster \
  --tasks $(aws ecs list-tasks --cluster suyashkadam-prod-cluster --query 'taskArns[0]' --output text) \
  --query 'tasks[0].stoppedReason'

# Check container logs
aws logs get-log-events \
  --log-group-name /ecs/suyashkadam-prod \
  --log-stream-name $(aws logs describe-log-streams \
    --log-group-name /ecs/suyashkadam-prod \
    --order-by LastEventTime --descending \
    --query 'logStreams[0].logStreamName' --output text) \
  --limit 50 --query 'events[*].message' --output text
```

### CloudFront returning 502/503
```bash
# Check ALB health
aws elbv2 describe-target-health \
  --target-group-arn <target-group-arn>
# All targets should show "healthy"
# If "initial" — wait 2-3 minutes for health checks to pass
```

### CodeBuild failing
```bash
# View build logs
aws codebuild list-builds-for-project --project-name suyashkadam-prod-build
aws codebuild batch-get-builds --ids <build-id> --query 'builds[0].phases[*].{Name:phaseType,Status:phaseStatus}'
```

### ECR image pull error
```bash
# Ensure NAT Gateway is working — ECS tasks in private subnets
# need NAT to reach ECR
aws ec2 describe-nat-gateways --filter Name=state,Values=available
```
