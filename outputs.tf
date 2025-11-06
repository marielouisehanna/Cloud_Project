output "s3_bucket_name" {
  description = "Name of the S3 bucket"
  value       = aws_s3_bucket.secret_santa_website.id
}

output "s3_website_url" {
  description = "S3 website endpoint"
  value       = "http://${aws_s3_bucket.secret_santa_website.bucket}.s3-website-${aws_s3_bucket.secret_santa_website.region}.amazonaws.com"
}

output "api_gateway_url" {
  description = "API Gateway endpoint URL"
  value       = aws_apigatewayv2_stage.prod.invoke_url
}

output "dynamodb_table_name" {
  description = "DynamoDB table name"
  value       = aws_dynamodb_table.secret_santa_matches.name
}