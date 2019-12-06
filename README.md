# CloudNonceDiscovery
This is the source code for COMSM0010 coursework.

## Dependencies
* Python 3
* Boto3
* awscli

## Confuguration
1. Install all dependencies and configure the AWS credentials with awscli tool. Type in ```awscli configure```in terminal and
enter the credential information.
2. Create a S3 bucket with a valid name.

## Run
1. Run cloud nonce discovery program
```bash
python3 CDN.py
```
In the program, you will be requested to enter bucket name, difficulty, number of instances to run, timeout peroid and confidence. 
To use the timeout and confidence specification, please type '-1' when asked to enter number of EC2 instances.
During the running, you could type in 'quit' to terminate all instances and quit the program.

2. Run local nonce discovery program
```bash
python3 local_nonce_discovery.py
```
In the program, you will be requested to enter difficulty, number of processes to run.
