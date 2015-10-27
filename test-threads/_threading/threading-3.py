#!/usr/bin/env python
# encoding: utf-8

import sys, time, threading

class myCounter(threading.Thread):
    def __init__(self, start, interval, threadName):
        threading.Thread.__init__(self, name=threadName) 
        self.startNum   = start
        self.interval   = interval
        self.stopSignal = False

    def run(self):
        i = self.startNum
        while not self.stopSignal:
            i +=self.interval
            print  "%s-%s\n" % self.getName(), str(i)
            time.sleep(1)

    def stop(self):
        self.stopSignal = True

t0 = myCounter(1 ,1, 't0')
t1 = myCounter(1 ,4, 't1')
t2 = myCounter(1 ,8, 't2')

t0.start() 
t1.start() 
t2.start() 

time.sleep(5)
t0.stop()
time.sleep(5)
t1.stop()
time.sleep(5)
t2.stop()
