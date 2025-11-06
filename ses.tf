resource "aws_ses_email_identity" "sender_email" {
  email = "CloudUSJ1@gmail.com"  
}

resource "aws_ses_email_identity" "recipient_1" {
  email = "marielouisehanna2003@gmail.com"
}

resource "aws_ses_email_identity" "recipient_2" {
  email = "husseindakroub80@gmail.com"
}
output "ses_verification_status" {
  description = "SES email verification status"
  value       = "Check your email inbox for verification link from AWS"
}
