# ============================================================
# DEV ENVIRONMENT
# Cheaper settings: t3.micro, single-AZ, no NAT Gateway,
# db.t3.micro, short backup retention
# ============================================================

module "vpc" {
  source = "../../modules/vpc"

  env                  = "dev"
  vpc_cidr             = "10.0.0.0/16"
  public_subnet_cidrs  = ["10.0.1.0/24", "10.0.2.0/24"]
  private_subnet_cidrs = ["10.0.11.0/24", "10.0.12.0/24"]
  enable_nat_gateway   = false  # Save $32/month in dev
}

module "security_group" {
  source = "../../modules/security-group"

  env     = "dev"
  vpc_id  = module.vpc.vpc_id
  your_ip = var.your_ip
}

module "ec2" {
  source = "../../modules/ec2"

  env               = "dev"
  instance_type     = "t3.micro"  # Free tier eligible
  subnet_id         = module.vpc.public_subnet_ids[0]
  security_group_id = module.security_group.web_sg_id
  key_name          = var.key_name
}

module "rds" {
  source = "../../modules/rds"

  env               = "dev"
  db_name           = "appdb"
  db_username       = "admin"
  db_password       = var.db_password
  instance_class    = "db.t3.micro"
  subnet_ids        = module.vpc.private_subnet_ids
  security_group_id = module.security_group.db_sg_id
  multi_az          = false  # Single-AZ in dev saves cost
}
