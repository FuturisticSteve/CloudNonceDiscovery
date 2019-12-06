import hashlib
import os, sys
from multiprocessing import Value, Process
import time



def find_nonce(transaction, difficulty, start, end, result):

    zero = '0' * difficulty

    for iteration in range(start, end):
        #if iteration%200000 == 0:
            #send_message('iteration: ' + str(iteration))
        candidate = str(iteration)
        feed = transaction + candidate
        #print(feed)

        sha1 = hashlib.sha256(feed.encode("utf8")).hexdigest()
        sha2 = hashlib.sha256(sha1.encode("utf8"))

        if sha2.hexdigest()[0:difficulty]==zero:
            print(sha2.hexdigest())
            print(iteration)
            result.value = iteration
            #print(_result)




if __name__ == '__main__':
    starttime = time.time()

    transction = 'COMSM0010cloud'

    difficulty = input('Please enter the difficulty:')
    parallel = input('Please enter the number of processed:')
    parallel = int(parallel)

    # split work
    total = 4294967296
    workload = []
    split = total / parallel
    for iter in range(0, parallel):
        start = iter * split
        end = (iter + 1) * split - 1
        workload.append([int(start), int(end)])

    print(workload)

    result = Value('q',-1)

    processList = []

    for i in range(parallel):
        p = Process(target=find_nonce, args=(transction, int(difficulty), workload[i][0], workload[i][1], result, ))
        processList.append(p)
        p.start()


    while(result.value == -1):
        #print(_result)
        pass

    print('The nonce is: ' + str(result.value))

    endtime = time.time()

    for p in processList:
        p.terminate()
    print("Time used: {:.2f}" .format(endtime-starttime))





