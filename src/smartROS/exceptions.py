class LibError(Exception):
    """Base exception for all other."""
    #def __new__(cls, *args, **kw):
    #    return super().__new__(cls, *args, **kw)  # ignoring args and kwargs!
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
    def __str__(self):
        if len(self.args)==0:
            return "Error: {}".format(self.__class__.__name__) 
        r="{}: {}".format(self.__class__.__name__, self.args[0])
        if len(self.args)>=2:
            r+=", args: {}".format( ", ".join(self.args[1:]) )
        return r

class LoginError(LibError):
    """Login attempt errors."""
    pass

class ConfigError(LibError):
    """Login attempt errors."""
    pass

class ConnectionError(LibError):
    """Connection related errors."""
    pass

class CipherUnsupportedError(LibError):
    """Connection related errors."""
    pass

class FatalError(LibError):
    """Exception raised when !fatal is received."""
    pass

TRAP_CATEGORIES = {
                    0 : "missing item or command",
                    1 : "argument value failure",
                    2 : " execution of command interrupted",
                    3 : " scripting related failure",
                    4 : " general failure",
                    5 : " API related failure",
                    6 : " TTY related failure",
                    7 : " value generated with :return command",
                   }

class TrapError(LibError):
    """Exception raised when !trap is received."""
    def __init__(self, traps=None):
        res=""
        r  = []
        if traps:
            for k,trap in traps:
                category=trap.get('category',None)
                message =trap.get('message',"")
                if category!=None:
                    r.append( "{} : {}".format( TRAP_CATEGORIES.get(category,""), message ) )
                else:
                    r.append( "{}".format( message ) )
        res+="\n".join(r)
        super().__init__(res)
