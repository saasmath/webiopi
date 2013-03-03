#   Copyright 2012-2013 Eric Ptak - trouch.com
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from webiopi.utils import *
from webiopi.protocols.rest import *

class Port():
    def __init__(self, channelCount):
        self.channelCount = channelCount
        self.MAX = 1
        
    def checkChannel(self, channel):
        if not channel in range(self.channelCount):
            raise ValueError("Channel %d out of range [%d..%d]" % (channel, 0, self.channelCount-1))

    def checkValue(self, value):
        if not value in range(self.MAX+1):
            raise ValueError("Value %d out of range [%d..%d]" % (value, 0, self.MAX))
    

    @request("GET", "channel-count")
    @response("%d")
    def getChannelCount(self):
        return self.channelCount

class GPIOPort(Port):
    def __init__(self, channelCount):
        Port.__init__(self, channelCount)
    
    def __family__(self):
        return "GPIOPort"
    
    def __getFunction__(self, channel):
        raise NotImplementedError
    
    def __setFunction__(self, channel, func):
        raise NotImplementedError
    
    def __input__(self, chanel):
        raise NotImplementedError
        
    def __readInteger__(self):
        raise NotImplementedError
    
    def __output__(self, chanel, value):
        raise NotImplementedError
        
    def __writeInteger__(self, value):
        raise NotImplementedError
    
    def getFunction(self, channel):
        self.checkChannel(channel)
        return self.__getFunction__(channel)  
    
    @request("GET", "%(channel)d/function")
    def getFunctionString(self, channel):
        func = self.getFunction(channel)
        if func == GPIO.IN:
            return "IN"
        elif func == GPIO.OUT:
            return "OUT"
        elif func == GPIO.PWM:
            return "PWM"
        else:
            return "UNKNOWN"
        
    def setFunction(self, channel, value):
        self.checkChannel(channel)
        self.__setFunction__(channel, value)
        return self.getFunction(channel)

    @request("POST", "%(channel)d/function/%(value)s")
    def setFunctionString(self, channel, value):
        value = value.lower()
        if value == "in":
            self.setFunction(channel, GPIO.IN)
        elif value == "out":
            self.setFunction(channel, GPIO.OUT)
        elif value == "pwm":
            self.setFunction(channel, GPIO.PWM)
        else:
            raise ValueError("Bad Function")
        return self.getFunctionString(channel)  

    @request("GET", "%(channel)d/value")
    @response("%d")
    def input(self, channel):
        self.checkChannel(channel)
        return self.__input__(channel)

    @request("GET", "*")
    @response(contentType=M_JSON)
    def readAll(self, compact=False):
        if compact:
            f = "f"
            v = "v"
        else:
            f = "function"
            v = "value"
            
        values = {}
        for i in range(self.channelCount):
            if compact:
                func = self.getFunction(i)
            else:
                func = self.getFunctionString(i)
            values[i] = {f: func, v: int(self.input(i))}
        return jsonDumps(values)

    @request("GET", "integer")
    @response("%d")
    def readInteger(self):
        return self.__readInteger__()
    
    @request("POST", "%(channel)d/value/%(value)d")
    @response("%d")
    def output(self, channel, value):
        self.checkChannel(channel)
        self.checkValue(value)
        self.__output__(channel, value)
        return self.input(channel)  

    @request("POST", "integer/%(value)d")
    @response("%d")
    def writeInteger(self, value):
        self.__writeInteger__(value)
        return self.readInteger()
    
from webiopi.devices.digital.mcp23XXX import MCP23008, MCP23009, MCP23017, MCP23018
from webiopi.devices.digital.mcp23XXX import MCP23S08, MCP23S09, MCP23S17, MCP23S18
from webiopi.devices.digital.pcf8574 import PCF8574, PCF8574A