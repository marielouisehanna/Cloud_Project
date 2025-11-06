resource "aws_s3_bucket" "secret_santa_website" {
  bucket = "secret-santa-app-${random_string.bucket_suffix.result}"

  tags = {
    Name        = "Secret Santa Website"
    Project     = "SecretSanta"
    Environment = "Dev"
  }
}

resource "random_string" "bucket_suffix" {
  length  = 8
  special = false
  upper   = false
}

resource "aws_s3_bucket_public_access_block" "website" {
  bucket = aws_s3_bucket.secret_santa_website.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}