resource "aws_apigatewayv2_api" "secret_santa_api" {
  name          = "secret-santa-api"
  protocol_type = "HTTP"
  
  cors_configuration {
    allow_origins = ["*"]
    allow_methods = ["POST", "GET", "OPTIONS"]
    allow_headers = ["content-type"]
  }
}

resource "aws_apigatewayv2_stage" "prod" {
  api_id      = aws_apigatewayv2_api.secret_santa_api.id
  name        = "prod"
  auto_deploy = true
}

resource "aws_apigatewayv2_integration" "lambda_integration" {
  api_id           = aws_apigatewayv2_api.secret_santa_api.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.secret_santa_generator.invoke_arn
}

resource "aws_apigatewayv2_route" "generate_route" {
  api_id    = aws_apigatewayv2_api.secret_santa_api.id
  route_key = "POST /generate"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
}

resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.secret_santa_generator.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.secret_santa_api.execution_arn}/*/*"
}