#!/usr/bin/env python
# coding: utf-8
import unittest
import sys
import smartROS

if __name__ == '__main__':
    router = smartROS.getRouter("Primary",True);
    router.console()
    router.disconnect()
