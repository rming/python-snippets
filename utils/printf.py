#!/usr/bin/env python
#coding:utf-8

import sys
def printf(format, *args):
      sys.stdout.write((format % args).encode('utf-8'))
