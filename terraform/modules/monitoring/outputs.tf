output "sns_topic_arn"    { value = aws_sns_topic.alerts.arn }
output "dashboard_name"   { value = aws_cloudwatch_dashboard.main.dashboard_name }
output "cpu_alarm_name"   { value = aws_cloudwatch_metric_alarm.cpu_high.alarm_name }
