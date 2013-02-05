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
from webiopi.onewire import OneWire
from webiopi.rest import *

class Temperature():
    def __getCelius__(self):
        raise NotImplementedError

    def __getFahrenheit__(self):
        raise NotImplementedError
    
    def Celcius2Fahrenheit(self):
        return 1.8*self.getCelcius() + 32

    def Fahrenheit2Celcius(self):
        return (self.getFahrenheit() - 32)/1.8

    @request("GET", "celcius")
    @response("%.02f")
    def getCelcius(self):
        return self.__getCelcius__()
    
    @request("GET", "fahrenheit")
    @response("%.02f")
    def getFahrenheit(self):
        return self.__getFahrenheit__()
    

class TMPXXX(I2C, Temperature):
    def __init__(self, slave=0b1001000, name="TMPXXX"):
        I2C.__init__(self, slave, name)
        
    def __getCelcius__(self):
        d = self.readBytes(2)
        return ((d[0] << 4) | (d[1] >> 4)) *0.0625
    
    def __getFahrenheit__(self):
        return self.Celcius2Fahrenheit()

class TMP075(TMPXXX):
    def __init__(self, slave=0b1001000):
        TMPXXX.__init__(self, slave, "TMP075")

class TMP102(TMPXXX):
    def __init__(self, slave=0b1001000):
        TMPXXX.__init__(self, slave, "TMP102")

class TMP275(TMPXXX):
    def __init__(self, slave=0b1001000):
        TMPXXX.__init__(self, slave, "TMP275")

class OneWireTemp(OneWire, Temperature):
    def __init__(self, slave=None, family=0, name="1-Wire-Temp"):
        OneWire.__init__(self, slave, family, "TEMP", name)
        
    def __getCelcius__(self):
        data = self.read()
        lines = data.split("\n")
        if lines[0].endswith("YES"):
            temp = lines[1][-5:]
            return int(temp) / 1000.0
    
    def __getFahrenheit__(self):
        return self.Celcius2Fahrenheit()

class DS18B20(OneWireTemp):
    def __init__(self, slave=None):
        OneWireTemp.__init__(self, slave, 0x28, "DS18B20")