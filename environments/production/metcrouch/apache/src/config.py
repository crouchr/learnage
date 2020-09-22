import configparser
import funcs


class VerifyConfig():
    """A class to contain the info stored in the ini file"""

    def __init__(self):
        self.values = {}
        # this is where the file is installed into
        # if funcs.get_verify_env() == 'DEV':
        #     VERIFY_INI_FILE = "/home/crouchr/PycharmProjects/learnage/environments/dev/metcrouch/apache/src/minimet.ini"
        # elif funcs.get_verify_env() == 'STAGING':
        #     VERIFY_INI_FILE = "/opt/reveal-verify/backend/etc/verify.ini"
        # else:  # LIVE
        #     VERIFY_INI_FILE = "/opt/reveal-verify/backend/etc/verify.ini"

        VERIFY_INI_FILE = "/home/crouchr/PycharmProjects/learnage/environments/dev/metcrouch/apache/src/minimet.ini"

        self.config_pathname = VERIFY_INI_FILE
        #self.reveal = funcs.get_verify_env()

        config = configparser.ConfigParser()
        config.read(self.config_pathname)
        for section in config.sections():
            self.values[section] = ConfigSectionMap(self.config_pathname, section)
            #revealFuncs.doLog("NULL", "VerifyConfig() : value for [" + section.__str__() + "] is " + self.values[section].__str__())

    def get_ini_pathname(self):
        return self.config_pathname

    #def get_reveal_variable(self):
    #    return self.reveal


def ConfigSectionMap(configPathname, section):
    """Return a dictionary of values from the ini file section"""
    dict1 = {}
    config = configparser.ConfigParser()
    config.read(configPathname)

    options = config.options(section)
    for option in options:
        try:
            dict1[option] = config.get(section, option)
            # if dict1[option] == -1:
            #    DebugPrint("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None

    return dict1
