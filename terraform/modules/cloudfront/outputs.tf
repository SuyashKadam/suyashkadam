output "cloudfront_domain_name"    { value = aws_cloudfront_distribution.main.domain_name }
output "cloudfront_distribution_id" { value = aws_cloudfront_distribution.main.id }
output "cloudfront_arn"            { value = aws_cloudfront_distribution.main.arn }
output "waf_arn" {
  value = var.enable_waf ? aws_wafv2_web_acl.cloudfront[0].arn : null
}
