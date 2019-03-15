import os, sys
import ssl
import json
import re
from collections import ChainMap

from .logmod import *
from .exceptions import *
from .rosapi import *


def printres(res):
    if type(res)==list or type(res)==tuple:
        for r in res: 
            print(r)
    else:
        print(res)

## helper
def cmd_not_impl(object,cmd,args=None):
    return "*{}* : `{}` not impelmented".format(object,cmd)


class RosAPIObject(object):

    def __init__(self, parent, attr_name):
        self.name   = attr_name
        self.parent = parent
        #logger.debug("RosAPIObjects init {}->{} ".format(self.parent.name,self.name))

    def __str__(self):
        return "RosAPIObject, name={}->{}".format(self.parent.name,self.name)

    def __getattr__(self, name):
        if name.startswith("__"):
            #logger.debug("Attribute error: {}".format(name))
            raise AttributeError
        logger.debug("GETATTR name={} -> {}".format(self.name,name))
        return RosAPIObject(self,name)

    @log
    def __call__(self, *args, **kwargs):
        logger.debug("Call to {}({},{})".format(self.name,args,kwargs))
        #unwind objects and get str repr of command
        cmd=""
        obj=self
        while obj.name!="root":
            cmd="/"+obj.name+cmd
            obj=obj.parent
        # normailze name accoring to dict:
        XLAT = {
                "__" : "-",
                }
        for k,v in XLAT.items():
            cmd=cmd.replace(k,v)
        return obj.do( cmd, *args, **kwargs )

class RouterContext(object):
    api  = None
    name = "root"
    # groups:
    # 0 - keyword if present
    # 1 - type of quotes if present. I.e. if non empty - value in quotes used
    # 2 - value inside quotes if present
    # 3 - value without quotes if present 
    # 4 - soul text if present. First is command, rest are optional parameters
    reConsoleParser = re.compile(r"([\w.]+)\s*=\s*(?:(?P<sym>[\"'])((?:\\(?P=sym)|(?:(?!(?P=sym))).)*)(?P=sym)|(\w+))|(\S+)")

    def __init__(self, rid, fReadOnly=True):
        dir_cur=os.path.dirname(os.path.realpath(__file__))
        config=self.read_config(dir_cur)

        sid=str(rid)
        cfg=config.get(sid,None)
        if cfg==None:
            raise ConfigError("No settings for \"{}\" in config found!".format(sid))

        #ctx = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        ctx = ssl.create_default_context()
        ctx.check_hostname = False

        if cfg["api_ca_cert"]:
            cert=os.path.join(dir_cur, 'certs')
            cert=os.path.join(cert, cfg["api_ca_cert"] )
            try:
                ctx.load_verify_locations(cafile=cert)
            except FileNotFoundError as inst:
                logger.error("{} : {}".format(str(inst),cert))
                raise
        else:
            #### NO CERT
            #  In the case no certificate is used in '/ip service' settings then anonymous Diffie-Hellman cipher have to be used to establish connection. 
            ctx.verify_mode = ssl.CERT_NONE
            ctx.set_ciphers('ADH')

        kwargs={ "host" : cfg['ip'], 
                    "port" : cfg['port'],
                    "ssl_wrapper" : ctx.wrap_socket 
                }
        kwargs["username"] = cfg[ ('api_rw_user','api_ro_user')[fReadOnly] ]
        kwargs["password"] = cfg[ ('api_rw_pass','api_ro_pass')[fReadOnly] ]

        try:
            logger.debug("Trying connect to router with params:")
            for k,v in kwargs.items():
                if k=="password":
                    v="*"*len(v)
                logger.debug("  {}={}".format(k,v))
            api = rosapi.connect(**kwargs)
        except Exception as inst:
            logger.error("Failed to connect to router!")
            raise
        else:
            logger.debug("Successfully connected to router!")
            self.api=api

    def __del__(self):
        self.disconnect()

    def disconnect(self):
        if self.api!=None:
            logger.debug("Disconnecting from router...")
            self.api.close()
            self.api=None

    def read_config(self, path):
        #read config
        config=dict()
        try:
            logger.debug("Parsing config file (json)...")
            path=os.path.join(path,'routers.json')
            with open(path) as f:
                config = json.load(f)
        except Exception as inst:
            logger.error(type(inst))
            logger.error(inst.args)
            logger.error(inst)
            return None
        finally:
            logger.debug("JSON succesfully parsed.")
            for section,cfg in config.items():
                logger.debug("{} : {}".format(section,cfg))
            mod = sys.modules[self.__module__]
        return config

    def parseConsoleCommand(self, s) -> dict():
        try:
            parsed = self.reConsoleParser.findall(s)
        except Exception as inst:
            raise
        res=dict()
        for (key,qoute_sym,val1,val2,cmd_or_option) in parsed:
            if cmd_or_option:
                if res.get("command",None):
                    if res.get('options',None):
                        res['options'].append(cmd_or_option)
                    else:
                        res['options']=[cmd_or_option]
                else:
                    res['command']=cmd_or_option
            if key:
                res[key] = val1 or val2
        return res

    @log
    def get_AddressListItems(self,addresListName):
        if not self.api:
            return None
        try:
            params = {'?=list': addresListName}
            #res=self.api(cmd="/ip/firewall/address-list/print")
            res=self.api(cmd="/ip/firewall/address-list/print",**params)
        except Exception as inst:
            print("ERROR: {}".format(str(inst)))
        else:
            if res:
                    print(res)


    def __getattr__(self, name):
        if name.startswith("__"):
            #logger.debug("Attribute error: {}".format(name))
            raise AttributeError
        #logger.debug("GETATTR {}->{}".format(self.name,name))
        return RosAPIObject(self, name)

    @log
    def do(self, text, where=None, **kwargs):
        logger.debug("Execute:\n cmd={}\n kwargs={}".format(text,kwargs))
        res=None
        if not self.api:
           return res
        
        try:
            res=self.api(cmd=text, where=where, **kwargs)
        except Exception as inst:
            logger.error(str(inst))
            res="ERROR: {}".format(str(inst))
        return res

    @log
    def console(self):
        print("Enter /quit to exit console mode!")
        while True:
            text=input("#>")
            text_parsed=self.parseConsoleCommand(text)
            for t in text_parsed.items():
                print(t)

            command=text_parsed.get('command',None)
            if not command:
                print("No command entered!")
                continue
            del text_parsed['command']

            clause_where   = text_parsed.get('where',None)
            if clause_where!=None:
                del text_parsed['where']

            clause_options = text_parsed.get('options',None)
            if clause_options!=None:
                del text_parsed['options']

            if command=="/quit":
                break

            if self.api:
                try:
                    #res=self.api(cmd=command)

                    clause_rest = text_parsed.get('options',None)

                    res=self.do(command, where=clause_where, )

                except Exception as inst:
                    print("ERROR: {}".format(str(inst)))
                else:
                    if res:
                        printres(res)
                        
@log
def getRouter(rid,readonly=True,noexceptions=False):
    try:
        context=RouterContext(rid,readonly)
    except Exception as inst:
        logger.error("Failed to get router context!")
        if noexceptions:
            return None
        raise
    return None if context.api==None else context


