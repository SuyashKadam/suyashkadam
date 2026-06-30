# ── Web Security Group (HTTP/HTTPS from internet) ────────────
resource "aws_security_group" "web" {
  name        = "${var.env}-web-sg"
  description = "Allow HTTP and HTTPS from internet"
  vpc_id      = var.vpc_id

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow SSH only from your IP, never 0.0.0.0/0
  ingress {
    description = "SSH from my IP only"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["${var.your_ip}/32"]
  }

  egress {
    description = "All outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "${var.env}-web-sg"
    Environment = var.env
  }
}

# ── DB Security Group (only from web SG, never internet) ─────
resource "aws_security_group" "db" {
  name        = "${var.env}-db-sg"
  description = "Allow MySQL only from web security group"
  vpc_id      = var.vpc_id

  ingress {
    description     = "MySQL from web tier"
    from_port       = 3306
    to_port         = 3306
    protocol        = "tcp"
    security_groups = [aws_security_group.web.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "${var.env}-db-sg"
    Environment = var.env
  }
}
