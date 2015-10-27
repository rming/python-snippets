#!/usr/bin/env python
#-*- coding:utf-8 -*-

import threading
import time,random

class ShareInt():

    def __init__(self):
        self.threadCondition=threading.Condition()
        self.shareObject=[]
        
        
    #所有对共享空间操作的方法(read or write)都封闭在acquire()和release()中间
    def set(self,num):
        self.threadCondition.acquire() 
        # 在调用一个读或者写共享空间的方法时，需要先拿到一个基本锁
        # 基本锁的获得采用竞争机制，无法判断哪个线程会先运行
        # 不拿基本锁会出现运行时错误:cannot notify on un-aquired lock
        
        if len(self.shareObject)!=0:
            print "%s threading try write! But shareObject is full" %(threading.currentThread().getName())
            self.threadCondition.wait() 
            # 在条件满足的情况下，会block掉调用这个方法的线程
            # 这里使用while语句更好，因为block在这个位置后，
            # 当再次运行此线程的时候，会从头再一次检查条件。
        
        self.shareObject.append(num)
        
        self.threadCondition.notify() 
        # 一定要先调用notify()方法，在release()释放基本锁
        self.threadCondition.release() 
        # 可以理解为"通知"被wait的线程进入runnable状态，然后在它获得锁后开始运行
        # 最后一定要release()释放锁，否则会导致死锁
                                         
    def get(self):
        self.threadCondition.acquire()
        
        if len(self.shareObject)==0:
            print "%s threading try read! But shareObject is empty" %(threading.currentThread().getName())
            self.threadCondition.wait()
            
        tempNum=self.shareObject[0]
        self.shareObject.remove(tempNum)
        self.threadCondition.notify()
        self.threadCondition.release()
        return tempNum
