#!/usr/bin/env python

import ConfigParser
import os

# ====================================================================================================#
# exception class for errors loading the configuration
# ====================================================================================================#
class ConfigError(Exception):
    pass

# ====================================================================================================#
# The Config __init__ reads the config file and retains the parameters.
# Once initialized, get_parameterName() returns the value
# If initialization fails, an exception is raised. ConfigParser exceptions are caught and reraised.
# ====================================================================================================#
class Config(object):
    def __init__(self, configPath = None):
        self.consumerKey    = None        # API key
        self.consumerSecret = None        # Secret Key
        self.userToken      = None        # OAuth User Token
        self.userSecret     = None        # OAuth User Secret
        self.dbPath         = None
        defaultFileName     = "serendipity.config"

        if (configPath == None):
            configPath = os.getcwd() + "/" + "../config/" + defaultFileName

        parser = ConfigParser.RawConfigParser()
        if (parser.read(configPath) == []):
            raise ConfigError("Parser failed to .read the config file.")

        try:
            self.consumerKey    = parser.get("SectionAuth", "consumer_key"      )
            self.consumerSecret = parser.get("SectionAuth", "consumer_secret"   ) 
            self.userToken      = parser.get("SectionAuth", "user_token"        )
            self.userSecret     = parser.get("SectionAuth", "user_secret"       )
            self.dbPath         = parser.get("SectionDB"  , "db_path"           )
        except Exception, detail:
            raise ConfigError(detail)
            
# ====================================================================================================#
    def get_consumerKey(self):
        return(self.consumerKey)
# ====================================================================================================#
    def get_consumerSecret(self):
        return(self.consumerSecret)
# ====================================================================================================#
    def get_userToken(self):
        return(self.userToken)
# ====================================================================================================#
    def get_userSecret(self):
        return(self.userSecret)
# ====================================================================================================#
    def get_dbPath(self):
        return(self.dbPath)
# ========================================END CLASS Config============================================#
    
# ====================================================================================================#
# ====================================================================================================#
# ========                                                                                     =======#
# ========                 M A I N           JUST TEST CASES                                   =======#
# ========                                                                                     =======#
# ====================================================================================================#
# ====================================================================================================#
if __name__ == "__main__":
    
    goodConfigFile   = os.getcwd() + "/" + "../config/goodconfigfile.config"
    badConfigSection = os.getcwd() + "/" + "../config/badconfigsection.config"
    badConfigAttr    = os.getcwd() + "/" + "../config/badconfigattr.config"
    iCaseContent     = 0
    iExpectedResult  = 1
    testCases = [[None,             "Pass"], 
                 [goodConfigFile,   "Pass"], 
                 ["BadFileName",    "Fail"], 
                 [badConfigSection, "Fail"],
                 [badConfigAttr,    "Fail"]]

    for testCase in testCases:
        try:
            print "============= START CASE ==============="
            print "Test case: ConfigFileName=", testCase[iCaseContent]
            config = Config(testCase[iCaseContent])
        except ConfigError, detail:
            print "ConfigError: ", detail
            if testCase[iExpectedResult] == "Fail":
                print "-->EXPECTED RESULT"
            else:
                print "-->UNEXPECTED RESULT"
                
            print "=============  END CASE   ==============="
        except Exception, detail:
            if testCase[iExpectedResult] == "Fail":
                print "-->EXPECTED RESULT"
            else:
                print "-->UNEXPECTED RESULT"
                
            print "Unknown exception: ", detail
            print "=============  END CASE   ==============="
        else:
            print "Config loaded successfully."
            print config.get_consumerKey()
            print config.get_consumerSecret()
            print config.get_userToken()
            print config.get_userSecret()
            if testCase[iExpectedResult] == "Pass":
                print "-->EXPECTED RESULT"
            else:
                print "-->UNEXPECTED RESULT"
                
            print "=============   END CASE  ==============="
            
    exit()
