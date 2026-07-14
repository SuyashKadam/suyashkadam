# Suyash Kadam — DevOps Portfolio

Production-grade AWS infrastructure for a containerized web application, built entirely with **Terraform**.

## Live Architecture

| Layer | Technology | Details |
|-------|-----------|---------|
| CDN + Security | CloudFront + WAF | Global edge, OWASP rules, rate limiting |
| Load Balancing | ALB (Multi-AZ) | HTTP routing across 3 AZs |
| Containers | ECS Fargate | Min 3 / Max 6 tasks, private subnets |
| Reverse Proxy | Nginx (Ubuntu 22.04) | Gzip, security headers, health endpoint |
| Registry | ECR | Image scanning on push, lifecycle policies |
| CI/CD | CodeBuild + GitHub Webhook | Auto-deploy on `git push` to master |
| Networking | VPC, NAT Gateway (×3 HA) | Isolated private subnets |
| Monitoring | CloudWatch + SNS | CPU/Memory/Latency/5xx alerts via email |

## Auto-Scaling

Containers scale out at **80% CPU or Memory** (min 3 → max 6), with email alerts via SNS.

### Deployment

See [DEPLOYMENT.md](./DEPLOYMENT.md) for full step-by-step instructions.

```bash
cd terraform/environments/prod
terraform init
terraform apply
# Output: cloudfront_url = "https://d1234abcde.cloudfront.net"
```

## Repository Structure

```
├── app/
│   ├── Dockerfile        # Ubuntu 22.04 + Nginx
│   ├── nginx.conf        # Reverse proxy config
│   ├── index.html        # Portfolio website
│   ├── style.css
│   └── app.js
├── terraform/
│   ├── environments/prod/    # Root module (deploy from here)
│   └── modules/
│       ├── vpc/          # VPC, subnets, NAT Gateways
│       ├── alb/          # Application Load Balancer
│       ├── ecs/          # ECS cluster, service, auto-scaling
│       ├── ecr/          # Container registry
│       ├── cloudfront/   # CDN + WAF
│       ├── monitoring/   # CloudWatch alarms, SNS, dashboard
│       └── codebuild/    # CI/CD pipeline
├── buildspec.yml         # CodeBuild pipeline definition
└── DEPLOYMENT.md         # Step-by-step deployment guide
```
