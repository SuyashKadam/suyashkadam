output "cloudfront_url" {
  description = "CloudFront distribution URL — use this to access the website"
  value       = "https://${module.cloudfront.cloudfront_domain_name}"
}

output "alb_dns_name" {
  description = "ALB DNS name (internal; access via CloudFront URL instead)"
  value       = module.alb.alb_dns_name
}

output "ecr_repository_url" {
  description = "ECR repository URL for pushing Docker images"
  value       = module.ecr.repository_url
}

output "ecs_cluster_name" {
  description = "ECS cluster name"
  value       = module.ecs.cluster_name
}

output "ecs_service_name" {
  description = "ECS service name"
  value       = module.ecs.service_name
}

output "codebuild_project_name" {
  description = "CodeBuild project name — trigger this to deploy"
  value       = module.codebuild.project_name
}

output "sns_topic_arn" {
  description = "SNS topic ARN for CloudWatch alerts"
  value       = module.monitoring.sns_topic_arn
}

output "vpc_id" {
  description = "VPC ID"
  value       = module.vpc.vpc_id
}

output "cloudfront_distribution_id" {
  description = "CloudFront distribution ID"
  value       = module.cloudfront.cloudfront_distribution_id
}
