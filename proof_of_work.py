import boto3
import logging
import time
import os, sys
import threading
from botocore.exceptions import ClientError

golden_nonce = []
running = []


def main(difficulty, parallel):

    start_time = time.time()
    # upload credential file for boto3
    upload_file(os.path.expanduser('~/.aws/credentials'), 'script-python-find-golden-nonce', 'credentials')
    #upload_file('nonce_discovery.py', 'script-python-find-golden-nonce', 'nonce_discovery.py')

    initialize()

    # split work
    total = 4294967296
    workload = []
    split = total / parallel
    for iter in range(0, parallel):
        start = iter * split
        end = (iter + 1) * split - 1
        workload.append(str(difficulty) + ',' + str(int(start)) + ',' + str(int(end)))
    #print(workload)
    #send splited work to sqs
    for message in workload:
        send_message_to_sqs(message)

    # load n instances
    for iter in range(0, parallel):
        create_instance()
        print('Instance ' + str(iter+1) + ' is up.')

    running.append(1)

    # get result from result quene
    sqs = boto3.resource('sqs', region_name='us-east-1')
    queue = sqs.get_queue_by_name(QueueName='result.fifo')

    while True:
        message = queue.receive_messages()
        for iter in message:
            result = iter.body
            iter.delete()
            print(result)

    ec2 = boto3.resource('ec2', region_name='us-east-1')
    ec2.instances.terminate()

    endtime = time.time()

    golden_nonce.append(result)

    print('The nonce is ' + result)
    print('Time used is ' + str(endtime-start_time) + 's')






def initialize():
    sqs = boto3.resource('sqs', region_name='us-east-1')

    sqs.create_queue(QueueName='feed.fifo', Attributes={'FifoQueue':'true', 'ContentBasedDeduplication':'true'})
    sqs.create_queue(QueueName='result.fifo', Attributes={'FifoQueue':'true', 'ContentBasedDeduplication':'true'})

    # clear the feed quene
    queue = sqs.get_queue_by_name(QueueName='feed.fifo')
    temp = queue.receive_messages()
    while temp != []:
        for legacy in temp:
            print(legacy.body)
            legacy.delete()
        temp = queue.receive_messages()

    # clear the result quene
    sqs = boto3.resource('sqs', region_name='us-east-1')
    queue = sqs.get_queue_by_name(QueueName='result.fifo')
    temp = queue.receive_messages()
    while temp != []:
        for legacy in temp:
            print(legacy.body)
            legacy.delete()
        temp = queue.receive_messages()


def create_instance():
    ec2 = boto3.resource('ec2', region_name='us-east-1')

    with open('startup.sh', 'r') as f:
        userdata = f.read()

    ec2.create_instances(
        ImageId='ami-04b9e92b5572fa0d1', MinCount=1, MaxCount=1, InstanceType='t2.micro',
        SecurityGroups = ['launch-wizard-1'], KeyName='pow', UserData = userdata
    )

def send_message_to_sqs(message):
    sqs = boto3.resource('sqs', region_name='us-east-1')
    queue = sqs.get_queue_by_name(QueueName='feed.fifo')

    response = queue.send_message(
        MessageBody = message,
        MessageGroupId = 'messageGroup1'
    )

def get_message_from_sqs():
    sqs = boto3.resource('sqs', region_name='us-east-1')
    queue = sqs.get_queue_by_name(QueueName='result.fifo')

    result = ''
    for message in queue.receive_messages():
        # Print out the body of the message
        result = message.body
        message.delete()
        return result

def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name, ExtraArgs={'ACL':'public-read'})
    except ClientError as e:
        logging.error(e)
        return False
    return True


def test(a):
    print(a)

if __name__ == '__main__':

    difficulty = input('Please enter the difficulty:')
    parallel = input('Please enter the number of instances:')

    print(parallel + ' EC2 instances will run tasks under difficulty ' + difficulty)

    #t = threading.Thread(target=main, args=(int(difficulty), int(parallel), ))
    #t.start()
    main(int(difficulty), int(parallel))

    #prompt = "Enter 'quit' to end the program.\n"
    #message = ''
    #while golden_nonce == [] and running == []:
       # pass

   # while message != 'quit' and golden_nonce == [] and running != []:
        #message = input(prompt)

    #ec2 = boto3.resource('ec2', region_name='us-east-1')
    #ec2.instances.terminate()
    #print()
