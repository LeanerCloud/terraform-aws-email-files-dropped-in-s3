# Terraform Module: email-files-dropped-in-s3

This Terraform module sets up an AWS Lambda function that sends an email via Amazon SES whenever a new object is created in a specified S3 bucket.

## The story behind this module

I saw this [conversation](https://www.reddit.com/r/aws/comments/11ljleg/email_files_from_s3_as_an_attachment) on the AWS Reddit about this topic and realized I'd also benefit greatly from such a tool.

My use case is to save time reading the CSV daily business report files "conveniently" dropped into an S3 bucket by the AWS Marketplace, where I'm selling some AWS cost optimization [tools](https://aws.amazon.com/marketplace/seller-profile?id=a7ef2f5c-28b4-4dc2-90f5-ce4da9127c7f).

Previously I had to log in using MFA, go to S3, find the bucket, browse to the file, etc, which took a loooong time.

I spent a few hours building this (with plenty of help from ChatGPT), but now that I have this, the file I'm interested in is delivered by email immediately and I just need to open it in a few seconds.

The email looks like this:

<img width="296" alt="Screenshot 2023-03-08 at 22 21 46" src="https://user-images.githubusercontent.com/95209/223853304-91b9116a-0e8e-4ee7-8fc7-8d99ea41f23f.png">

## Usage

```hcl
module "email_sender" {
  source  = "LeanerCloud/email-files-dropped-in-s3/aws"
  version = "0.0.3"

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

## Contributing

If you find this useful you can always [buy me a coffee](https://github.com/cristim).

You may also want to try my [LeanerCloud.com](https://LeanerCloud.com) AWS cost optimization tools, chances are they can save you some money.


## License

This module is distributed under the MIT License, see the LICENSE file for more details.
