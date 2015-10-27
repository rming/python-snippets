#!/usr/bin/env python
#-*- coding:utf-8 -*-
import time
#多线程，适合高IO 爬虫类
import multiprocessing.dummy as Threads


class hello:
    def name(self, person_name):
        print Threads.current_process().name
        for i in range(10):
            time.sleep(1)
            print 'hello %s %d' %(person_name,i)

pool_size = Threads.cpu_count()*2

pool = Threads.Pool(pool_size)

print pool

names = [
    u'lily'.encode('utf-8'),
    u'fish'
]

hello = hello()
results = pool.map(hello.name, names)

pool.close()
pool.join()

