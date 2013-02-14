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

from webiopi.rest import *
from webiopi.utils import *
from webiopi.devices.i2c import *
from webiopi.devices.spi import *
from webiopi.devices.digital import *

class AnalogPort(Port):
    def __init__(self, channelCount, resolution):
        Port.__init__(self, channelCount)
        self.resolution = resolution
        self.MAX = 2**resolution - 1
    
    @request("GET", "resolution")
    @response("%d")
    def getResolution(self):
        return self.resolution
    
    @request("GET", "max-integer")
    @response("%d")
    def getMaxInteger(self):
        return int(self.MAX)
    
class ADC(AnalogPort):
    def __init__(self, channelCount, resolution):
        AnalogPort.__init__(self, channelCount, resolution)

    def __family__(self):
        return "ADC"
    
    def __readInteger__(self, channel, diff):
        raise NotImplementedError
    
    @request("GET", "%(channel)d/integer")
    @response("%d")
    def readInteger(self, channel, diff=False):
        self.checkChannel(channel)
        return self.__readInteger__(channel, diff)
    
    @request("GET", "%(channel)d/float")
    @response("%.2f")
    def readFloat(self, channel, diff=False):
        return self.readInteger(channel, diff) / self.MAX
    
    @request("GET", "*/integer")
    @response(contentType=M_JSON)
    def readAllInteger(self):
        values = {}
        for i in range(self.channelCount):
            values[i] = self.readInteger(i)
        return jsonDumps(values)
            
    @request("GET", "*/float")
    @response(contentType=M_JSON)
    def readAllFloat(self):
        values = {}
        for i in range(self.channelCount):
            values[i] = float("%.2f" % self.readFloat(i))
        return jsonDumps(values)
    
class DAC(AnalogPort):
    def __init__(self, channelCount, resolution):
        AnalogPort.__init__(self, channelCount, resolution)
    
    def __family__(self):
        return "DAC"
    
    def __writeInteger__(self, channel, value):
        raise NotImplementedError
    
    @request("POST", "%(channel)d/integer/%(value)d")        
    def writeInteger(self, channel, value):
        self.checkChannel(channel)
        self.checkValue(value)
        self.__writeInteger__(channel, value)
    
    @request("POST", "%(channel)d/float/%(value)f")        
    def writeFloat(self, channel, value):
        self.writeInteger(channel, int(value * self.MAX))

class PWM(DAC):
    def __init__(self, channelCount, resolution, frequency):
         DAC.__init__(self, channelCount, resolution)
         self.frequency = frequency
         self.period = 1.0/frequency
         
         # Futaba servos standard
         self.servo_neutral = 0.00152
         self.servo_travel_time = 0.0004
         self.servo_travel_angle = 45.0
         
    def __family__(self):
        return "PWM"
    
    @request("POST", "%(channel)d/angle/%(value)f")
    def writeAngle(self, channel, value):
        self.writeFloat(channel, (value*self.servo_travel_time/self.servo_travel_angle+self.servo_neutral)/self.period)
    

class MCP3X0X(SPI, ADC):
    def __init__(self, chip, channelCount, resolution):
        SPI.__init__(self, chip, 0, 8, 10000, "MCP3%d0%d" % (resolution-10, channelCount))
        ADC.__init__(self, channelCount, resolution)
        self.MSB_MASK = 2**(resolution-8) - 1

    def __str__(self):
        return "%s(chip=%d)" % (self.name, self.chip)

    def __readInteger__(self, channel, diff):
        data = self.__command__(channel, diff)
        r = self.xfer(data)
        return ((r[1] & self.MSB_MASK) << 8) | r[2]
    
class MCP300X(MCP3X0X):
    def __init__(self, chip, channelCount):
        MCP3X0X.__init__(self, chip, channelCount, 10)

    def __command__(self, channel, diff):
        d = [0x00, 0x00, 0x00]
        d[0] |= 1
        d[1] |= (not diff) << 7
        d[1] |= ((channel >> 2) & 0x01) << 6
        d[1] |= ((channel >> 1) & 0x01) << 5
        d[1] |= ((channel >> 0) & 0x01) << 4
        return d
        
class MCP3004(MCP300X):
    def __init__(self, chip=0):
        MCP300X.__init__(self, chip, 4)
        
class MCP3008(MCP300X):
    def __init__(self, chip=0):
        MCP300X.__init__(self, chip, 8)
        
class MCP320X(MCP3X0X):
    def __init__(self, chip, channelCount):
        MCP3X0X.__init__(self, chip, channelCount, 12)

    def __command__(self, channel, diff):
        d = [0x00, 0x00, 0x00]
        d[0] |= 1 << 2
        d[0] |= (not diff) << 1
        d[0] |= (channel >> 2) & 0x01
        d[1] |= ((channel >> 1) & 0x01) << 7
        d[1] |= ((channel >> 0) & 0x01) << 6
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
        DAC.__init__(self, channelCount, 12)
        self.buffered=False
        self.gain=False
        self.shutdown=False

    def __str__(self):
        return "%s(chip=%d)" % (self.name, self.chip)

    def __writeInteger__(self, channel, value):
        d = bytearray(2)
        d[0]  = 0
        d[0] |= (channel & 0x01) << 7
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


class PCA9685(PWM, I2C):
    
    MODE1    = 0x00
    PWM_BASE = 0x06
    PRESCALE = 0xFE
    
    M1_SLEEP    = 1<<4
    M1_AI       = 1<<5
    M1_RESTART  = 1<<7
    
    def __init__(self, slave=0x40, frequency=50):
        I2C.__init__(self, slave, "PCA9685")
        PWM.__init__(self, 16, 12, frequency)
        self.prescale = int(25000000.0/((2**12)*self.frequency))
        self.mode1 = self.M1_RESTART | self.M1_AI
        
        self.writeRegister(self.MODE1, self.M1_SLEEP)
        self.writeRegister(self.PRESCALE, self.prescale)
        time.sleep(0.01)

        self.writeRegister(self.MODE1, self.mode1)
    
    def __writeInteger__(self, channel, value):
        addr = int(channel * 4 + self.PWM_BASE) 
        d = bytearray(4)
        d[0] = 0
        d[1] = 0
        d[2] = (value & 0x0FF)
        d[3] = (value & 0xF00) >> 8
        self.writeRegisters(addr, d)
