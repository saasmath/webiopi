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

from webiopi.i2c import *
from webiopi.rest import *
from webiopi.utils import *

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

class InputPort(Port):
    def __init__(self, channelCount):
        Port.__init__(self, channelCount)
    
    def __family__(self):
        return "Input"
    
    def __input__(self, chanel):
        raise NotImplementedError
        
    def __readInteger__(self):
        raise NotImplementedError
    
    @request("GET", "%(channel)d/value")
    @response("%d")
    def input(self, channel):
        self.checkChannel(channel)
        return self.__input__(channel)

    @request("GET", "*")
    @response(contentType=M_JSON)
    def readAll(self):
        values = {}
        for i in range(self.channelCount):
            values[i] = int(self.input(i))
        return jsonDumps(values)

    @request("GET", "integer")
    @response("%d")
    def readInteger(self):
        return self.__readInteger__()
    
class OutputPort(Port):
    def __init__(self, channelCount):
        Port.__init__(self, channelCount)
    
    def __family__(self):
        return "Output"
    
    def __output__(self, chanel, value):
        raise NotImplementedError
        
    def __readInteger__(self):
        raise NotImplementedError
    
    def __writeInteger__(self, value):
        raise NotImplementedError

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
    
class GPIOPort(InputPort, OutputPort):
    def __init__(self, channelCount):
        InputPort.__init__(self, channelCount)
        OutputPort.__init__(self, channelCount)
        
    def __family__(self):
        return "GPIOPort"
    
        
class PCF8574(I2C, GPIOPort):
    def __init__(self, slave=0x20):
        slave = toint(slave)
        if slave in range(0x20, 0x28):
            name = "PCF8574"
        elif slave in range(0x38, 0x40):
            name = "PCF8574A"
        else:
            raise ValueError("Bad slave address for PCF8574(A) : 0x%02X not in range [0x20..0x27, 0x38..0x3F]" % slave)
        
        I2C.__init__(self, slave, name)
        GPIOPort.__init__(self, 8)
        
    def __input__(self, channel):
        mask = 1 << channel
        d = self.readByte()
        return (d & mask) == mask 

    def __readInteger__(self):
        return self.readByte()
    
    def __output__(self, channel, value):
        mask = 1 << channel
        b = self.readByte()
        if value:
            b |= mask
        else:
            b &= ~mask
        self.writeByte(b)

    def __writeInteger__(self, value):
        self.writeByte(value)
        
class PCF8574A(PCF8574):
    def __init__(self, slave=0x38):
        PCF8574.__init__(self, slave)
