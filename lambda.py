import boto3
import json
import os
import subprocess
import sys
import tempfile


FUNCTION_NAME = os.environ['FUNCTION_NAME']


ssm_client = boto3.client('ssm')


def get_ssm_param_name(key_group):
    return '/{}/{}'.format(FUNCTION_NAME, key_group)


def install_paramiko(python_dir):
    cmd = [
        'pip', 'install',
        '--no-cache-dir',
        '--target', python_dir,
        'paramiko==2.4.1',
    ]
    subprocess.run(cmd, check=True)


def read_keys(key_group):
    param_name = get_ssm_param_name(key_group)
    try:
        response = ssm_client.get_parameter(
            Name=param_name,
            WithDecryption=True,
        )
    except ssm_client.exceptions.ParameterNotFound:
        return None
    else:
        return json.loads(response['Parameter']['Value'])


def write_keys(key_group, keys):
    param_name = get_ssm_param_name(key_group)
    ssm_client.put_parameter(
        Name=param_name,
        Description='Managed by terraform-aws-ssh-keys',
        Value=json.dumps(keys),
        Type='SecureString',
        Overwrite=False,
    )


def lambda_handler(event, context):

    key_group = event['group']

    keys = read_keys(key_group)

    if not keys:

        keys = {}

        with tempfile.TemporaryDirectory() as temp_dir:

            # Install and import Paramiko.
            cmd = [
                'pip', 'install',
                '--no-cache-dir',
                '--target', temp_dir,
                'paramiko==2.4.1',
            ]
            subprocess.run(cmd, check=True)
            sys.path.insert(0, temp_dir)
            import paramiko

            # Generate key pairs for multiple algorithms.
            algorithms = {
                'ecdsa': lambda: paramiko.ECDSAKey.generate(),
                'rsa': lambda: paramiko.RSAKey.generate(bits=2048),
            }
            for algorithm, generate_private_key in sorted(algorithms.items()):

                keys[algorithm] = {}

                # Generate a private key.
                private_key_path = os.path.join(temp_dir, algorithm)
                private_key = generate_private_key()
                private_key.write_private_key_file(private_key_path, password=None)
                with open(private_key_path) as open_file:
                    keys[algorithm]['private'] = open_file.read()

                # Generate a public key.
                public_key = private_key.from_private_key_file(private_key_path, password=None)
                keys[algorithm]['public'] = '{} {}'.format(
                    public_key.get_name(),
                    public_key.get_base64(),
                )

        write_keys(key_group, keys)

    return keys
