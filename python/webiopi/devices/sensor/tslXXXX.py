#   Copyright 2013 Andreas Riegg
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


from webiopi.devices.i2c import *
from webiopi.devices.sensor import Luminosity

class TSL_LIGHT_X(I2C, Luminosity):
    VAL_COMMAND = 0x80
    REG_CONTROL = 0x00 | VAL_COMMAND
    REG_CONFIG  = 0x01 | VAL_COMMAND

    VAL_PWON    = 0x03
    VAL_PWOFF   = 0x00

    def __init__(self, slave=0b0111001, name="TSL_LIGHT_X"):
        I2C.__init__(self, toint(slave), name)  
        self.wake() # devices are powered down after power reset, wake them

    def wake(self):
        self.__wake__()

    def __wake__(self):
        self.writeRegister(self.REG_CONTROL, self.VAL_PWON)

    def sleep(self):
        self.__sleep__()
        
    def __sleep__(self):
        self.writeRegister(self.REG_CONTROL, self.VAL_PWOFF)         
    
class TSL2561X(TSL_LIGHT_X):
    VAL_TIME_402_MS   = 0x02
    VAL_TIME_101_MS   = 0x01
    VAL_TIME_14_MS    = 0x00
    VAL_INVALID       = -1
        
    REG_CHANNEL_0_LOW = 0x0C | TSL_LIGHT_X.VAL_COMMAND
    REG_CHANNEL_1_LOW = 0x0E | TSL_LIGHT_X.VAL_COMMAND
    
    MASK_GAIN         = 0x10
    MASK_TIME         = 0x03
  
    def __init__(self, slave=0b0111001, time=402, gain=1, name="TSL2561X"):
        TSL_LIGHT_X.__init__(self, slave, name)      
        time = toint(time)
        self.setTime(time)
        gain = toint(gain)
        self.setGain(gain)


    def __getLux__(self):
        ch0_bytes = self.readRegisters(self.REG_CHANNEL_0_LOW, 2)
        ch1_bytes = self.readRegisters(self.REG_CHANNEL_1_LOW, 2)
        ch0_word = ch0_bytes[1] << 8 | ch0_bytes[0]
        ch1_word = ch1_bytes[1] << 8 | ch1_bytes[0]
        if ch0_word == 0 | ch1_word == 0:
            return self.VAL_INVALID # Driver security, avoid crash in lux calculation
        else:
            return self.__calculateLux__(ch0_word, ch1_word)

    def setGain(self, gain):
        self.gain = gain
        self.__setGain__()

    def getGain(self):
        return self.__getGain__()

    def setTime(self, time):
        self.time = time
        self.__setTime__()

    def getTime(self):
        return self.__getTime__()

    def __setGain__(self):
        if self.gain == 1:
            bit_gain = 0
        elif self.gain == 16:
            bit_gain = 1
        else:
            raise ValueError("Gain %d out of range [%d,%d]" % (self.gain, 1, 16))
        new_byte_gain = (bit_gain << 4) & self.MASK_GAIN
        
        current_byte_config = self.readRegister(self.REG_CONFIG)
        new_byte_config = (current_byte_config & ~self.MASK_GAIN) | new_byte_gain
        self.writeByte(new_byte_config)
    
    def __getGain__(self):
        current_byte_config = self.readRegister(self.REG_CONFIG)
        if (current_byte_config & self.MASK_GAIN):
            return 16
        else:
            return 1

    def __setTime__(self):
        if not self.time in [14, 101, 402]:
            raise ValueError("Time %d out of range [%d,%d,%d]" % (self.time, 14, 101, 402))
        if self.time == 402:
            bits_time = self.VAL_TIME_402_MS
        elif self.time == 101:
            bits_time = self.VAL_TIME_101_MS
        elif self.time == 14:
            bits_time = self.VAL_TIME_14_MS            
        new_byte_time = bits_time & self.MASK_TIME

        current_byte_config = self.readRegister(self.REG_CONFIG)
        new_byte_config = (current_byte_config & ~self.MASK_TIME) | new_byte_time
        self.writeByte(new_byte_config)
        
    def __getTime__(self):
        current_byte_config = self.readRegister(self.REG_CONFIG)
        bits_time = (current_byte_config & self.MASK_TIME)
        if bits_time == self.VAL_TIME_402_MS:
            t = 402
        elif bits_time == self.VAL_TIME_101_MS:
            t = 101
        elif bits_time == self.VAL_TIME_14_MS:
            t =  14
        else:
            t = self.VAL_INVALID # indicates undefined
        return t
          
class TSL2561CS(TSL2561X):
    # Package CS (Chipscale) chip version
    def __init__(self, slave=0b0111001, time=402,  gain=1):
        TSL2561X.__init__(self, slave, time, gain, "TSL2561CS")

    def __calculateLux__(self, channel0_value, channel1value):
        channelRatio = channel1value / channel0_value
        if 0 < channelRatio <= 0.52:
            lux = 0.0315 * channel0_value - 0.0593 * channel0_value *(channelRatio**1.4)
        elif 0.52 < channelRatio <= 0.65:
            lux = 0.0229 * channel0_value - 0.0291 * channel1value
        elif 0.65 < channelRatio <= 0.80:
            lux = 0.0157 * channel0_value - 0.0180 * channel1value
        elif 0.80 < channelRatio <= 1.30:
            lux = 0.00338 * channel0_value - 0.00260 * channel1value
        else: # if channelRatio > 1.30
            lux = 0
        return lux
            
class TSL2561T(TSL2561X):
    # Package T (TMB-6)  chip version
    def __init__(self, slave=0b0111001, time=402, gain=1):
        TSL2561X.__init__(self, slave, time, gain, "TSL2561T")
        
    def __calculateLux__(self, channel0_value, channel1_value):
        channel_ratio = channel1_value / channel0_value
        if 0 < channel_ratio <= 0.50:
            lux = 0.0304 * channel0_value - 0.062 * channel0_value * (channel_ratio**1.4)
        elif 0.50 < channel_ratio <= 0.61:
            lux = 0.0224 * channel0_value - 0.031 * channel1_value
        elif 0.61 < channel_ratio <= 0.80:
            lux = 0.0128 * channel0_value - 0.0153 * channel1_value
        elif 0.80 < channel_ratio <= 1.30:
            lux = 0.00146 * channel0_value - 0.00112 * channel1_value
        else: # if channel_ratio > 1.30
            lux = 0
        return lux

