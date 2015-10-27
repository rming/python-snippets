#!/usr/bin/env python
#-*- coding:utf-8 -*-

import threading
import random,time

class Maker(threading.Thread):
    
    def __init__(self,threadName,shareObject):
        threading.Thread.__init__(self,name=threadName)
        self.shareObject=shareObject
        
    def run(self):
        for x in range(1,5):
            time.sleep(random.randrange(1,4))
            self.shareObject.set(x)
            print "%s threading write %d" %(threading.currentThread().getName(),x)
