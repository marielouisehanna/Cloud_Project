resource "aws_lambda_function" "secret_santa_generator" {
  filename      = "lambda_function.zip"
  function_name = "secret-santa-generator"
  role          = aws_iam_role.lambda_role.arn
  handler       = "lambda_function.handler"
  runtime       = "python3.11"

  environment {
    variables = {
      DYNAMODB_TABLE = aws_dynamodb_table.secret_santa_matches.name
    }
  }

  tags = {
    Name        = "Secret Santa Generator"
    Project     = "SecretSanta"
    Environment = "Dev"
  }
}