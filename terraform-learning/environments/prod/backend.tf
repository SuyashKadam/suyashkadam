terraform {
  backend "s3" {
    bucket         = "yourname-terraform-state-2024"  # Same bucket, different key
    key            = "prod/terraform.tfstate"          # prod/ prefix separates it from dev
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"
  }
}
