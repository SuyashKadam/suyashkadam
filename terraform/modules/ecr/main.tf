locals {
  name_prefix = "${var.project_name}-${var.environment}"
}

resource "aws_ecr_repository" "app" {
  name                 = "${local.name_prefix}-app"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "AES256"
  }

  tags = {
    Name        = "${local.name_prefix}-app"
    Project     = var.project_name
    Environment = var.environment
  }
}

# Keep only the last 10 images to save cost
resource "aws_ecr_lifecycle_policy" "app" {
  repository = aws_ecr_repository.app.name

  policy = jsonencode({
    rules = [{
      rulePriority = 1
      description  = "Expire untagged images after 7 days"
      selection = {
        tagStatus   = "untagged"
        countType   = "sinceImagePushed"
        countUnit   = "days"
        countNumber = 7
      }
      action = { type = "expire" }
    },
    {
      rulePriority = 2
      description  = "Keep only last 10 tagged images"
      selection = {
        tagStatus     = "tagged"
        tagPrefixList = ["v", "sha", "latest"]
        countType     = "imageCountMoreThan"
        countNumber   = 10
      }
      action = { type = "expire" }
    }]
  })
}
