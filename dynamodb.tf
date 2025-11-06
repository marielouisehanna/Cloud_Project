resource "aws_dynamodb_table" "secret_santa_matches" {
  name           = "SecretSantaMatches"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "session_id"

  attribute {
    name = "session_id"
    type = "S"
  }

  ttl {
    attribute_name = "expiration_time"
    enabled        = true
  }

  tags = {
    Name        = "Secret Santa Matches"
    Project     = "SecretSanta"
    Environment = "Dev"
  }
}