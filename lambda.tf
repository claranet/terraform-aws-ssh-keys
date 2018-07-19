module "lambda" {
  source = "github.com/claranet/terraform-aws-lambda?ref=v0.9.1"

  function_name = "${var.name}"
  description   = "SSH host key management"
  handler       = "lambda.lambda_handler"
  runtime       = "python3.6"
  memory_size   = 256
  timeout       = 300

  reserved_concurrent_executions = 1

  source_path = "${path.module}/lambda.py"

  attach_policy = true
  policy        = "${data.aws_iam_policy_document.lambda.json}"

  environment {
    variables {
      FUNCTION_NAME = "${var.name}"
    }
  }
}

data "aws_iam_policy_document" "lambda" {
  statement {
    effect = "Allow"

    actions = [
      "ssm:GetParameter*",
      "ssm:PutParameter*",
    ]

    resources = [
      "arn:aws:ssm:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:parameter/${var.name}/*",
    ]
  }
}
