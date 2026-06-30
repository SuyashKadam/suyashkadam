variable "env" {
  type = string
}

variable "vpc_id" {
  type = string
}

variable "your_ip" {
  description = "Your local IP for SSH access. Get it: curl ifconfig.me"
  type        = string
}
