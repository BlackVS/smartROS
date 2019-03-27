#################################################################################
import configparser

#don't change default dirs if use insta;;.sh
_APP_NAME = "smartros" # keyword, don't change if not sure

class Settings(object):
    config_global = {
        'app_config_dir': "/etc/%s/" % _APP_NAME,
        # defaults
        'app_tmp_dir'   : "/tmp/" + _APP_NAME,          # script must have write permissions to this folder
        'app_log_dir'   : "/var/log/" + _APP_NAME,      # script must have write permissions to this folder
        'app_certs_dir' : "/etc/%s/certs" % _APP_NAME,  # default certificates folder
        'debug'        : False,
        #debug       = True
       }

    def __getattr__(self, name):
        if name.startswith("__"):
            raise AttributeError
        v=self.config_global.get(name,None)
        if v==None:
            raise AttributeError
        if name=="debug" and type(v)==str:
            return v.lower()=="true"
        return v

    #
    def __init__(self, config_file="/etc/%s/main.conf" % _APP_NAME):
        config_parser = configparser.ConfigParser(defaults=self.config_global, default_section='global')
        try:
            config_parser.read(config_file)
            self.config_global.update(config_parser['global'])
            ### generate template - only once
            # with open('smartROS/main.conf.template', 'w') as file:
            #    config_parser.write(file)
        except Exception as inst:
            pass

SETTINGS=Settings()