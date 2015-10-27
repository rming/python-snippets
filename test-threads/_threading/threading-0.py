#!/usr/bin/env python
# encoding: utf-8

import sys, time, threading

def func():
    for i in range(0,100):
        print i
        time.sleep(1)

t = threading.Thread(target=func)
t.start()


