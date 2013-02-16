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
from webiopi.devices.digital import Port
from webiopi.protocols.rest import *

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
    
class DAC(ADC):
    def __init__(self, channelCount, resolution):
        ADC.__init__(self, channelCount, resolution)
    
    def __family__(self):
        return "DAC"
    
    def __writeInteger__(self, channel, value):
        raise NotImplementedError
    
    @request("POST", "%(channel)d/integer/%(value)d")
    @response("%d")    
    def writeInteger(self, channel, value):
        self.checkChannel(channel)
        self.checkValue(value)
        self.__writeInteger__(channel, value)
        return self.readInteger(channel)
    
    @request("POST", "%(channel)d/float/%(value)f")        
    @response("%.2f")    
    def writeFloat(self, channel, value):
        self.writeInteger(channel, int(value * self.MAX))
        return self.readFloat(channel)
    

class PWM(DAC):
    def __init__(self, channelCount, resolution, frequency):
         DAC.__init__(self, channelCount, resolution)
         self.frequency = frequency
         self.period = 1.0/frequency
         
         # Futaba servos standard
         self.servo_neutral = 0.00152
         self.servo_travel_time = 0.0004
         self.servo_travel_angle = 45.0
         
         self.reverse = [False for i in range(channelCount)]
         
    def __family__(self):
        return "PWM"

    @request("GET", "%(channel)d/reverse")
    @response("%d")    
    def getReverse(self, channel):
        self.checkChannel(channel)
        return self.reverse[channel]
    
    @request("POST", "%(channel)d/reverse/%(value)b")
    @response("%d")    
    def setReverse(self, channel, value):
        self.checkChannel(channel)
        self.reverse[channel] = value
        return value
    
    @request("GET", "%(channel)d/angle")
    @response("%.2f")
    def readAngle(self, channel):
        f = self.readFloat(channel)
        f *= self.period
        f -= self.servo_neutral
        f *= self.servo_travel_angle
        f /= self.servo_travel_time

        if self.reverse[channel]:
            f = -f
        else:
            f = f
        return f
        
    @request("POST", "%(channel)d/angle/%(value)f")
    @response("%.2f")
    def writeAngle(self, channel, value):
        if self.reverse[channel]:
            f = -value
        else:
            f = value
        
        f *= self.servo_travel_time
        f /= self.servo_travel_angle
        f += self.servo_neutral
        f /= self.period
        
        self.writeFloat(channel, f)
        return self.readAngle(channel)

from webiopi.devices.analog.mcp3x0x import MCP3004, MCP3008, MCP3204, MCP3208
from webiopi.devices.analog.mcp492X import MCP4921, MCP4922
from webiopi.devices.analog.pca9685 import PCA9685