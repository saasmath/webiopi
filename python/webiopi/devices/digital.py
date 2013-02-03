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
from webiopi.rest import route
from webiopi.utils import *

class PCF8574(I2C):
    def __init__(self, addr=0x20):
        I2C.__init__(self, addr, "PCF8574")
        self.channelCount = 8
        
    @route("GET", "%(channel)d/value", "%d")
    def input(self, channel):
        if not channel in range(self.channelCount):
            raise Exception("Channel %d out of range [%d-%d]" % (channel, 0, self.channelCount-1))

        mask = 1 << channel
        d = self.readByte()
        return (d & mask) == mask 

    @route("POST", "%(channel)d/value/%(value)d", "%d")
    def output(self, channel, value):
        if not channel in range(self.channelCount):
            raise Exception("Channel %d out of range [%d-%d]" % (channel, 0, self.channelCount-1))

        mask = 1 << channel
        b = self.readByte()
        if value:
            b |= mask
        else:
            b &= ~mask
        self.writeByte(b)
        return self.input(channel)  

    @route("GET", "*", "%s")
    def readAll(self):
        values = {}
        for i in range(self.channelCount):
            values[i] = int(self.input(i))
        return jsonDumps(values)

    @route("GET", "byte", "%d")
    def readByte(self):
        return I2C.readByte(self)
    
    @route("POST", "byte/%(value)d")
    def writeByte(self, value):
        I2C.writeByte(self, value)