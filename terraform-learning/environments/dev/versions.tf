terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region

  # These tags get applied to EVERY resource automatically
  default_tags {
    tags = {
      Environment = "dev"
      ManagedBy   = "terraform"
      Project     = "learning"
    }
  }
}
