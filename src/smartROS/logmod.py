import logging, logging.handlers
import functools

from  .settings import *

class _DummyLogger():
    def __init__(self, fdebug=False):
        self._debug=fdebug

    def debug(self,msg):
        if self._debug:
            print("DEBUG: {}".format(msg))

    def error(self,msg):
        if self._debug:
            print("ERROR: {}".format(msg))

    def warning(self,msg):
        if self._debug:
            print("WARNING: {}".format(msg))

#logger = logging.getLogger(getLoggerName())
#debug  = False
#logger_handlers = []

class Logger(object):
    logger  = None
    logname = None
    logger_handlers = []

    def __init__(self, logname="smartROS", debug=False):
        self.logname = logname
        self.logger=self.initLogger(debug)

#    def __call__(self, cmd, where=None, **kwargs):
#

    def initLogger(self,debug):
        try:
            logger_name=self.logname
            log_file = "{0}/{1}.log".format(SETTINGS.app_log_dir, logger_name)
            logging.basicConfig(level=(logging.INFO,logging.DEBUG)[debug])
            logger = logging.getLogger(logger_name)
            # create file handler which logs even debug messages
            # fh = logging.FileHandler(log_file)
            #if not os.path.isfile(log_file):
            #    touch(log_file)
            fh = logging.handlers.RotatingFileHandler(log_file, mode='a', maxBytes=10*1024*1024, backupCount=5, encoding=None, delay=0)
            fh.setLevel((logging.INFO,logging.DEBUG)[debug])
            # create console handler with a higher log level
            ch = logging.StreamHandler()
            ch.setLevel(logging.ERROR)
            # create formatter and add it to the handlers
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            fh.setFormatter(formatter)
            ch.setFormatter(formatter)
            # add the handlers to the logger
            logger.addHandler(fh)
            logger.addHandler(ch)
            logger.debug("Initing logger...")
            logger_handlers = [fh.stream]
        except Exception as inst:
            print("Failed to create logger")
            print(type(inst))
            print(inst.args)
            print(inst)
            raise
        return logger

    def __getattr__(self, name):
        if name=="debug":
            return self.logger.debug
        if name=="info":
            return self.logger.info
        if name=="error":
            return self.logger.error
        if name=="warning":
            return self.logger.warning
        raise AttributeError

logger=Logger(debug=SETTINGS.debug)

def log(func):
    @functools.wraps(func)
    def decorator(*args, **kwargs):
        #logger = logging.getLogger(getLoggerName())
        logger.debug('>>> Entering: %s', func.__name__)
        result = func(*args, **kwargs)
        logger.debug('<<< Exiting: {}, res={}'.format(func.__name__,result))
        return result
    return decorator
