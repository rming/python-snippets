#!/usr/bin/env python
# encoding: utf-8

import sys, time, threading

class myThreading(threading.Thread):
    def run(self):
        for i in range(0,100):
            print i
            time.sleep(1)

t = myThreading()

t.start() 
