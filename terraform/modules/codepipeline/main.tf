locals {
  name_prefix = "${var.project_name}-${var.environment}"
}

data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# ---------- CodeStar Connection to GitHub ----------
resource "aws_codestarconnections_connection" "github" {
  name          = "${local.name_prefix}-github"
  provider_type = "GitHub"

  tags = {
    Name        = "${local.name_prefix}-github-connection"
    Project     = var.project_name
    Environment = var.environment
  }
}

# ---------- S3 Artifact Bucket ----------
resource "aws_s3_bucket" "artifacts" {
  bucket        = "${local.name_prefix}-pipeline-artifacts-${data.aws_caller_identity.current.account_id}"
  force_destroy = true

  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

resource "aws_s3_bucket_versioning" "artifacts" {
  bucket = aws_s3_bucket.artifacts.id
  versioning_configuration { status = "Enabled" }
}

resource "aws_s3_bucket_public_access_block" "artifacts" {
  bucket                  = aws_s3_bucket.artifacts.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_lifecycle_configuration" "artifacts" {
  bucket = aws_s3_bucket.artifacts.id
  rule {
    id     = "expire-old-artifacts"
    status = "Enabled"
    filter { prefix = "" }
    expiration { days = 30 }
  }
}

# ---------- IAM Role for CodePipeline ----------
resource "aws_iam_role" "pipeline" {
  name = "${local.name_prefix}-pipeline-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "codepipeline.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy" "pipeline" {
  name = "${local.name_prefix}-pipeline-policy"
  role = aws_iam_role.pipeline.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "S3Artifacts"
        Effect = "Allow"
        Action = [
          "s3:GetObject", "s3:GetObjectVersion",
          "s3:PutObject", "s3:GetBucketAcl",
          "s3:GetBucketLocation", "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.artifacts.arn,
          "${aws_s3_bucket.artifacts.arn}/*"
        ]
      },
      {
        Sid    = "CodeBuild"
        Effect = "Allow"
        Action = [
          "codebuild:BatchGetBuilds",
          "codebuild:StartBuild",
          "codebuild:StopBuild"
        ]
        Resource = "*"
      },
      {
        Sid    = "CodeStarConnections"
        Effect = "Allow"
        Action = [
          "codestar-connections:UseConnection"
        ]
        Resource = aws_codestarconnections_connection.github.arn
      },
      {
        Sid    = "ECS"
        Effect = "Allow"
        Action = [
          "ecs:DescribeServices",
          "ecs:DescribeTaskDefinition",
          "ecs:DescribeTasks",
          "ecs:ListTasks",
          "ecs:RegisterTaskDefinition",
          "ecs:UpdateService"
        ]
        Resource = "*"
      },
      {
        Sid      = "IAMPassRole"
        Effect   = "Allow"
        Action   = ["iam:PassRole"]
        Resource = "*"
        Condition = {
          StringEqualsIfExists = {
            "iam:PassedToService" = [
              "ecs-tasks.amazonaws.com",
              "ecs.amazonaws.com"
            ]
          }
        }
      },
      {
        Sid    = "SNSApproval"
        Effect = "Allow"
        Action = ["sns:Publish"]
        Resource = var.sns_topic_arn
      }
    ]
  })
}

# ---------- CodePipeline ----------
resource "aws_codepipeline" "main" {
  name     = "${local.name_prefix}-pipeline"
  role_arn = aws_iam_role.pipeline.arn

  artifact_store {
    location = aws_s3_bucket.artifacts.bucket
    type     = "S3"
  }

  # ── Stage 1: Source ──────────────────────────────────────
  stage {
    name = "Source"

    action {
      name             = "GitHub-Source"
      category         = "Source"
      owner            = "AWS"
      provider         = "CodeStarSourceConnection"
      version          = "1"
      output_artifacts = ["source_output"]

      configuration = {
        ConnectionArn        = aws_codestarconnections_connection.github.arn
        FullRepositoryId     = var.github_repo
        BranchName           = var.github_branch
        OutputArtifactFormat = "CODE_ZIP"
        DetectChanges        = "true"
      }
    }
  }

  # ── Stage 2: Build ───────────────────────────────────────
  stage {
    name = "Build"

    action {
      name             = "Docker-Build-Push"
      category         = "Build"
      owner            = "AWS"
      provider         = "CodeBuild"
      version          = "1"
      input_artifacts  = ["source_output"]
      output_artifacts = ["build_output"]

      configuration = {
        ProjectName = var.codebuild_project_name
      }
    }
  }

  # ── Stage 3: Manual Approval ─────────────────────────────
  stage {
    name = "Approve"

    action {
      name     = "Manual-Approval"
      category = "Approval"
      owner    = "AWS"
      provider = "Manual"
      version  = "1"

      configuration = {
        NotificationArn    = var.sns_topic_arn
        CustomData         = "New build is ready. Review CodeBuild logs then approve to deploy to ECS."
        ExternalEntityLink = "https://console.aws.amazon.com/codesuite/codebuild/projects/${var.codebuild_project_name}/history"
      }
    }
  }

  # ── Stage 4: Deploy ──────────────────────────────────────
  stage {
    name = "Deploy"

    action {
      name            = "ECS-Deploy"
      category        = "Deploy"
      owner           = "AWS"
      provider        = "ECS"
      version         = "1"
      input_artifacts = ["build_output"]

      configuration = {
        ClusterName = var.ecs_cluster_name
        ServiceName = var.ecs_service_name
        FileName    = "imagedefinitions.json"
        DeploymentTimeout = "15"
      }
    }
  }

  tags = {
    Name        = "${local.name_prefix}-pipeline"
    Project     = var.project_name
    Environment = var.environment
  }
}

# ---------- CloudWatch alarm for pipeline failures ----------
resource "aws_cloudwatch_event_rule" "pipeline_failed" {
  name        = "${local.name_prefix}-pipeline-failed"
  description = "Alert when CodePipeline stage fails"

  event_pattern = jsonencode({
    source      = ["aws.codepipeline"]
    detail-type = ["CodePipeline Stage Execution State Change"]
    detail = {
      state    = ["FAILED"]
      pipeline = [aws_codepipeline.main.name]
    }
  })
}

resource "aws_cloudwatch_event_target" "pipeline_failed_sns" {
  rule      = aws_cloudwatch_event_rule.pipeline_failed.name
  target_id = "SendToSNS"
  arn       = var.sns_topic_arn
}

resource "aws_sns_topic_policy" "allow_eventbridge" {
  arn = var.sns_topic_arn

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid    = "AllowEventBridge"
      Effect = "Allow"
      Principal = { Service = "events.amazonaws.com" }
      Action   = "SNS:Publish"
      Resource = var.sns_topic_arn
    }]
  })
}
