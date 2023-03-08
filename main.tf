data "archive_file" "lambda_code" {
  type        = "zip"
  source_dir  = "${path.module}/lambda"
  output_path = "${path.module}/email_sender.zip"
}

data "aws_s3_bucket" "bucket" {
  bucket = var.bucket_name
}


resource "aws_s3_bucket_notification" "bucket_notification" {
  for_each = var.filter_paths

  bucket = data.aws_s3_bucket.bucket.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.email_sender.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = each.value
  }
}


resource "aws_lambda_function" "email_sender" {
  function_name = "email_sender_lambda"
  role          = aws_iam_role.lambda.arn
  handler       = "handler.lambda_handler"
  runtime       = "python3.8"

  environment {
    variables = {
      EMAIL_FROM = var.email_from
      EMAIL_TO   = var.email_to
    }
  }

  filename         = "email_sender.zip"
  source_code_hash = filebase64sha256(data.archive_file.lambda_code.output_path)
}

resource "aws_lambda_permission" "s3_lambda_permission" {
  statement_id  = "AllowS3ObjectAccess"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.email_sender.arn
  principal     = "s3.amazonaws.com"
  source_arn    = data.aws_s3_bucket.bucket.arn
}

resource "aws_iam_role_policy_attachment" "lambda" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  role       = aws_iam_role.lambda.name
}

resource "aws_iam_role" "lambda" {
  name = "lambda_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  inline_policy {
    name = "lambda_policy"

    policy = jsonencode({
      Version = "2012-10-17",
      Statement = [
        {
          Action = [
            "logs:CreateLogGroup",
            "logs:CreateLogStream",
            "logs:PutLogEvents"
          ],
          Effect   = "Allow",
          Resource = "arn:aws:logs:*:*:*",
        },
        {
          Action = [
            "s3:GetObject"
          ],
          Effect   = "Allow",
          Resource = "${data.aws_s3_bucket.bucket.arn}/*",
        },
        {

          Condition = {
            StringNotEqualsIfExists = {
              "${var.kms_key_arn}" : ""
            }
          }
          Action = [
            "kms:Decrypt"
          ],
          Effect   = "Allow",
          Resource = var.kms_key_arn,
        },
        {
          Action = [
            "ses:SendRawEmail"
          ],
          Effect   = "Allow",
          Resource = "*",
        }
      ]
    })
  }
}
