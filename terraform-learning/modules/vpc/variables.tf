variable "env" {
  description = "Environment name (dev or prod)"
  type        = string
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
}

variable "public_subnet_cidrs" {
  description = "List of CIDRs for public subnets (one per AZ)"
  type        = list(string)
}

variable "private_subnet_cidrs" {
  description = "List of CIDRs for private subnets (one per AZ)"
  type        = list(string)
}

variable "enable_nat_gateway" {
  description = "Set false in dev to save cost (~$32/month each)"
  type        = bool
  default     = false
}
