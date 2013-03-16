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
from webiopi.devices.digital import GPIOPort
from webiopi.protocols.rest import *

class NativeGPIO(GPIOPort):
    def __init__(self):
        GPIOPort.__init__(self, 54)
        self.export = range(54)
        self.post_value = True
        self.post_function = True
        
    def __str__(self):
        return "GPIO"
    
    def checkChannelExported(self, channel):
        if not channel in self.export:
            raise GPIO.InvalidChannelException("Channel %d is not allowed" % channel)
        
    def checkPostingFunctionAllowed(self):
        if not self.post_function:
            raise ValueError("POSTing function to native GPIO not allowed")
    
    def checkPostingValueAllowed(self):
        if not self.post_value:
            raise ValueError("POSTing value to native GPIO not allowed")
    
    def __digitalRead__(self, channel):
        self.checkChannelExported(channel)
        return GPIO.input(channel)
    
    def __digitalWrite__(self, channel, value):
        self.checkChannelExported(channel)
        self.checkPostingValueAllowed()
        GPIO.output(channel, value)

    def __getFunction__(self, channel):
        self.checkChannelExported(channel)
        return GPIO.getFunction(channel)
    
    def __setFunction__(self, channel, value):
        self.checkChannelExported(channel)
        self.checkPostingFunctionAllowed()
        GPIO.setFunction(channel, value)
        
    def __portRead__(self):
        value = 0
        for i in self.export:
            value |= GPIO.input(i) << i
        return value 
            
    def __portWrite__(self, value):
        if len(self.export) < 54:
            for i in self.export:
                if GPIO.getFunction(i) == GPIO.OUT:
                    GPIO.output(i, (value >> i) & 1)
        else:
            raise Exception("Please limit exported GPIO to write integers")
            
    @request("GET", "*")
    @response(contentType=M_JSON)
    def wildcard(self, compact=False):
        if compact:
            f = "f"
            v = "v"
        else:
            f = "function"
            v = "value"
            
        values = {}
        for i in self.export:
            if compact:
                func = GPIO.getFunction(i)
            else:
                func = GPIO.getFunctionString(i)
            values[i] = {f: func, v: int(GPIO.input(i))}
        return values

    
    @request("GET", "%(channel)d/pulse", "%s")
    def getPulse(self, channel):
        self.checkChannelExported(channel)
        self.checkChannel(channel)
        return GPIO.getPulse(channel)
    
    @request("POST", "%(channel)d/sequence/%(args)s")
    @response("%d")
    def outputSequence(self, channel, args):
        self.checkChannelExported(channel)
        self.checkPostingValueAllowed()
        self.checkChannel(channel)
        (period, sequence) = args.split(",")
        period = int(period)
        GPIO.outputSequence(channel, period, sequence)
        return int(sequence[-1])
        
    @request("POST", "%(channel)d/pulse/")
    def pulse(self, channel):
        self.checkChannelExported(channel)
        self.checkPostingValueAllowed()
        self.checkChannel(channel)
        GPIO.pulse(channel)
        return "OK"
        
    @request("POST", "%(channel)d/pulseRatio/%(value)f")
    def pulseRatio(self, channel, value):
        self.checkChannelExported(channel)
        self.checkPostingValueAllowed()
        self.checkChannel(channel)
        GPIO.pulseRatio(channel, value)
        return GPIO.getPulse(channel)
        
    @request("POST", "%(channel)d/pulseAngle/%(value)f")
    def pulseAngle(self, channel, value):
        self.checkChannelExported(channel)
        self.checkPostingValueAllowed()
        self.checkChannel(channel)
        GPIO.pulseAngle(channel, value)
        return GPIO.getPulse(channel)
        
    def setup(self):
        pass
    
    def close(self):
        pass
