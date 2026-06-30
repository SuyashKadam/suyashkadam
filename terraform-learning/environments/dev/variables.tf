variable "aws_region" {
  default = "us-east-1"
}

variable "key_name" {
  description = "EC2 key pair name. Create one in AWS Console first."
  type        = string
}

variable "your_ip" {
  description = "Your public IP for SSH. Run: curl ifconfig.me"
  type        = string
}

variable "db_password" {
  description = "RDS password. Pass via env var: export TF_VAR_db_password=xxx"
  type        = string
  sensitive   = true
}
