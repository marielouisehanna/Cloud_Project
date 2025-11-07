# Secret Santa Generator

A serverless Secret Santa Generator built on **AWS** using **Terraform** for infrastructure as code.  
This project allows authenticated users to create, manage, and email Secret Santa matches via a simple web interface.

---

## Architecture Overview

![Secret Santa Architecture](image.png)

### Components
- **S3 + CloudFront** — Static website hosting with HTTPS and global CDN caching.  
- **Cognito** — Handles user authentication (signup/login).  
- **API Gateway** — Exposes REST endpoints for backend Lambda functions.  
- **Lambda Functions**
  - `generate_matches`: Creates random Secret Santa pairings and stores them.
  - `get_matches`: Retrieves existing matches for logged-in users.
- **DynamoDB** — Stores match data (valid for 30 days).  
- **SES** — Sends Secret Santa match emails.  
- **IAM** — Manages roles and permissions.  

---

## Frontend Features

- Simple HTML/JS website with a snow animation.  
- Form to add participants and budget.  
- Authentication required before accessing the form.  
- CSV download for organizers.

---

## Backend Logic

- Randomized Secret Santa pair generation.  
- Stores match data in DynamoDB.  
- Sends participant match emails via AWS SES.  
- Sessions expire after 30 days.

---

## Deployment

1. Configure AWS credentials.  
2. Deploy infrastructure:
   ```bash
   terraform init
   terraform apply
   ```
3. Upload frontend files to the S3 bucket.  
4. Access your website via the CloudFront domain (HTTPS enabled).

---

![Secret Santa Website Login Page](image_2.png)
