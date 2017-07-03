# -*- coding: utf-8 -*-
import os
import Test
import GetUrlResponse as gur
import math
import threading
import time


def single_thread(path):
    data = Test.read_file(path)
    out_list = []
    for sentence in data:
        new_str = ''
        my_array = sentence.split('\t')
        question = my_array[1]
        new_str += my_array[0] + '\t' + my_array[1] + '\t' + gur.get_response_string(question) + '\t' + my_array[3] + '\t' + my_array[4]
        out_list.append(new_str)
    Test.write_file('data/single.txt', out_list)


def chunks(arr, m):
    n = int(math.ceil(len(arr) / float(m)))
    return [arr[i:i + n] for i in range(0, len(arr), n)]


def multi_thread(path):
    data = Test.read_file(path)
    td_data = chunks(data, 16)
    out_list = []
    threads = []
    for i in range(16):
        threads.append(threading.Thread(target=gur.get_response_batch(), args=(out_list, td_data[i],)))
    for t in threads:
        # t.setDaemon(True)
        t.start()
        t.join()
    Test.write_file('data/multi.txt', out_list)


if __name__ == '__main__':
    # start = time.time()
    # single_thread('E:/pyworkspace/Test/data/dingdong_small.txt')
    # elapsed1 = (time.time() - start)

    start = time.time()
    single_thread('E:/pyworkspace/Test/data/dingdong_small.txt')
    elapsed2 = (time.time() - start)

    # print elapsed1
    print elapsed2

