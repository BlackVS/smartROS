#!/usr/bin/env python3
# coding: utf-8
import unittest
import sys
import smartROS

if __name__ == '__main__':
    router=None
    try:
        #router = smartROS.getRouter("No SSL",True); # r/o, Simple conenction without SSL
        #router = smartROS.getRouter("TLS",True); # r/o, TLS without certificate
        router = smartROS.getRouter("TLS+cert",True); # r/o, TLS with certificate
    except Exception as inst:
        print("Error {}".format(str(inst)))
    if router:
        router.console()
        router.disconnect()
