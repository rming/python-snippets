#!/usr/bin/env python
#coding:utf-8
#

class Singleton(object):
    """
     使用__new__方法
    """
    def __new__(cls, *args, **kw):
        if not hasattr(cls, '_instance'):
            orig = super(Singleton, cls)
            cls._instance = orig.__new__(cls, *args, **kw)
        return cls._instance

class MyClass(Singleton):
    a = 1


class Borg(object):
    """
    共享属性
    创建实例时把所有实例的__dict__指向同一个字典,这样它们具有相同的属性和方法.
    """
    _state = {}
    def __new__(cls, *args, **kw):
        ob = super(Borg, cls).__new__(cls, *args, **kw)
        ob.__dict__ = cls._state
        return ob

class MyClass2(Borg):
    a = 1


def singleton(cls, *args, **kw):
    """
    装饰器版本
    """
    instances = {}
    def getinstance():
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]
    return getinstance

@singleton
class MyClass:
    pass

"""
import方法
作为python的模块是天然的单例模式
"""
# mysingleton.py
class My_Singleton(object):
    def foo(self):
        pass

my_singleton = My_Singleton()

# to use
from mysingleton import my_singleton

my_singleton.foo()
