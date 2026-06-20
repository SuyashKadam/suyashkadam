output "project_name"    { value = aws_codebuild_project.app.name }
output "project_arn"     { value = aws_codebuild_project.app.arn }
output "role_arn"        { value = aws_iam_role.codebuild.arn }
output "artifacts_bucket" { value = aws_s3_bucket.artifacts.bucket }
