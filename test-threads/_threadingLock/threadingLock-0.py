#!/usr/bin/env python
# encoding: utf-8

import time, threading
mylock = threading.RLock()
num = 0

class myThreading(threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self, name=name)

    def run(self):
        global num 
        while  True:
            mylock.acquire()
            print '\nThread(%s) locked, Number: %d'%(self.getName(), num)
            if num >= 4:
                mylock.release()
                print '\nThread(%s) released, Number: %d'%(self.getName(), num)
                break
            num +=1
            print '\nThread(%s) released, Number: %d'%(self.getName(), num)
            mylock.release()


if __name__=='__main__':
    t0 = myThreading('A')
    t1 = myThreading('B')
    t0.start() 
    t1.start() 
