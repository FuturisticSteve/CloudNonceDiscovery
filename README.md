# CloudNonceDiscovery
This is the source code for COMSM0010 coursework

## Dependencies
* Python 3
* Boto3
* awscli

## Confuguration
1. Install all dependencies and configure the AWS credentials with awscli tool. Type in ```awscli configure```in terminal and
enter the credential information.
2. Create a S3 bucket with a valid name.

## Run
```bash
python3 CDN.py
```
In the program, you will be requested to enter bucket name, difficulty, number of instances to run and timeout peroid.
