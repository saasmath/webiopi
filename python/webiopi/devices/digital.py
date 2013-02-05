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

from webiopi.i2c import I2C
from webiopi.rest import *
from webiopi.utils import *

class Expander():
    def __init__(self, channelCount):
        self.channelCount = channelCount
        
    def __checkChannel__(self, channel):
        if not channel in range(self.channelCount):
            raise ValueError("Channel %d out of range [%d-%d]" % (channel, 0, self.channelCount-1))

    @request("GET", "channel-count")
    @response("%d")
    def getChannelCount(self):
        return self.channelCount

class GPIOExpander(Expander):
    def __init__(self, channelCount):
        Expander.__init__(self, channelCount)
    
    def __family__(self):
        return "GPIOExpander"
    
    def __input__(self, chanel):
        raise NotImplementedError
        
    def __output__(self, chanel, value):
        raise NotImplementedError
        
    def __readInteger__(self):
        raise NotImplementedError
    
    def __writeInteger__(self, value):
        raise NotImplementedError

    @request("GET", "%(channel)d")
    @response("%d")
    def input(self, channel):
        self.__checkChannel__(channel)
        return self.__input__(channel)

    @request("POST", "%(channel)d/%(value)d")
    @response("%d")
    def output(self, channel, value):
        self.__checkChannel__(channel)
        self.__output__(channel, value)
        return self.input(channel)  

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
        return self.__readInteger__(self)
    
    @request("POST", "integer/%(value)d")
    @response("%d")
    def writeInteger(self, value):
        self.__writeInteger__(value)
        return self.readInteger()
        
class PCF8574(I2C, GPIOExpander):
    def __init__(self, addr=0x20):
        I2C.__init__(self, addr, "PCF8574")
        GPIOExpander.__init__(self, 8)
        
    def __input__(self, channel):
        mask = 1 << channel
        d = self.readByte()
        return (d & mask) == mask 

    def __output__(self, channel, value):
        mask = 1 << channel
        b = self.readByte()
        if value:
            b |= mask
        else:
            b &= ~mask
        self.writeByte(b)

    def __readInteger__(self):
        return I2C.readByte(self)
    
    def __writeInteger__(self, value):
        I2C.writeByte(self, value)