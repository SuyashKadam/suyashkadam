# ============================================================
# PROD ENVIRONMENT
# Production-grade: t3.small, multi-AZ RDS, NAT Gateway,
# deletion protection, 7-day backups
# ============================================================

module "vpc" {
  source = "../../modules/vpc"

  env                  = "prod"
  vpc_cidr             = "10.1.0.0/16"  # Different CIDR than dev — no overlap
  public_subnet_cidrs  = ["10.1.1.0/24", "10.1.2.0/24", "10.1.3.0/24"]
  private_subnet_cidrs = ["10.1.11.0/24", "10.1.12.0/24", "10.1.13.0/24"]
  enable_nat_gateway   = true  # Private subnets need outbound internet in prod
}

module "security_group" {
  source = "../../modules/security-group"

  env     = "prod"
  vpc_id  = module.vpc.vpc_id
  your_ip = var.your_ip
}

module "ec2" {
  source = "../../modules/ec2"

  env               = "prod"
  instance_type     = "t3.small"  # Bigger than dev
  subnet_id         = module.vpc.public_subnet_ids[0]
  security_group_id = module.security_group.web_sg_id
  key_name          = var.key_name
}

module "rds" {
  source = "../../modules/rds"

  env               = "prod"
  db_name           = "appdb"
  db_username       = "admin"
  db_password       = var.db_password
  instance_class    = "db.t3.small"
  subnet_ids        = module.vpc.private_subnet_ids
  security_group_id = module.security_group.db_sg_id
  multi_az          = true  # Automatic failover in prod
}
