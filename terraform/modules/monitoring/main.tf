locals {
  name_prefix = "${var.project_name}-${var.environment}"
}

# ---------- SNS Topic ----------
resource "aws_sns_topic" "alerts" {
  name         = "${local.name_prefix}-alerts"
  display_name = "DevOps Alerts - ${upper(var.environment)}"

  tags = {
    Name        = "${local.name_prefix}-alerts"
    Project     = var.project_name
    Environment = var.environment
  }
}

resource "aws_sns_topic_subscription" "email" {
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email
}

# ---------- CloudWatch Dashboard ----------
resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = "${local.name_prefix}-dashboard"

  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6
        properties = {
          title  = "ECS CPU Utilization"
          view   = "timeSeries"
          region = data.aws_region.current.name
          metrics = [[
            "AWS/ECS",
            "CPUUtilization",
            "ClusterName", var.ecs_cluster_name,
            "ServiceName", var.ecs_service_name
          ]]
          period = 60
          stat   = "Average"
          yAxis  = { left = { min = 0, max = 100 } }
          annotations = {
            horizontal = [{ value = var.cpu_threshold, color = "#ff6961", label = "Scale threshold" }]
          }
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 0
        width  = 12
        height = 6
        properties = {
          title  = "ECS Memory Utilization"
          view   = "timeSeries"
          region = data.aws_region.current.name
          metrics = [[
            "AWS/ECS",
            "MemoryUtilization",
            "ClusterName", var.ecs_cluster_name,
            "ServiceName", var.ecs_service_name
          ]]
          period = 60
          stat   = "Average"
          yAxis  = { left = { min = 0, max = 100 } }
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 6
        width  = 12
        height = 6
        properties = {
          title  = "ALB Request Count"
          view   = "timeSeries"
          region = data.aws_region.current.name
          metrics = [[
            "AWS/ApplicationELB",
            "RequestCount",
            "LoadBalancer", var.alb_arn_suffix
          ]]
          period = 60
          stat   = "Sum"
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 6
        width  = 12
        height = 6
        properties = {
          title  = "ALB Target Response Time"
          view   = "timeSeries"
          region = data.aws_region.current.name
          metrics = [[
            "AWS/ApplicationELB",
            "TargetResponseTime",
            "LoadBalancer", var.alb_arn_suffix
          ]]
          period = 60
          stat   = "p99"
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 12
        width  = 12
        height = 6
        properties = {
          title  = "ALB HTTP 5xx Errors"
          view   = "timeSeries"
          region = data.aws_region.current.name
          metrics = [[
            "AWS/ApplicationELB",
            "HTTPCode_Target_5XX_Count",
            "LoadBalancer", var.alb_arn_suffix
          ]]
          period = 60
          stat   = "Sum"
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 12
        width  = 12
        height = 6
        properties = {
          title  = "ECS Running Task Count"
          view   = "timeSeries"
          region = data.aws_region.current.name
          metrics = [[
            "ECS/ContainerInsights",
            "RunningTaskCount",
            "ClusterName", var.ecs_cluster_name,
            "ServiceName", var.ecs_service_name
          ]]
          period = 60
          stat   = "Average"
          annotations = {
            horizontal = [
              { value = 3, color = "#2ca02c", label = "Min capacity" },
              { value = 6, color = "#ff7f0e", label = "Max capacity" }
            ]
          }
        }
      }
    ]
  })
}

data "aws_region" "current" {}

# ---------- CloudWatch Alarms ----------

# CPU High — triggers auto-scaling and email alert
resource "aws_cloudwatch_metric_alarm" "cpu_high" {
  alarm_name          = "${local.name_prefix}-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ECS"
  period              = 60
  statistic           = "Average"
  threshold           = var.cpu_threshold
  alarm_description   = "ECS CPU utilization exceeded ${var.cpu_threshold}% — auto-scaling triggered"
  treat_missing_data  = "notBreaching"

  dimensions = {
    ClusterName = var.ecs_cluster_name
    ServiceName = var.ecs_service_name
  }

  alarm_actions = [aws_sns_topic.alerts.arn]
  ok_actions    = [aws_sns_topic.alerts.arn]

  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

# Memory High
resource "aws_cloudwatch_metric_alarm" "memory_high" {
  alarm_name          = "${local.name_prefix}-memory-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "MemoryUtilization"
  namespace           = "AWS/ECS"
  period              = 60
  statistic           = "Average"
  threshold           = var.cpu_threshold
  alarm_description   = "ECS Memory utilization exceeded ${var.cpu_threshold}%"
  treat_missing_data  = "notBreaching"

  dimensions = {
    ClusterName = var.ecs_cluster_name
    ServiceName = var.ecs_service_name
  }

  alarm_actions = [aws_sns_topic.alerts.arn]
  ok_actions    = [aws_sns_topic.alerts.arn]

  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

# ALB 5xx spike
resource "aws_cloudwatch_metric_alarm" "alb_5xx" {
  alarm_name          = "${local.name_prefix}-alb-5xx-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "HTTPCode_Target_5XX_Count"
  namespace           = "AWS/ApplicationELB"
  period              = 60
  statistic           = "Sum"
  threshold           = 10
  alarm_description   = "ALB is returning more than 10 HTTP 5xx errors per minute"
  treat_missing_data  = "notBreaching"

  dimensions = {
    LoadBalancer = var.alb_arn_suffix
  }

  alarm_actions = [aws_sns_topic.alerts.arn]
  ok_actions    = [aws_sns_topic.alerts.arn]

  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

# ALB unhealthy hosts
resource "aws_cloudwatch_metric_alarm" "unhealthy_hosts" {
  alarm_name          = "${local.name_prefix}-unhealthy-hosts"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "UnHealthyHostCount"
  namespace           = "AWS/ApplicationELB"
  period              = 60
  statistic           = "Average"
  threshold           = 0
  alarm_description   = "One or more ECS tasks are failing ALB health checks"
  treat_missing_data  = "notBreaching"

  dimensions = {
    LoadBalancer = var.alb_arn_suffix
    TargetGroup  = var.target_group_arn_suffix
  }

  alarm_actions = [aws_sns_topic.alerts.arn]
  ok_actions    = [aws_sns_topic.alerts.arn]

  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

# P99 latency > 2s
resource "aws_cloudwatch_metric_alarm" "high_latency" {
  alarm_name          = "${local.name_prefix}-high-latency"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 3
  metric_name         = "TargetResponseTime"
  namespace           = "AWS/ApplicationELB"
  period              = 60
  extended_statistic  = "p99"
  threshold           = 2
  alarm_description   = "P99 response time exceeded 2 seconds"
  treat_missing_data  = "notBreaching"

  dimensions = {
    LoadBalancer = var.alb_arn_suffix
  }

  alarm_actions = [aws_sns_topic.alerts.arn]
  ok_actions    = [aws_sns_topic.alerts.arn]

  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}
