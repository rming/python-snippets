#!/usr/bin/env python
#-*- coding:utf-8 -*-

import threading
import time,random

class User(threading.Thread):
    
    def __init__(self,threadName,shareObject):
        threading.Thread.__init__(self,name=threadName)
        self.shareObject=shareObject
        self.sum=0
        
    def run(self):
        for x in range(1,5):
            time.sleep(random.randrange(1,4))
            tempNum=self.shareObject.get()
            print "%s threading read %d" %(threading.currentThread().getName(),tempNum)
            self.sum=self.sum+tempNum
            
    def display(self):
        print "sum is %d" %(self.sum)
