#1. Initially based on https://github.com/luqasz/librouteros
#2. ROS >= 6.43

import os
from socket import create_connection, error as SOCKET_ERROR, timeout as SOCKET_TIMEOUT
from collections import ChainMap
import pyparsing as pp
from pyparsing import pyparsing_common as ppc

import re
import ssl

from .exceptions import *
from .connections import *
from .logmod import *

def login_plain(api, username, password):
    """Login using post routeros 6.43 authorization method."""
    api('/login', **{'name': username, 'password': password})


class CONN_WRAPPER_NO_SSL(object):
    def __call__(self, sock):
        return sock

    def __str__(self):
        return "NO SSL Wrapper, just bypass calls"

class CONN_WRAPPER_TLS(object):
    wrapper  = None
    protocol = None
    ciphers  = None
    def __init__(self, protocol=ssl.PROTOCOL_TLSv1_2, ciphers="ADH-AES128-SHA256"):
        self.wrapper  = lambda sock: ssl.wrap_socket(sock, ssl_version=protocol, ciphers=ciphers)
        self.protocol = protocol
        self.ciphers  = ciphers

    def __call__(self, sock):
        if self.wrapper:
            return self.wrapper(sock)
        return None

    def __str__(self):
        if self.wrapper:
            return "SSL Wrapper, {}, {}".format(self.protocol.name, self.ciphers)
        return "SSL Wrapper, not initialized"

class CONN_WRAPPER_TLS_CERT(object):
    ctx  = None
    cert = None
    wrapper = None

    def __init__(self, cert_name, certs_dir='certs'):
        #ctx = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        #
        if not os.path.isabs(certs_dir):
            dir_cur=os.path.dirname(os.path.realpath(__file__))
            certs_dir=os.path.join(dir_cur, certs_dir)
        #now certs_dir is abs path
        if not os.path.exists(certs_dir):
            logger.error("Path {} not exists!".format(certs_dir))
            raise FileNotFoundError(certs_dir)
        cert=os.path.join(certs_dir, cert_name)
        if not os.path.exists(cert):
            logger.error("File {} not exists!".format(cert))
            raise FileNotFoundError(cert)
        try:
             ctx.load_verify_locations(cafile=cert)
        except FileNotFoundError as inst:
                logger.error("{} : {}".format(str(inst),cert))
                raise
        self.ctx=ctx
        self.wrapper=ctx.wrap_socket
        self.cert=cert

    def __call__(self, sock):
        if self.wrapper:
            return self.wrapper(sock)
        return None

    def __str__(self):
        if self.wrapper:
            return "SSL Wrapper, cert={}".format(self.cert)
        return "SSL Wrapper, not initialized"

