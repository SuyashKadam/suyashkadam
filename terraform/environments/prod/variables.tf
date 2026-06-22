variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name used as prefix for all resources"
  type        = string
  default     = "suyashkadam"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "prod"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets (ALB, NAT Gateway)"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets (ECS tasks)"
  type        = list(string)
  default     = ["10.0.11.0/24", "10.0.12.0/24", "10.0.13.0/24"]
}

variable "availability_zones" {
  description = "Availability zones to use"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b", "us-east-1c"]
}

variable "container_cpu" {
  description = "ECS task CPU units (1 vCPU = 1024)"
  type        = number
  default     = 256
}

variable "container_memory" {
  description = "ECS task memory in MiB"
  type        = number
  default     = 512
}

variable "min_capacity" {
  description = "Minimum number of ECS tasks"
  type        = number
  default     = 3
}

variable "max_capacity" {
  description = "Maximum number of ECS tasks"
  type        = number
  default     = 6
}

variable "cpu_alarm_threshold" {
  description = "CPU utilization % that triggers auto-scaling and CloudWatch alarm"
  type        = number
  default     = 80
}

variable "alert_email" {
  description = "Email address to receive CloudWatch SNS alerts"
  type        = string
  default     = "yogiraj123ano@gmail.com"
}

variable "image_tag" {
  description = "Docker image tag to deploy (set by CI/CD pipeline)"
  type        = string
  default     = "latest"
}

variable "enable_waf" {
  description = "Attach AWS WAF WebACL to CloudFront"
  type        = bool
  default     = true
}

variable "github_repo" {
  description = "GitHub repository in owner/repo format"
  type        = string
  default     = "suyashkadam/suyashkadam"
}

variable "github_branch" {
  description = "GitHub branch to trigger the pipeline"
  type        = string
  default     = "master"
}
