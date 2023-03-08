output "lambda_function_arn" {
  value = aws_lambda_function.email_sender.arn
}

output "s3_bucket_name" {
  value = data.aws_s3_bucket.bucket.id
}

output "email_sender_role_arn" {
  value = aws_iam_role.lambda.arn
}

output "email_sender_role_name" {
  value = aws_iam_role.lambda.name
}
