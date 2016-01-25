#!/usr/bin/env python
#coding:utf-8
#
#

def foo(*args, **kwargs):
    print 'args = ', args
    print 'kwargs = ', kwargs
    print '---------------------------------------'
    for k,v in kwargs.items():
            print k,v

if __name__ == '__main__':
    foo(1,2,3,4)
    foo(a=1,b=2,c=3)
    foo(1,2,3,4, a=1,b=2,c=3)
    foo('a', 1, None, a=1, b='2', c=3)
    pass
    foo(*(1,2,3,5), **{'a':1,'b':2})
