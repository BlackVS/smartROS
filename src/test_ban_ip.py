#!/usr/bin/env python3
# coding: utf-8
import sys, os, re
import argparse
import smartROS

class ArgumentParserError(Exception): pass

class ThrowingArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise ArgumentParserError(message)

parser = ThrowingArgumentParser()

if __name__ == '__main__':
    router = None
    logger = smartROS.logger

    try:
        parser = ThrowingArgumentParser(add_help=True, description='Add new ip to blacklist')
        parser.add_argument('ip', help="IP to ban")
        parser.add_argument("-t", "--timeout", default=86400, help="TTL for being in blacklist")
        parser.add_argument("-r", "--router" , required=True, help="router id")
        parser.add_argument("-l", "--list" , default="Blacklist", help="Address list for blacklisted ips")
        parser.add_argument("-bl", "--banlocal" , action='store_false', help="Ignore IANA local addresses")
        args = parser.parse_args()

        logger.debug(args)
        logger.debug("{} : ban {} for {} sec\n".format(args.router, args.ip, args.timeout ))

        #file_path = "/tmp/ros_ban_ip.log"
        #with open(file_path, 'a') as file:
        #    file.write("{} : ban {} for {} sec\n".format(args.router, args.ip, args.timeout ))

        logger.debug("checking arguments")
        if args.banlocal:
            logger.debug("Check if local address")
            rfc1918 = re.compile('^(10(\.(25[0-5]|2[0-4][0-9]|1[0-9]{1,2}|[0-9]{1,2})){3}|((172\.(1[6-9]|2[0-9]|3[01]))|192\.168)(\.(25[0-5]|2[0-4][0-9]|1[0-9]{1,2}|[0-9]{1,2})){2})')
            logger.debug("compiled rfc1918")
            if rfc1918.match(args.ip):
                logger.debug("local address - exiting")
                print("{} is private. Ignoring. Use -bl or --banlocal if wish to ban local ip too".format(args.ip))
                parser.print_help()
                os._exit(2) 
        router = smartROS.getRouter(args.router,False); #open for read-write!!! carefully

        logger.debug("router={}".format(router))
        if not router:
            logger.error("Can't connect to router")
            os._exit(1)



        #check if already banned
        logger.debug("check if ip={} banned".format(args.ip))
        res=router.ip.firewall.address__list.print(where="list=='{}' and address=='{}'".format(args.list,args.ip))

        logger.debug("banned={}".format(res))
        if not res:
            #not listed
            logger.debug("not banned = will be banned!!!")
            router.ip.firewall.address__list.add( address=args.ip,      
                                                    list   =args.list,
                                                    timeout=args.timeout, 
                                                    comment="Added via ban ip script",
                                                )
        else:
            logger.warning("{} is already banned".format(args.ip))


    except ArgumentParserError as inst:
        logger.error("Wrong arguments - {}\n".format(str(inst)))
        parser.print_help()
        os._exit(1) 

    except Exception as inst:
        logger.warning("Failed to run application!")
        logger.error("Error: {}".format(type(inst)))
        logger.error("args : {}".format(inst.args))
        logger.error("msg  : {}".format(str(inst)))
        os._exit(1) 

    finally:
        if router:
            router.disconnect()