aws_region   = "us-east-1"
project_name = "suyashkadam"
environment  = "prod"
alert_email  = "yogiraj123ano@gmail.com"
github_repo  = "suyashkadam/suyashkadam"

# VPC
vpc_cidr             = "10.0.0.0/16"
public_subnet_cidrs  = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
private_subnet_cidrs = ["10.0.11.0/24", "10.0.12.0/24", "10.0.13.0/24"]
availability_zones   = ["us-east-1a", "us-east-1b", "us-east-1c"]

# ECS
container_cpu    = 256
container_memory = 512
min_capacity     = 3
max_capacity     = 6

# Scaling & Alerting
cpu_alarm_threshold = 80

# WAF
enable_waf = true
