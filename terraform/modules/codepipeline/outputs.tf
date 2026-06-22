output "pipeline_name"              { value = aws_codepipeline.main.name }
output "pipeline_arn"               { value = aws_codepipeline.main.arn }
output "codestar_connection_arn"    { value = aws_codestarconnections_connection.github.arn }
output "codestar_connection_status" { value = aws_codestarconnections_connection.github.connection_status }
output "artifacts_bucket"           { value = aws_s3_bucket.artifacts.bucket }
