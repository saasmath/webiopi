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
        
