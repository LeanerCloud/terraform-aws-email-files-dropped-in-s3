# Terraform Module: email-files-dropped-in-s3

This Terraform module sets up an AWS Lambda function that sends an email via Amazon SES whenever a new object is created in a specified S3 bucket.

## Usage

```hcl
module "email_sender" {
  source  = "LeanerCloud/email-files-dropped-in-s3/aws"
  version = "0.0.2"

  bucket_name = "my-s3-bucket"
  email_from  = "sender@example.com"
  email_to    = "recipient@example.com"
  kms_key_arn = "arn:aws:kms:us-east-1:xxxxxxxxxxxx:key/yyyyyyyyyyyyyyyyy"
  }
```

## Variables

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|----------|
| bucket_name | The name of the S3 bucket that will trigger the Lambda function | `string` | n/a | yes |
| email_from | The email address of the sender | `string` | n/a | yes |
| email_to | The email address of the recipient | `string` | n/a | yes |
| kms_key_arn | The ARN of the KMS key used to encrypt and decrypt sensitive data | `string` | `""` | no |
| filter_paths | A set of S3 object key prefixes to filter on. Only objects with keys that match at least one of these prefixes will trigger the Lambda function.| `string` | `[""]` | no |

## Outputs

| Name | Description |
|------|-------------|
| lambda_function_arn | ARN of the Lambda function |
| s3_bucket_name | Name of the S3 bucket |
| email_sender_role_arn | ARN of the IAM role for the Lambda function |
| email_sender_role_name | Name of the IAM role for the Lambda function |

## License

This module is distributed under the MIT License, see the LICENSE file for more details.
