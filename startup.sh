#!/bin/bash
sudo apt -y update
sudo apt -y install python3
sudo apt -y install python3-pip
pip3 install boto3
sudo apt -y install awscli
mkdir ~/.aws/
cd ~/.aws/
wget https://script-python-find-golden-nonce.s3.amazonaws.com/config
wget https://script-python-find-golden-nonce.s3.amazonaws.com/credentials
cd ..
wget https://script-python-find-golden-nonce.s3.amazonaws.com/nonce_discovery.py
python3 nonce_discovery.py