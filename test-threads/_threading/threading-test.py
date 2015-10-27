#!/usr/bin/env python
# encoding: UTF-8
import threading

# 方法1：将要执行的方法作为参数传给Thread的构造方法
def func():
    print 'func() passed to Thread'

t = threading.Thread(target=func)
t.start()


# 方法2：从Thread继承，并重写run()
class MyThread(threading.Thread):
    def run(self):
        print 'MyThread extended from Thread'

t = MyThread()
t.start()
t.stop()
