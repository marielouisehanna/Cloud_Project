resource "aws_lambda_function" "get_matches" {
  filename         = "lambda_get_matches.zip"
  function_name    = "get_matches"
  handler          = "lambda_get_matches.handler"
  runtime          = "python3.11"
  role             = aws_iam_role.lambda_role.arn

  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.secret_santa_matches.name
    }
  }

  depends_on = [
    aws_iam_role_policy.lambda_dynamodb_ses
  ]
}

resource "aws_lambda_permission" "api_gateway_get_matches" {
  statement_id  = "AllowAPIGatewayInvokeGetMatches"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.get_matches.function_name
  principal     = "apigateway.amazonaws.com"
}
