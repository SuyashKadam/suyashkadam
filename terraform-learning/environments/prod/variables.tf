variable "aws_region" {
  default = "us-east-1"
}

variable "key_name" {
  type = string
}

variable "your_ip" {
  type = string
}

variable "db_password" {
  type      = string
  sensitive = true
}
