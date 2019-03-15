#!/usr/bin/env python3
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

    def test_noRouter(self):
        router = smartROS.getRouter(-1,noexceptions=True);
        self.assertTrue ( router==None )

    #def test_Router0_RO_connect(self): 
    #    router = smartROS.getRouter(0,True);
    #    self.assertTrue ( router!=None )
    #    router.disconnect()

    #def test_Router0_RW_connect(self): 
    #    router = smartROS.getRouter(0,False);
    #    self.assertTrue ( router!=None )
    #    router.disconnect()

    def test_Router1_RO_connect(self): 
        router = smartROS.getRouter(1,True);
        self.assertTrue ( router!=None )
        router.disconnect()

    def test_Router1_RW_connect(self): 
        router = smartROS.getRouter(1,False);
        self.assertTrue ( router!=None )
        router.disconnect()

    def test_RouterPrimary_RO_connect(self):
        router = smartROS.getRouter("Primary",True);
        self.assertTrue ( router!=None )
        router.disconnect()

    def test_RouterPrimary_RW_connect(self):
        router = smartROS.getRouter("Primary",False);
        self.assertTrue ( router!=None )
        router.disconnect()

    def test_RouterPrimary_RO_console(self):
        router = smartROS.getRouter("Primary",True);
        self.assertTrue ( router!=None )
        router.console()
        router.disconnect()

    def test_RouterPrimary_RO_console(self):
        router = smartROS.getRouter("Primary",True);
        self.assertTrue ( router!=None )
        #router.get_AddressListItems("Blacklist")
        res=router.ip.address.print(where="dynamic==True")
        if type(res)==list or type(res)==tuple:
            for r in res: print(r)
        else:
            print(res)
        router.disconnect()

    def test_RouterPrimary_RO_console(self):
        router = smartROS.getRouter("Primary",True);
        self.assertTrue ( router!=None )
        res=router.do("/ip/firewall/address-list/print", where="list==Blacklist")
        res=router.ip.firewall.address__list.print(where="list==Blacklist") # TRICK: '__' means "-" here. "-" cannot be used in Python directly names but in ROS can
        res=router.ip.route.print(where="dynamic==true")
        res=router.ip.route.print(where="not has dynamic and dst-address=='0.0.0.0/0'") # here is some of ROS stranges - route has dynamic=yes for dynamic routes and hasn't attribute "dynamic" in other cases. I.e. dynamic=no impossible %)
        printres(res)
        router.disconnect()

if __name__ == '__main__':
    unittest.main()
