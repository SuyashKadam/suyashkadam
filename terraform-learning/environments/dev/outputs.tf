output "vpc_id" {
  value = module.vpc.vpc_id
}

output "ec2_public_ip" {
  value       = module.ec2.public_ip
  description = "SSH: ssh -i ~/.ssh/my-dev-keypair.pem ec2-user@<this_ip>"
}

output "rds_endpoint" {
  value       = module.rds.db_endpoint
  description = "Connect to this from your EC2 instance"
}
