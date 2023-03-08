variable "email_from" {
  description = "The email address of the sender"
  type        = string
}

variable "email_to" {
  description = "The email address of the recipient"
  type        = string
}

variable "bucket_name" {
  description = "The name of the S3 bucket that will trigger the Lambda function"
  type        = string
}

variable "kms_key_arn" {
  description = "The ARN of the KMS key used to encrypt and decrypt sensitive data"
  type        = string
  default     = ""
}

variable "filter_paths" {
  description = "A set of S3 object key prefixes to filter on. Only objects with keys that match at least one of these prefixes will trigger the Lambda function. Defaults to matching all object keys with '*'."
  type        = set(string)
  default     = [""]
}
