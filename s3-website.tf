resource "aws_s3_bucket_website_configuration" "website" {
  bucket = aws_s3_bucket.secret_santa_website.id

  index_document {
    suffix = "index.html"
  }

  error_document {
    key = "error.html"
  }
}

resource "aws_s3_bucket_policy" "website" {
  bucket = aws_s3_bucket.secret_santa_website.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "PublicReadGetObject"
        Effect    = "Allow"
        Principal = "*"
        Action    = "s3:GetObject"
        Resource  = "${aws_s3_bucket.secret_santa_website.arn}/*"
      }
    ]
  })

  depends_on = [aws_s3_bucket_public_access_block.website]
}

# Upload the index.html file to S3
resource "aws_s3_object" "index_html" {
  bucket       = aws_s3_bucket.secret_santa_website.id
  key          = "index.html"
  source       = "index.html"
  content_type = "text/html"
  etag         = filemd5("index.html")
}