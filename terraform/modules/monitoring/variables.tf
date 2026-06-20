variable "project_name"            { type = string }
variable "environment"             { type = string }
variable "ecs_cluster_name"        { type = string }
variable "ecs_service_name"        { type = string }
variable "alert_email"             { type = string }
variable "cpu_threshold"           { type = number }
variable "alb_arn_suffix"          { type = string }
variable "target_group_arn_suffix" { type = string }
