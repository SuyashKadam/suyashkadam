variable "aws_region" {
  default = "us-east-1"
}

variable "state_bucket_name" {
  description = "Must be globally unique. Change 'yourname' to something unique."
  default     = "yourname-terraform-state-2024"
}

variable "lock_table_name" {
  default = "terraform-state-lock"
}
