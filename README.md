# terraform-aws-ssh-keys

This module creates an AWS Lambda function that manages SSH keys. SSH keys are stored in the SSM Parameter Store.

The Lambda function generates ECDSA and RSA key pairs. It accepts a single `group` argument which is used to store/retrieve the key pair group from an SSM parameter.

One use case for this module is for centralized SSH host keys on EC2 instances in an auto scaling group. When an EC2 instance boots up, it can call this function and swap out its SSH host keys with the keys returned by the Lambda function.

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|:----:|:-----:|:-----:|
| name | Name used for Terraform resources. | string | - | yes |

## Outputs

| Name | Description |
|------|-------------|
| lambda_function_arn | The ARN of the Lambda function. |
| lambda_function_name | The name of the Lambda function. |
