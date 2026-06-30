provider "aws" {
  region = "us-east-1"
}

# ── Dev IAM Policy ───────────────────────────────────────────
# Allows full Terraform access to dev state only
resource "aws_iam_policy" "terraform_dev" {
  name        = "TerraformDevAccess"
  description = "Allows terraform operations on dev environment"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "DevStateAccess"
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          "arn:aws:s3:::yourname-terraform-state-2024",
          "arn:aws:s3:::yourname-terraform-state-2024/dev/*"
        ]
      },
      {
        Sid    = "StateLocking"
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:DeleteItem",
          "dynamodb:DescribeTable"
        ]
        Resource = "arn:aws:dynamodb:us-east-1:*:table/terraform-state-lock"
      }
    ]
  })
}

# ── Prod IAM Policy ──────────────────────────────────────────
# Allows full Terraform access to prod state AND requires MFA
resource "aws_iam_policy" "terraform_prod" {
  name        = "TerraformProdAccess"
  description = "Allows terraform operations on prod. MFA required."

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "ProdStateAccess"
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          "arn:aws:s3:::yourname-terraform-state-2024",
          "arn:aws:s3:::yourname-terraform-state-2024/prod/*"
        ]
      },
      {
        Sid    = "StateLocking"
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:DeleteItem",
          "dynamodb:DescribeTable"
        ]
        Resource = "arn:aws:dynamodb:us-east-1:*:table/terraform-state-lock"
      },
      {
        Sid    = "DenyWithoutMFA"
        Effect = "Deny"
        Action = "*"
        Resource = "*"
        Condition = {
          BoolIfExists = {
            "aws:MultiFactorAuthPresent" = "false"
          }
        }
      }
    ]
  })
}

# ── CI/CD OIDC Role (GitHub Actions → AWS, no stored keys) ──
data "aws_iam_openid_connect_provider" "github" {
  url = "https://token.actions.githubusercontent.com"
}

resource "aws_iam_role" "github_actions_dev" {
  name = "GitHubActionsTerraformDev"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Federated = data.aws_iam_openid_connect_provider.github.arn
      }
      Action = "sts:AssumeRoleWithWebIdentity"
      Condition = {
        StringLike = {
          # Only allow your repo to assume this role
          "token.actions.githubusercontent.com:sub" = "repo:your-github-username/your-repo:*"
        }
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "github_dev" {
  role       = aws_iam_role.github_actions_dev.name
  policy_arn = aws_iam_policy.terraform_dev.arn
}
