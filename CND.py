import boto3
import logging
import time
import os, sys
import threading
from botocore.exceptions import ClientError
import numpy as np

golden_nonce = []
running = []


def main(difficulty, parallel, bucket_name):

    start_time = time.time()
    # upload credential file for boto3
    upload_file(os.path.expanduser('~/.aws/credentials'), bucket_name, 'credentials')
    upload_file(os.path.expanduser('~/.aws/config'), bucket_name, 'config')
    upload_file('nonce_discovery.py', bucket_name)

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
            #print(result)
        if message != []:
            break

    ec2 = boto3.resource('ec2', region_name='us-east-1')
    ec2.instances.terminate()

    end_time = time.time()

    golden_nonce.append(result)

    print('The nonce is ' + result)
    print("Time used: {:.2f}" .format(end_time-start_time))






def initialize():
    sqs = boto3.resource('sqs', region_name='us-east-1')

    sqs.create_queue(QueueName='feed.fifo', Attributes={'FifoQueue':'true', 'ContentBasedDeduplication':'true'})
    sqs.create_queue(QueueName='result.fifo', Attributes={'FifoQueue':'true', 'ContentBasedDeduplication':'true'})

    # clear the feed quene
    queue = sqs.get_queue_by_name(QueueName='feed.fifo')
    temp = queue.receive_messages()
    while temp != []:
        for legacy in temp:
            #print(legacy.body)
            legacy.delete()
        temp = queue.receive_messages()

    # clear the result quene
    sqs = boto3.resource('sqs', region_name='us-east-1')
    queue = sqs.get_queue_by_name(QueueName='result.fifo')
    temp = queue.receive_messages()
    while temp != []:
        for legacy in temp:
            #print(legacy.body)
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

# calculate n estimation according to timeout and confidence
def calulateN(difficulty, timeout, confidence):
    # difficulty 4
    thread4 = np.array([1, 2, 4, 8])
    time4 = np.array([141.581, 103.556, 143.040, 142.481])
    # difficulty 5
    thread5 = np.array([1, 2, 4, 8])
    time5 = np.array([139.276, 149.524, 141.977, 139.854])
    # difficulty 6
    thread6 = np.array([1, 2, 4, 8])
    time6 = np.array([179.117, 168.778, 153.090, 152.076])
    # difficulty 7
    thread7 = np.array([1, 2, 4, 8])
    time7 = np.array([827.448, 815.965, 427.377, 307.727])

    t_max = timeout * (1+(1-confidence))

    A = np.vstack([time4, np.ones(len(time4))]).T
    k4, b4 = np.linalg.lstsq(A, thread4, rcond=None)[0]
    A = np.vstack([time5, np.ones(len(time5))]).T
    k5, b5 = np.linalg.lstsq(A, thread5, rcond=None)[0]
    A = np.vstack([time6, np.ones(len(time6))]).T
    k6, b6 = np.linalg.lstsq(A, thread6, rcond=None)[0]
    A = np.vstack([time7, np.ones(len(time7))]).T
    k7, b7 = np.linalg.lstsq(A, thread7, rcond=None)[0]


    if difficulty == 4:
        return t_max * k4 +b4
    if difficulty == 5:
        return t_max * k5 + b5
    if difficulty == 6:
        return t_max * k6 + b6
    if difficulty == 7:
        return t_max * k7 + b7

# timeout thread
def timeOut(timeout):
    time.sleep(timeout)
    ec2 = boto3.resource('ec2', region_name='us-east-1')
    ec2.instances.terminate()
    print('All instances terminated!')


if __name__ == '__main__':

    bucket_name = input('Please enter bucket name:')
    difficulty = input('Please enter the difficulty:')
    parallel = input("Please enter the number of instances (use '-1' to skip):")
    timeout = input('Please enter the timeout peroid (in seconds):')
    confidence = input('Please type in the confidence (in decimal):')

    if (difficulty == '4' or difficulty == '5' or difficulty == '6' or difficulty == '7') and parallel == '-1':
        n = calulateN(int(difficulty), int(timeout), int(confidence))
        print(str(int(n)) + ' EC2 instances will run tasks for ' + timeout + ' senconds under difficulty of ' + difficulty + ' and confidence of ' + confidence)
        t = threading.Thread(target=main, args=(int(difficulty), int(n), bucket_name,))
        t.start()
        t2 = threading.Thread(target=timeOut, args=(int(timeout),))
        t2.start()

    else:
        t = threading.Thread(target=main, args=(int(difficulty), int(parallel), bucket_name,))
        t.start()


    prompt = "Enter 'quit' to end the program.\n"
    message = ''
    while golden_nonce == [] and running == []:
        pass

    while message != 'quit':
        message = input(prompt)


    ec2 = boto3.resource('ec2', region_name='us-east-1')
    ec2.instances.terminate()
    print('All instances terminated!')
    sys.exit(1)
