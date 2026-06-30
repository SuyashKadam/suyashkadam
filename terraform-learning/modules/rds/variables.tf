variable "env" {
  type = string
}

variable "db_name" {
  type = string
}

variable "db_username" {
  type = string
}

variable "db_password" {
  type      = string
  sensitive = true  # Won't appear in plan/apply output
}

variable "instance_class" {
  type = string
}

variable "subnet_ids" {
  type = list(string)
}

variable "security_group_id" {
  type = string
}

variable "multi_az" {
  description = "Multi-AZ for prod. Single-AZ for dev to save cost."
  type        = bool
  default     = false
}
