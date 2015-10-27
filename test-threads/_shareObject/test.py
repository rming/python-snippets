#!/usr/bin/env python
#-*- coding:utf-8 -*-

from user import User
from maker import Maker
from shareInt import ShareInt

shareObject=ShareInt()
user1=User("user1",shareObject)
maker1=Maker("maker1",shareObject)

user1.start()
maker1.start()

user1.join()
maker1.join()

user1.display()

print "main threading over!"