class RosAPI(object):
    def __init__(self, protocol):
        self.protocol = protocol

    @staticmethod
    def cast_python2ros(value):
        if type(value) == bool:
            return ("no","yes")[value]
        return str(value)

    @staticmethod
    def cast_ros2python(value):
        XLAT = { 'yes'  : True, 
                 'true' : True, 
                 'no'   : False, 
                 'false': False
               }
        #check if int
        if re.match(r"[-+]?\d+$", value.strip()):
           return int(value)
        #if in map - map or return as is strt
        return XLAT.get(value,value)

    @staticmethod
    def compose_keyvalue(key, value):
        return '={}={}'.format(key, RosAPI.cast_python2ros(value))

    @staticmethod
    def compose_args(args):
        return [ RosAPI.compose_keyvalue(k,v) for k, v in args.items() ]

    @staticmethod
    def compose_where(s) -> list:
        def call_op_Unary(tokens):
            res=""
            op, v = tokens[0]
            if op=="HAS":
                res="?{}\n".format(v)
            elif op=="NOT":
                res="{}?#!\n".format(v)
            else:
                raise
            return res

        def call_op_Binary(tokens):
            res=""
            a,op,b=tokens[0][:3]
            if op=='==':
                res="?={}={}\n".format(a,b)
            elif op=="!=":
                res="?={}={}\n?#!\n".format(a,b)
            elif op=="<":
                res="?<{}={}\n".format(a,b)
            elif op==">":
                res="?>{}={}\n".format(a,b)
            elif op=="<=":
                res="?>{}={}\n?#!\n".format(a,b)
            elif op==">=":
                res="?<{}={}\n?#!\n".format(a,b)
            elif op=="AND" or op=="OR": #can be more than 3 tokens!
                if op=="AND": 
                    o="?#&\n"
                elif op=="OR": 
                    o="?#|\n"
                res="".join(tokens[0][0::2])+o*((len(tokens[0])-1)//2)
            else:
                raise

            return res

        def parseaction_identifier(str,location,tokens):
            m={ "true" : "yes",
                "yes"  : "yes", #not remove - adds ignore case to "yes" i.e. allows Yes, YES, yes etc 
                "false": "no" , 
                "no"   : "no"   #not remove - adds ignore case to "no" i.e. allows NO, no, No etc 
              }
            s=m.get( tokens[0].lower(), None)
            if s:
                return s
            return None

        def parseaction_ipv4_address(str,location,tokens):
            return None

        def parseaction_ipv4_network(str,location,tokens):
            return None

        def parseaction_index(str,location,tokens):
            return None

        number     = pp.Word(pp.nums)
        string     = pp.quotedString.setParseAction( pp.removeQuotes )
        identifier = pp.Word(pp.alphas+".", pp.alphanums + "-_").setParseAction(parseaction_identifier)
        index      = pp.Word("*", pp.alphanums).setParseAction(parseaction_index)
        ipv4_address = ppc.ipv4_address.setParseAction(parseaction_ipv4_address)
        ipv4_mask32  = pp.Regex('[1-2][0-9]|[3][0-2]|[0-9]')
        ipv4_network = pp.Combine( ppc.ipv4_address + "/" + ipv4_mask32).setParseAction(parseaction_ipv4_network)
        #end of ipv4

        operand = ipv4_network | ipv4_address | identifier | number | string 

        operator        = pp.Regex(">=|<=|!=|>|<|==").setName("operator")
        
        expr = pp.operatorPrecedence(operand,[
                                            (pp.CaselessKeyword("HAS"), 1, pp.opAssoc.RIGHT, call_op_Unary),
                                            (operator,                  2, pp.opAssoc.LEFT,  call_op_Binary),
                                            (pp.CaselessKeyword("NOT"), 1, pp.opAssoc.RIGHT, call_op_Unary),
                                            (pp.CaselessKeyword("AND"), 2, pp.opAssoc.LEFT,  call_op_Binary),
                                            (pp.CaselessKeyword("OR"),  2, pp.opAssoc.LEFT,  call_op_Binary),
                                               ])

        try:
            res = expr.parseString( s, parseAll=True )
        except Exception as inst:
            logger.error("Failed to parse: {}\n{}".format(s, str(inst)))
            raise
            #return None

        return res[0].split()

    @staticmethod
    def parse_word(word):
        _, key, value = word.split('=', 2)
        value = RosAPI.cast_ros2python(value)
        return (key, value)

    # /ip/route/print where="dst-address=='0.0.0.0/0'"
    def __call__(self, cmd, where=None, **kwargs):
        """
        Call Api with given command.
        :param cmd:    Command word. eg. /ip/address/print
        :param where:  "Where" clause in human readable form
        :param kwargs: Dictionary with optional arguments.
        """

        words=[]
        if where: #conditional arguments
            words += RosAPI.compose_where(where)
        if kwargs:#parameter arguments
            words += RosAPI.compose_args(kwargs) 
        self.protocol.writeSentence(cmd, *words)
        return self._readResponse()

    def _readSentence(self):
        """
        Read one sentence and parse words.
        :returns: Reply word, dict with attribute words.
        """
        reply_word, words = self.protocol.readSentence()
        words = dict( map(RosAPI.parse_word,words) )
        return reply_word, words

    def _readResponse(self):
        """
        Read untill !done is received.

        :throws TrapError: If one or more !trap is received.
        :returns: Full response
        """
        response = []
        reply_word = None
        while reply_word != '!done':
            reply_word, words = self._readSentence()
            response.append((reply_word, words))

        self._trapCheck(response)
        # Remove empty sentences
        return tuple(words for reply_word, words in response if words)

    def close(self):
        self.protocol.close()

    @staticmethod
    def _trapCheck(response):
        errors_trap = tuple( filter(lambda v: v[0]=='!trap', response) )
        if errors_trap:
            raise TrapError(traps=errors_trap)


def connect(host, port, username, password, ssl_wrapper=CONN_WRAPPER_NO_SSL, timeout=10, src_addr=None, encoding='ISO-8859-1'):
    """
    Connect and login to routeros device.
    Upon success return a Api class.

    :param host: Host's ip/name to connect to. May be ipv4,ipv6,FQDN.
    :param port: Host's port to connect to.
    :param username   : Username to login with.
    :param password   : Password to login with. Only ASCII characters allowed.
    :param timeout    : Socket timeout. Defaults to 10.
    :param src_addr   : Source address to bind to.
    :param ssl_wrapper: Callable (e.g. ssl.SSLContext instance) to wrap socket with.
    :param encoding   : how to decode stream. By default 'ISO-8859-1' or will fail on cyrrilic symbols in comments -> ASCII, UTF-8 will fail for them
    """

    logger.debug("  host:port={}:{}".format(host,port))
    logger.debug("  username={}".format(username))
    logger.debug("  password={}".format("*"*len(password)))
    logger.debug("  ssl wrapper={}".format(ssl_wrapper))
    logger.debug("  timeout ={}s".format(timeout))
    logger.debug("  src addres={}".format(src_addr))
    logger.debug("  encoding={}".format(encoding))

    try:
        sock = create_connection( (host, port), timeout, src_addr)
        sock = ssl_wrapper(sock)
        transport=SocketTransport(sock)
    except (SOCKET_ERROR, SOCKET_TIMEOUT) as error:
        raise ConnectionError(error)
    except:
        logger.error("Failed to create transport!")
        raise

    protocol = ApiProtocol(transport=transport, encoding=encoding)
    api = RosAPI(protocol=protocol)

    for method in (login_plain,):#only plain for now
        try:
            method(api=api, username=username, password=password)
            return api
        except TrapError:
            pass
        except (ConnectionError, FatalError):
            transport.close()
            raise


