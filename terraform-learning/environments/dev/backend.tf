# ── Remote State Configuration ───────────────────────────────
# This tells Terraform WHERE to store the state file.
# Change the bucket name to match what you created in bootstrap.
#
# IMPORTANT: You cannot use variables here. Values must be literal strings.
terraform {
  backend "s3" {
    bucket         = "yourname-terraform-state-2024"  # Change this
    key            = "dev/terraform.tfstate"           # Path inside the bucket
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"
  }
}
