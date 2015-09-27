"""
Let's knock over the production server!!!
"""
from requests import get
from random import randrange, seed
from time import time
import threading
from threading import Thread

if __name__ == '__main__':
    def hammer_server(thread_name):
        server_name = "" # server location in either ip address or server name form
        base_url = "http://{}/getinfo".format(server_name)
        seed(time())
        REQUESTS_PER_THREAD = 100
        for request_num in range(REQUESTS_PER_THREAD):
            power_val = randrange(0, 9)
            url = "{}?{}={}".format(base_url,"power", power_val)
            res = get(url)
            if(res.status_code != 200):
                print("{} failure with status code: {}".format(thread_name, res.status_code))
            else:
                print("successful call to: {}".format(url))

    # build the thread list
    thread_list = []
    THREAD_COUNT = 1000
    for t_num in range(THREAD_COUNT):
        t_name = "thread #{}".format(t_num)
        t = Thread(target=hammer_server, args=(t_name, ))
        thread_list.append(t)

    # run the threads
    for t in thread_list:
        t.start()