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
from webiopi.devices.i2c import I2C
from webiopi.devices.digital import GPIOPort

class MCP230XX(GPIOPort, I2C):
    IODIR   = 0x00
    IPOL    = 0x01
    GPINTEN = 0x02
    DEFVAL  = 0x03
    INTCON  = 0x04
    IOCON   = 0x05
    GPPU    = 0x06
    INTF    = 0x07
    INTCAP  = 0x08
    GPIO    = 0x09
    OLAT    = 0x0A
    
    BANK0_IOCON = 0x0A
    
    def __init__(self, slave, channelCount, name="MCP230XX"):
        I2C.__init__(self, toint(slave), name)
        GPIOPort.__init__(self, channelCount)
        self.banks = int(self.channelCount / 8)
        
    def getChannel(self, register, channel):
        self.checkChannel(channel)
        addr = register * self.banks + int(channel / 8) 
        mask = 1 << (channel % 8)
        return (addr, mask)
    
    def __input__(self, channel):
        (addr, mask) = self.getChannel(self.GPIO, channel) 
        d = self.readRegister(addr)
        return (d & mask) == mask

    def __output__(self, channel, value):
        (addr, mask) = self.getChannel(self.GPIO, channel) 
        d = self.readRegister(addr)
        if value:
            d |= mask
        else:
            d &= ~mask
        self.writeRegister(addr, d)
        
    def __getFunction__(self, channel):
        (addr, mask) = self.getChannel(self.IODIR, channel) 
        d = self.readRegister(addr)
        return GPIO.IN if (d & mask) == mask else GPIO.OUT
        
    def __setFunction__(self, channel, value):
        if not value in [GPIO.IN, GPIO.OUT]:
            raise ValueError("Requested function not supported")

        (addr, mask) = self.getChannel(self.IODIR, channel) 
        d = self.readRegister(addr)
        if value == GPIO.IN:
            d |= mask
        else:
            d &= ~mask
        self.writeRegister(addr, d)

    def __readInteger__(self):
        value = 0
        for i in range(self.banks):
            value |= self.readRegister(self.banks*self.GPIO+i) << 8*i
        return value
    
    def __writeInteger__(self, value):
        for i in range(self.banks):
            self.writeRegister(self.banks*self.GPIO+i,  (value >> 8*i) & 0xFF)

class MCP23008(MCP230XX):
    def __init__(self, slave=0x20):
        MCP230XX.__init__(self, slave, 8, "MCP23008")

class MCP23009(MCP230XX):
    def __init__(self, slave=0x20):
        MCP230XX.__init__(self, slave, 8, "MCP23009")

class MCP23017(MCP230XX):
    def __init__(self, slave=0x20):
        MCP230XX.__init__(self, slave, 16, "MCP23017")

class MCP23018(MCP230XX):
    def __init__(self, slave=0x20):
        MCP230XX.__init__(self, slave, 16, "MCP23018")

