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

class GPIOPort(Port):
    def __init__(self, channelCount):
        Port.__init__(self, channelCount)
    
    def __family__(self):
        return "GPIO"
    
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
    
class PCF8574(I2C, GPIOPort):
    FUNCTIONS = [GPIO.IN for i in range(8)]
    
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
        self.writeInteger(0xFF)
        self.readInteger()
        
    def __getFunction__(self, channel):
        return self.FUNCTIONS[channel]
    
    def __setFunction__(self, channel, value):
        if not value in [GPIO.IN, GPIO.OUT]:
            raise ValueError("Requested function not supported")
        self.FUNCTIONS[channel] = value
        
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
        I2C.__init__(self, slave, name)
        GPIOPort.__init__(self, channelCount)
        self.banks = int(channelCount / 8)
        
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

