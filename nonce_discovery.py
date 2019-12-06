import hashlib
import boto3
import time
import random

def getmessage():
    sqs = boto3.resource('sqs', region_name='us-east-1')
    queue = sqs.get_queue_by_name(QueueName='feed.fifo')

    # get message from feed queue
    while True:
        #time.sleep(1)
        message = queue.receive_messages()
        for iter in message:
            feed = iter.body
            iter.delete()
            #print(feed)
        if message != []:
            break

    #print(feed)
    feed = feed.split(',')
    return int(feed[0]), int(feed[1]), int(feed[2])

def send_message(message):

    sqs = boto3.resource('sqs', region_name='us-east-1')
    queue = sqs.get_queue_by_name(QueueName='result.fifo')
    response = queue.send_message(
        MessageBody = message,
        MessageGroupId = 'messageGroup1'
    )
    #print(response.get('MessageId'))
    #print(response.get('MD5OfMessageBody'))


def find_nonce(transaction, difficulty, start, end):

    zero = '0' * difficulty

    for iteration in range(start, end):

        candidate = str(iteration)
        feed = transaction + candidate
        #print(feed)

        sha1 = hashlib.sha256(feed.encode("utf8")).hexdigest()
        sha2 = hashlib.sha256(sha1.encode("utf8"))

        if sha2.hexdigest()[0:difficulty]==zero:
            print(sha2.hexdigest())
            return candidate
    return '-1'

if __name__ == '__main__':
    transction = 'COMSM0010cloud'

    difficulty, start, end = getmessage()
    nonce = find_nonce(transction, difficulty,start, end)
    # send nonce to result queue
    send_message(nonce)
    print("The nonce is:" + nonce)



