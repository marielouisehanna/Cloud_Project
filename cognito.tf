resource "aws_cognito_user_pool" "secret_santa_users" {
  name = "secret-santa-user-pool"

  # Allow users to sign in with email
  username_attributes      = ["email"]
  auto_verified_attributes = ["email"]

  # Password policy
  password_policy {
    minimum_length    = 8
    require_lowercase = true
    require_numbers   = true
    require_symbols   = true
    require_uppercase = true
  }

  # Email configuration
  email_configuration {
    email_sending_account = "COGNITO_DEFAULT"
  }

  # Account recovery
  account_recovery_setting {
    recovery_mechanism {
      name     = "verified_email"
      priority = 1
    }
  }

  # User attributes
  schema {
    attribute_data_type = "String"
    name               = "email"
    required           = true
    mutable            = false

    string_attribute_constraints {
      min_length = 1
      max_length = 256
    }
  }

  tags = {
    Name        = "Secret Santa User Pool"
    Environment = "Production"
  }
}

# User pool client (for your app)
resource "aws_cognito_user_pool_client" "secret_santa_client" {
  name         = "secret-santa-web-client"
  user_pool_id = aws_cognito_user_pool.secret_santa_users.id

  # OAuth settings
  allowed_oauth_flows_user_pool_client = true
  allowed_oauth_flows                  = ["implicit"]
  allowed_oauth_scopes                 = ["email", "openid", "profile"]
  callback_urls                        = [
    "https://${aws_cloudfront_distribution.secret_santa_cdn.domain_name}",
    "http://localhost:3000"  # For local testing
  ]
  logout_urls = [
    "https://${aws_cloudfront_distribution.secret_santa_cdn.domain_name}",
    "http://localhost:3000"
  ]

  supported_identity_providers = ["COGNITO"]

  # Token validity
  access_token_validity  = 1  # 1 hour
  id_token_validity      = 1  # 1 hour
  refresh_token_validity = 30 # 30 days

  # Allow username/password auth
  explicit_auth_flows = [
    "ALLOW_USER_PASSWORD_AUTH",
    "ALLOW_REFRESH_TOKEN_AUTH",
    "ALLOW_USER_SRP_AUTH"
  ]

  # Security settings
  prevent_user_existence_errors = "ENABLED"
}

# Cognito domain for hosted UI
resource "aws_cognito_user_pool_domain" "secret_santa_domain" {
  domain       = "secret-santa-${random_string.cognito_domain_suffix.result}"
  user_pool_id = aws_cognito_user_pool.secret_santa_users.id
}

# Random suffix for unique domain
resource "random_string" "cognito_domain_suffix" {
  length  = 8
  special = false
  upper   = false
}

# Outputs
output "cognito_user_pool_id" {
  description = "Cognito User Pool ID"
  value       = aws_cognito_user_pool.secret_santa_users.id
}

output "cognito_client_id" {
  description = "Cognito App Client ID"
  value       = aws_cognito_user_pool_client.secret_santa_client.id
}

output "cognito_domain" {
  description = "Cognito Hosted UI Domain"
  value       = "https://${aws_cognito_user_pool_domain.secret_santa_domain.domain}.auth.us-east-1.amazoncognito.com"
}
