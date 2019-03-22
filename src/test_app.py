#!/usr/bin/env python
# coding: utf-8
import unittest
import sys
import smartROS

def printres(res):
    if type(res)==list or type(res)==tuple:
        for r in res: 
            print(r)
    else:
        print(res)

class TestStringMethods(unittest.TestCase):

    #def test_noRouter(self):
    #    router = smartROS.getRouter(-1,noexceptions=True);
    #    self.assertTrue ( router==None )

    def test_Router_NoSSL_RO(self): 
        router = smartROS.getRouter("No SSL",True);
        self.assertTrue ( router!=None )
        router.disconnect()

    def test_Router_TLS_RW(self): 
        router = smartROS.getRouter("TLS",False);
        self.assertTrue ( router!=None )
        router.disconnect()

    def test_Router_TLSwithCert_RO(self): 
        router = smartROS.getRouter("TLS+cert",True);
        self.assertTrue ( router!=None )
        router.disconnect()

    def test_Router_TLS_testCmd(self):
        router = smartROS.getRouter("TLS",True);
        self.assertTrue ( router!=None )
        #router.get_AddressListItems("Blacklist")
        res=router.ip.address.print(where="dynamic==True")
        if type(res)==list or type(res)==tuple:
            for r in res: print(r)
        else:
            print(res)
        router.disconnect()

if __name__ == '__main__':
    unittest.main()
