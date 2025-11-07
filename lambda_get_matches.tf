resource "aws_lambda_function" "get_matches" {
  filename         = "lambda_get_matches.zip"
  function_name    = "get_matches"
  handler          = "lambda_get_matches.handler"
  runtime          = "python3.11"
  role             = aws_iam_role.lambda_role.arn
  source_code_hash = filebase64sha256("lambda_get_matches.zip")

  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.secret_santa_matches.name
    }
  }

  depends_on = [
    aws_iam_role_policy.lambda_dynamodb_ses
  ]
}

resource "aws_apigatewayv2_integration" "get_matches_integration" {
  api_id           = aws_apigatewayv2_api.secret_santa_api.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.get_matches.invoke_arn
}

resource "aws_apigatewayv2_route" "get_matches_route" {
  api_id    = aws_apigatewayv2_api.secret_santa_api.id
  route_key = "GET /get-matches"
  target    = "integrations/${aws_apigatewayv2_integration.get_matches_integration.id}"
}

resource "aws_lambda_permission" "api_gateway_get_matches" {
  statement_id  = "AllowAPIGatewayInvokeGetMatches"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.get_matches.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.secret_santa_api.execution_arn}/*/*"
}
