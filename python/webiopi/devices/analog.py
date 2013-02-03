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
from webiopi.spi import SPI
from webiopi.rest import route
from webiopi.utils import *

class ADC():
    def __init__(self, resolution, channelCount):
        self.resolution = resolution
        self.channelCount = channelCount
        self.MAX = (2**resolution - 1) * 1.0 
 
    def __readInteger__(self, adcChannel, diff):
        raise NotImplementedError
    
    @route("GET", "%(adcChannel)d/integer", "%d")
    def readInteger(self, adcChannel, diff=False):
        if not adcChannel in range(self.channelCount):
            raise ValueError("Channel %d out of range [%d-%d]" % (adcChannel, 0, self.channelCount-1))
        return self.__readInteger__(adcChannel, diff)
    
    @route("GET", "%(adcChannel)d/float", "%.02f")
    def readFloat(self, adcChannel, diff=False):
        return self.readInteger(adcChannel, diff) / self.MAX
    
    @route("GET", "*/integer", "%s")
    def readAllInteger(self):
        values = {}
        for i in range(self.channelCount):
            values[i] = self.readInteger(i)
        return jsonDumps(values)
            
    @route("GET", "*/float", "%s")
    def readAllFloat(self):
        values = {}
        for i in range(self.channelCount):
            values[i] = self.readFloat(i)
        return jsonDumps(values)
    
class DAC():
    def __init__(self, resolution, channelCount):
        self.resolution = resolution
        self.channelCount = channelCount
        self.MAX = 2**resolution - 1 
    
    def __writeInteger__(self, dacChannel, value):
        raise NotImplementedError
    
    @route("POST", "%(dacChannel)d/integer/%(value)d")        
    def writeInteger(self, dacChannel, value):
        if not dacChannel in range(self.channelCount):
            raise ValueError("Channel %d out of range [%d-%d]" % (dacChannel, 0, self.channelCount-1))
        self.__writeInteger__(dacChannel, value)
    
    @route("POST", "%(dacChannel)d/float/%(value)f")        
    def writeFloat(self, dacChannel, value):
        self.writeInteger(dacChannel, int(value * self.MAX))

class MCP3X0X(SPI, ADC):
    def __init__(self, chip, resolution, channelCount):
        SPI.__init__(self, chip, 0, 8, 10000, "MCP3%d0%d" % (resolution-10, channelCount))
        ADC.__init__(self, resolution, channelCount)
        self.MSB_MASK = 2**(resolution-8) - 1

    def __str__(self):
        return "%s(chip=%d)" % (self.name, self.chip)

    def __readInteger__(self, adcChannel, diff):
        data = self.__command__(adcChannel, diff)
        r = self.xfer(data)
        return ((r[1] & self.MSB_MASK) << 8) | r[2]
    
class MCP300X(MCP3X0X):
    def __init__(self, chip, channelCount):
        MCP3X0X.__init__(self, chip, 10, channelCount)

    def __command__(self, mcpChannel, diff):
        d = [0x00, 0x00, 0x00]
        d[0] |= 1
        d[1] |= (not diff) << 7
        d[1] |= ((mcpChannel >> 2) & 0x01) << 6
        d[1] |= ((mcpChannel >> 1) & 0x01) << 5
        d[1] |= ((mcpChannel >> 0) & 0x01) << 4
        return d
        
class MCP3004(MCP300X):
    def __init__(self, chip):
        MCP300X.__init__(self, chip, 4)
        
class MCP3008(MCP300X):
    def __init__(self, chip):
        MCP300X.__init__(self, chip, 8)
        
class MCP320X(MCP3X0X):
    def __init__(self, chip, channelCount):
        MCP3X0X.__init__(self, chip, 12, channelCount)

    def __command__(self, mcpChannel, diff):
        d = [0x00, 0x00, 0x00]
        d[0] |= 1 << 2
        d[0] |= (not diff) << 1
        d[0] |= (mcpChannel >> 2) & 0x01
        d[1] |= ((mcpChannel >> 1) & 0x01) << 7
        d[1] |= ((mcpChannel >> 0) & 0x01) << 6
        return d
    
class MCP3204(MCP320X):
    def __init__(self, chip=0):
        MCP320X.__init__(self, chip, 4)
        
class MCP3208(MCP320X):
    def __init__(self, chip=0):
        MCP320X.__init__(self, chip, 8)
        
class MCP492X(SPI, DAC):
    def __init__(self, chip, channelCount):
        SPI.__init__(self, chip, 0, 8, 10000, "MCP492%d" % channelCount)
        DAC.__init__(self, 12, channelCount)
        self.channelCount = channelCount
        self.buffered=False
        self.gain=False
        self.shutdown=False

    def __str__(self):
        return "%s(chip=%d)" % (self.name, self.chip)

    def __writeInteger__(self, dacChannel, value):
        d = bytearray(2)
        d[0]  = 0
        d[0] |= (dacChannel & 0x01) << 7
        d[0] |= (self.buffered & 0x01) << 6
        d[0] |= (not self.gain & 0x01) << 5
        d[0] |= (not self.shutdown & 0x01) << 4
        d[0] |= (value >> 8) & 0x0F
        d[1]  = value & 0xFF
        self.writeBytes(d)

class MCP4921(MCP492X):
    def __init__(self, chip=0):
        MCP492X.__init__(self, chip, 1)

class MCP4922(MCP492X):
    def __init__(self, chip=0):
        MCP492X.__init__(self, chip, 2)
