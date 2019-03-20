#!/usr/bin/env python3
# coding: utf-8
import unittest
import sys
import smartROS

if __name__ == '__main__':
    router = smartROS.getRouter(0,True);
    if router:
        router.console()
        router.disconnect()
