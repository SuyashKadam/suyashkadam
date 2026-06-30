resource "aws_db_subnet_group" "main" {
  name       = "${var.env}-db-subnet-group"
  subnet_ids = var.subnet_ids

  tags = {
    Name        = "${var.env}-db-subnet-group"
    Environment = var.env
  }
}

resource "aws_db_instance" "main" {
  identifier = "${var.env}-mysql"

  engine         = "mysql"
  engine_version = "8.0"
  instance_class = var.instance_class

  db_name  = var.db_name
  username = var.db_username
  password = var.db_password

  allocated_storage     = var.env == "prod" ? 100 : 20
  max_allocated_storage = var.env == "prod" ? 1000 : 100  # Auto-scaling storage
  storage_type          = "gp3"
  storage_encrypted     = true

  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [var.security_group_id]

  # Never expose RDS to the internet
  publicly_accessible = false

  # Multi-AZ in prod = automatic failover, false in dev = saves cost
  multi_az = var.multi_az

  # Automated backups
  backup_retention_period = var.env == "prod" ? 7 : 1
  backup_window           = "03:00-04:00"
  maintenance_window      = "sun:04:00-sun:05:00"

  # Protect prod DB from accidental terraform destroy
  deletion_protection = var.env == "prod" ? true : false
  skip_final_snapshot = var.env == "prod" ? false : true

  final_snapshot_identifier = var.env == "prod" ? "${var.env}-mysql-final-snapshot" : null

  tags = {
    Name        = "${var.env}-mysql"
    Environment = var.env
    ManagedBy   = "terraform"
  }
}
