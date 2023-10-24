#!/usr/bin/python
import time
from PreludeCorrelator.idmef import IDMEF
from PreludeCorrelator.pluginmanager import Plugin

# By default, alert only on saturday and sunday, and everyday from 6:00pm to 9:00am.
class BusinessHourPlugin(Plugin):
    BUSINESSHOUR_HWORKSTART = 9
    BUSINESSHOUR_HWORKEND   = 17
    BUSINESSHOUR_OFFDAYS    = '[5,6]'

    def __init__(self,env):
        Plugin.__init__(self, env)
            self.__hworkstart = int(self.getConfigValue("hworkstart", self.BUSINESSHOUR_HWORKSTART))
            self.__hworkend = int(self.getConfigValue("hworkend", self.BUSINESSHOUR_HWORKEND))
            self.__offdays = eval(self.getConfigValue("offdays", self.BUSINESSHOUR_OFFDAYS))
    
    def run(self, idmef):
        self.__t = time.localtime(int(idmef.Get("alert.create_time")))
        if not (self.__t.tm_wday in self.__offdays or self.__t.tm_hour < self.__hworkstart or self.__t.tm_hour > self.__hworkend):
            return
        
        #if idmef.Get("alert.assessment.impact.completion") != "succeeded":
        #    return

        ca = IDMEF()
        ca.addAlertReference(idmef)
        ca.Set("alert.classification", idmef.Get("alert.classification"))
        ca.Set("alert.correlation_alert.name", "Critical system activity on day off")
        
        ca.alert()
        