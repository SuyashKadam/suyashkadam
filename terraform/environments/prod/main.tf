# ---------- VPC ----------
module "vpc" {
  source               = "../../modules/vpc"
  project_name         = var.project_name
  environment          = var.environment
  vpc_cidr             = var.vpc_cidr
  public_subnet_cidrs  = var.public_subnet_cidrs
  private_subnet_cidrs = var.private_subnet_cidrs
  availability_zones   = var.availability_zones
}

# ---------- ECR ----------
module "ecr" {
  source       = "../../modules/ecr"
  project_name = var.project_name
  environment  = var.environment
}

# ---------- ALB ----------
module "alb" {
  source            = "../../modules/alb"
  project_name      = var.project_name
  environment       = var.environment
  vpc_id            = module.vpc.vpc_id
  public_subnet_ids = module.vpc.public_subnet_ids
}

# ---------- ECS ----------
module "ecs" {
  source                = "../../modules/ecs"
  project_name          = var.project_name
  environment           = var.environment
  vpc_id                = module.vpc.vpc_id
  private_subnet_ids    = module.vpc.private_subnet_ids
  ecr_repository_url    = module.ecr.repository_url
  alb_target_group_arn  = module.alb.target_group_arn
  alb_security_group_id = module.alb.alb_security_group_id
  container_cpu         = var.container_cpu
  container_memory      = var.container_memory
  min_capacity          = var.min_capacity
  max_capacity          = var.max_capacity
  image_tag             = var.image_tag
}

# ---------- CloudFront + WAF ----------
module "cloudfront" {
  source       = "../../modules/cloudfront"
  project_name = var.project_name
  environment  = var.environment
  alb_dns_name = module.alb.alb_dns_name
  enable_waf   = var.enable_waf
}

# ---------- Monitoring ----------
module "monitoring" {
  source                  = "../../modules/monitoring"
  project_name            = var.project_name
  environment             = var.environment
  ecs_cluster_name        = module.ecs.cluster_name
  ecs_service_name        = module.ecs.service_name
  alert_email             = var.alert_email
  cpu_threshold           = var.cpu_alarm_threshold
  alb_arn_suffix          = module.alb.alb_arn_suffix
  target_group_arn_suffix = module.alb.target_group_arn_suffix
}

# ---------- CodeBuild (build + push to ECR) ----------
module "codebuild" {
  source              = "../../modules/codebuild"
  project_name        = var.project_name
  environment         = var.environment
  ecr_repository_url  = module.ecr.repository_url
  ecr_repository_name = module.ecr.repository_name
  ecs_cluster_name    = module.ecs.cluster_name
  ecs_service_name    = module.ecs.service_name
  aws_region          = var.aws_region
}

# ---------- CodePipeline (Source > Build > Approve > Deploy) ----------
module "codepipeline" {
  source                 = "../../modules/codepipeline"
  project_name           = var.project_name
  environment            = var.environment
  github_repo            = var.github_repo
  github_branch          = var.github_branch
  codebuild_project_name = module.codebuild.project_name
  ecs_cluster_name       = module.ecs.cluster_name
  ecs_service_name       = module.ecs.service_name
  sns_topic_arn          = module.monitoring.sns_topic_arn
}
